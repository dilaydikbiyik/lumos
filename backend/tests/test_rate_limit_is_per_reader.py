"""Every reader shared one rate-limit bucket behind the proxy."""
import base64
import json
from types import SimpleNamespace

from backend.limiter import reader_key


def _token(sub):
    body = base64.urlsafe_b64encode(json.dumps({"sub": sub}).encode()).decode().rstrip("=")
    return f"h.{body}.s"


def _request(headers):
    return SimpleNamespace(headers=headers, client=SimpleNamespace(host="10.0.0.1"))


def test_two_readers_behind_one_proxy_have_two_buckets():
    a = reader_key(_request({"authorization": f"Bearer {_token('user_a')}"}))
    b = reader_key(_request({"authorization": f"Bearer {_token('user_b')}"}))
    assert a == "user:user_a" and b == "user:user_b"


def test_a_visitor_is_keyed_by_the_forwarded_address_and_garbage_does_not_crash():
    # The proxy appends the real address on the right; the left is the client's say.
    assert reader_key(_request({"x-forwarded-for": "6.6.6.6, 1.2.3.4"})) == "ip:1.2.3.4"
    assert reader_key(_request({"authorization": "Bearer not-a-token"})) == "ip:10.0.0.1"


def test_a_partial_volatility_answer_is_filled_and_not_cached(monkeypatch):
    import pandas as pd

    from backend.services import volatility

    days = pd.bdate_range("2024-01-01", periods=300)
    stored = []
    monkeypatch.setattr(volatility.cache_service, "get", lambda k: None)
    monkeypatch.setattr(volatility.cache_service, "set", lambda k, v, **kw: stored.append(k))
    monkeypatch.setattr(volatility, "fetch_price_history",
                        lambda tickers, period="5y": {"XU100.IS": pd.Series(range(100, 400), index=days, dtype=float)})
    out = volatility.compute_volatility(["XU100.IS", "SPY"])
    assert set(out) == {"XU100.IS", "SPY"} and stored == []

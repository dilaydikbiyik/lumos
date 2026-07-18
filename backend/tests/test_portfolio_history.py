"""Daily holdings value series — live tickers move, flat assets don't."""
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd

from backend.services.portfolio_history import portfolio_value_history


def _holding(**kw):
    base = dict(
        id=1, asset_type="stock", ticker=None, quantity=None,
        purchase_date=None, purchase_amount=10000.0, manual_current_value=None,
    )
    base.update(kw)
    return SimpleNamespace(**base)


def _series(days, start=100.0, step=1.0):
    idx = pd.to_datetime([date.today() - timedelta(days=days - i) for i in range(days)])
    return pd.Series([start + step * i for i in range(days)], index=idx)


def test_live_holding_follows_prices_and_flat_stays_put():
    bought = date.today() - timedelta(days=20)
    live = _holding(id=1, asset_type="etf", ticker="SPY", purchase_date=bought,
                    purchase_amount=10000.0)
    cash = _holding(id=2, asset_type="cash", purchase_amount=5000.0, purchase_date=bought)

    with patch("backend.services.portfolio_history.fetch_price_history",
               return_value={"SPY": _series(40)}), \
         patch("backend.services.portfolio_history.enrich_holdings", return_value={}):
        out = portfolio_value_history([live, cash], days=30)

    assert out["live_count"] == 1 and out["flat_count"] == 1
    values = [p["value"] for p in out["series"]]
    # prices rise monotonically → the live part must push the series up
    assert values[-1] > values[0]
    # the flat 5000 TL is present on the last day
    assert values[-1] > 5000
    assert out["change_pct"] > 0


def test_holding_enters_series_only_after_purchase():
    bought = date.today() - timedelta(days=5)
    cash = _holding(id=1, asset_type="cash", purchase_amount=5000.0, purchase_date=bought)

    with patch("backend.services.portfolio_history.fetch_price_history", return_value={}), \
         patch("backend.services.portfolio_history.enrich_holdings", return_value={}):
        out = portfolio_value_history([cash], days=30)

    # No points before the purchase date (zero-value days are dropped)
    first = date.fromisoformat(out["series"][0]["date"])
    assert first >= bought


def test_summary_reports_monthly_plan_tracking(client):
    import asyncio

    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user
    from backend.repositories import user_repository
    from backend.tests.conftest import _TestSession

    app.dependency_overrides[get_current_user] = lambda: "user_plan_track"

    async def seed():
        async with _TestSession() as db:
            user = await user_repository.get_or_create(db, "user_plan_track")
            user.monthly_contribution = 10000
            await db.commit()

    asyncio.run(seed())

    res = client.post("/holdings", json={
        "asset_type": "cash", "name": "Bu ayın katkısı",
        "purchase_amount": 4000,
        "purchase_date": __import__("datetime").date.today().isoformat(),
    })
    assert res.status_code in (200, 201), res.text

    summary = client.get("/holdings/summary").json()
    assert summary["monthly_contribution"] == 10000
    assert summary["invested_this_month"] >= 4000


def test_practice_snapshot_counts_unpriced_slices_as_flat_base():
    """A 50% cash slice must dampen the weekly pct, not vanish from the base."""
    from backend.services import practice_mode

    with patch("backend.services.practice_mode.fetch_price_history",
               return_value={"SPY": _series(10, start=100, step=2)}):  # ~+10% week
        out = practice_mode.practice_snapshot({"SPY": 0.5, "CASH": 0.5}, 100000)

    # Base includes the flat 50k: total pct is roughly half of SPY's move
    assert out["current_value"] > 100000
    spy_pct = out["per_asset"]["SPY"]["weekly_change_pct"]
    assert abs(out["weekly_change_pct"] - spy_pct / 2) < 0.6
    assert out["per_asset"]["CASH"]["weekly_change_pct"] == 0.0
    assert out["biggest_mover"]["ticker"] == "SPY"


# ── Portfolio drift (post-purchase advice) ───────────────────────────────────

def test_drift_stays_quiet_when_the_mix_is_close_to_target():
    from backend.services.drift import compute_drift

    holdings = [_holding(id=1, asset_type="etf", purchase_amount=6000),
                _holding(id=2, asset_type="cash", purchase_amount=4000)]
    values = {1: 6000.0, 2: 4000.0}                       # 60 / 40
    target = [SimpleNamespace(category="stocks", weight=0.62),
              SimpleNamespace(category="cash", weight=0.38)]

    out = compute_drift(holdings, values, target)
    assert out["verdict"] == "balanced"
    assert out["max_drift_pct"] < 5
    # never nudges someone to trade over noise
    assert "gerekmiyor" in out["message"]


def test_drift_flags_a_winner_that_grew_into_an_outsized_bet():
    from backend.services.drift import compute_drift

    holdings = [_holding(id=1, asset_type="etf", purchase_amount=5000),
                _holding(id=2, asset_type="cash", purchase_amount=5000)]
    values = {1: 9000.0, 2: 3000.0}                       # 75 / 25 after a rally
    target = [SimpleNamespace(category="stocks", weight=0.50),
              SimpleNamespace(category="cash", weight=0.50)]

    out = compute_drift(holdings, values, target)
    assert out["verdict"] == "serious"
    assert out["max_drift_pct"] >= 10
    # the cheap remedy (steer new money) is preferred over selling
    assert "yeni katkılarını" in out["message"]
    assert "Lumos senin adına işlem yapmaz" in out["honesty_note"]


def test_drift_reports_unavailable_without_holdings():
    from backend.services.drift import compute_drift

    out = compute_drift([], {}, [SimpleNamespace(category="stocks", weight=1.0)])
    assert out["available"] is False


def test_drift_files_a_reit_etf_as_real_estate_not_stocks():
    """VNQ is recorded as an 'etf' holding; mapping by type alone would report
    'you own no real estate' while the user holds exactly that."""
    from backend.services.drift import compute_drift

    holdings = [_holding(id=1, asset_type="etf", ticker="VNQ", purchase_amount=5000),
                _holding(id=2, asset_type="etf", ticker="SPY", purchase_amount=5000)]
    values = {1: 5000.0, 2: 5000.0}
    target = [SimpleNamespace(category="reit", weight=0.5, ticker="VNQ"),
              SimpleNamespace(category="stocks", weight=0.5, ticker="SPY")]

    out = compute_drift(holdings, values, target)
    reit = next(r for r in out["rows"] if r["category"] == "reit")
    assert reit["actual_pct"] == 50.0      # not 0
    assert out["verdict"] == "balanced"


# ── EVDS batching (the province list used to time out) ───────────────────────

def test_evds_batches_are_fetched_in_parallel_and_survive_one_failure():
    """81 provinces = 6 chunks. Sequentially, at ~13s per round trip from a US
    datacenter, that exceeded every timeout. Chunks now run at once, and a
    failing chunk costs only its own series."""
    import time
    from unittest.mock import patch

    from backend.services import evds_service

    calls = []

    class _Resp:
        def __init__(self, code): self.code = code
        def raise_for_status(self): pass
        def json(self):
            return {"items": [{"Tarih": "2026-Q1", self.code.replace(".", "_"): "100"}]}

    def slow_get(url, **kw):
        calls.append(url)
        time.sleep(0.3)                      # simulate a slow round trip
        if "FAILME" in url:
            raise RuntimeError("chunk down")
        code = url.split("series=")[1].split("&")[0].split("-")[0]
        return _Resp(code)

    codes = [f"CODE{i}" for i in range(30)] + ["FAILME"]
    with patch("backend.services.evds_service.httpx.get", slow_get), \
         patch("backend.services.evds_service.cache_service.get", return_value=None), \
         patch("backend.services.evds_service.cache_service.set"), \
         patch("backend.services.evds_service.settings") as st:
        st.TCMB_EVDS_API_KEY = "x"
        started = time.time()
        out = evds_service.fetch_quarterly_series_batch(codes, "01-01-2010", "01-01-2026")
        elapsed = time.time() - started

    assert len(calls) == 3                   # 31 codes / 15 per chunk
    assert elapsed < 0.8                     # parallel, not 3 × 0.3s
    assert any(v for v in out.values())      # the healthy chunks still answered

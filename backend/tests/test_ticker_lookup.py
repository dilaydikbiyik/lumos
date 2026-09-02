"""
Ticker lookup: the add-asset form should fill itself from the symbol, and a
symbol that doesn't resolve must be reported rather than silently saved.
"""


def test_lookup_returns_name_price_and_currency(client, monkeypatch):
    from backend.services import ticker_lookup

    monkeypatch.setattr(ticker_lookup, "lookup", lambda t: {
        "ticker": "SPY", "name": "SPDR S&P 500 ETF Trust",
        "price": 765.53, "currency": "USD", "exchange": "PCX",
    })

    res = client.get("/holdings/lookup", params={"ticker": "spy"})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["name"] == "SPDR S&P 500 ETF Trust"
    assert body["price"] == 765.53
    assert body["currency"] == "USD"


def test_unknown_symbol_is_404_not_a_silent_success(client, monkeypatch):
    """A typo must surface now, not as broken live tracking weeks later."""
    from backend.services import ticker_lookup

    monkeypatch.setattr(ticker_lookup, "lookup", lambda t: None)
    assert client.get("/holdings/lookup", params={"ticker": "NOTREAL"}).status_code == 404


def test_absurd_symbol_is_rejected_before_the_network(client):
    assert client.get("/holdings/lookup", params={"ticker": "X" * 40}).status_code == 422


def test_lookup_caches_a_miss_so_upstream_is_not_hammered(monkeypatch):
    """Repeated bad symbols must not mean repeated upstream calls."""
    import uuid

    from backend.services import ticker_lookup

    # The cache is a real on-disk store shared across runs — a fixed symbol
    # would be already-cached on the second run and the test would pass for
    # the wrong reason (or fail, as it did).
    symbol = f"MISS{uuid.uuid4().hex[:8].upper()}"
    calls = {"n": 0}

    class _Fast:
        last_price = None

    class _Ticker:
        def __init__(self, symbol):
            calls["n"] += 1
            self.fast_info = _Fast()
            self.info = {}

    fake_yf = type("yf", (), {"Ticker": _Ticker})
    monkeypatch.setitem(__import__("sys").modules, "yfinance", fake_yf)

    assert ticker_lookup.lookup(symbol) is None
    assert ticker_lookup.lookup(symbol) is None
    assert calls["n"] == 1


def test_falls_back_to_the_download_path_when_fast_info_has_no_price(monkeypatch):
    """
    fast_info reaches a Yahoo endpoint that is unreliable from our datacenter:
    SPY resolved locally but 404'd from production while the app was pricing
    SPY fine elsewhere. Lookup must never be weaker than valuation.
    """
    from backend.services import market_data, ticker_lookup

    class _Fast:
        last_price = None
        currency = "USD"
        exchange = "PCX"

    class _Ticker:
        def __init__(self, symbol):
            self.fast_info = _Fast()
            self.info = {"longName": "SPDR S&P 500 ETF Trust"}

    monkeypatch.setitem(__import__("sys").modules, "yfinance", type("yf", (), {"Ticker": _Ticker}))
    monkeypatch.setattr(market_data, "fetch_current_price", lambda s: 765.5)

    result = ticker_lookup.lookup("FALLBACKSPY")
    assert result is not None
    assert result["price"] == 765.5
    assert result["name"] == "SPDR S&P 500 ETF Trust"


def test_missing_name_is_null_not_the_symbol_echoed_back(monkeypatch):
    """A price with no name must not silently become the stored asset name."""
    from backend.services import ticker_lookup

    monkeypatch.setattr(ticker_lookup, "_name_from_search", lambda s: None)

    class _Fast:
        last_price = 291.5
        currency = "TRY"
        exchange = "IST"

    class _Ticker:
        def __init__(self, symbol):
            self.fast_info = _Fast()

        @property
        def info(self):
            raise RuntimeError("info endpoint unavailable from this datacenter")

    monkeypatch.setitem(__import__("sys").modules, "yfinance", type("yf", (), {"Ticker": _Ticker}))

    result = ticker_lookup.lookup("NONAME.IS")
    assert result["price"] == 291.5
    assert result["name"] is None


def test_name_falls_back_to_search_when_info_is_unavailable(monkeypatch):
    """
    Ticker.info answers nothing from our production datacenter, so every
    lookup returned a price and no name — leaving the user typing the name
    the feature exists to remove. A second endpoint covers it.
    """
    from backend.services import ticker_lookup

    class _Fast:
        last_price = 764.79
        currency = "USD"
        exchange = "PCX"

    class _Ticker:
        def __init__(self, symbol):
            self.fast_info = _Fast()

        @property
        def info(self):
            raise RuntimeError("quoteSummary blocked from this datacenter")

    monkeypatch.setitem(__import__("sys").modules, "yfinance", type("yf", (), {"Ticker": _Ticker}))
    monkeypatch.setattr(ticker_lookup, "_name_from_search", lambda s: "State Street SPDR S&P 500 ETF Trust")

    result = ticker_lookup.lookup("SEARCHNAME1")
    assert result["name"] == "State Street SPDR S&P 500 ETF Trust"
    assert result["price"] == 764.79


def test_search_never_labels_a_holding_with_another_company(monkeypatch):
    """A fuzzy search hit must not become the asset's name."""
    import httpx

    from backend.services import ticker_lookup

    class _Res:
        status_code = 200

        @staticmethod
        def json():
            return {"quotes": [{"symbol": "SPYD", "longname": "Some Other Fund"}]}

    monkeypatch.setattr(httpx, "get", lambda *a, **k: _Res())
    assert ticker_lookup._name_from_search("SPY") is None


def test_a_failure_is_remembered_only_briefly(monkeypatch):
    """
    Upstream rate-limits us intermittently: MSFT resolved locally while
    production returned nothing. Caching that as "not found" for as long as a
    success would tell a user their valid symbol does not exist.
    """
    from backend.services import cache as cache_service
    from backend.services import ticker_lookup

    seen = {}
    monkeypatch.setattr(
        cache_service, "set",
        lambda key, value, ttl=None: seen.update({"value": value, "ttl": ttl}),
    )
    monkeypatch.setattr(ticker_lookup, "_name_from_search", lambda s: None)

    class _Fast:
        last_price = None

    class _Ticker:
        def __init__(self, symbol):
            self.fast_info = _Fast()
            self.info = {}

    monkeypatch.setitem(__import__("sys").modules, "yfinance", type("yf", (), {"Ticker": _Ticker}))
    monkeypatch.setattr("backend.services.market_data.fetch_current_price", lambda s: None)

    assert ticker_lookup.lookup("BLIPTEST1") is None
    assert seen["value"] == {}
    assert seen["ttl"] == ticker_lookup._MISS_TTL_SECONDS
    assert seen["ttl"] < ticker_lookup._TTL_SECONDS

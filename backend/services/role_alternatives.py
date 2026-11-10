"""
The other funds that could have played each role — offered while teaching.

The engine has to pick one fund per role, and a reader who only ever sees the
pick learns nothing about the choice. This shows, beside each fund the
portfolio can hold, the funds that could have stood in its place and what
actually differs between them — measured, not described: five-year
volatility, worst fall, and how long the fund has existed. Often the honest
answer is "almost nothing" (GLD and IAU, BND and AGG move together to the
decimal); sometimes it is a real lesson (a 7-10 year Treasury fund falls
harder than the whole bond market when rates rise).

Two kinds of alternative:

  * same_holdings — funds in this market's universe that share an overlap
    group, found from the same rule the engine uses. The app will never hold
    two of them together, because that would be one exposure under two names.
  * same_role — funds the universe does not hold, declared per market for the
    defensive sleeve and gold.

Like the stock explorer, it is impersonal by construction: it reads the
market and the reader's language and nothing about the reader. No row is
called better; rows are the role's fund first, then the others by name.
"""
import logging
from datetime import date

import numpy as np

from backend.exceptions import MarketDataError
from backend.i18n import t
from backend.markets import get_market_pack
from backend.services import cache as cache_service
from backend.services.market_data import fetch_price_history
from backend.services.portfolio_engine import _BOND_ASSET, _CASH_ASSET, _overlap_group

logger = logging.getLogger("lumos.role_alternatives")

_DAYS = 252
_WINDOW = 5
_CACHE_TTL = 12 * 3600


def _table(pack) -> dict[str, dict]:
    """role fund -> {"kind", "alternatives": [tickers]} for this market."""
    universe = [*pack.asset_universe, *pack.reit_assets]
    group_of = {a["ticker"]: _overlap_group(a) for a in universe}
    table: dict[str, dict] = {}
    for a in universe:
        same = [b["ticker"] for b in universe
                if b["ticker"] != a["ticker"] and group_of[b["ticker"]] == group_of[a["ticker"]]]
        if same:
            table[a["ticker"]] = {"kind": "same_holdings", "alternatives": same}
    for chosen, alts in pack.role_alternatives.items():
        entry = table.setdefault(chosen, {"kind": "same_role", "alternatives": []})
        entry["alternatives"] += [x["ticker"] for x in alts]
    return table


def _names(pack, lang: str) -> dict[str, str]:
    names = {a["ticker"]: a["name"] for a in [*pack.asset_universe, *pack.reit_assets]}
    for role, default in ((pack.cash_asset, _CASH_ASSET), (pack.bond_asset, _BOND_ASSET)):
        asset = role or default
        names[asset["ticker"]] = (t(asset["name_key"], lang) if "name_key" in asset
                                  else asset.get("name", asset["ticker"]))
    for alts in pack.role_alternatives.values():
        names.update({x["ticker"]: x["name"] for x in alts})
    return names


def _facts(market: str, tickers: list[str]) -> dict[str, dict]:
    """Measured facts per ticker, in the market's currency, cached per day.

    In the reader's currency: a Turkish reader was shown the T-bill fund at
    0.3% volatility and -0.3% at worst (its dollar figures) while the asset
    classes page showed them the same fund falling 35% in lira."""
    key = f"role_alternatives:v2:{market}:{date.today().isoformat()}"
    cached = cache_service.get(key)
    if cached is not None:
        return cached
    # One fetch, one basis (dividends reinvested) for every fund compared —
    # the same rule the stock explorer had to learn.
    from backend.services.fx_history import in_home_currency

    history = in_home_currency(fetch_price_history(tickers, period="max"),
                               get_market_pack(market).currency, "max")
    out = {}
    for tk in tickers:
        s = history.get(tk)
        if s is None or s.empty:
            continue
        s = s.dropna()
        recent = s.tail(_DAYS * _WINDOW)
        out[tk] = {
            "history_years": round(len(s) / _DAYS, 1),
            "volatility_pct": round(float(np.log(recent / recent.shift(1)).dropna().std()
                                          * np.sqrt(_DAYS)) * 100, 1),
            "worst_drop_pct": round(float((recent / recent.cummax() - 1).min()) * 100, 1),
        }
    cache_service.set(key, out, ttl=_CACHE_TTL)
    return out


def alternatives(market: str, lang: str) -> dict:
    pack = get_market_pack(market)
    table = _table(pack)
    tickers = sorted({tk for chosen, e in table.items() for tk in (chosen, *e["alternatives"])})
    try:
        facts = _facts(pack.code, tickers)
    except MarketDataError as exc:
        logger.warning("role alternatives: no market data (%s)", exc)
        return {"available": False, "market": pack.code, "roles": {}}

    names = _names(pack, lang)

    def row(tk: str) -> dict:
        return {"ticker": tk, "name": names.get(tk, tk),
                "holds": t(f"holds.{tk.replace('.', '_')}", lang),
                **facts.get(tk, {})}

    roles = {}
    for chosen, entry in table.items():
        others = sorted(entry["alternatives"], key=lambda tk: names.get(tk, tk).casefold())
        roles[chosen] = {
            "kind": entry["kind"],
            "note": t(f"alternatives.{entry['kind']}", lang),
            "window_years": _WINDOW,
            "rows": [row(chosen)] + [row(tk) for tk in others],
        }
    return {"available": True, "market": pack.code, "roles": roles}

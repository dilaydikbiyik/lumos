"""
Live holding valuation — "SPY'ım ikiye katlandı, görecek miyim?" sorusunun cevabı.

Değer kaynağı önceliği (dürüstlük etiketiyle birlikte döner):
  1. manual   — kullanıcının girdiği güncel değer her şeyi ezer
  2. live     — borsa varlıkları: yfinance güncel fiyat × adet
                (adet girilmediyse alış tarihi fiyatından türetilir)
  3. index    — emlak/arsa: TCMB ulusal konut endeksi oranıyla tahmin
                ("endekse göre tahmin" — parsel iddiası değil)
  4. purchase — hiçbir kaynak yoksa alış tutarı (değişim gösterilmez)

Fail-open: veri kaynakları çökerse sessizce purchase basis'e düşülür —
varlık listesi asla kırılmaz.
"""
import logging
from datetime import date
from typing import Optional

from backend.services import evds_service
from backend.services.market_data import fetch_price_history

logger = logging.getLogger("lumos.valuation")

EXCHANGE_TYPES = {"stock", "fund", "etf", "gold", "crypto"}
REAL_ESTATE_TYPES = {"real_estate", "land"}

NATIONAL_KFE_SERIES = "TP.KFE.TR"


def _price_on_or_before(series, target: date) -> Optional[float]:
    """En yakın (hedef tarihte veya öncesindeki) kapanış fiyatı."""
    try:
        eligible = series[series.index.date <= target]
        if len(eligible) == 0:
            return None
        return float(eligible.iloc[-1])
    except Exception:
        return None


def _exchange_values(holdings) -> dict[int, dict]:
    """Borsa varlıkları için canlı değerler — tek toplu yfinance çağrısı."""
    tickers = sorted({
        h.ticker for h in holdings
        if h.asset_type in EXCHANGE_TYPES and h.ticker
    })
    if not tickers:
        return {}

    try:
        history = fetch_price_history(tickers, period="10y")
    except Exception as exc:
        logger.warning("live valuation skipped — market data unavailable: %s", exc)
        return {}

    out: dict[int, dict] = {}
    for h in holdings:
        if h.asset_type not in EXCHANGE_TYPES or not h.ticker:
            continue
        series = history.get(h.ticker)
        if series is None or series.empty:
            continue

        latest = float(series.iloc[-1])

        units = h.quantity
        if units is None and h.purchase_date is not None:
            entry_price = _price_on_or_before(series, h.purchase_date)
            if entry_price and entry_price > 0:
                units = h.purchase_amount / entry_price

        if units is None:
            # Adet de alış tarihi de yok — canlı takip için veri yetersiz
            continue

        live_value = round(units * latest, 2)
        out[h.id] = {
            "value": live_value,
            "source": "live",
            "change_pct": round((live_value / h.purchase_amount - 1) * 100, 1)
            if h.purchase_amount else None,
        }
    return out


def _real_estate_values(holdings) -> dict[int, dict]:
    """Emlak/arsa için ulusal KFE endeksi oranıyla tahmini güncel değer."""
    re_holdings = [
        h for h in holdings
        if h.asset_type in REAL_ESTATE_TYPES and h.purchase_date is not None
    ]
    if not re_holdings:
        return {}

    try:
        earliest = min(h.purchase_date for h in re_holdings)
        index = evds_service.fetch_series(
            NATIONAL_KFE_SERIES,
            start=earliest.strftime("01-%m-%Y"),
            end=date.today().strftime("%d-%m-%Y"),
        )
    except Exception as exc:
        logger.warning("index valuation skipped — EVDS unavailable: %s", exc)
        return {}

    if not index:
        return {}

    months = sorted(index)
    latest_val = index[months[-1]]

    out: dict[int, dict] = {}
    for h in re_holdings:
        purchase_month = h.purchase_date.strftime("%Y-%m")
        # alış ayı veya öncesindeki en yakın endeks noktası
        base_months = [m for m in months if m <= purchase_month]
        if not base_months:
            continue
        base_val = index[base_months[-1]]
        if base_val <= 0:
            continue
        ratio = latest_val / base_val
        est = round(h.purchase_amount * ratio, 2)
        out[h.id] = {
            "value": est,
            "source": "index",
            "change_pct": round((ratio - 1) * 100, 1),
        }
    return out


def enrich_holdings(holdings) -> dict[int, dict]:
    """
    holding.id -> {"value", "source", "change_pct"} haritası.
    Öncelik: manual > live/index > purchase (haritada olmayanlar purchase'tır).
    """
    enrichment: dict[int, dict] = {}
    enrichment.update(_exchange_values(holdings))
    enrichment.update(_real_estate_values(holdings))

    # manual her şeyi ezer
    for h in holdings:
        if h.manual_current_value is not None:
            enrichment[h.id] = {
                "value": h.manual_current_value,
                "source": "manual",
                "change_pct": round((h.manual_current_value / h.purchase_amount - 1) * 100, 1)
                if h.purchase_amount else None,
            }
    return enrichment


def current_value(holding, enrichment: dict[int, dict]) -> float:
    """Tek varlığın bilinen en iyi değeri."""
    info = enrichment.get(holding.id)
    if info:
        return info["value"]
    return holding.purchase_amount

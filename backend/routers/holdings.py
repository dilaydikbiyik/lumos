import asyncio
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.i18n import t
from backend.middleware.language import language
from backend.limiter import limiter
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import holding_repository, user_repository
from backend.schemas.holding import (
    OFF_EXCHANGE_TYPES,
    VALUE_INSTEAD_OF_TICKER,
    CashErosion,
    HoldingCreate,
    HoldingRead,
    HoldingUpdate,
    PortfolioSummary,
)
from backend.markets import get_market_pack
from backend.services import fx_service, inflation_service, ticker_lookup
from backend.services.holdings_valuation import current_value, enrich_holdings, purchase_in

router = APIRouter()


@router.get("/lookup")
@limiter.limit("30/minute")
async def lookup_ticker(
    request: Request,
    ticker: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    Resolve a symbol to its real name, price and currency so the user does not
    have to type them — and so a mistyped symbol is caught before it is saved.

    The price also comes back in the USER's currency. Without that the client
    filled "quantity × price" into an amount field labelled in lira while the
    price was in dollars, storing a 48x-wrong number.
    """
    if not ticker or len(ticker) > 20:
        raise HTTPException(status_code=422, detail=t("error.invalid_symbol", lang))
    # yfinance is blocking HTTP — keep the event loop free
    result = await asyncio.to_thread(ticker_lookup.lookup, ticker)
    if result is None:
        # Deliberately not "this symbol does not exist": the upstream quote
        # service rate-limits us intermittently, so a failure here is often a
        # blip on a perfectly valid symbol. The client says so, and never
        # blocks the user from adding the asset by hand.
        raise HTTPException(status_code=404, detail=t("error.symbol_unverified", lang))

    user = await user_repository.get_or_create(db, user_id)
    user_ccy = _currency_of(user)
    asset_ccy = (result.get("currency") or "USD").upper()
    converted = await asyncio.to_thread(
        fx_service.convert, result["price"], asset_ccy, user_ccy
    )
    result["user_currency"] = user_ccy
    # None when the rate is unknown — the client then declines to auto-fill
    # rather than filling in a number from the wrong currency.
    result["price_in_user_currency"] = round(converted, 4) if converted is not None else None
    return result


def _currency_of(user) -> str:
    """The currency a user's totals are expressed in — their market's."""
    return get_market_pack(getattr(user, "market", None)).currency


# Names the portfolio engine writes from a translation key. A holding
# recorded from a recommendation stores the name in the language the reader
# had THEN, so a reader who switched to English kept seeing "Nakit / Kısa
# Vade" under "What you own". A stored name that is exactly one of these
# translations is the app's label, not the reader's, and is shown in their
# current language. Anything the reader typed themselves is left alone.
_ENGINE_NAME_KEYS = ("asset.cash.name", "asset.bond.name")
_ENGINE_NAMES = {t(key, lang): key for key in _ENGINE_NAME_KEYS for lang in ("tr", "en", "de")}


def _serialize(holding, enrichment: dict, lang: str = "tr") -> HoldingRead:
    read = HoldingRead.model_validate(holding)
    if read.name in _ENGINE_NAMES:
        read.name = t(_ENGINE_NAMES[read.name], lang)
    info = enrichment.get(holding.id)
    read.current_value = info["value"] if info else holding.purchase_amount
    read.value_source = info["source"] if info else "purchase"
    read.value_change_pct = info.get("change_pct") if info else None
    return read


@router.get("", response_model=list[HoldingRead])
@limiter.limit("30/minute")
async def list_holdings(
    request: Request,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    user = await user_repository.get_or_create(db, user_id)
    holdings = await holding_repository.list_for_user(db, user.id)
    # enrich_holdings calls yfinance (sync HTTP) — run in thread pool
    enrichment = await asyncio.to_thread(enrich_holdings, holdings, _currency_of(user),
                                         user.market or "TR")
    return [_serialize(h, enrichment, lang) for h in holdings]


@router.post("", response_model=HoldingRead, status_code=201)
async def create_holding(
    body: HoldingCreate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    # Gold and crypto are the two exchange types a reader often holds OFF an
    # exchange: metal in a drawer, a bank gold account, coins in their own
    # wallet. Requiring a ticker for those meant the most common holding of
    # a Turkish beginner — physical gold — could not be recorded as gold at
    # all, on the same screen the gold card explains that drawer gold is its
    # own thing. A value the reader states is enough; valuation already
    # prefers a manual value over everything and skips ticker-less holdings.
    #
    # The message used to be hard-coded English, so a Turkish or German
    # reader who hit it was told why in a language they had not chosen.
    if body.asset_type not in OFF_EXCHANGE_TYPES and not body.ticker:
        stated_value = body.asset_type in VALUE_INSTEAD_OF_TICKER and body.manual_current_value
        if not stated_value:
            raise HTTPException(status_code=422, detail=t("holdings.tickerRequired", lang))
    user = await user_repository.get_or_create(db, user_id)
    payload = body.model_dump()
    # Amounts are always entered in the currency the UI is showing, which is
    # the market's. Recording it removes the assumption that every stored
    # figure is lira — the assumption that let dollars be compared to lira.
    payload.setdefault("currency", None)
    payload["currency"] = payload.get("currency") or _currency_of(user)
    return await holding_repository.create(db, user.id, payload)


@router.patch("/{holding_id}", response_model=HoldingRead)
async def update_holding(
    holding_id: int,
    body: HoldingUpdate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    user = await user_repository.get_or_create(db, user_id)
    holding = await holding_repository.get_for_user(db, user.id, holding_id)
    if holding is None:
        raise HTTPException(status_code=404, detail=t("holdings.notFound", lang))
    changes = body.model_dump(exclude_unset=True)
    return await holding_repository.update(db, holding, changes)


@router.delete("/{holding_id}", status_code=204)
async def delete_holding(
    holding_id: int,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    user = await user_repository.get_or_create(db, user_id)
    holding = await holding_repository.get_for_user(db, user.id, holding_id)
    if holding is None:
        raise HTTPException(status_code=404, detail=t("holdings.notFound", lang))
    await holding_repository.delete(db, holding)


@router.get("/history")
@limiter.limit("20/minute")
async def value_history(
    request: Request,
    # Out-of-range values used to be clamped silently; now they are refused.
    days: int = Query(30, ge=7, le=365),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Daily value series of the user's holdings — live tickers follow real
    closes, everything else is carried flat at its best-known value."""
    from backend.services.portfolio_history import portfolio_value_history

    user = await user_repository.get_or_create(db, user_id)
    holdings = await holding_repository.list_for_user(db, user.id)
    return await asyncio.to_thread(portfolio_value_history, holdings, days,
                                   _currency_of(user), user.market or "TR")


@router.get("/drift")
@limiter.limit("20/minute")
async def portfolio_drift(
    request: Request,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """Has the portfolio drifted away from what the risk profile called for?
    The target is recomputed from the saved risk score, so nothing is stored."""
    from backend.services import path_portfolio
    from backend.services.drift import compute_drift

    user = await user_repository.get_or_create(db, user_id)
    if user.risk_score is None:
        return {"available": False, "reason": t("error.no_profile", lang)}

    holdings = await holding_repository.list_for_user(db, user.id)
    if not holdings:
        return {"available": False, "reason": t("drift.none", lang)}

    enrichment = await asyncio.to_thread(enrich_holdings, holdings, _currency_of(user),
                                         user.market or "TR")
    values = {h.id: current_value(h, enrichment) for h in holdings}
    # The market picks the investable universe, so the drift target has to be
    # built against the user's own market — comparing a German portfolio to a
    # Turkish target would invent drift that isn't there.
    # The plan the reader was given, for their path — the whole plan, since
    # the holdings are everything they own. Built as given (no property
    # "already committed"): a home bought with the plan's property part is
    # the plan being followed, not a reason to re-plan the target around it.
    target, plan = await asyncio.to_thread(
        lambda: path_portfolio.build_for_path(
            user.investment_path, user.risk_score, user.budget or sum(values.values()),
            user.market or "TR", lang, monthly_outgoings=user.monthly_outgoings,
        )
    )
    return compute_drift(holdings, values, path_portfolio.plan_targets(target, plan, user.market or "TR", holdings), lang)


@router.get("/health")
@limiter.limit("20/minute")
async def health_score(
    request: Request,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """Fener: 0-100 portfolio health with plain-language notes."""
    from backend.services.health_score import compute_health

    user = await user_repository.get_or_create(db, user_id)
    holdings = await holding_repository.list_for_user(db, user.id)
    enrichment = await asyncio.to_thread(enrich_holdings, holdings, _currency_of(user),
                                         user.market or "TR")
    by_type: dict[str, float] = {}
    for h in holdings:
        by_type[h.asset_type] = by_type.get(h.asset_type, 0.0) + current_value(h, enrichment)
    return compute_health(by_type, lang)


@router.get("/summary", response_model=PortfolioSummary)
@limiter.limit("20/minute")
async def portfolio_summary(
    request: Request,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Wealth snapshot: total invested, best-known current value, and how much
    of the declared budget is still uninvested.
    """
    user = await user_repository.get_or_create(db, user_id)
    holdings = await holding_repository.list_for_user(db, user.id)

    enrichment = await asyncio.to_thread(enrich_holdings, holdings, _currency_of(user),
                                         user.market or "TR")
    ccy = _currency_of(user)
    total_invested = sum(purchase_in(h, ccy) for h in holdings)
    total_value = sum(current_value(h, enrichment) for h in holdings)
    by_type: dict[str, float] = {}
    for h in holdings:
        by_type[h.asset_type] = by_type.get(h.asset_type, 0.0) + current_value(h, enrichment)

    remaining = None
    if user.budget is not None:
        remaining = max(user.budget - total_invested, 0.0)

    # "Param eriyor mu?" — idle cash + uninvested budget both lose real value monthly
    idle_cash = by_type.get("cash", 0.0) + (remaining or 0.0)
    cash_erosion = None
    if idle_cash > 0:
        # The user's OWN market. This omitted the argument, so the default
        # applied and every US and German reader was shown Turkish
        # inflation eating their cash: 100.000 idle came back as 2.025 lost
        # per month when the German figure is 548. A frightening number
        # that is 3.7x too large is worse than no number, and this one sits
        # under a heading that asks "is my money melting?".
        erosion = inflation_service.monthly_cash_erosion(
            idle_cash, market=user.market or "TR")
        cash_erosion = CashErosion(
            **erosion,
            idle_cash=round(idle_cash, 2),
            cash_holdings=round(by_type.get("cash", 0.0), 2),
            uninvested_budget=round(remaining or 0.0, 2),
        )

    # Monthly-plan tracking: what entered the portfolio this calendar month
    today = date.today()
    invested_this_month = sum(
        purchase_in(h, ccy) for h in holdings
        if (h.purchase_date or (h.created_at.date() if h.created_at else None))
        and (h.purchase_date or h.created_at.date()).year == today.year
        and (h.purchase_date or h.created_at.date()).month == today.month
    )

    return PortfolioSummary(
        total_budget=user.budget,
        total_invested=total_invested,
        remaining_budget=remaining,
        total_current_value=total_value,
        holdings_count=len(holdings),
        by_type=by_type,
        cash_erosion=cash_erosion,
        monthly_contribution=user.monthly_contribution,
        invested_this_month=round(invested_this_month, 2),
    )

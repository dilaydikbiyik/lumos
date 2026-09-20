from typing import Literal, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, model_validator
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.auth import permissions as perms
from backend.i18n import t
from backend.middleware.language import language
from backend.limiter import limiter
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import holding_repository, user_repository

router = APIRouter()

FearTag = Literal["param_eriyor", "kandirilirim", "anlamiyorum", "batiririm"]


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    clerk_user_id: str
    email: Optional[str]
    risk_score: Optional[float]
    budget: Optional[float]
    investment_path: Optional[str]
    plan: str = "free"
    market: str = "TR"
    primary_fear: Optional[str]
    monthly_income: Optional[float] = None
    monthly_outgoings: Optional[float] = None
    monthly_contribution: Optional[float] = None
    # The client needs these to decide which controls to OFFER; every
    # privileged endpoint still checks server-side, so hiding a button is a
    # courtesy and never the access control itself.
    role: str = "user"
    permissions: list[str] = []

    @model_validator(mode="after")
    def _derive_permissions(self):
        # Derived from the role, never stored: two places holding the same
        # truth is how a revoked role keeps its powers.
        object.__setattr__(self, "permissions",
                           sorted(perms.permissions_for(self.role)))
        return self


class MonthlyIncomeUpdate(BaseModel):
    monthly_income: float


class MonthlyOutgoingsUpdate(BaseModel):
    """Rent plus essential monthly costs — not the same number as income."""
    monthly_outgoings: float


class InvestmentPathUpdate(BaseModel):
    # Flow 0 — chosen journey: stocks-only / real-estate-only / both / let AI suggest
    investment_path: Literal["stocks", "real_estate", "hybrid", "undecided"]


class FearCheckInUpdate(BaseModel):
    primary_fear: FearTag


@router.get("/me", response_model=UserRead)
async def get_me(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """GET /users/me — return the current user's saved data."""
    return await user_repository.get_or_create(db, user_id)


@router.patch("/me/investment-path", response_model=UserRead)
async def update_investment_path(
    body: InvestmentPathUpdate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """PATCH /users/me/investment-path — set the user's chosen journey (Flow 0)."""
    return await user_repository.set_investment_path(db, user_id, body.investment_path)


@router.patch("/me/income", response_model=UserRead)
async def update_monthly_income(
    body: MonthlyIncomeUpdate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """PATCH /users/me/income — save the user's monthly net income once so
    affordability checks never have to re-ask for it."""
    return await user_repository.set_monthly_income(db, user_id, body.monthly_income)


@router.patch("/me/outgoings", response_model=UserRead)
async def update_monthly_outgoings(
    body: MonthlyOutgoingsUpdate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    PATCH /users/me/outgoings — rent plus essential monthly costs.

    Separate from income on purpose. The emergency reserve is six months of
    what someone SPENDS, and the budget planner was being handed income in
    its place: a reader earning 40,000 and spending 15,000 was told to hold
    back 240,000 instead of 90,000, which shrank every other part of the plan
    behind it.
    """
    return await user_repository.set_monthly_outgoings(db, user_id, body.monthly_outgoings)


@router.patch("/me/fear-check-in")
async def fear_check_in(
    body: FearCheckInUpdate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    Onboarding fear check-in — "what scares you most about investing?"
    Returns immediate, tag-specific reassurance (zero AI cost).
    """
    user = await user_repository.set_primary_fear(db, user_id, body.primary_fear)
    return {
        "primary_fear": user.primary_fear,
        # Reassurance matched to the stated fear — no AI call needed
        "reassurance": t(f"fear.{body.primary_fear}", lang),
    }


@router.get("/me/readiness")
async def readiness_score(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Courage indicator — a simple, transparent 0-100 readiness score built
    from concrete milestones the user has actually completed. No mystery
    algorithm: every point is explained.
    """
    user = await user_repository.get_or_create(db, user_id)
    holdings = await holding_repository.list_for_user(db, user.id)

    # Stable keys, not sentences: the client owns the wording, so the
    # checklist speaks whatever language the reader picked.
    milestones = {
        "risk_profile": user.risk_score is not None,
        "path_chosen": user.investment_path is not None,
        "fear_shared": user.primary_fear is not None,
        "first_holding": len(holdings) > 0,
        "three_holdings": len(holdings) >= 3,
    }
    score = round(sum(milestones.values()) / len(milestones) * 100)

    return {
        "score": score,
        "milestones": milestones,
        "ready_for_real_investing": score >= 60,
    }


class MarketUpdate(BaseModel):
    market: str


@router.get("/markets")
async def list_markets():
    """Available Market Packs — for the market selector."""
    from backend.markets import public_markets

    return {"markets": public_markets()}


@router.get("/markets/pack")
@limiter.limit("30/minute")
async def market_pack_content(
    request: Request,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The educational content for the user's market, in the UI's language.

    Market and language are separate choices: an English reader investing in
    Germany needs German RULES in English PROSE. This endpoint is where the
    two meet — the pack supplies the facts, the header supplies the wording.
    """
    from backend.markets import get_market_pack
    from backend.middleware.language import get_language

    user = await user_repository.get_or_create(db, user_id)
    pack = get_market_pack(user.market)
    lang = get_language(request)
    return {
        "code": pack.code,
        "name": pack.name,
        "currency": pack.currency,
        "regulator": pack.regulator,
        "broker_note": pack.say("broker_note", lang),
        "tax_note": pack.say("tax_note", lang),
        "disclaimer": pack.say("disclaimer", lang),
        "fear_options": pack.fears(lang),
        "live_inflation": pack.inflation_source != "none",
        "live_housing_index": pack.housing_index_source != "none",
        "regional_housing_breakdown": pack.regional_housing_breakdown,
        "listing_sites": [site.name for site in pack.listing_sites],
        "assumptions": {
            "mortgage_rate_pct": pack.mortgage_rate_pct,
            "mortgage_term_years": pack.mortgage_term_years,
            "transfer_tax_pct": pack.transfer_tax_pct,
            "agency_commission_pct": pack.agency_commission_pct,
            "vat_pct": pack.vat_pct,
            "annual_upkeep_pct": pack.annual_upkeep_pct,
        },
    }


@router.patch("/me/market", response_model=UserRead)
async def update_market(
    body: MarketUpdate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change the user's market pack (TR/US/DE)."""
    from fastapi import HTTPException

    from backend.markets import MARKET_PACKS
    from backend.repositories import user_repository

    code = body.market.upper()
    if code not in MARKET_PACKS:
        raise HTTPException(status_code=422, detail=f"Unknown market '{code}'. Available: {list(MARKET_PACKS)}")

    return await user_repository.set_market(db, user_id, code)


class AccountDeletion(BaseModel):
    """
    A typed confirmation rather than a bare DELETE.

    The client must echo the user's own id back. It is not a security control
    — the token already proves who is calling — it is a guard against a stray
    request, a double-tapped button or a replayed call erasing an account
    that nobody meant to erase.
    """
    confirm_user_id: str


@router.delete("/me")
@limiter.limit("3/hour")
async def delete_me(
    request: Request,
    body: AccountDeletion,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    Erase the account: our rows first, then the Clerk login.

    Apple requires deletion to be reachable from inside the app for anything
    that lets you create an account, and "email us and we will get to it" does
    not qualify. Order matters — if Clerk went first and our delete then
    failed, the rows would be orphaned with no login left that could ever ask
    for them again.
    """
    from fastapi import HTTPException

    from backend.services import clerk_service

    if body.confirm_user_id != user_id:
        raise HTTPException(status_code=400, detail=t("account.confirmMismatch", lang))

    await user_repository.delete_account(db, user_id)
    identity_removed = clerk_service.delete_user(user_id)

    # Say which half happened. Reporting a clean deletion when the login is
    # still alive is the one failure the user would discover by themselves.
    return {
        "data_deleted": True,
        "identity_deleted": identity_removed,
        "message": t("account.deleted" if identity_removed
                     else "account.deletedDataOnly", lang),
    }


@router.get("/me/path-suggestion")
async def path_suggestion(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    A suggested path for someone who answered "not sure yet".

    Rule-based, not an LLM call, for the same reason `readiness_score` is:
    a beginner told which world to start in deserves reasons they can argue
    with. "The model said so" is not one, and a model asked twice need not
    answer the same way.

    A SUGGESTION. Nothing is saved; the user still chooses.
    """
    from backend.markets import get_market_pack
    from backend.services import path_advisor

    user = await user_repository.get_or_create(db, user_id)
    pack = get_market_pack(user.market or "TR")

    result = path_advisor.suggest(
        horizon=user.time_horizon,
        budget=user.budget,
        primary_fear=user.primary_fear,
        entry_threshold=pack.property_entry_threshold,
    )
    return {
        "path": result.path,
        "confident": result.confident,
        # Sentences, in the reader's language — the engine writes prose here
        # the same way every other engine in the app does.
        "reasons": [t(key, lang) for key in result.reasons],
        "entry_threshold": pack.property_entry_threshold,
        "currency": pack.currency,
    }


@router.get("/me/plans")
async def list_plans(user_id: str = Depends(get_current_user)):
    """AI plan tiers — pricing page payload (billing-ready)."""
    from backend.services.ai_tiers import public_tiers

    return {"plans": public_tiers()}

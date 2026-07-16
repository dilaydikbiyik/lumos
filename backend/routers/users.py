from typing import Literal, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import holding_repository, user_repository

router = APIRouter()

FearTag = Literal["param_eriyor", "kandirilirim", "anlamiyorum", "batiririm"]

# Reassurance copy shown once, matched to the stated fear — no AI call needed
_FEAR_REASSURANCE = {
    "param_eriyor": "Anlıyoruz — bu yüzden her portföyde enflasyona karşı reel getiriyi de göstereceğiz, sadece nominal sayıyı değil.",
    "kandirilirim": "Bu haklı bir endişe. Lumos sana hiçbir hisse/fon satmıyor, komisyon almıyor — sadece bilgi veriyor. Kararı hep sen verirsin.",
    "anlamiyorum": "Sorun değil, kimse doğuştan bilmiyor. Her terimi günlük dille açıklayacağız — anlamadığın hiçbir şeyi geçmeyeceğiz.",
    "batiririm": "Bu korku çoğu yeni başlayanda var. Küçük adımlarla, sanal pratikle başlayacağız — gerçek parayla asla acele etmeyeceksin.",
}


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


class MonthlyIncomeUpdate(BaseModel):
    monthly_income: float


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


@router.patch("/me/fear-check-in")
async def fear_check_in(
    body: FearCheckInUpdate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Onboarding fear check-in — "what scares you most about investing?"
    Returns immediate, tag-specific reassurance (zero AI cost).
    """
    user = await user_repository.set_primary_fear(db, user_id, body.primary_fear)
    return {
        "primary_fear": user.primary_fear,
        "reassurance": _FEAR_REASSURANCE[body.primary_fear],
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

    milestones = {
        "Risk profilini tamamladın": user.risk_score is not None,
        "Yatırım yolunu seçtin": user.investment_path is not None,
        "Korkunu paylaştın": user.primary_fear is not None,
        "İlk varlığını ekledin": len(holdings) > 0,
        "En az 3 varlık takip ediyorsun": len(holdings) >= 3,
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


@router.get("/me/plans")
async def list_plans(user_id: str = Depends(get_current_user)):
    """AI plan tiers — pricing page payload (billing-ready)."""
    from backend.services.ai_tiers import public_tiers

    return {"plans": public_tiers()}

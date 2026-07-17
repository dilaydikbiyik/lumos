from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

AssetType = Literal[
    "stock", "fund", "etf", "real_estate", "land",
    "vehicle", "gold", "crypto", "cash", "other",
]

# Assets that cannot be priced from an exchange — user provides valuations
OFF_EXCHANGE_TYPES = {"real_estate", "land", "vehicle", "cash", "other"}


# Optional 1-tap emotion tag at purchase time — feeds the monthly behavior report
EmotionTag = Literal["plan", "fomo", "tuyo", "panik"]


class HoldingCreate(BaseModel):
    asset_type: AssetType
    name: str = Field(..., min_length=1, max_length=120)
    ticker: Optional[str] = Field(None, max_length=20)
    purchase_date: Optional[date] = None
    purchase_amount: float = Field(..., gt=0)
    quantity: Optional[float] = Field(None, gt=0)
    manual_current_value: Optional[float] = Field(None, gt=0)
    note: Optional[str] = Field(None, max_length=1000)
    emotion_tag: Optional[EmotionTag] = None


class HoldingUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    purchase_date: Optional[date] = None
    purchase_amount: Optional[float] = Field(None, gt=0)
    quantity: Optional[float] = Field(None, gt=0)
    manual_current_value: Optional[float] = Field(None, gt=0)
    note: Optional[str] = Field(None, max_length=1000)


class HoldingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_type: AssetType
    name: str
    ticker: Optional[str]
    purchase_date: Optional[date]
    purchase_amount: float
    quantity: Optional[float]
    manual_current_value: Optional[float]
    note: Optional[str]
    emotion_tag: Optional[EmotionTag]
    created_at: datetime

    # Live valuation (filled by holdings_valuation.py — not stored in the DB)
    current_value: Optional[float] = None
    value_source: Optional[str] = None   # manual | live | index | purchase
    value_change_pct: Optional[float] = None


class CashErosion(BaseModel):
    """'Param eriyor mu?' — real monthly purchasing-power loss on idle cash."""
    monthly_inflation_pct: float
    erosion_amount: float
    # What the erosion was computed ON (cash holdings + uninvested budget) —
    # the UI must name this amount, not a different field
    idle_cash: float = 0.0


class PortfolioSummary(BaseModel):
    """Wealth snapshot: what you own, what you spent, what's left of the budget."""
    total_budget: Optional[float]
    total_invested: float
    remaining_budget: Optional[float]
    total_current_value: float
    holdings_count: int
    by_type: dict[str, float]  # asset_type -> current value
    cash_erosion: Optional[CashErosion] = None
    # Monthly-plan tracking (quiz Q1: "her ay düzenli"): the planned amount
    # and what was actually recorded this calendar month
    monthly_contribution: Optional[float] = None
    invested_this_month: float = 0.0

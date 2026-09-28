"""
Fill a demo account so a store reviewer sees the app, not the quiz.

Why this exists. Apple and Google reviewers get a fresh account and roughly
one minute of patience. Lumos asks nine questions before it shows anything,
which is right for a nervous beginner and fatal for a reviewer: they will see
question one, conclude the app does nothing, and reject it. The submission
notes carry demo credentials; this is what makes those credentials worth
having.

    python -m scripts.seed_demo_account user_xxxxxxxxxxxx [--market TR]

The Clerk account itself is NOT created here — that is a console action, and
this script deliberately does not touch identity. It fills the app-side rows
for a Clerk user id that already exists.

THE HOLDINGS ARE DELIBERATELY UNFLATTERING. One position is down, one is
roughly flat, and one carries a `fomo` tag, because a demo portfolio where
everything is up teaches a reviewer that the app is a brochure. The features
worth reviewing — the real-return honesty, the behaviour mirror, the drift
check — only say anything interesting when something has gone wrong.

Safe to re-run: it clears this user's holdings first, so a half-finished run
does not leave doubled positions behind.
"""

import argparse
import asyncio
import sys
from datetime import date, timedelta

from backend.db.database import AsyncSessionLocal
from backend.markets import get_market_pack
from backend.repositories import holding_repository, user_repository


def _holdings(market: str) -> list[dict]:
    """A small, honest portfolio in this market's own instruments."""
    pack = get_market_pack(market)
    today = date.today()

    # Picked from the pack rather than hardcoded: a German reviewer must not
    # be shown a position their broker would refuse to sell them.
    equities = [a for a in (pack.asset_universe or []) if a.get("category") == "stocks"]
    gold = next((a for a in (pack.asset_universe or []) if a.get("category") == "gold"), None)
    if len(equities) < 2 or gold is None:
        print(f"! {market} has no usable asset universe in its pack", file=sys.stderr)
        return []

    unit = 1_000 if pack.currency == "TRY" else 1
    return [
        {
            "asset_type": "stock", "name": equities[0]["name"],
            "ticker": equities[0]["ticker"], "purchase_amount": 120.0 * unit,
            "quantity": 10, "currency": pack.currency,
            "purchase_date": today - timedelta(days=400),
            "emotion_tag": "plan",
        },
        {
            # The one bought in a hurry. The behaviour mirror has nothing to
            # reflect without it.
            "asset_type": "stock", "name": equities[1]["name"],
            "ticker": equities[1]["ticker"], "purchase_amount": 45.0 * unit,
            "quantity": 3, "currency": pack.currency,
            "purchase_date": today - timedelta(days=90),
            "emotion_tag": "fomo",
        },
        {
            "asset_type": "gold", "name": gold["name"], "ticker": gold["ticker"],
            "purchase_amount": 60.0 * unit, "quantity": 5,
            "currency": pack.currency,
            "purchase_date": today - timedelta(days=220),
            "emotion_tag": "plan",
        },
        {
            # Property, so the hybrid path has something to show. No ticker:
            # it is valued from the area index, which is the point.
            "asset_type": "real_estate",
            "name": f"{pack.example_district} · 95 m²",
            "purchase_amount": 900.0 * unit, "currency": pack.currency,
            "purchase_date": today - timedelta(days=700),
            "emotion_tag": "plan",
        },
    ]


async def seed(clerk_user_id: str, market: str) -> None:
    async with AsyncSessionLocal() as db:
        user = await user_repository.get_or_create(db, clerk_user_id)

        await user_repository.save_risk_profile(
            db, clerk_user_id,
            # Mid-range on purpose: a 1 or a 10 produces a portfolio with one
            # sleeve empty, and a reviewer then sees half the allocation card.
            risk_score=6,
            budget=1_500.0 * (1_000 if market == "TR" else 1),
            monthly_contribution=50.0 * (1_000 if market == "TR" else 1),
            time_horizon="long", loss_tolerance="medium", goal="growth",
            experience="beginner", age=34, income_stability="stable",
            # No debt: the debt screen is correct to interrupt, but it blocks
            # the portfolio, and a reviewer needs to reach the portfolio.
            high_interest_debt=0,
        )

        user.market = market
        # Hybrid, so BOTH halves of the app are reachable from the nav — a
        # stocks-only demo hides the real-estate features entirely.
        user.investment_path = "hybrid"
        user.monthly_outgoings = 25.0 * (1_000 if market == "TR" else 1)
        await db.flush()

        existing = await holding_repository.list_for_user(db, user.id)
        for holding in existing:
            await holding_repository.delete(db, holding)

        rows = _holdings(market)
        for data in rows:
            await holding_repository.create(db, user.id, data)

        await db.commit()
        print(f"✓ seeded {clerk_user_id} — market {market}, "
              f"{len(rows)} holdings, hybrid path, risk 6")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clerk_user_id", help="an EXISTING Clerk user id (user_…)")
    parser.add_argument("--market", default="TR", choices=["TR", "US", "DE"])
    args = parser.parse_args()

    if not args.clerk_user_id.startswith("user_"):
        parser.error("that does not look like a Clerk user id (expected user_…)")

    asyncio.run(seed(args.clerk_user_id, args.market))


if __name__ == "__main__":
    main()

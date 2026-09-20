"""
Splitting a budget between property, market assets and a cash reserve.

The properties that matter are not "does it return a number" but "is the
number one a person could actually act on": you cannot allocate to a flat you
cannot buy, you cannot invest a reserve you are supposed to be able to spend,
and a plan that locks everything into one illiquid asset is not a plan.
"""
import pytest

from backend.services.budget_split import (
    MAX_PROPERTY_SHARE,
    RESERVE_MONTHS,
    split,
)

TR_THRESHOLD = 1_000_000.0


def test_the_reserve_comes_off_the_top_before_anything_is_invested():
    """
    It is not an allocation competing with the others. It is what stops a bad
    month turning into a forced sale at the worst price.
    """
    result = split(budget=2_000_000, monthly_outgoings=30_000,
                   risk_score=5, entry_threshold=TR_THRESHOLD)

    assert result.reserve == pytest.approx(30_000 * RESERVE_MONTHS)
    assert "split.reason.reserve_from_outgoings" in result.reasons
    # And it is not double-counted anywhere.
    assert result.total == pytest.approx(2_000_000)


def test_a_reserve_never_swallows_the_whole_budget():
    """
    High outgoings against small savings would otherwise leave nothing to
    plan, and a page that says "invest 0" helps nobody.
    """
    result = split(budget=100_000, monthly_outgoings=50_000,
                   entry_threshold=TR_THRESHOLD)

    assert result.reserve <= 100_000 * 0.5
    assert result.market_amount > 0


def test_an_assumed_reserve_says_that_it_was_assumed():
    result = split(budget=1_000_000, entry_threshold=TR_THRESHOLD)
    assert "split.reason.reserve_assumed" in result.reasons


def test_property_is_not_allocated_when_it_cannot_be_bought():
    """
    The failure this prevents: "40% to real estate" on a budget that buys no
    real estate at all — advice that cannot be followed.
    """
    result = split(budget=200_000, risk_score=3, entry_threshold=TR_THRESHOLD)

    assert result.property_vehicle == "reit"
    assert "split.reason.below_entry_reit" in result.reasons
    assert result.property_amount < result.market_amount


def test_a_lower_risk_score_leans_toward_property():
    """
    Not a claim that property returns more — it is the asset people find
    easiest to hold through a bad year without selling.
    """
    cautious = split(budget=10_000_000, risk_score=1, entry_threshold=TR_THRESHOLD)
    bold = split(budget=10_000_000, risk_score=9, entry_threshold=TR_THRESHOLD)

    assert cautious.property_amount > bold.property_amount
    assert cautious.property_vehicle == bold.property_vehicle == "physical"


def test_nothing_locks_more_than_the_cap_into_one_illiquid_asset():
    """
    However much the numbers favour property, a plan that leaves someone
    unable to move for a decade is a well-argued trap.
    """
    for score in (0, 1, 2, 3, 5, 8, 10):
        result = split(budget=50_000_000, risk_score=score,
                       entry_threshold=TR_THRESHOLD)
        investable = result.total - result.reserve
        assert result.property_amount <= investable * MAX_PROPERTY_SHARE + 1


def test_a_property_share_that_would_buy_nothing_is_lifted_or_abandoned():
    """
    A share landing just under the entry bar buys nothing. Either round up to
    something real, or say property is not on the table — never leave an
    amount that purchases a fraction of a flat.
    """
    result = split(budget=1_600_000, risk_score=9,
                   monthly_outgoings=10_000, entry_threshold=TR_THRESHOLD)

    if result.property_vehicle == "physical":
        assert result.property_amount >= TR_THRESHOLD
        assert "split.reason.rounded_to_entry" in result.reasons
    else:
        assert "split.reason.entry_would_overcommit" in result.reasons


def test_a_single_world_path_plans_everything_inside_that_world():
    """That is the point of having chosen it."""
    stocks = split(budget=5_000_000, risk_score=5, path="stocks",
                   entry_threshold=TR_THRESHOLD)
    assert stocks.property_amount == 0
    assert stocks.market_amount > 0
    assert "split.reason.path_stocks" in stocks.reasons

    property_only = split(budget=5_000_000, risk_score=5, path="real_estate",
                          entry_threshold=TR_THRESHOLD)
    assert property_only.market_amount == 0
    assert property_only.property_amount > 0
    assert "split.reason.path_real_estate" in property_only.reasons


def test_a_real_estate_path_below_the_bar_still_gets_an_honest_vehicle():
    result = split(budget=150_000, path="real_estate", entry_threshold=TR_THRESHOLD)
    assert result.property_vehicle == "reit"


def test_the_parts_always_add_back_to_the_budget():
    """Money that vanishes between the input and the plan is the worst bug here."""
    for budget in (0, 1, 50_000, 999_999, 1_000_000, 7_345_678):
        for score in (None, 0, 5, 10):
            for outgoings in (None, 0, 12_000):
                for path in ("hybrid", "stocks", "real_estate", "undecided"):
                    r = split(budget=budget, risk_score=score,
                              monthly_outgoings=outgoings,
                              entry_threshold=TR_THRESHOLD, path=path)
                    assert r.total == pytest.approx(budget, abs=0.01), (
                        budget, score, outgoings, path)
                    assert r.reserve >= 0
                    assert r.property_amount >= 0
                    assert r.market_amount >= 0


def test_no_budget_says_so_rather_than_dividing_zero():
    result = split(budget=0, entry_threshold=TR_THRESHOLD)
    assert result.reasons == ["split.reason.no_budget"]
    assert result.as_dict()["reserve_pct"] == 0


def test_every_split_carries_its_reasoning():
    for budget in (500_000, 5_000_000):
        for path in ("hybrid", "stocks", "real_estate"):
            result = split(budget=budget, risk_score=5, path=path,
                           entry_threshold=TR_THRESHOLD)
            assert result.reasons, (budget, path)


def test_the_endpoint_answers_in_sentences_not_keys(client):
    body = client.get("/api/v1/planning/budget-split",
                      headers={"X-Lumos-Lang": "en"}).json()

    assert set(body) >= {"reserve", "property_amount", "market_amount",
                         "property_vehicle", "reasons", "currency", "path"}
    assert not any(r.startswith("split.reason.") for r in body["reasons"])


def test_the_entry_bar_changes_the_answer_and_comes_from_the_market():
    """
    The invariant is that the threshold is CONSULTED, not that a particular
    budget lands one way. An earlier version of this test asserted that
    $120k "clears the US bar" and failed — correctly: after the reserve and
    the over-commitment cap, buying at that size would have locked 74% of
    everything into one illiquid asset, so the engine refused. The rule was
    right and the expectation was wrong.
    """
    budget = 3_000_000.0
    reachable = split(budget=budget, risk_score=5, entry_threshold=500_000)
    out_of_reach = split(budget=budget, risk_score=5, entry_threshold=9_000_000)

    assert reachable.property_vehicle == "physical"
    assert out_of_reach.property_vehicle == "reit"
    assert "split.reason.below_entry_reit" in out_of_reach.reasons


def test_each_market_brings_its_own_entry_bar():
    """"Enough to buy a flat" is a fact about a country, not a constant."""
    from backend.markets import MARKET_PACKS

    thresholds = {code: pack.property_entry_threshold
                  for code, pack in MARKET_PACKS.items()}
    assert len(set(thresholds.values())) > 1, thresholds
    for code, value in thresholds.items():
        assert value > 0, code


def test_the_reserve_is_six_months_of_spending_not_of_income():
    """
    The planner was handed `monthly_income` where it asked for outgoings.
    Someone earning 40,000 and spending 15,000 was told to keep back 240,000
    instead of 90,000 — and every other part of the plan shrank behind it.
    """
    spending = split(budget=2_000_000, monthly_outgoings=15_000,
                     risk_score=5, entry_threshold=TR_THRESHOLD)
    earning = split(budget=2_000_000, monthly_outgoings=40_000,
                    risk_score=5, entry_threshold=TR_THRESHOLD)

    assert spending.reserve == pytest.approx(90_000)
    assert earning.reserve == pytest.approx(240_000)
    # And the difference goes back into the plan rather than vanishing.
    assert spending.property_amount + spending.market_amount > \
           earning.property_amount + earning.market_amount


def test_the_planner_reads_outgoings_from_the_user(client):
    """End to end: the endpoint must use the outgoings column, not income."""
    import asyncio

    from backend.repositories import user_repository
    from backend.tests.conftest import FAKE_USER_ID, _TestSession

    async def seed():
        async with _TestSession() as db:
            user = await user_repository.get_or_create(db, FAKE_USER_ID)
            user.budget = 2_000_000
            user.risk_score = 5
            user.monthly_income = 40_000       # deliberately different
            user.monthly_outgoings = 15_000
            await db.commit()

    asyncio.run(seed())

    body = client.get("/api/v1/planning/budget-split").json()
    assert body["reserve"] == pytest.approx(90_000), (
        "the reserve followed income instead of outgoings"
    )


def test_a_reader_who_already_bought_property_gets_the_rest_replanned():
    """
    Without this the plan keeps telling somebody who has just bought a flat
    to put another 40% into property — the moment a plan stops being
    believable, and the moment they most need the rest of it replanned.
    """
    fresh = split(budget=1_000_000, risk_score=5, entry_threshold=TR_THRESHOLD)
    after = split(budget=1_000_000, risk_score=5, entry_threshold=TR_THRESHOLD,
                  committed_property=600_000)

    assert fresh.property_amount > 0
    assert after.property_amount == 0
    assert after.market_amount > fresh.market_amount
    assert "split.reason.already_committed" in after.reasons
    # The reserve is untouched: it is not an investment to be reallocated.
    assert after.reserve == fresh.reserve


def test_a_real_estate_path_still_plans_inside_its_world_after_a_purchase():
    """Owning one plot is not a reason to overrule the path they chose."""
    result = split(budget=1_000_000, risk_score=5, path="real_estate",
                   entry_threshold=TR_THRESHOLD, committed_property=600_000)
    assert result.market_amount == 0
    assert "split.reason.already_committed" in result.reasons


def test_the_endpoint_counts_property_holdings_as_committed(client):
    import asyncio

    from backend.repositories import user_repository
    from backend.tests.conftest import FAKE_USER_ID, _TestSession

    async def seed():
        async with _TestSession() as db:
            user = await user_repository.get_or_create(db, FAKE_USER_ID)
            user.budget = 2_000_000
            user.risk_score = 5
            user.monthly_outgoings = 10_000
            await db.commit()

    asyncio.run(seed())
    client.post("/api/v1/holdings", json={
        "asset_type": "land", "name": "plot", "purchase_amount": 900_000,
    })

    body = client.get("/api/v1/planning/budget-split").json()
    assert body["property_amount"] == 0, "an owned plot was not counted"
    assert any("already" in r.lower() or "zaten" in r.lower() or "bereits" in r.lower()
               for r in body["reasons"]), body["reasons"]

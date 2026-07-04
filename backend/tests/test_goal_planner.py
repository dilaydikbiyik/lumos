"""
Goal-based investing math tests.
"""

from backend.services.goal_planner import progress_and_drift, required_monthly_contribution


def test_zero_current_savings_requires_positive_contribution():
    result = required_monthly_contribution(target_amount=800000, years=3, current_savings=0)
    assert result["monthly_contribution"] > 0
    assert result["already_on_track"] is False


def test_already_saved_enough_needs_no_contribution():
    result = required_monthly_contribution(target_amount=100000, years=1, current_savings=200000, annual_growth_pct=0)
    assert result["already_on_track"] is True
    assert result["monthly_contribution"] == 0.0


def test_contribution_plan_reaches_target_when_followed():
    plan = required_monthly_contribution(target_amount=800000, years=3, current_savings=100000)
    progress = progress_and_drift(
        target_amount=800000, years_remaining=3,
        current_savings=100000, actual_monthly_contribution=plan["monthly_contribution"],
    )
    assert progress["on_track"] is True
    assert progress["delay_months"] == 0


def test_underfunded_plan_shows_delay():
    plan = required_monthly_contribution(target_amount=800000, years=3, current_savings=0)
    half_effort = plan["monthly_contribution"] / 2
    progress = progress_and_drift(
        target_amount=800000, years_remaining=3,
        current_savings=0, actual_monthly_contribution=half_effort,
    )
    assert progress["on_track"] is False
    assert progress["delay_months"] > 0


def test_goal_plan_endpoint(client):
    res = client.post("/planning/goal-plan", json={
        "target_amount": 800000, "years": 3, "current_savings": 100000,
    })
    assert res.status_code == 200
    assert res.json()["monthly_contribution"] > 0


def test_goal_progress_endpoint(client):
    res = client.post("/planning/goal-progress", json={
        "target_amount": 800000, "years_remaining": 3,
        "current_savings": 100000, "actual_monthly_contribution": 5000,
    })
    assert res.status_code == 200
    assert "on_track" in res.json()

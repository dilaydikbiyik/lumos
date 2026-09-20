"""
Account deletion — the one destructive endpoint in the app.

Apple rejects any app that lets you create an account but not delete one from
inside the app, so this is a store gate as well as a privacy obligation. It is
also the endpoint where a bug is unrecoverable, which is why the tests below
care as much about what must NOT be deleted as about what must.
"""
from unittest.mock import patch

from backend.tests.conftest import FAKE_USER_ID


def _seed(client):
    """Give the account something to lose: a profile, a holding, feedback."""
    client.post("/profile", json={
        "age": 30, "monthly_income": 40000, "risk_tolerance": "orta",
        "investment_horizon": "uzun", "goal": "emeklilik",
    })
    created = client.post("/holdings", json={
        "asset_type": "stock", "name": "S&P 500 ETF", "ticker": "SPY",
        "purchase_amount": 100000, "quantity": 5,
    })
    assert created.status_code == 201, created.text
    # Free text is exactly where a name or a situation ends up, which is why
    # deletion has to take it along rather than merely unlink it.
    noted = client.post("/feedback", json={
        "message": "a note that names its author",
        "category": "confusing", "page": "/recommend",
    })
    assert noted.status_code in (200, 201), noted.text


def test_deleting_an_account_removes_the_data_and_the_login(client):
    _seed(client)
    with patch("backend.services.clerk_service.delete_user", return_value=True) as clerk:
        res = client.request("DELETE", "/users/me",
                             json={"confirm_user_id": FAKE_USER_ID})

    assert res.status_code == 200, res.text
    body = res.json()
    assert body["data_deleted"] is True
    assert body["identity_deleted"] is True
    # Deleting our rows and leaving the login alive is the failure mode that
    # looks like success: the user signs back in and finds a fresh account.
    clerk.assert_called_once_with(FAKE_USER_ID)

    # Nothing of the user survives.
    assert client.get("/holdings").json() == []
    # A deleted account has no profile at all — not an empty one, which would
    # mean the row survived with its answers cleared.
    assert not (client.get("/profile").json() or {})


def test_a_failed_identity_delete_is_reported_not_papered_over(client):
    """
    If Clerk is down we still erase our side, but we must say so. Claiming a
    clean deletion while the login still works is the one lie the user would
    discover by themselves, on their next sign-in.
    """
    _seed(client)
    with patch("backend.services.clerk_service.delete_user", return_value=False):
        res = client.request("DELETE", "/users/me",
                             json={"confirm_user_id": FAKE_USER_ID})

    assert res.status_code == 200
    body = res.json()
    assert body["data_deleted"] is True
    assert body["identity_deleted"] is False
    assert "support" in body["message"].lower() or "destek" in body["message"].lower()


def test_a_mismatched_confirmation_deletes_nothing(client):
    """A stray or replayed request must not be able to erase an account."""
    _seed(client)
    with patch("backend.services.clerk_service.delete_user") as clerk:
        res = client.request("DELETE", "/users/me",
                             json={"confirm_user_id": "user_someone_else"})

    assert res.status_code == 400
    clerk.assert_not_called()
    # The account is untouched — this is the assertion that matters.
    assert len(client.get("/holdings").json()) == 1


def test_deletion_is_idempotent(client):
    """
    Deleting twice must not 500. A double-tapped button, a retried request
    after a timeout — the second call has nothing to do and should say so
    calmly rather than erroring at someone who is already leaving.
    """
    _seed(client)
    with patch("backend.services.clerk_service.delete_user", return_value=True):
        first = client.request("DELETE", "/users/me",
                               json={"confirm_user_id": FAKE_USER_ID})
        second = client.request("DELETE", "/users/me",
                                json={"confirm_user_id": FAKE_USER_ID})

    assert first.status_code == 200
    assert second.status_code == 200


def test_the_confirmation_body_is_required(client):
    """A bare DELETE with no body must not be enough to erase an account."""
    with patch("backend.services.clerk_service.delete_user") as clerk:
        res = client.request("DELETE", "/users/me")
    assert res.status_code == 422
    clerk.assert_not_called()

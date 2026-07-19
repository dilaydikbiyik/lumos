"""
In-app feedback: anyone signed in can send, only admins can read.
"""


def test_submit_feedback(client):
    res = client.post("/feedback", json={
        "message": "risk skorunun nasil ciktigini anlamadim",
        "category": "confusing",
        "page": "/recommend",
    })
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_empty_message_rejected(client):
    res = client.post("/feedback", json={"message": ""})
    assert res.status_code == 422


def test_unknown_category_is_dropped_not_rejected(client):
    """A junk category must not cost the user their message."""
    res = client.post("/feedback", json={"message": "bir sey bozuk", "category": "nonsense"})
    assert res.status_code == 200


def test_listing_requires_admin(client):
    assert client.get("/feedback").status_code == 403


def test_admin_reads_submitted_feedback(client):
    import asyncio
    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user
    from backend.repositories import user_repository
    from backend.tests.conftest import _TestSession

    client.post("/feedback", json={"message": "grafik cok karisik", "page": "/dashboard"})

    app.dependency_overrides[get_current_user] = lambda: "user_fb_admin"

    async def promote():
        async with _TestSession() as db:
            user = await user_repository.get_or_create(db, "user_fb_admin")
            user.role = "admin"
            await db.commit()

    asyncio.run(promote())

    res = client.get("/feedback")
    assert res.status_code == 200
    messages = [row["message"] for row in res.json()]
    assert "grafik cok karisik" in messages

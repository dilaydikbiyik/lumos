"""
Lightweight RBAC tests — /admin/stats gated by User.role.
"""


def test_regular_user_gets_403(client):
    res = client.get("/admin/stats")
    assert res.status_code == 403


def test_admin_gets_stats(client):
    import asyncio
    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user
    from backend.repositories import user_repository
    from backend.tests.conftest import _TestSession

    app.dependency_overrides[get_current_user] = lambda: "user_admin_1"

    async def promote():
        async with _TestSession() as db:
            user = await user_repository.get_or_create(db, "user_admin_1")
            user.role = "admin"
            await db.commit()

    asyncio.run(promote())

    res = client.get("/admin/stats")
    assert res.status_code == 200
    body = res.json()
    assert "total_users" in body and "ai_messages_today" in body

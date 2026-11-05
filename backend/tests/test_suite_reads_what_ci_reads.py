"""
The test suite sees the same settings CI sees.

A CORS test passed on the author's machine and failed in CI, because
settings read the developer's .env — FRONTEND_URL was the Vercel address
here and the localhost default there. The local gate went green and CI went
red on the same commit. While the two run against different settings, a
passing local run says nothing about CI, which is the only reason to run it.
"""
from backend.config import Settings, settings


def test_settings_were_not_loaded_from_a_dotenv_file():
    assert Settings.model_config.get("env_file") is None, (
        "the test suite is reading .env — set LUMOS_IGNORE_DOTENV before any "
        "backend import (backend/tests/conftest.py does this)"
    )


def test_the_developers_frontend_url_is_not_in_effect():
    """The value that broke CI: only the process environment may set it."""
    import os

    expected = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    assert settings.FRONTEND_URL == expected

"""
The app imports with error monitoring switched on.

sentry-sdk 2.19 loaded its Starlette integration, which imports
starlette.templating; Starlette 1.x raises ImportError there when markupsafe
is installed without jinja2. The app never started — and nothing noticed,
because SENTRY_DSN is unset everywhere the tests run. Production would have
gone down the day monitoring was turned on.

A subprocess, because the DSN is read once at import and this test session
has already imported the app without one.
"""
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_the_app_starts_with_a_sentry_dsn():
    env = {**os.environ,
           "SENTRY_DSN": "http://public@127.0.0.1:9/1",   # nothing listens; init does not connect
           "LUMOS_IGNORE_DOTENV": "1",
           "DATABASE_URL": "sqlite+aiosqlite:///:memory:"}
    res = subprocess.run([sys.executable, "-c", "import backend.main"],
                         cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
    assert res.returncode == 0, res.stderr[-2000:]

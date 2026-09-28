"""
Crashes that happen in the reader's browser.

The backend has had Sentry wired for a while; the frontend never did, so a
React crash — the kind that replaces the whole screen with an error boundary —
left no trace anywhere but that reader's own console. The todo said to set
SENTRY_DSN "on Render and Vercel (the code is already wired)", and the Vercel
half of that was not true: setting it there would have been a no-op while
looking like coverage.

Reported THROUGH the backend rather than by adding a Sentry SDK to the client.
The bundle is already 359 KB and the backend is already instrumented, so a
second SDK would buy duplicate machinery at a real download cost for every
reader. It also means a crash report goes to an origin this app controls
rather than straight to a third party from the reader's browser.

DELIBERATELY THIN. No cookies, no local storage, no form contents — a crash
in this app happens on screens holding income, debts and holdings, and a
stack trace is quite enough to fix a bug without carrying any of that.
"""

import logging

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from backend.limiter import limiter
from backend.middleware.verify_clerk import get_current_user

logger = logging.getLogger("lumos.client")

router = APIRouter()


class ClientError(BaseModel):
    message: str = Field(max_length=500)
    # Truncated rather than rejected: a stack that arrives shortened is still
    # the line that crashed, and refusing it would lose the only report.
    stack: str = Field(default="", max_length=4000)
    # Where it happened, so a crash on one screen is not chased across all of
    # them. Path only — the query string can carry identifiers.
    path: str = Field(default="", max_length=200)
    component: str = Field(default="", max_length=200)


@router.post("", status_code=204)
@limiter.limit("10/minute")
async def report_client_error(
    request: Request,
    body: ClientError,
    user_id: str = Depends(get_current_user),
):
    """
    Record a crash the error boundary caught.

    Rate limited hard: a crash inside a render loop can fire continuously,
    and a client that melts down must not be able to melt the log with it.

    Returns 204 and never an error. A failure to report a crash cannot be
    allowed to cause one — the reader is already looking at a broken screen.
    """
    logger.error(
        "client crash on %s [%s]: %s\n%s",
        body.path or "?", body.component or "?", body.message, body.stack,
        extra={"clerk_user_id": user_id},
    )
    return None

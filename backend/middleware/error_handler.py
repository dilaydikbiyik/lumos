"""
Global exception handlers — every error path returns the same shape:

    {"detail": <human message>, "error": {"code", "message", "request_id"}}

`detail` stays for backward compatibility with the frontend's
extractErrorMessage; the `error` envelope adds a machine-readable code
and the correlation id from RequestIDMiddleware.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.exceptions import AIServiceError, MarketDataError
from backend.i18n import t
from backend.middleware.language import get_language
from backend.middleware.request_id import request_id_var

logger = logging.getLogger(__name__)


def _error_response(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "detail": message,
            "error": {"code": code, "message": message, "request_id": request_id_var.get()},
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(MarketDataError)
    async def market_data_error_handler(request: Request, exc: MarketDataError):
        logger.error("[%s] Market data unavailable on %s %s: %s",
                     request_id_var.get(), request.method, request.url, exc)
        return _error_response(
            503, "market_data_unavailable",
            t("error.market_data", get_language(request)),
        )

    @app.exception_handler(AIServiceError)
    async def ai_service_error_handler(request: Request, exc: AIServiceError):
        logger.error("[%s] AI service failure on %s %s: %s",
                     request_id_var.get(), request.method, request.url, exc)
        return _error_response(
            503, "ai_unavailable",
            t("error.ai_unavailable", get_language(request)),
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        # `str(exc)` used to be returned verbatim. Nothing in the app raises
        # ValueError deliberately, so the only things this handler ever sees
        # are incidental — raised by a driver, an SDK or the standard library
        # — and those messages routinely carry a connection string, a URL with
        # a key in its query, or a fragment of the input that triggered them.
        # A test proves it: a ValueError carrying an API key was served to the
        # client in full, in `detail` AND in `error.message`.
        #
        # The message is logged and a curated one is returned, which is what
        # the other two handlers already did. The inconsistency was the bug.
        logger.warning("[%s] Invalid value on %s %s: %s",
                       request_id_var.get(), request.method, request.url.path, exc)
        return _error_response(
            422, "invalid_value", t("error.invalid_value", get_language(request)),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("[%s] Unhandled error on %s %s",
                         request_id_var.get(), request.method, request.url)
        return _error_response(
            500, "internal_error",
            t("error.internal", get_language(request)),
        )


class UnhandledErrorMiddleware:
    """
    Turns an unhandled exception into the 500 envelope INSIDE the CORS layer.

    Starlette routes `@app.exception_handler(Exception)` to its
    ServerErrorMiddleware, which always sits outside every user middleware —
    CORS included. So a crash produced a response with no
    Access-Control-Allow-Origin and no X-Request-ID. The web app is
    cross-origin (Vercel calling Render), so the browser hid that response
    and reported "no response"; the client's retry policy then re-ran the
    crashing GET four more times over ~37 seconds before showing a generic
    message, and the translated one was never seen.

    Registered first, so it is the innermost middleware: the request id and
    language are already set, and CORS wraps what it returns.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        started = False

        async def tracking_send(message):
            nonlocal started
            if message["type"] == "http.response.start":
                started = True
            await send(message)

        try:
            await self.app(scope, receive, tracking_send)
        except Exception:
            if started:
                raise  # half a response is already out; nothing clean to send
            request = Request(scope)
            logger.exception("[%s] Unhandled error on %s %s",
                             request_id_var.get(), request.method, request.url.path)
            response = _error_response(500, "internal_error",
                                       t("error.internal", get_language(request)))
            await response(scope, receive, send)

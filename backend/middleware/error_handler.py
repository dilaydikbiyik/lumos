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
            "Market data is temporarily unavailable. Please try again shortly.",
        )

    @app.exception_handler(AIServiceError)
    async def ai_service_error_handler(request: Request, exc: AIServiceError):
        logger.error("[%s] AI service failure on %s %s: %s",
                     request_id_var.get(), request.method, request.url, exc)
        return _error_response(
            503, "ai_unavailable",
            "The AI assistant is temporarily unavailable. Please try again shortly.",
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return _error_response(422, "invalid_value", str(exc))

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("[%s] Unhandled error on %s %s",
                         request_id_var.get(), request.method, request.url)
        return _error_response(
            500, "internal_error",
            "An unexpected error occurred. Please try again later.",
        )

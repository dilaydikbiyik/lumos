import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.exceptions import AIServiceError, MarketDataError

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(MarketDataError)
    async def market_data_error_handler(request: Request, exc: MarketDataError):
        logger.error("Market data unavailable on %s %s: %s", request.method, request.url, exc)
        return JSONResponse(
            status_code=503,
            content={"detail": "Market data is temporarily unavailable. Please try again shortly."},
        )

    @app.exception_handler(AIServiceError)
    async def ai_service_error_handler(request: Request, exc: AIServiceError):
        logger.error("AI service failure on %s %s: %s", request.method, request.url, exc)
        return JSONResponse(
            status_code=503,
            content={"detail": "The AI assistant is temporarily unavailable. Please try again shortly."},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred. Please try again later."},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc)},
        )

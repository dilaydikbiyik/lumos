"""
Domain exceptions — mapped to HTTP responses in middleware/error_handler.py.
"""


class MarketDataError(Exception):
    """External market data source failed and no cached fallback exists."""


class AIServiceError(Exception):
    """AI provider call failed in a way the adapters could not soften."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Uptime monitoring endpoint for Render.com."""
    return {"status": "ok", "version": "0.1.0"}

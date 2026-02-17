from __future__ import annotations

from fastapi import APIRouter

from backend.core.config import settings
from backend.models.schemas import HealthResponse
from backend.parsers.registry import get_registered_parsers

router = APIRouter()


@router.get("/api/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="ok",
        mode="mock" if settings.use_mock else "claude",
        supported_formats=get_registered_parsers(),
    )

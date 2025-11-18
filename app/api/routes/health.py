from fastapi import APIRouter

from ...schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["system"])


@router.get("", response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    return HealthResponse()

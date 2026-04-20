"""API маршруты"""
import traceback
from fastapi import APIRouter, HTTPException, status

from api.schemas import (
    ErrorResponse,
    HealthResponse,
    SummarizeRequest,
    SummarizeResponse,
)
from cache.memory import get_cache
from config.settings import get_settings
from core.exceptions import ValidationError
from core.logging import get_logger
from services.pipeline import get_summarization_pipeline

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/summarize",
    response_model=SummarizeResponse,
    responses={
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def summarize(request: SummarizeRequest) -> SummarizeResponse:
    """Суммировать предоставленный текст"""
    try:
        pipeline = get_summarization_pipeline()
        response = await pipeline.execute(request)
        return response
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", extra={
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Эндпоинт проверки здоровья"""
    settings = get_settings()
    cache = get_cache()
    
    logger.info("Health check requested")
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        cache_stats=cache.get_stats(),
    )


@router.post("/cache/clear")
async def clear_cache() -> dict:
    """Очистить кеш"""
    cache = get_cache()
    cache.clear()
    logger.info("Cache cleared")
    return {"message": "Cache cleared successfully"}

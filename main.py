"""Главное FastAPI приложение"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from config.settings import get_settings
from core.logging import get_logger, setup_logging

# Настроить логирование
settings = get_settings()
logger = setup_logging(settings.log_level, settings.log_file)
app_logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Менеджер контекста lifespan для событий запуска/остановки"""
    # Запуск
    app_logger.info("Application startup", extra={
        "app_name": settings.app_name,
        "version": settings.app_version,
    })
    yield
    # Остановка
    app_logger.info("Application shutdown")


def create_app() -> FastAPI:
    """Создать и настроить FastAPI приложение"""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    
    # Добавить CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Включить маршруты
    app.include_router(router, prefix="/api/v1")
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_config=None,  # Использовать наше кустомное логирование
    )

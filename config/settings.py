"""Управление конфигурацией"""

from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """Параметры приложения"""

    # Исправлено: используем SettingsConfigDict вместо ConfigDict
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # API Configuration
    app_name: str = "LLM Service"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    log_file: str | None = "logs/app.log"

    # Конфигурация GigaChat
    gigachat_api_key: str | None = None
    gigachat_model: str = "GigaChat"

    # LLM Configuration
    llm_timeout: int = 30
    llm_max_retries: int = 3
    llm_retry_delay: float = 1.0

    # Cache Configuration
    cache_ttl_seconds: int = 600

    # Ограничения реквестов
    max_request_length: int = 10000


@lru_cache
def get_settings() -> Settings:
    """Получить параметры приложения"""
    return Settings()


def get_settings_dict() -> dict:
    """Получить параметры как словарь для структурированного логирования"""
    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "debug": settings.debug,
        "log_level": settings.log_level,
    }

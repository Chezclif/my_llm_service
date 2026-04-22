"""Конфигурация pytest и фиксчуры"""

import asyncio
from unittest.mock import MagicMock

import pytest

from cache.memory import Cache
from config.settings import Settings


@pytest.fixture
def event_loop():
    """Создать экземпляр цикла событий по умолчанию для каждого тестового случая."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Предоставить mock параметры"""
    settings = MagicMock(spec=Settings)
    settings.app_name = "LLM Service"
    settings.app_version = "0.1.0"
    settings.debug = False
    settings.log_level = "DEBUG"
    settings.gigachat_api_key = "test-key"
    settings.gigachat_model = "test-model"
    settings.llm_timeout = 30
    settings.llm_max_retries = 3
    settings.llm_retry_delay = 1.0
    settings.cache_ttl_seconds = 600
    settings.max_request_length = 10000
    return settings


@pytest.fixture
def cache():
    """Предоставить свежий экземпляр кеша"""
    return Cache()

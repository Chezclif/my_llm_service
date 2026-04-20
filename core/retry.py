"""Логика повторных попыток с экспоненциальной задержкой"""
import asyncio
import time
from typing import Callable, Optional, TypeVar

from core.logging import get_logger

T = TypeVar("T")
logger = get_logger(__name__)


class RetryConfig:
    """Конфигурация для логики повторных попыток"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    def get_delay(self, attempt: int) -> float:
        """Рассчитать задержку для попытки с экспоненциальной задержкой"""
        delay = self.initial_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)


async def async_retry(
    func: Callable,
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs
) -> T:
    """Повторить асинхронную функцию с экспоненциальной задержкой"""
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(config.max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < config.max_retries - 1:
                delay = config.get_delay(attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed, retrying in {delay}s: {str(e)}"
                )
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {config.max_retries} attempts failed")
    
    raise last_exception


def sync_retry(
    func: Callable,
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs
) -> T:
    """Повторить синхронную функцию с экспоненциальной задержкой"""
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(config.max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < config.max_retries - 1:
                delay = config.get_delay(attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed, retrying in {delay}s: {str(e)}"
                )
                time.sleep(delay)
            else:
                logger.error(f"All {config.max_retries} attempts failed")
    
    raise last_exception

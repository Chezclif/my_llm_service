"""Оркестрация конвейера"""

import time

from api.schemas import SummarizeRequest, SummarizeResponse
from cache.memory import get_cache
from core.exceptions import LLMAPIError, LLMTimeoutError, ParseError
from core.logging import get_logger
from llm.client import get_llm_client
from llm.prompts import PromptBuilder

logger = get_logger(__name__)


class SummarizationPipeline:
    """Конвейер для суммирования текста"""

    FALLBACK_RESPONSE = "Сервис временно недоступен, попробуйте позже."

    def __init__(self):
        self.cache = get_cache()
        self.llm_client = get_llm_client()

    async def execute(self, request: SummarizeRequest) -> SummarizeResponse:
        """Открыть сдвиг суммирования"""
        start_time = time.time()

        # Шаг 1: Логировать входящий запрос
        logger.info(
            "Summarization request received",
            extra={
                "text_length": len(request.text),
                "temperature": request.temperature,
                "text": request.text,
            },
        )

        # Шаг 2: Проверить кеш
        _, system_prompt = PromptBuilder.build_summarize_prompt(request.text)
        cached_result = self.cache.get(
            text=request.text,
            model="GigaChat",
            temperature=request.temperature,
            system_prompt=system_prompt,
        )

        if cached_result:
            elapsed = time.time() - start_time
            logger.info(
                "Cache hit",
                extra={
                    "elapsed_seconds": elapsed,
                },
            )
            return SummarizeResponse(
                original_text_length=len(request.text),
                summary=cached_result,
                from_cache=True,
            )

        logger.info("Cache miss")

        # Шаг 3: Вызвать LLM с обработкой ошибок и fallback
        try:
            summary = await self.llm_client.summarize(request.text, request.temperature)

            # Шаг 4: Проверить и очистить ответ
            summary = self._post_process_response(summary)

            # Шаг 5: Сохранить в кеш
            from config.settings import get_settings

            settings = get_settings()
            self.cache.set(
                text=request.text,
                model="GigaChat",
                temperature=request.temperature,
                system_prompt=system_prompt,
                value=summary,
                ttl=settings.cache_ttl_seconds,
            )

            elapsed = time.time() - start_time
            logger.info(
                "Summarization completed",
                extra={
                    "elapsed_seconds": elapsed,
                    "summary_length": len(summary),
                },
            )

            return SummarizeResponse(
                original_text_length=len(request.text),
                summary=summary,
                from_cache=False,
            )

        except (LLMAPIError, LLMTimeoutError) as e:
            elapsed = time.time() - start_time
            logger.error(
                f"LLM service unavailable: {str(e)}",
                extra={
                    "elapsed_seconds": elapsed,
                    "error_type": type(e).__name__,
                },
            )
            # Вернуть fallback ответ
            return SummarizeResponse(
                original_text_length=len(request.text),
                summary=self.FALLBACK_RESPONSE,
                from_cache=False,
            )

        except ParseError as e:
            elapsed = time.time() - start_time
            logger.error(
                f"Response parsing failed: {str(e)}",
                extra={
                    "elapsed_seconds": elapsed,
                },
            )
            # Вернуть fallback ответ
            return SummarizeResponse(
                original_text_length=len(request.text),
                summary=self.FALLBACK_RESPONSE,
                from_cache=False,
            )

    @staticmethod
    def _post_process_response(response: str) -> str:
        """Постобработка ответа LLM"""
        # Удалить лишние пробелы
        response = response.strip()

        # Убедиться, что ответ не пустой
        if not response:
            raise ParseError("LLM returned empty response")

        return response


def get_summarization_pipeline() -> SummarizationPipeline:
    """Получить экземпляр конвейера суммирования"""
    return SummarizationPipeline()

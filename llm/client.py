"""Сервис интеграции LLM"""

from gigachat import Chat, GigaChatAsyncClient, Messages, MessagesRole

from config.settings import get_settings
from core.exceptions import LLMAPIError, LLMTimeoutError, ParseError
from core.logging import get_logger
from core.retry import RetryConfig, async_retry
from llm.prompts import PromptBuilder

logger = get_logger(__name__)


class LLMClient:
    """Клиент для взаимодействия с API LLM"""

    def __init__(self):
        self.settings = get_settings()
        self.timeout = self.settings.llm_timeout
        self.max_retries = self.settings.llm_max_retries
        self.retry_delay = self.settings.llm_retry_delay

    async def _call_api(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Выполнить фактический вызов API к LLM через GigaChat SDK"""
        try:
            async with GigaChatAsyncClient(
                credentials=self.settings.gigachat_api_key,
                verify_ssl_certs=False,
                timeout=self.timeout,
            ) as giga:
                response = await giga.achat(
                    Chat(
                        model=self.settings.gigachat_model,
                        messages=[
                            Messages(role=MessagesRole.SYSTEM, content=system_prompt),
                            Messages(role=MessagesRole.USER, content=user_prompt),
                        ],
                        temperature=temperature,
                    )
                )

                if not response.choices or not response.choices[0].message:
                    raise ParseError("Invalid response structure from LLM API")

                content = response.choices[0].message.content
                if content is None:
                    raise ParseError("LLM API returned empty response content")

                return str(content)

        except TimeoutError as e:
            raise LLMTimeoutError(f"LLM API call timed out after {self.timeout}s") from e
        except Exception as e:
            # GigaChat SDK может выбрасывать различные типы исключений
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                raise LLMTimeoutError(f"LLM API call timed out: {error_msg}") from e
            elif "401" in error_msg or "unauthorized" in error_msg.lower():
                raise LLMAPIError("Unauthorized: Check your API key") from e
            else:
                raise LLMAPIError(f"LLM API error: {error_msg}") from e

    async def call_with_retry(
        self, system_prompt: str, user_prompt: str, temperature: float
    ) -> str:
        """Вызвать LLM с логикой повторных попыток"""
        retry_config = RetryConfig(
            max_retries=self.max_retries,
            initial_delay=self.retry_delay,
        )

        return await async_retry(
            self._call_api,
            system_prompt,
            user_prompt,
            temperature,
            config=retry_config,
        )

    async def summarize(self, text: str, temperature: float) -> str:
        """Суммировать текст"""
        system_prompt, user_prompt = PromptBuilder.build_summarize_prompt(text)

        logger.info(
            "Calling LLM API",
            extra={
                "text_length": len(text),
                "temperature": temperature,
            },
        )

        try:
            summary = await self.call_with_retry(system_prompt, user_prompt, temperature)

            logger.info(
                "LLM API call successful",
                extra={
                    "summary_length": len(summary),
                },
            )

            return summary
        except (LLMAPIError, LLMTimeoutError, ParseError) as e:
            logger.error(
                f"LLM error: {str(e)}",
                extra={
                    "error_type": type(e).__name__,
                },
            )
            raise


def get_llm_client() -> LLMClient:
    """Получить экземпляр LLM клиента"""
    return LLMClient()

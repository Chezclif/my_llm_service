"""Модульные тесты для сервиса LLM"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from cache.memory import Cache, get_cache
from config.settings import get_settings
from core.exceptions import LLMAPIError, LLMTimeoutError, ParseError
from api.schemas import SummarizeRequest, SummarizeResponse
from llm.client import LLMClient
from llm.prompts import PromptBuilder
from services.pipeline import SummarizationPipeline


# Тестовые данные
SAMPLE_TEXT = """Machine learning is a subset of artificial intelligence (AI) that focuses on 
the development of algorithms and models that enable computers to learn from data. Unlike traditional 
programming where rules are explicitly defined, machine learning systems improve their performance 
through experience and data exposure. Deep learning, neural networks, and natural language processing 
are key technologies driving recent advances in AI."""

EXPECTED_SUMMARY = "Machine learning enables computers to learn from data without explicit programming rules."


class TestCache:
    """Тесты для механизма кеширования"""
    
    def test_cache_get_set(self):
        """Протестировать операции получения и установки кеша"""
        cache = Cache()
        
        cache.set(
            text="test",
            model="test-model",
            temperature=0.7,
            system_prompt="test",
            value="cached_value",
            ttl=600,
        )
        
        result = cache.get(
            text="test",
            model="test-model",
            temperature=0.7,
            system_prompt="test",
        )
        
        assert result == "cached_value"
    
    def test_cache_miss(self):
        """Протестировать сценарий промаха кеша"""
        cache = Cache()
        
        result = cache.get(
            text="nonexistent",
            model="test-model",
            temperature=0.7,
            system_prompt="test",
        )
        
        assert result is None
    
    def test_cache_expiration(self):
        """Протестировать истечение TTL кеша"""
        cache = Cache()
        
        cache.set(
            text="test",
            model="test-model",
            temperature=0.7,
            system_prompt="test",
            value="cached_value",
            ttl=0,  # Моментально истекает
        )
        
        # Небольшая задержка, чтобы наверняка истекла
        import time
        time.sleep(0.1)
        
        result = cache.get(
            text="test",
            model="test-model",
            temperature=0.7,
            system_prompt="test",
        )
        
        assert result is None
    
    def test_cache_stats(self):
        """Протестировать статистику кеша"""
        cache = Cache()
        
        # Установить и попасть
        cache.set(
            text="test",
            model="test-model",
            temperature=0.7,
            system_prompt="test",
            value="value",
            ttl=600,
        )
        cache.get(
            text="test",
            model="test-model",
            temperature=0.7,
            system_prompt="test",
        )
        
        # Miss
        cache.get(
            text="nonexistent",
            model="test-model",
            temperature=0.7,
            system_prompt="test",
        )
        
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["total_requests"] == 2


class TestValidation:
    """Тесты для валидации запроса"""
    
    def test_valid_request(self):
        """Протестировать корректный запрос"""
        request = SummarizeRequest(
            text=SAMPLE_TEXT,
            temperature=0.7,
        )
        assert request.text == SAMPLE_TEXT
        assert request.temperature == 0.7
    
    def test_invalid_text_too_short(self):
        """Протестировать валидацию: текст слишком короткий"""
        with pytest.raises(ValueError):
            SummarizeRequest(text="short")
    
    def test_invalid_text_too_long(self):
        """Протестировать валидацию: текст слишком длинный"""
        long_text = "a" * 10001
        with pytest.raises(ValueError):
            SummarizeRequest(text=long_text)
    
    def test_invalid_temperature_negative(self):
        """Протестировать валидацию: температура слишком низкая"""
        with pytest.raises(ValueError):
            SummarizeRequest(text=SAMPLE_TEXT, temperature=-0.5)
    
    def test_invalid_temperature_too_high(self):
        """Протестировать валидацию: температура слишком высокая"""
        with pytest.raises(ValueError):
            SummarizeRequest(text=SAMPLE_TEXT, temperature=2.5)
    
    def test_empty_text_validation(self):
        """Протестировать валидацию: пустой текст"""
        with pytest.raises(ValueError):
            SummarizeRequest(text="   ")


class TestPromptBuilder:
    """Тесты для построения промпта"""
    
    def test_build_prompt(self):
        """Протестировать построение промпта"""
        system_prompt, user_prompt = PromptBuilder.build_summarize_prompt(SAMPLE_TEXT)
        
        assert "суммировании" in system_prompt.lower()
        assert SAMPLE_TEXT in user_prompt
        assert "суммируйте" in user_prompt.lower()


@pytest.mark.asyncio
class TestLLMClient:
    """Тесты для LLM клиента"""
    
    async def test_successful_llm_call(self):
        """Протестировать успешный вызов API LLM"""
        # Создаем мок-объект для ответа
        mock_message = MagicMock()
        mock_message.content = EXPECTED_SUMMARY
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        
        # Мокируем GigaChatAsyncClient
        mock_giga_client = AsyncMock()
        mock_giga_client.achat = AsyncMock(return_value=mock_response)
        mock_giga_client.__aenter__ = AsyncMock(return_value=mock_giga_client)
        mock_giga_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("llm.client.GigaChatAsyncClient", return_value=mock_giga_client):
            client = LLMClient()
            result = await client.summarize(SAMPLE_TEXT, 0.7)
            assert result == EXPECTED_SUMMARY
    
    async def test_llm_timeout(self):
        """Протестировать обработку тайм-аута API LLM"""
        client = LLMClient()
        
        with patch.object(client, "_call_api", side_effect=LLMTimeoutError("Timeout")):
            with pytest.raises(LLMTimeoutError):
                await client.call_with_retry("system", "user", 0.7)
    
    async def test_llm_invalid_response(self):
        """Протестировать парсинг недопустимого ответа API LLM"""
        # Мокируем ответ без choices
        mock_response = MagicMock()
        mock_response.choices = []
        
        mock_giga_client = AsyncMock()
        mock_giga_client.achat = AsyncMock(return_value=mock_response)
        mock_giga_client.__aenter__ = AsyncMock(return_value=mock_giga_client)
        mock_giga_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("llm.client.GigaChatAsyncClient", return_value=mock_giga_client):
            client = LLMClient()
            with pytest.raises(LLMAPIError):
                await client.summarize(SAMPLE_TEXT, 0.7)


@pytest.mark.asyncio
class TestPipeline:
    """Тесты для конвейера суммирования"""
    
    async def test_pipeline_with_valid_request(self):
        """Протестировать конвейер с корректным запросом"""
        request = SummarizeRequest(text=SAMPLE_TEXT)
        pipeline = SummarizationPipeline()
        
        with patch.object(
            pipeline.llm_client,
            "summarize",
            return_value=EXPECTED_SUMMARY
        ):
            response = await pipeline.execute(request)
            
            assert isinstance(response, SummarizeResponse)
            assert response.original_text_length == len(SAMPLE_TEXT)
            assert response.summary == EXPECTED_SUMMARY
            assert not response.from_cache
    
    async def test_pipeline_cache_hit(self):
        """Протестировать попадание в кеш конвейера"""
        request = SummarizeRequest(text=SAMPLE_TEXT)
        pipeline = SummarizationPipeline()
        
        # Set cache
        _, system_prompt = PromptBuilder.build_summarize_prompt(SAMPLE_TEXT)
        pipeline.cache.set(
            text=SAMPLE_TEXT,
            model="GigaChat",
            temperature=request.temperature,
            system_prompt=system_prompt,
            value=EXPECTED_SUMMARY,
            ttl=600,
        )
        
        response = await pipeline.execute(request)
        
        assert response.from_cache
        assert response.summary == EXPECTED_SUMMARY
    
    async def test_pipeline_llm_failure_fallback(self):
        """Протестировать fallback конвейера при неудаче LLM"""
        request = SummarizeRequest(text=SAMPLE_TEXT)
        pipeline = SummarizationPipeline()
        
        # Очистить кеш для гарантии свежего теста
        pipeline.cache.clear()
        
        with patch.object(
            pipeline.llm_client,
            "summarize",
            side_effect=LLMAPIError("API Error")
        ):
            response = await pipeline.execute(request)
            
            assert pipeline.FALLBACK_RESPONSE in response.summary
    
    async def test_pipeline_parse_error_fallback(self):
        """Протестировать fallback конвейера при ошибке парсинга"""
        request = SummarizeRequest(text=SAMPLE_TEXT)
        pipeline = SummarizationPipeline()
        
        # Очистить кеш для гарантии свежего теста
        pipeline.cache.clear()
        
        with patch.object(
            pipeline.llm_client,
            "summarize",
            side_effect=ParseError("Parse Error")
        ):
            response = await pipeline.execute(request)
            
            assert pipeline.FALLBACK_RESPONSE in response.summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""Интеграционные тесты для FastAPI эндпоинтов"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app


client = TestClient(app)


class TestHealthEndpoint:
    """Тесты для эндпоинта проверки здоровья"""
    
    def test_health_check(self):
        """Протестировать эндпоинт проверки здоровья"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "cache_stats" in data


class TestSummarizeEndpoint:
    """Тесты для эндпоинта суммирования"""
    
    SAMPLE_TEXT = "Machine learning is an important field. It enables computers to learn. Deep learning is a subset."
    
    @patch("llm.client.LLMClient.summarize")
    def test_summarize_valid_request(self, mock_summarize):
        """Протестировать эндпоинт суммирования с корректным запросом"""
        mock_summarize.return_value = "Machine learning and deep learning are important."
        
        response = client.post(
            "/api/v1/summarize",
            json={
                "text": self.SAMPLE_TEXT,
                "temperature": 0.7,
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "original_text_length" in data
        assert data["original_text_length"] == len(self.SAMPLE_TEXT)
    
    def test_summarize_missing_text(self):
        """Протестировать эндпоинт суммирования с отсутствующим обязательным полем"""
        response = client.post(
            "/api/v1/summarize",
            json={"temperature": 0.7}
        )
        
        assert response.status_code == 422  # Ошибка валидации
    
    def test_summarize_text_too_short(self):
        """Протестировать эндпоинт суммирования с текстом слишком коротким"""
        response = client.post(
            "/api/v1/summarize",
            json={
                "text": "short",
                "temperature": 0.7,
            }
        )
        
        assert response.status_code == 422
    
    def test_summarize_text_too_long(self):
        """Протестировать эндпоинт суммирования с текстом слишком длинным"""
        long_text = "a" * 10001
        response = client.post(
            "/api/v1/summarize",
            json={
                "text": long_text,
                "temperature": 0.7,
            }
        )
        
        assert response.status_code == 422
    
    def test_summarize_invalid_temperature(self):
        """Протестировать эндпоинт суммирования с недопустимой температурой"""
        response = client.post(
            "/api/v1/summarize",
            json={
                "text": self.SAMPLE_TEXT,
                "temperature": 3.0,  # слишком высока
            }
        )
        
        assert response.status_code == 422


class TestCacheEndpoint:
    """Тесты для эндпоинта управления кешем"""
    
    def test_clear_cache(self):
        """Протестировать эндпоинт очистки кеша"""
        response = client.post("/api/v1/cache/clear")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

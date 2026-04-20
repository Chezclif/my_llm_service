# LLM Service - Copilot Instructions

## Проект
Минималистичный FastAPI сервис для обработки текста через LLM API (GigaChat) с поддержкой кеширования, ретраев и структурированного логирования.

## Архитектура
- **API Layer**: FastAPI с Pydantic валидацией
- **Service Layer**: LLM интеграция, pipeline orchestration
- **Core Layer**: Конфигурация, логирование, кеширование, ретраи
- **Test Layer**: Unit и integration тесты

## Основные команды

### Подготовка
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Запуск
```bash
python main.py
```

### Тестирование
```bash
pytest                          # Все тесты
pytest tests/test_service.py    # Unit тесты
pytest tests/test_api.py        # API тесты
pytest --cov=app                # С покрытием
```

## Основные файлы

- `main.py` - FastAPI приложение (точка входа)
- `api/routes.py` - HTTP эндпоинты
- `api/schemas.py` - Pydantic модели
- `services/pipeline.py` - Бизнес-логика (orchestration)
- `llm/client.py` - LLM API интеграция
- `llm/prompts.py` - Построение промптов
- `cache/memory.py` - In-memory кеш
- `config/settings.py` - Конфигурация
- `core/` - Утилиты (логирование, ретраи, exceptions)

## Ключевые особенности

1. **Валидация**: Pydantic schemas для request/response
2. **Кеширование**: In-memory кеш с TTL (600 сек)
3. **Ретраи**: Экспоненциальная задержка (1s, 2s, 4s...)
4. **Fallback**: Graceful degradation при сбое LLM
5. **Логирование**: JSON структурированные логи
6. **Тестирование**: Покрытие основных сценариев

## API Endpoints

- `POST /api/v1/summarize` - Суммаризация текста
- `GET /api/v1/health` - Проверка здоровья + статистика кеша
- `POST /api/v1/cache/clear` - Очистка кеша

## Конфигурация

Отредактируйте `.env`:
```env
GIGACHAT_API_KEY=your_key_here
LLM_TIMEOUT=30
LLM_MAX_RETRIES=3
CACHE_TTL_SECONDS=600
```

## Примеры использования

### cURL
```bash
curl -X POST http://localhost:8000/api/v1/summarize \
  -H "Content-Type: application/json" \
  -d '{"text":"Your text...","temperature":0.7}'
```

### Python
```python
import requests
r = requests.post(
    "http://localhost:8000/api/v1/summarize",
    json={"text": "Your text...", "temperature": 0.7}
)
print(r.json())
```

## Структура запроса/ответа

### Request
```json
{
  "text": "Text to summarize (10-10000 chars)",
  "temperature": 0.7
}
```

### Response
```json
{
  "original_text_length": 150,
  "summary": "Summary text here",
  "from_cache": false
}
```

## Отладка

Включите DEBUG mode в `.env`:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

Логи в JSON формате для удобного анализа.

# LLM Service - FastAPI + GigaChat Integration

Минималистичный но полнофункциональный сервис для обработки текста через LLM API с использованием FastAPI и Pydantic.

## 🎯 Возможности

- **Pipeline архитектура**: слои UI → Validation → Business Logic → LLM Integration → Response
- **Resilience**: таймауты, ретраи с экспоненциальной задержкой, fallback ответы
- **Кеширование**: in-memory кеш с TTL и статистикой
- **Структурированное логирование**: JSON-формат для всех событий
- **Валидация данных**: Pydantic models для request/response
- **Тестирование**: Unit и integration тесты
- **Обработка ошибок**: graceful error handling и user-friendly messages

## 📋 Требования

- Python 3.11+
- pip

## 🚀 Установка и запуск

### 1. Клонирование и подготовка

```bash
cd /Users/vitaliiulyanchenko/my_llm_service

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Конфигурация

```bash
# Скопируйте файл конфигурации
cp .env.example .env

# Отредактируйте .env и добавьте ваш GigaChat API key
# Минимально необходимо:
GIGACHAT_API_KEY=your_actual_api_key_here
```

### 4. Запуск сервера

```bash
./venv/bin/python main.py
```

Сервер запустится на `http://localhost:8000`

## 📚 API Документация

### Swagger UI
```
http://localhost:8000/docs
```

### Endpoints

#### 1. Суммаризация текста
```
POST /api/v1/summarize
```

**Request:**
```json
{
  "text": "Your text to summarize...",
  "temperature": 0.7
}
```

**Response (успех):**
```json
{
  "original_text_length": 150,
  "summary": "Краткое резюме текста...",
  "from_cache": false
}
```

**Response (из кеша):**
```json
{
  "original_text_length": 150,
  "summary": "Краткое резюме текста...",
  "from_cache": true
}
```

**Response (ошибка сервиса - fallback):**
```json
{
  "original_text_length": 150,
  "summary": "Сервис временно недоступен, попробуйте позже.",
  "from_cache": false
}
```

#### 2. Health Check
```
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "cache_stats": {
    "hits": 5,
    "misses": 2,
    "total_requests": 7,
    "hit_rate_percent": 71.43,
    "cached_entries": 3
  }
}
```

#### 3. Очистка кеша
```
POST /api/v1/cache/clear
```

**Response:**
```json
{
  "message": "Cache cleared successfully"
}
```

## 🧪 Тестирование

### Запуск всех тестов
```bash
pytest
```

### Запуск с покрытием
```bash
pytest --cov=. tests/
```

### Запуск конкретного файла тестов
```bash
pytest tests/test_service.py -v
pytest tests/test_api.py -v
```

### Тестирование и формирование HTML отчета о пройденых тестах
```bash
./venv/bin/python3 -m pytest tests/ \
  --html=reports/test_report.html \
  --self-contained-html \
  -v
```

- **Местоположение**: `reports/test_report.html`
- **Формат**: Self-contained HTML (не требует внешних файлов)
- **Содержит**: Все детали тестов, логи, статистика

### Сценарии тестирования

1. **Корректный запрос** → ожидаемый ответ
2. **Некорректный ввод** → валидационная ошибка (422)
3. **Отсутствие поля** → ошибка валидации
4. **Текст слишком длинный** → ошибка валидации
5. **Сбой сети** → fallback ответ
6. **Повторный запрос** → ответ из кеша

## 📝 Примеры использования

### Python requests
```python
import requests

url = "http://localhost:8000/api/v1/summarize"
data = {
    "text": "Machine learning is a subset of artificial intelligence...",
    "temperature": 0.7
}

response = requests.post(url, json=data)
print(response.json())
```

### cURL
```bash
curl -X POST http://localhost:8000/api/v1/summarize \
  -H "Content-Type: application/json" \
  -d '{"text":"Your text here...","temperature":0.7}'
```

### Проверка здоровья сервиса
```bash
curl http://localhost:8000/api/v1/health
```

## 🏗️ Архитектура

```
request → Validation (Pydantic) 
        → Pipeline Orchestration
        → Cache Check (Cache hit?)
        ├─ YES: Return from cache
        └─ NO: 
            → LLM API Call (with retry logic)
            → Response Validation & Post-processing
            → Store in Cache
            → Return Response
        → Error Handling (Fallback if needed)
```

## 📊 Структура проекта

```
my_llm_service/
├── api/                       # HTTP эндпоинты
│   ├── __init__.py
│   ├── routes.py             # FastAPI маршруты
│   └── schemas.py            # Pydantic модели
├── services/                 # Бизнес-логика
│   ├── __init__.py
│   └── pipeline.py           # Orchestration pipeline
├── llm/                      # Работа с моделью и промпты
│   ├── __init__.py
│   ├── client.py             # LLM API интеграция
│   └── prompts.py            # Построение промптов
├── cache/                    # Реализация кеша
│   ├── __init__.py
│   └── memory.py             # In-memory TTL кеш
├── config/                   # Конфигурации
│   ├── __init__.py
│   └── settings.py           # Pydantic Settings
├── core/                     # Вспомогательные утилиты
│   ├── __init__.py
│   ├── exceptions.py         # Custom exceptions
│   ├── logging.py            # Structured JSON logging
│   └── retry.py              # Retry logic
├── tests/                    # Тесты
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_api.py           # API endpoint тесты
│   └── test_service.py       # Unit тесты
├── main.py                   # Точка входа FastAPI
├── requirements.txt          # Python зависимости
├── pytest.ini                # Pytest конфигурация
├── .env.example              # Шаблон переменных окружения
├── .gitignore                # Git ignore файл
└── README.md                 # This file
```

## 🔧 Конфигурация

### Переменные окружения

```env
# API Configuration
GIGACHAT_API_KEY=your_api_key              # GigaChat API ключ (обязательный)
GIGACHAT_MODEL=GigaChat                    # Модель (по умолчанию)

# Service Configuration
LOG_LEVEL=INFO                             # Уровень логирования
DEBUG=False                                # Debug mode
LOG_FILE=logs/app.log                      # Файл с логами

# LLM Configuration
LLM_TIMEOUT=30                             # Таймаут API запроса (сек)
LLM_MAX_RETRIES=3                          # Максимум попыток
LLM_RETRY_DELAY=1.0                        # Начальная задержка (сек)

# Cache Configuration
CACHE_TTL_SECONDS=600                      # TTL кеша (10 минут)

# Request Limits
MAX_REQUEST_LENGTH=10000                   # Максимальная длина текста
```

## 📊 Логирование

Все события логируются в JSON формате:

```json
{
  "timestamp": "2026-04-20T10:30:45.123456",
  "level": "INFO",
  "logger": "services.pipeline",
  "message": "Summarization request received",
  "context": {
    "text_length": 500,
    "temperature": 0.7
  }
}
```

### События логирования

- `Summarization request received` - входящий запрос
- `Cache hit/miss` - состояние кеша
- `Calling LLM API` - запрос к LLM
- `LLM API call successful` - успешный ответ
- `LLM error` - ошибка LLM
- `Summarization completed` - завершение обработки

## 🔄 Resilience Features

### Таймауты
Все API запросы к LLM имеют таймаут (по умолчанию 30 сек)

### Ретраи
- Максимум 3 попытки
- Экспоненциальная задержка: 1s, 2s, 4s...
- Логирование каждой попытки

### Fallback
При недоступности LLM сервис возвращает:
```json
{
  "original_text_length": 150,
  "summary": "Сервис временно недоступен, попробуйте позже.",
  "from_cache": false
}
```

## 🚦 Статус коды

- `200` - успешный запрос
- `422` - ошибка валидации
- `500` - внутренняя ошибка сервера
- `503` - сервис недоступен

## 📈 Мониторинг кеша

Health endpoint предоставляет статистику кеша:
- `hits` - количество попаданий в кеш
- `misses` - количество промахов
- `total_requests` - всего запросов
- `hit_rate_percent` - процент попаданий
- `cached_entries` - активные записи в кеше

## 🐛 Отладка

### Включение debug mode
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

### Просмотр логов
Адрес файла по умолчанию
logs/app.log


## 📄 Лицензия

MIT



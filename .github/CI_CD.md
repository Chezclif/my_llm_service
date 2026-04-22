# CI/CD Pipeline

## Overview

Проект использует GitHub Actions для автоматизации проверки качества кода и тестирования.

## Pipeline stages

### 1. **Lint** - Проверка качества кода
Запускается на Python 3.11, 3.12, 3.13
- **Ruff**: быстрая проверка стиля кода и потенциальных ошибок
- **Black**: проверка форматирования кода
- **MyPy**: проверка типов (опционально, не блокирует pipeline)

### 2. **Test** - Запуск тестов
Запускается на Python 3.11, 3.12, 3.13
- Запуск pytest с покрытием
- Генерация HTML отчета
- Загрузка результатов на Codecov
- Артефакты сохраняются для скачивания

### 3. **Dependencies** - Проверка зависимостей
- Сухая установка всех зависимостей
- Проверка импортов ключевых модулей
- Верификация совместимости

### 4. **Build** - Финальный статус
Суммирует результаты всех предыдущих job'ов

## Local Development

### Setup

```bash
# Установка dev зависимостей (включает pre-commit)
pip install -r requirements-dev.txt

# ИЛИ установить через виртуальное окружение
./venv/bin/pip install -r requirements-dev.txt

# Установка pre-commit hooks
./venv/bin/pre-commit install
# или если pre-commit установлен глобально:
pre-commit install
```

**Важно**: Если вы используете виртуальное окружение, всегда используйте `./venv/bin/pre-commit install` вместо `pre-commit install`

### Running Checks Locally

```bash
# Все проверки сразу
./run_tests.sh

# Или отдельно:

# Лinting (через venv)
./venv/bin/ruff check --fix .
./venv/bin/black .
./venv/bin/mypy .

# Или если инструменты установлены глобально:
ruff check --fix .
black .
mypy .

# Тестирование
pytest tests/
pytest tests/ --cov=. --cov-report=html

# Проверка форматирования (без изменений)
black --check .
ruff check .
```

## Artifacts

При прохождении тестов создаются артефакты:
- `test-report-py*.html` - Детальный HTML отчет тестов
- `coverage.xml` - XML файл покрытия кода

## Badges

Вы можете добавить badge в README:

```markdown
[![CI](https://github.com/yourusername/my_llm_service/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/my_llm_service/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/yourusername/my_llm_service/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/my_llm_service)
```

## Configuration

### GitHub Actions Secrets

Для загрузки покрытия на Codecov:
1. Перейти в Settings → Secrets and variables → Actions
2. Нажать "New repository secret"
3. Добавить: `CODECOV_TOKEN` (получить на https://codecov.io)

### pyproject.toml

Все инструменты настроены в `pyproject.toml`:
- Ruff settings
- Black settings
- MyPy settings
- Pytest settings

### .pre-commit-config.yaml

Локальные hooks перед коммитом:
- Ruff (с автофиксом)
- Black (форматирование)
- MyPy (проверка типов)
- Базовые проверки (trailing whitespace, etc.)

## Troubleshooting

### MyPy ошибки
Если mypy выдает ошибки, которые вам кажутся неправильными:
```bash
# Проверить конкретный файл
mypy llm/client.py --show-error-codes

# Игнорировать конкретную линию
x = some_function()  # type: ignore
```

### Ruff/Black конфликты
Они настроены для совместной работы. Если есть конфликт, запустить:
```bash
black .
ruff check --fix .
```

### Test failures локально
```bash
# Запустить с вывод вспомогательной информации
pytest -vvv tests/test_service.py

# Запустить последний тест, который не прошел
pytest --lf

# Запустить с debug информацией
pytest --pdb tests/test_service.py
```

## Performance

- Tests запускаются параллельно с `pytest-xdist` (включено с флагом `-n`)
- Pip кеш используется для ускорения установки зависимостей
- Matrix testing на 3 версиях Python одновременно

## Continuous Integration Best Practices

1. **Коммитьте часто** - маленькие, атомарные коммиты
2. **Пишите тесты** - минимум 80% покрытия
3. **Следуйте стилю** - используйте локальные проверки перед пушем
4. **Читайте ошибки** - GitHub Actions детально логирует проблемы
5. **Актуализируйте зависимости** - регулярно обновляйте requirements

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Black Documentation](https://black.readthedocs.io/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Pre-commit Framework](https://pre-commit.com/)

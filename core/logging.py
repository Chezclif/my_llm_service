"""Конфигурация структурированного логирования"""

import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class JSONFormatter(logging.Formatter):
    """JSON форматтер для структурированного логирования"""

    def format(self, record: logging.LogRecord) -> str:
        """Форматировать запись логирования как JSON"""
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Добавить дополнительные поля
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key not in (
                    "name",
                    "msg",
                    "args",
                    "created",
                    "filename",
                    "funcName",
                    "levelname",
                    "levelno",
                    "lineno",
                    "module",
                    "msecs",
                    "message",
                    "pathname",
                    "process",
                    "processName",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                ) and not key.startswith("_"):
                    log_data[key] = value

        # Добавить информацию об исключении
        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(log_level: str = "INFO", log_file: str | None = None) -> logging.Logger:
    """Настроить структурированное JSON логирование"""
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Удалить существующие обработчики
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Обработчик консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    # Обработчик файла (если указан)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Получить экземпляр логгера"""
    return logging.getLogger(name)


class StructuredLogger:
    """Обертка для структурированного логирования с контекстом"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def info(self, message: str, **context):
        """Логировать инфо-сообщение с контекстом"""
        extra = {"context": context} if context else {}
        self.logger.info(message, extra=extra)

    def error(self, message: str, **context):
        """Логировать сообщение об ошибке с контекстом"""
        extra = {"context": context} if context else {}
        self.logger.error(message, extra=extra)

    def warning(self, message: str, **context):
        """Логировать предупреждение с контекстом"""
        extra = {"context": context} if context else {}
        self.logger.warning(message, extra=extra)

    def debug(self, message: str, **context):
        """Логировать отладочное сообщение с контекстом"""
        extra = {"context": context} if context else {}
        self.logger.debug(message, extra=extra)

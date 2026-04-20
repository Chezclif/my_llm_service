"""Пользовательские исключения"""


class LLMServiceException(Exception):
    """Базовое исключение для сервиса LLM"""
    pass


class ValidationError(LLMServiceException):
    """Возникает при неудаче валидации ввода"""
    pass


class LLMAPIError(LLMServiceException):
    """Возникает при неудаче вызова API LLM"""
    pass


class LLMTimeoutError(LLMServiceException):
    """Возникает при истечении времени вызова API LLM"""
    pass


class ParseError(LLMServiceException):
    """Возникает при неудаче парсинга ответа"""
    pass

"""Модели запроса и ответа"""
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class SummarizeRequest(BaseModel):
    """Модель запроса для суммирования текста"""
    
    text: str = Field(
        ...,
        min_length=10,
        max_length=10000,
        description="Text to summarize"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="LLM temperature (0-2)"
    )
    
    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Проверить поле text"""
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()


class SummarizeResponse(BaseModel):
    """Модель ответа для суммирования текста"""
    
    original_text_length: int
    summary: str
    from_cache: bool = False


class ErrorResponse(BaseModel):
    """Модель ошибки ответа"""
    
    error_code: str
    error_message: str
    details: Optional[dict] = None


class HealthResponse(BaseModel):
    """Ответ проверки здоровья"""
    
    status: str
    version: str
    cache_stats: dict

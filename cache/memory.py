"""Кеширование в памяти с поддержкой TTL"""

import hashlib
import json
import time
from typing import Any


class CacheEntry:
    """Запись кеша с TTL"""

    def __init__(self, value: Any, ttl: int) -> None:  # Добавлена аннотация возврата
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl

    def is_expired(self) -> bool:
        """Проверить, истек ли срок действия записи кеша"""
        return time.time() - self.created_at > self.ttl


class Cache:
    """Кеш в памяти с TTL"""

    def __init__(self) -> None:  # Добавлена аннотация возврата
        self._cache: dict[str, CacheEntry] = {}
        self._stats: dict[str, int | float] = {  # Явная аннотация типа
            "hits": 0,
            "misses": 0,
            "total_requests": 0,
        }

    @staticmethod
    def _generate_key(
        text: str,  # Добавлена аннотация
        model: str,  # Добавлена аннотация
        temperature: float,  # Добавлена аннотация
        system_prompt: str,  # Добавлена аннотация
    ) -> str:  # Добавлена аннотация возврата
        """Сгенерировать ключ кеша из параметров"""
        key_data = json.dumps(
            {
                "text": text,
                "model": model,
                "temperature": temperature,
                "system_prompt": system_prompt,
            },
            sort_keys=True,
            ensure_ascii=False,
        )

        return hashlib.sha256(key_data.encode()).hexdigest()

    def get(self, text: str, model: str, temperature: float, system_prompt: str) -> Any | None:
        """Получить значение из кеша"""
        self._stats["total_requests"] += 1
        key = self._generate_key(text, model, temperature, system_prompt)

        if key not in self._cache:
            self._stats["misses"] += 1
            return None

        entry = self._cache[key]
        if entry.is_expired():
            del self._cache[key]
            self._stats["misses"] += 1
            return None

        self._stats["hits"] += 1
        return entry.value

    def set(
        self, text: str, model: str, temperature: float, system_prompt: str, value: Any, ttl: int
    ) -> None:
        """Установить значение в кеш"""
        key = self._generate_key(text, model, temperature, system_prompt)
        self._cache[key] = CacheEntry(value, ttl)

    def clear(self) -> None:
        """Очистить весь кеш"""
        self._cache.clear()

    def get_stats(self) -> dict[str, int | float]:  # Уточнен тип возврата
        """Получить статистику кеша"""
        total = self._stats["total_requests"]
        hits = self._stats["hits"]
        hit_rate = (hits / total * 100) if total > 0 else 0

        return {
            "hits": hits,
            "misses": self._stats["misses"],
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 2),
            "cached_entries": len(self._cache),
        }


# Глобальный экземпляр кеша
_cache = Cache()


def get_cache() -> Cache:
    """Получить глобальный экземпляр кеша"""
    return _cache

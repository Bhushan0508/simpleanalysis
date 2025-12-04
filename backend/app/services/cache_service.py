import json
import logging
from typing import Optional, Any
from datetime import timedelta
import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis caching service for stock data"""

    _redis_client: Optional[redis.Redis] = None

    @classmethod
    async def get_client(cls) -> redis.Redis:
        """Get or create Redis client"""
        if cls._redis_client is None:
            try:
                cls._redis_client = redis.from_url(
                    settings.REDIS_URL,
                    password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                    decode_responses=True
                )
                # Test connection
                await cls._redis_client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise

        return cls._redis_client

    @classmethod
    async def close(cls):
        """Close Redis connection"""
        if cls._redis_client:
            await cls._redis_client.close()
            cls._redis_client = None
            logger.info("Redis connection closed")

    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            client = await cls.get_client()
            value = await client.get(key)

            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    @classmethod
    async def set(
        cls,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 300 seconds / 5 minutes)

        Returns:
            True if successful, False otherwise
        """
        try:
            client = await cls.get_client()
            serialized_value = json.dumps(value)

            if ttl is None:
                ttl = 300  # Default 5 minutes

            await client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    @classmethod
    async def delete(cls, key: str) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            client = await cls.get_client()
            await client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    @classmethod
    async def delete_pattern(cls, pattern: str) -> int:
        """
        Delete all keys matching a pattern

        Args:
            pattern: Key pattern (e.g., "stock:*")

        Returns:
            Number of keys deleted
        """
        try:
            client = await cls.get_client()
            keys = []

            async for key in client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                deleted = await client.delete(*keys)
                return deleted

            return 0
        except Exception as e:
            logger.error(f"Error deleting keys with pattern {pattern}: {e}")
            return 0

    @classmethod
    async def exists(cls, key: str) -> bool:
        """
        Check if key exists in cache

        Args:
            key: Cache key

        Returns:
            True if exists, False otherwise
        """
        try:
            client = await cls.get_client()
            result = await client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False

    @classmethod
    def make_stock_key(cls, symbol: str, data_type: str = "info") -> str:
        """
        Generate cache key for stock data

        Args:
            symbol: Stock symbol
            data_type: Type of data (info, historical, etc.)

        Returns:
            Cache key string
        """
        return f"stock:{symbol}:{data_type}"

    @classmethod
    def make_search_key(cls, query: str) -> str:
        """
        Generate cache key for search results

        Args:
            query: Search query

        Returns:
            Cache key string
        """
        return f"search:{query.lower()}"

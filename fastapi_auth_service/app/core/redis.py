"""
Redis Connection Module.

This module provides a function to connect to Redis asynchronously
using settings from a central configuration file (Pydantic Settings).
"""

import redis.asyncio as redis  # Using an asynchronous Redis client
from fastapi_auth_service.app.core.settings import settings  # Import settings from Pydantic config


# Redis cache is created once and is accessible as a variable
redis_cache = redis.Redis(
    host=settings.REDIS_HOST,  # Redis server address, for example "localhost"
    port=settings.REDIS_PORT,  # Redis server port, usually 6379
    decode_responses=True      # Decodes bytes into strings automatically
)

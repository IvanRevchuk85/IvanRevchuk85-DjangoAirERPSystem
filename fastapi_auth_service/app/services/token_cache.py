"""
Module for working with access and refresh tokens in Redis.

A global Redis client (redis_cache) is used, connected via asynchronous redis.
All values ​​are taken from settings.py via Pydantic configuration.
"""

from fastapi_auth_service.app.core.redis import redis_cache  # Global redis client
# Project Configuration (Pydantic)
from fastapi_auth_service.app.core.settings import settings


# Access token lifetime in seconds (from .env -> settings.py)
ACCESS_TOKEN_EXPIRE_SECONDS = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

# Refresh token lifetime in seconds (from .env -> settings.py)
REFRESH_TOKEN_EXPIRE_SECONDS = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


async def store_access_token(token: str, user_id: int) -> None:
    """
    Stores the access token in Redis with a binding to the user_id.
    Used for additional token verification (optional).
    """
    await redis_cache.set(f"access_token:{token}", user_id, ex=ACCESS_TOKEN_EXPIRE_SECONDS)


async def store_refresh_token(token: str, user_id: int) -> None:
    """
   Stores a refresh token in Redis with a binding to user_id. 
   This allows for logout/revocation of the token and session extension.
    """
    await redis_cache.set(f"refresh_token:{token}", user_id, ex=REFRESH_TOKEN_EXPIRE_SECONDS)


async def is_access_token_valid(token: str) -> bool:
    """
    Checks for the presence of an access token in Redis.
    Used to validate the token on the server side.
    """
    value = await redis_cache.get(f"access_token:{token}")
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False


async def is_refresh_token_valid(token: str) -> bool:
    """
    Checks for a refresh token in Redis.
    Used before refreshing an access token.
    """
    return await redis_cache.exists(f"refresh_token:{token}") == 1


async def delete_access_token(token: str) -> None:
    """
    Removes an access token from Redis (logout or revoke rights).
    """
    await redis_cache.delete(f"access_token:{token}")


async def delete_refresh_token(token: str) -> None:
    """
    Removes a refresh token from Redis (logout or revoke the refresh token).
    """
    await redis_cache.delete(f"refresh_token:{token}")

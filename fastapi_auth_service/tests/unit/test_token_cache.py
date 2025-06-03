import pytest
import asyncio
from fastapi_auth_service.app.services.token_cache import (
    store_access_token,
    is_access_token_valid,
    delete_access_token,
    redis_cache
)
from fastapi_auth_service.tests.db_waiter import wait_for_postgres  #


@pytest.mark.asyncio
async def test_store_and_validate_access_token():
    await wait_for_postgres()
    token = "test_token_123"
    user_id = 99

    await store_access_token(token, user_id)
    result = await is_access_token_valid(token)
    assert result is True


@pytest.mark.asyncio
async def test_access_token_expiration():
    await wait_for_postgres()
    token = "token_expires"
    user_id = 101

    await redis_cache.set(f"access_token:{token}", user_id, ex=1)
    await asyncio.sleep(2)

    result = await is_access_token_valid(token)
    assert result is False


@pytest.mark.asyncio
async def test_delete_access_token():
    await wait_for_postgres()
    token = "token_delete"
    user_id = 123

    await store_access_token(token, user_id)
    await delete_access_token(token)
    result = await is_access_token_valid(token)
    assert result is False


@pytest.mark.asyncio
async def test_invalid_token_data():
    await wait_for_postgres()
    token = "bad_token_value"

    # Save a string instead of an ID, as if someone had replaced the Redis value
    await redis_cache.set(f"access_token:{token}", "not_a_number")
    result = await is_access_token_valid(token)
    assert result is False

import pytest
import uuid

from fastapi import status
from uuid import uuid4


@pytest.mark.anyio
async def test_register_user(async_client, wait_for_db):
    """
    Checking successful registration of a new user.
    """
    # Generate a unique email
    email = f"user_{uuid4().hex}@example.com"

    response = await async_client.post("/auth/register", json={
        "email": email,
        "password": "StrongPass123!"
    })

    # Allow both codes 200 or 201 depending on the implementation
    assert response.status_code in (
        status.HTTP_200_OK, status.HTTP_201_CREATED), response.text
    assert response.json(), "Ответ пустой, возможно, сервер упал или не возвращает JSON"

    data = response.json()
    assert "email" in data
    assert data["email"] == email


@pytest.mark.asyncio
async def test_register_duplicate_user(async_client):
    """
    Checks that registration with an existing email gives an error.
    """
    email = f"{uuid.uuid4().hex}@example.com"
    user_data = {
        "email": email,
        "password": "StrongPass123!"
    }

    # First registration
    response1 = await async_client.post("/auth/register", json=user_data)
    assert response1.status_code in (200, 201)

    # Second registration with the same email
    response2 = await async_client.post("/auth/register", json=user_data)
    assert response2.status_code == 400  # or 409 - depends on the implementation
    assert "detail" in response2.json()
    assert "существует" in response2.json()["detail"].lower()

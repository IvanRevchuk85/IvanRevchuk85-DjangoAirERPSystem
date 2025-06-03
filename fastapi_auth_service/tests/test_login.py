import pytest
from fastapi import status
from uuid import uuid4  # To generate a unique email
from httpx import AsyncClient


@pytest.mark.anyio
async def test_login_user(async_client, wait_for_db):
    """
    ✅ Successful login after registration.
    """
    # 🆕 Generate a unique email
    email = f"user_{uuid4().hex}@example.com"
    password = "StrongPass123!"

    # 🔐 Register a user
    register_response = await async_client.post("/auth/register", json={
        "email": email,
        "password": password
    })
    print("REGISTER STATUS:", register_response.status_code)
    print("REGISTER BODY:", register_response.text)

    assert register_response.status_code in [
        status.HTTP_201_CREATED, status.HTTP_200_OK]

    # 🔑 Login
    login_response = await async_client.post("/auth/login", data={
        "username": email,
        "password": password
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})

    assert login_response.status_code == status.HTTP_200_OK
    json_data = login_response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_wrong_password(async_client, wait_for_db):
    """
    ❌ Login with incorrect password - should return 401.
    """
    # 🆕 Unique email
    email = f"user_{uuid4().hex}@example.com"
    correct_password = "CorrectPass123!"
    wrong_password = "WrongPass456!"

    # 🔐 Register a user
    register_response = await async_client.post("/auth/register", json={
        "email": email,
        "password": correct_password
    })

    assert register_response.status_code in [
        status.HTTP_200_OK, status.HTTP_201_CREATED]

    # 🚫 We are trying to log in with an incorrect password.
    response = await async_client.post("/auth/login", data={
        "username": email,
        "password": wrong_password
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})

    # ✅ Failure check
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_logout_user_success(authorized_client: AsyncClient):
    """
    Checks whether the authorized user has successfully logged out.
    """
    # Call logout
    response = await authorized_client.post("/auth/logout")

    # Checking the status and message
    assert response.status_code == 200
    assert response.json() == {"message": "Logged out"}


@pytest.mark.asyncio
async def test_logout_user_unauthorized(async_client: AsyncClient):
    """
    Checks that logout is available even without a token.
    """
    response = await async_client.post("/auth/logout")

    # Check that the server is not complaining (200)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_refresh_access_token(async_client, registered_user):
    """
    Checks that the access_token can be refreshed using the refresh_token.
    """
    # Login
    response = await async_client.post("/auth/login", data={
        "username": registered_user["email"],
        "password": registered_user["password"]
    })
    assert response.status_code == 200, response.text

    tokens = response.json()
    assert "refresh_token" in tokens

    # Update access_token
    response2 = await async_client.post("/auth/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })

    assert response2.status_code == 200, response2.text
    new_tokens = response2.json()
    assert "access_token" in new_tokens

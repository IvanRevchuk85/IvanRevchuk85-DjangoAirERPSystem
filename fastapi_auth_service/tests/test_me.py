import pytest
from httpx import AsyncClient
from starlette import status
from uuid import uuid4


@pytest.mark.anyio
async def test_get_current_user(async_client, wait_for_db):
    """
    Checks that the authorized user can retrieve their data.
    """
    email = f"user_{uuid4().hex}@example.com"
    password = "StrongPass123!"

    # Register a user
    register_response = await async_client.post("/auth/register", json={
        "email": email,
        "password": password
    })
    assert register_response.status_code in {
        status.HTTP_200_OK, status.HTTP_201_CREATED}

    # Login
    login_response = await async_client.post("/auth/login", data={
        "username": email,
        "password": password
    })
    assert login_response.status_code == status.HTTP_200_OK

    # We receive a token
    token = login_response.json()["access_token"]

    # Updating your profile
    update_response = await async_client.put(
        "/users/profile",
        json={"first_name": "Test", "last_name": "User"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_response.status_code == status.HTTP_200_OK

    # We make a request to /users/profile
    me_response = await async_client.get("/users/profile", headers={
        "Authorization": f"Bearer {token}"
    })
    assert me_response.status_code == status.HTTP_200_OK

    me_data = me_response.json()
    assert me_data["email"] == email
    assert me_data["first_name"] == "Test"
    assert me_data["last_name"] == "User"


@pytest.mark.anyio
async def test_get_current_user_unauthorized(async_client, wait_for_db):
    """
    Checks that access is denied without a token.
    """
    response = await async_client.get("/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

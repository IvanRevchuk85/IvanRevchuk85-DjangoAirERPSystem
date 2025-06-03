import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.anyio
async def test_change_password_login(async_client, changed_password, wait_for_db):
    """
    Checks that after changing the password, 
    the user can log in with the new password, and the old one no longer works.
    """
    # Login with old password
    response_old = await async_client.post(
        "/auth/login",
        data={
            "username": changed_password["email"],
            "password": "StrongPass123!"  # Old Password
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response_old.status_code == status.HTTP_401_UNAUTHORIZED

    # Login with new password
    response_new = await async_client.post(
        "/auth/login",
        data={
            "username": changed_password["email"],
            "password": changed_password["password"]  # New Password
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response_new.status_code == status.HTTP_200_OK

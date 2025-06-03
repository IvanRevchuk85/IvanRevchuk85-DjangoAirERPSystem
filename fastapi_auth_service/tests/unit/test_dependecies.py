import pytest
from fastapi import Depends, HTTPException
from fastapi_auth_service.app.core.dependencies import is_admin, is_user
from fastapi_auth_service.app.models.user import User


@pytest.mark.asyncio
async def test_is_admin_returns_user_if_admin():
    """
    ✅ Checks that is_admin returns the user if he has the role 'admin'
    """
    # Create a fake user with the admin role
    admin_user = User(id=1, email="admin@test.com", role="admin")

    # Call the dependency directly by passing a fake user
    result = await is_admin(current_user=admin_user)

    # Make sure that the same object is returned.
    assert result == admin_user


@pytest.mark.asyncio
async def test_is_admin_raises_if_not_admin():
    """
    ❌ Checks that is_admin throws an exception if the user is not admin
    """
    # Fake user with role 'user'
    user = User(id=2, email="user@test.com", role="user")

    # Check that a 404 exception is raised
    with pytest.raises(HTTPException) as exc_info:
        await is_admin(current_user=user)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Not found"


@pytest.mark.asyncio
async def test_is_user_returns_user_if_role_is_user():
    """
    ✅ Checks that is_user returns the user if its role is user
    """
    user = User(id=3, email="testuser@example.com", role="user")

    result = await is_user(current_user=user)

    # Let's make sure the function returns the passed user.
    assert result == user


@pytest.mark.asyncio
async def test_is_user_raises_404_if_role_not_user():
    """
    ❌ Checks that is_user throws 404 if role is not user
    """
    user = User(id=4, email="notuser@example.com", role="admin")

    with pytest.raises(HTTPException) as exc_info:
        await is_user(current_user=user)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Not found"

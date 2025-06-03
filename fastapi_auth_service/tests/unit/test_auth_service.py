import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from fastapi_auth_service.app.services.auth_service import register_user, authenticate_user, change_user_password
from fastapi_auth_service.app.schemas.user import UserCreate, PasswordChange
from fastapi_auth_service.app.models.user import User
from fastapi_auth_service.app.utils.security import hash_password, verify_password

from fastapi_auth_service.app.models.user import UserRoleEnum


@pytest.mark.asyncio
async def test_register_user_success(wait_for_db):
    mock_session = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = lambda: None
    mock_session.execute.return_value = mock_result

    mock_user = User(id=1, email="test@example.com", hashed_password="hashed")
    mock_session.refresh = AsyncMock(return_value=None)
    mock_session.commit = AsyncMock()

    def _add(user):
        mock_user.email = user.email

    mock_session.add.side_effect = _add

    user_create = UserCreate(email="test@example.com",
                             password="StrongPass123!")
    result = await register_user(user_create, session=mock_session)

    assert result.email == "test@example.com"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_register_user_exiting_email(wait_for_db):
    """
    Registration with an existing email should result in an HTTP 400
    """
    existing_user = User(id=1, email="test@example.com",
                         hashed_password="hashed")
    mock_session = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = lambda: existing_user
    mock_session.execute.return_value = mock_result

    user_create = UserCreate(email="test@example.com",
                             password="StrongPass123!")

    with pytest.raises(HTTPException) as exc_info:
        await register_user(user_create, session=mock_session)

    assert exc_info.value.status_code == 400
    assert "существует" in exc_info.value.detail


@pytest.mark.asyncio
async def test_authenticate_user_success(wait_for_db):
    """
    Successful authentication by email and password
    """
    plain_password = "StrongPass123!"
    hashed = hash_password(plain_password)

    user = User(
        id=1,
        email="test@example.com",
        hashed_password=hashed,
        first_name="Ivan",
        last_name="Test",
        is_blocked=False,
        balance=200,
        created_at=None,
        updated_at=None,
        last_activity_at=None,
        role=UserRoleEnum.user
    )

    # Mocking the result execute
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = AsyncMock(return_value=user)

    # Mocking the session
    mock_session = MagicMock()
    mock_result.scalar_one_or_none = lambda: user

    mock_session = MagicMock()
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Mocking session.begin as an asynchronous context manager
    mock_transaction = AsyncMock()
    mock_transaction.__aenter__.return_value = None
    mock_transaction.__aexit__.return_value = None
    mock_session.begin.return_value = mock_transaction

    # Authentication
    authenticated_user = await authenticate_user(
        email="test@example.com",
        password=plain_password,
        session=mock_session,
    )

    assert authenticated_user is not None
    assert authenticated_user.email == user.email
    assert authenticated_user.first_name == user.first_name


@pytest.mark.asyncio
async def test_change_user_password_success(wait_for_db):
    """
    Successful password change
    """
    # Old and new password
    old_password = "OldPass123!"
    new_password = "NewPass456!"
    hashed_old = hash_password(old_password)

    # Create an "existing" user with a hash
    user = User(
        id=1,
        email="test@example.com",
        hashed_password=hashed_old,
        first_name="Ivan",
        last_name="Test",
        is_blocked=False,
        balance=100
    )

    # Mock the query result in the DB
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = lambda: user

    # Mock session.begin as an async context manager
    mock_transaction = AsyncMock()
    mock_transaction.__aenter__ = AsyncMock(return_value=None)
    mock_transaction.__aexit__ = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.begin.return_value = mock_transaction
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Input data
    data = PasswordChange(
        email="test@example.com",
        old_password=old_password,
        new_password=new_password
    )

    # Call the password change function
    await change_user_password(data, session=mock_session)

    # Let's check that the password has actually changed
    assert verify_password(new_password, user.hashed_password)

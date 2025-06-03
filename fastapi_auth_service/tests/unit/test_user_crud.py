import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_auth_service.app.repositories import user as user_crud
from fastapi_auth_service.app.models.user import User
from uuid import uuid4
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_get_balance_return_correct_balance(async_session: AsyncSession):
    """
    Checks that the get_balance function returns the correct user balance.
    """
    # Create a user manually
    new_user = User(
        email=f"test_balance_{uuid4().hex}@example.com",
        hashed_password="hashedpassword",
        first_name="Test",
        last_name="Balance",
        balance=250
    )
    async_session.add(new_user)
    await async_session.commit()
    await async_session.refresh(new_user)

    # Get the balance through repositories
    balance = await user_crud.get_balance(new_user.id, async_session)

    # Check that the balance matches
    assert balance == 250


@pytest.mark.asyncio
async def test_update_balance_changes_user_balance(async_session: AsyncSession):
    """
    Checks that update_balance adds a value to the user's current balance.
    """

    # Create a user manually with an initial balance of 100
    new_user = User(
        email=f"test_balance_{uuid4().hex}@example.com",
        hashed_password="hashedpassword",
        first_name="Test",
        last_name="Balance",
        balance=100
    )
    async_session.add(new_user)
    await async_session.commit()
    await async_session.refresh(new_user)

    # Update balance (add 500)
    amount_to_add = 500
    await user_crud.update_balance(new_user.id, amount_to_add, async_session)

    # Getting the user again
    updated_user = await async_session.get(User, new_user.id)

    # Check that the balance has increased by 500
    assert updated_user.balance == 100 + amount_to_add


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(async_session: AsyncSession):
    """
    Checks that get_user_by_id returns None if a user with that ID does not exist.
    """
    non_existent_user_id = 999999  # obviously non-existent ID

    # Trying to get the user
    user = await user_crud.get_user_by_id(non_existent_user_id, async_session)

    # Expecting user not found
    assert user is None


@pytest.mark.asyncio
async def test_get_balance_user_not_found(async_session: AsyncSession):
    """
    Checks that get_balance returns None if a user with that ID does not exist.
    """
    fake_user_id = 987654  # ID, that is not in the database

    # Trying to get balance of non-existent user
    balance = await user_crud.get_balance(fake_user_id, async_session)

    # Expect None
    assert balance is None


@pytest.mark.asyncio
async def test_update_balance_missing_name_or_lastname(async_session: AsyncSession):
    """
    Checks that update_balance does not fire if firstname or lastname are not set.
    """
    # Create a user without a first and last name
    user = User(
        email=f"user_noname_{uuid4().hex}@example.com",
        hashed_password="hashedpassword",
        balance=100
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    # We are trying to change the balance
    result = await user_crud.update_balance(user.id, 50, async_session)

    # Expecting None because first and last name are missing
    assert result is None


@pytest.mark.asyncio
async def test_update_balance_admin_forbidden(async_session: AsyncSession):
    """
    Checks that the administrator cannot have an active balance.
    Waiting for HTTP 403 Forbidden.
    """
    # Create a user with the admin role
    admin_user = User(
        email=f"admin_{uuid4().hex}@example.com",
        hashed_password="hashedpassword",
        first_name="Admin",
        last_name="User",
        role="admin",
        balance=0
    )
    async_session.add(admin_user)
    await async_session.commit()
    await async_session.refresh(admin_user)

    # Trying to change the balance - expecting an exception
    with pytest.raises(HTTPException) as exc_info:
        await user_crud.update_balance(admin_user.id, 100, async_session)

    # Checking that the error is 403
    assert exc_info.value.status_code == 403
    assert "Admin users cannot have an active balance" in exc_info.value.detail


@pytest.mark.asyncio
async def test_update_balance_prevent_negative_balance(async_session: AsyncSession):
    """
    Checks that update_balance does not allow the balance to go negative.
    If you try to subtract more than there is, None is returned.
    """
    # Create a user with a small balance
    user = User(
        email=f"negative_{uuid4().hex}@example.com",
        hashed_password="hashedpassword",
        first_name="No",
        last_name="Money",
        balance=100
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    # We are trying to subtract more than we have.
    result = await user_crud.update_balance(user.id, -200, async_session)

    # Expecting None - Operation not permitted
    assert result is None


@pytest.mark.asyncio
async def test_update_balance_requires_name_and_surname(async_session: AsyncSession):
    """
    Checks that the balance cannot be changed if the first or last name is not specified.
    """
    # Create a user without a first and last name
    user = User(
        email=f"noname_{uuid4().hex}@example.com",
        hashed_password="hashedpassword",
        first_name=None,
        last_name=None,
        balance=100
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    # We are trying to change the balance
    result = await user_crud.update_balance(user.id, 100, async_session)

    # Expect None - first and last name are required
    assert result is None


@pytest.mark.asyncio
async def test_update_user_only_first_name_returns_none(async_session: AsyncSession):
    """
    Checks that if only the first name is specified without the last name, 
    the update will not occur (returns None).
    """

    # Create a new user
    new_user = User(
        email=f"test_update_only_name_{uuid4().hex}@example.com",
        hashed_password="hashedpassword",
        first_name="Original",
        last_name="User"
    )
    async_session.add(new_user)
    await async_session.commit()
    await async_session.refresh(new_user)

    # Trying to update first name only (no last name)
    updates = {"first_name": "UpdatedOnly"}

    # Expecting a function to return None (update not allowed)
    result = await user_crud.update_user(user_id=new_user.id, updates=updates, session=async_session)

    assert result is None  # The update should not happen


@pytest.mark.asyncio
async def test_update_user_only_last_name_returns_none(async_session: AsyncSession):
    """
    Checks that if only the last name is specified without the first name,
    the update will not occur (returns None).
    """

    # Create a user
    new_user = User(
        email=f"test_update_only_last_{uuid4().hex}@example.com",
        hashed_password="hashedpassword",
        first_name="Original",
        last_name="User"
    )
    async_session.add(new_user)
    await async_session.commit()
    await async_session.refresh(new_user)

    # Trying to update only the last name
    updates = {"last_name": "UpdatedOnly"}

    # Expecting the update to be rejected
    result = await user_crud.update_user(user_id=new_user.id, updates=updates, session=async_session)

    assert result is None  # The update should not happen


@pytest.mark.asyncio
async def test_update_balance_missing_name_or_lastname_returns_none(async_session: AsyncSession):
    """
    Checks that if the user does not have a first_name or last_name,
    update_balance will return None (the operation will fail).
    """

    # User without name
    user_no_first_name = User(
        email=f"no_name_{uuid4().hex}@example.com",
        hashed_password="hashed",
        first_name=None,
        last_name="Last",
        balance=100,
        role="user"
    )
    async_session.add(user_no_first_name)

    # User without last name
    user_no_last_name = User(
        email=f"no_lastname_{uuid4().hex}@example.com",
        hashed_password="hashed",
        first_name="First",
        last_name=None,
        balance=100,
        role="user"
    )
    async_session.add(user_no_last_name)

    await async_session.commit()
    await async_session.refresh(user_no_first_name)
    await async_session.refresh(user_no_last_name)

    # Trying to change the balance
    result1 = await user_crud.update_balance(user_no_first_name.id, 50, async_session)
    result2 = await user_crud.update_balance(user_no_last_name.id, 50, async_session)

    assert result1 is None
    assert result2 is None

"""
CRUD functions for working with users in the database.

The following are implemented here:
- Getting a user by ID
- Getting a list of users with filtering and sorting
- Updating a user profile
- Getting the current user balance
- Changing the user balance
"""

from sqlalchemy import select, asc, desc, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from typing import List, Optional
from fastapi_auth_service.app.models.user import User
from datetime import datetime
from fastapi import HTTPException


async def get_user_by_id(user_id: int, session: AsyncSession) -> Optional[User]:
    """
    Get user from database by ID.

    :param user_id: User ID
    :param session: SQLAlchemy asynchronous session
    :return: user object or None if not found
    """

    query = select(User).where(User.id == user_id)  # Building an SQL query
    result = await session.execute(query)  # We carry out
    user = result.scalar_one_or_none()  # We get one user
    return user


async def get_users_filtered_sorted(
        session: AsyncSession,
        filters: dict,
        sort_by: str = "id",
        sort_order: str = "asc"
) -> List[User]:
    """
    Get all users with filtering and sorting
    :param session: Asynchronous SQLAlchemy session
    :param filters: Filter dictionary (id, first_name, last_name, is_blocked)
    :param sort_by: Sort field (id, balance, last_activity_at)
    :param sort_order: Sort direction ("asc" or "desc")
    :return: List of users as dictionaries
    """
    query = select(User)  # Let's start building a query
    # Applying filters
    if "id" in filters:
        query = query.where(User.id == filters["id"])
    if "first_name" in filters:
        query = query.where(User.first_name.ilike(
            f"%{filters['first_name']}%"))
    if "last_name" in filters:
        query = query.where(User.last_name.ilike(f"%{filters['last_name']}%"))
    if "is_blocked" in filters:
        query = query.where(User.is_blocked == filters["is_blocked"])

    # Excluding soft deleted users
    query = query.where(User.is_deleted == False)

    # Apply sorting
    # if an invalid field is passed - sort by id
    sort_column = getattr(User, sort_by, User.id)
    sort_fn = asc if sort_order.lower() == "asc" else desc
    query = query.order_by(sort_fn(sort_column))

    # We execute the request
    result = await session.execute(query)
    users = result.scalars().all()

    # We form a list of users in dictionary format
    return {
        user.id: {
            "user_id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_activity_at": user.last_activity_at,
            "block": user.is_blocked,
            "block_at": user.blocked_at,
            "role": user.role,
            "balance": user.balance
        }
        for user in users
    }


async def update_user(user_id: int, updates: dict, session: AsyncSession) -> Optional[User]:
    """
   Update user profile.

    Requirement: if updating first or last name - be sure to pass both fields!

    :param user_id: User ID
    :param updates: Fields to update
    :param session: Asynchronous session
    :return: Updated user or None
    """
    # Let's add an update timestamp
    updates["updated_at"] = datetime.utcnow()

    # Validation: If either first name or last name is updated, both fields must be set
    if ("first_name" in updates or "last_name" in updates):
        if not updates.get("first_name") or not updates.get("last_name"):
            # If one of the fields is missing, reject the update.
            return None

    # Forming an update request
    query = (
        update(User)
        .where(User.id == user_id)
        .values(**updates)
        # Session synchronization
        .execution_options(synchronize_session="fetch")
    )

    # We perform UPDATE
    await session.execute(query)

    # Commit the changes
    await session.commit()

    # We receive an updated user
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user


async def get_balance(user_id: int, session: AsyncSession) -> Optional[int]:
    """
    Get current balance of user by ID
    :param user_id: User ID
    :param session: SQLAlchemy asynchronous session
    :return: balance value or None if user not found
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user:
        return user.balance
    return None


async def update_balance(user_id: int, amount: int, session: AsyncSession) -> Optional[int]:
    """
    Update user balance (add or subtract).

    Requirements:
    - User must exist
    - First_name and last_name must be filled in
    - Balance cannot be less than 0

    :param user_id: User ID
    :param amount: How much to change balance
    :param session: Asynchronous session
    :return: New balance or None
    """
    # Getting the user
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        return None

    #  Admin cannot have an active balance
    if user.role == "admin":
        raise HTTPException(
            status_code=403, detail="Admin users cannot have an active balance")

    # Condition: first and last name are required
    if not user.first_name or not user.last_name:
        return None

    # We check that we won't go into the minus
    new_balance = user.balance + amount
    if new_balance < 0:
        return None

    # Updating the balance
    user.balance = new_balance
    user.updated_at = datetime.utcnow()
    await session.commit()

    return new_balance


async def set_block_status(user_id: int, block: bool, session: AsyncSession) -> bool:
    """
    Block or unblock user
    :param user_id: User ID
    :param block: True - block, False - unblock
    :param session: session
    :return: True/False - whether the update was successful
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        return False

    user.is_blocked = block
    user.updated_at = datetime.utcnow()
    await session.commit()
    return True


async def soft_delete_user(user_id: int, session: AsyncSession) -> bool:
    """
    Soft delete user (sets is_deleted = True).
    :param user_id: User ID
    :param sesson: asynchronous session
    :return: True if user found and deleted; False if not found
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        return False

    user.is_deleted = True  # Mark as deleted
    user.updated_at = datetime.utcnow()
    await session.commit()
    return True


async def get_deleted_users(session: AsyncSession):
    query = select(User).where(User.is_deleted == True)
    result = await session.execute(query)
    return result.scalars().all()

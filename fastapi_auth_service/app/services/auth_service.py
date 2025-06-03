from typing import Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi_auth_service.app.schemas.user import (
    UserCreate,
    UserOut,
    PasswordChange,
    UserRegisterResponse
)
from fastapi_auth_service.app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)
from fastapi_auth_service.app.models.user import User, UserRoleEnum
from fastapi_auth_service.app.services.token_cache import (
    store_access_token,
    store_refresh_token,
)


# ✅ User registration
async def register_user(user: UserCreate, session: AsyncSession) -> UserRegisterResponse:
    result = await session.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        if existing_user.is_deleted:
            # Recovering a deleted user
            existing_user.hashed_password = hash_password(user.password)
            existing_user.is_deleted = False
            existing_user.first_name = None
            existing_user.last_name = None
            existing_user.balance = 0
            existing_user.updated_at = None
            existing_user.last_activity_at = None
            existing_user.blocked_at = None
            await session.commit()
            return UserRegisterResponse(email=existing_user.email)

        raise HTTPException(
            status_code=400, detail="A user with this email already exists")

    # New user registration
    hashed_pw = hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed_pw,
                    role=UserRoleEnum.user)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return UserRegisterResponse(email=new_user.email)


# ✅ User authentication
async def authenticate_user(email: str, password: str, session: AsyncSession) -> Optional[UserOut]:
    async with session.begin():
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

    if not user:
        return None

    # Blocked
    if user.is_blocked:
        raise HTTPException(status_code=403, detail="Your account is blocked.")

    # Deleted
    if user.is_deleted:
        raise HTTPException(
            status_code=403, detail="Your account has been deleted.")

    if not verify_password(password, user.hashed_password):
        return None

    return UserOut(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_blocked=user.is_blocked,
        balance=user.balance,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_activity_at=user.last_activity_at,
        role=user.role
    )

# ✅ Generating and storing tokens


async def create_and_store_tokens(user_id: int) -> dict:
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    # Storing tokens in Redis with different lifetimes
    await store_access_token(access_token, user_id)
    await store_refresh_token(refresh_token, user_id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# ✅ Change password
async def change_user_password(data: PasswordChange, session: AsyncSession):
    async with session.begin():
        result = await session.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(data.old_password, user.hashed_password):
            raise HTTPException(
                status_code=401, detail="Old password is incorrect")

        user.hashed_password = hash_password(data.new_password)

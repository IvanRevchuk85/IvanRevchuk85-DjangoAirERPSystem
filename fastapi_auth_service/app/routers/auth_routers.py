from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from fastapi_auth_service.app.schemas.user import UserCreate, PasswordChange, UserRegisterResponse
from fastapi_auth_service.app.services.auth_service import (
    register_user,
    authenticate_user,
    change_user_password,
)
from fastapi_auth_service.app.services.token_cache import (
    store_access_token,
    store_refresh_token,
    delete_access_token,
    is_access_token_valid, is_refresh_token_valid,
)
from fastapi_auth_service.app.utils.security import (
    decode_access_token,
    decode_refresh_token,
    create_access_token,
    create_refresh_token,
    oauth2_scheme,
)

from fastapi_auth_service.app.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_auth_service.app.repositories import user as user_crud
from pydantic import BaseModel
from fastapi_auth_service.app.core.settings import settings


router = APIRouter()

# Регистрация


@router.post("/register", response_model=UserRegisterResponse)
async def register(user: UserCreate, session: AsyncSession = Depends(get_async_session)):
    return await register_user(user, session=session)


# Login
@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session)
):
    user = await authenticate_user(form_data.username, form_data.password, session=session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Attempt to increase user balance
    try:
        await user_crud.update_balance(user.id, 100, session)
        await session.commit()
    except Exception as e:
        # We'll just log it or ignore it so that the login doesn't break.
        print(f"Failed to update balance for user {user.id}: {str(e)}")

    # Generate a token only after all operations
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Storing tokens in Redis with their lifetime
    await store_access_token(access_token, user.id)
    await store_refresh_token(refresh_token, user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# Logout
@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    await delete_access_token(token)
    return {"message": "Logged out"}


# Change password
@router.post("/change-password")
async def change_password(data: PasswordChange, session: AsyncSession = Depends(get_async_session)):
    await change_user_password(data, session=session)
    return {"message": "Password updated successfully"}


# Token verification
@router.get("/me")
async def get_me(token: str = Depends(oauth2_scheme)):
    # Check: Token must be in Redis
    if not await is_access_token_valid(token):
        raise HTTPException(
            status_code=401, detail="Token is invalid or expired")

    # Additionally, we check the validity of the token (decode)
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return {"user_id": payload["sub"]}

#  Pydantic Schema for Token Refresh Request


class TokenRefreshRequest(BaseModel):
    refresh_token: str


#  Refresh access_token by refresh_token
@router.post("/refresh")
async def refresh_token(request: TokenRefreshRequest):
    payload = decode_refresh_token(request.refresh_token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Checking the validity of a refresh token in Redis
    if not await is_refresh_token_valid(request.refresh_token):
        raise HTTPException(
            status_code=401, detail="Refresh token is invalid or expired")

    # Create a new access_token
    new_access_token = create_access_token(data={"sub": payload["sub"]})
    await store_access_token(new_access_token, int(payload["sub"]))

    return {"access_token": new_access_token, "token_type": "bearer"}

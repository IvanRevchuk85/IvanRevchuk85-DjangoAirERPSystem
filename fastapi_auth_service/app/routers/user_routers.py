from fastapi import APIRouter, Body, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Literal

from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi_auth_service.app.repositories import user as user_crud
from fastapi_auth_service.app.database import get_async_session
from fastapi_auth_service.app.schemas.user import UserOut, UserUpdate, BalanceUpdate
from fastapi_auth_service.app.utils.security import get_current_user
from fastapi_auth_service.app.models.user import User

from fastapi_auth_service.app.core.dependencies import is_admin
from fastapi.encoders import jsonable_encoder


# Route prefix /users
router = APIRouter(tags=["Users"])

# GET endpoint at /users/


@router.get("/", summary="List of users with filtering and sorting")
async def get_users(
    id: Optional[int] = Query(None),
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    is_blocked: Optional[bool] = Query(None),
    sort_by: Literal["id", "balance", "last_activity_at"] = Query("id"),
    sort_order: Literal["asc", "desc"] = Query("asc"),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(is_admin)
):
    """
    Get user dictionary:
    {
        "users": {
            "1": {user_data...},
            "2": {user_data...}
        }
    }
    """

    # Create a dictionary of filters to pass to the repositories function
    filters = {}

    # Add filters only if they are passed
    if id is not None:
        filters["id"] = id
    if first_name:
        filters["first_name"] = first_name
    if last_name:
        filters["last_name"] = last_name
    if is_blocked is not None:
        filters["is_blocked"] = is_blocked

    # We receive filtered and sorted users from the database
    users = await user_crud.get_users_filtered_sorted(session, filters, sort_by, sort_order)

    return JSONResponse(content={"users": jsonable_encoder(users)})


@router.get("/balance")
async def get_balance(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    """
    Get the user's current balance.
    """
    balance = await user_crud.get_balance(current_user.id, session)
    if balance is None:
        raise HTTPException(
            status_code=404, detail="User not found or balance unavailable")
    return {"balance": balance}


#  Update user balance
@router.put("/balance")
async def update_balance(
    balance_update: BalanceUpdate,  # received through the request body
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Update the user's balance by the specified amount.
    """
    new_balance = await user_crud.update_balance(current_user.id, balance_update.amount, session)
    if new_balance is None:
        raise HTTPException(status_code=400, detail="Unable to update balance")
    return {"new_balance": new_balance}


@router.get("/profile", response_model=UserOut)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get the current user's profile.
    """
    if not current_user.first_name or not current_user.last_name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Profile incomplete")

    return UserOut(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_blocked=current_user.is_blocked,
        balance=current_user.balance,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_activity_at=current_user.last_activity_at,
        role=current_user.role,
    )

# Update user profile


@router.put("/profile", response_model=UserOut)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Update the current user's profile.
    """
    updates = user_update.dict(exclude_unset=True)

    updated_user = await user_crud.update_user(current_user.id, updates, session)
    if updated_user is None:
        raise HTTPException(status_code=400, detail="Unable to update profile")
    return updated_user

# Soft delete current user account


@router.delete("/me", summary="Delete your account (soft delete)")
async def delete_my_account(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    """
    Deletes the current user's account (soft delete).
    Sets is_deleted=True.
    """

    # Administrator cannot delete himself
    if current_user.role == "admin":
        raise HTTPException(
            status_code=403, detail="Admin cannot delete their own account.")

    success = await user_crud.soft_delete_user(current_user.id, session)

    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Account successfully deleted"}

#  Get list of deleted users


@router.get("/deleted", summary="Get list of deleted users")
async def get_deleted_users(
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(is_admin)
):
    users = await user_crud.get_deleted_users(session)
    return {"deleted_users": jsonable_encoder(users)}

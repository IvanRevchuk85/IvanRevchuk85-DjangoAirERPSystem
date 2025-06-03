from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_auth_service.app.models.user import User
from fastapi_auth_service.app.core.dependencies import is_admin

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_auth_service.app.database import get_async_session
from fastapi_auth_service.app.repositories import user as user_crud


router = APIRouter(tags=["Admin Panel"])


@router.get("/check", summary="Checking Administrator Access")
async def check_admin_access(current_user: User = Depends(is_admin)):
    return {"message": f"Welcome, admin {current_user.email}!"}


@router.post("/block/{user_id}")
async def block_user(
        user_id: int,
        current_user: User = Depends(is_admin),
        session: AsyncSession = Depends(get_async_session)
):
    success = await user_crud.set_block_status(user_id, True, session)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {user_id} has been blocked."}


@router.post("/unblock/{user_id}")
async def unblock_user(
        user_id: int,
        current_user: User = Depends(is_admin),
        session: AsyncSession = Depends(get_async_session)
):
    success = await user_crud.set_block_status(user_id, False, session)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {user_id} has been unblocked."}

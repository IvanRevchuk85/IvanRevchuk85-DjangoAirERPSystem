from fastapi import Depends, HTTPException, status
from fastapi_auth_service.app.models.user import User
from fastapi_auth_service.app.utils.security import get_current_user


# Проверка: пользователь - admin
async def is_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    return current_user

# Проверка: пользователь - обычный user
async def is_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "user":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    return current_user

"""
📦 Pydantic schemas for users

This module contains schemas:
🔷 For registration, login, password change
🔷 For input data validation
🔷 For response serialization

All schemas use Pydantic and are validated by FastAPI automatically.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, Literal


# ✅ Scheme: Input data during registration
class UserCreate(BaseModel):
    email: EmailStr  # Email is automatically validated as a string with @
    password: str = Field(..., min_length=8, max_length=24)

    @validator("password")
    def validate_password(cls, value):
        """
        🔐🤫 Password rules:
            - Minimum 1 lowercase letter
            - Minimum 1 uppercase letter
            - Minimum 1 number
            - The following symbols are prohibited: @, ", ', <, >
        """
        if (
            any(c in value for c in ['@', '"', "<", ">"]) or
            not any(c.isupper() for c in value) or
            not any(c.islower() for c in value) or
            not any(c.isdigit() for c in value)
        ):
            raise ValueError(
                "The password must contain numbers, upper and lower case letters, no symbols @ \" ' < >")
        return value

# ✅ Scheme: reply after registration (email only)


class UserRegisterResponse(BaseModel):
    email: EmailStr

# ✅ Schema: Full user data (used in /users/ and elsewhere)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    is_blocked: bool
    balance: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    last_activity_at: Optional[datetime]
    role: Literal["admin", "user"]

    class Config:
        from_attributes = True  # Pydantic V2: Replaces orm_mode

# ✅ Scheme: Public User (Limited Data)


class UserPublic(BaseModel):
    user_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    last_activity_at: Optional[datetime]
    balance: int

    class Config:
        from_attributes = True

# ✅ Scheme: Input data for password change


class PasswordChange(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=24)

    @validator("new_password")
    def validate_new_password(cls, value):
        """
        Repeat the same rules for the new password
        """
        if (
            any(c in value for c in ['@', '"', "<", ">"]) or
            not any(c.isupper() for c in value) or
            not any(c.islower() for c in value) or
            not any(c.isdigit() for c in value)
        ):
            raise ValueError(
                "The new password must contain numbers, upper and lower case letters, no symbols. @ \" ' < >")
        return value


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]


class BalanceUpdate(BaseModel):
    # = Field(..., gt=0, description="The replenishment amount must be greater 0")
    amount: int

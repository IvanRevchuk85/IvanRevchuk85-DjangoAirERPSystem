"""User model for storage in PostgreSQL via SQLAlchemy ORM."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Enum
from fastapi_auth_service.app.database import Base  # Base class for SQLAlchemy models
from datetime import datetime
import enum


# Enumerating roles
class UserRoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    """
    User model.
Represents the 'users' table in the database.
    """

    __tablename__ = "users"  # Table name in the database
    __table_args__ = {'extend_existing': True}  # Remove error from redefining table

    id = Column(Integer, primary_key=True, index=True)  # Unique user ID
    email = Column(String(255), unique=True, index=True, nullable=False)  # Email (unique)
    hashed_password = Column(String(255), nullable=False)  # Hashed password

    first_name = Column(String(100), nullable=True)  # Username (optional)
    last_name = Column(String(100), nullable=True)   # User's last name (optional)

    is_blocked = Column(Boolean, default=False, nullable=False)  # Blocking sign
    blocked_at = Column(DateTime(timezone=True), nullable=True)  # When a user has been blocked

    is_deleted = Column(Boolean, default=False, nullable=False)  # Deletion flag (soft delete)

    role = Column(
        Enum(UserRoleEnum, name="user_role_enum"),  # Using SQL Enum
        default=UserRoleEnum.user,
        nullable=False
    )  # User role: admin or user

    balance = Column(Integer, default=0, nullable=False)  # Account balance

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # Creation date
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)  # Latest update
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # Last activity

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"

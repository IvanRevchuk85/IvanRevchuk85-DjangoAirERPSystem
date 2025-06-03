"""
Unit tests for Pydantic user schemas from `schemas/user.py`.
Validation of emails and passwords is checked.
"""

import pytest
from pydantic import ValidationError
from fastapi_auth_service.app.schemas.user import (
    UserCreate,
    PasswordChange
)


def test_user_create_valid():
    """
    Check that UserCreate is successfully created with valid data.
    """
    user = UserCreate(email="valid@example.com", password="StrongPass123!")
    assert user.email == "valid@example.com"


def test_user_create_invalid_email():
    """
    Error if invalid email was sent.
    """
    with pytest.raises(ValidationError):
        UserCreate(email="invalid-email", password="StrongPass123!")


def test_user_create_weak_password():
    """
    Error when password is too weak.
    For example, without numbers, without symbols, etc.
    """
    with pytest.raises(ValidationError):
        UserCreate(email="test@example.com", password="weak")


def test_change_password_valid():
    """
    Checking the correct password change scheme.
    """
    change = PasswordChange(
        email="test@example.com",
        old_password="OldPass123!",
        new_password="NewPass456!"
    )
    assert change.new_password == "NewPass456!"


def test_change_password_weak():
    """
    Error if new password does not pass validation.
    """
    with pytest.raises(ValidationError):
        PasswordChange(
            email="test@example.com",
            old_password="OldPass123!",
            new_password="123"
        )

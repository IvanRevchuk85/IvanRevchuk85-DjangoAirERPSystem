"""
Unit tests for security.py - testing the hashing, password checking and token generation functions.
"""

import pytest
from fastapi_auth_service.app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from datetime import timedelta
import jwt


def test_get_password_hash():
    """
    Verifying that a hash is generated and is different from the original password.
    """
    password = "TestPassword123"
    hashed = hash_password(password)
    assert hashed != password
    assert isinstance(hashed, str)


def test_verify_password_success():
    """
    Successful comparison of password and its hash.
    """
    password = "MyStrongPassword"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_failure():
    """
    Error comparing invalid password with hash.
    """
    password = "MyStrongPassword"
    wrong = "WrongPassword"
    hashed = hash_password(password)
    assert verify_password(wrong, hashed) is False


def test_create_access_token():
    """
    Checking that a valid JWT token is created from the email in the payload.
    """
    data = {"sub": "test@example.com"}
    token = create_access_token(data, expires_delta=timedelta(minutes=30))
    assert isinstance(token, str)

    # Check that the token can be decoded
    decoded = jwt.decode(token, options={"verify_signature": False})
    assert decoded["sub"] == data["sub"]


def test_decode_access_token_valid():
    """
    Checks successful decryption of a valid JWT token.
    """
    # Create a token with payload
    token = create_access_token(
        {"sub": "123"}, expires_delta=timedelta(minutes=1))

    # Decoderum token
    decoded = decode_access_token(token)

    assert decoded is not None
    assert decoded.get("sub") == "123"


def test_decode_access_token_invalid():
    """
    Checks that None is returned if the token is invalid.
    """
    # Submitting an invalid token
    token = "invalid.token.value"
    decoded = decode_access_token(token)

    assert decoded is None

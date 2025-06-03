import pytest
import asyncio
import pytest_asyncio
import uuid

from httpx import AsyncClient, ASGITransport
from fastapi_auth_service.app.main import app
from fastapi_auth_service.app.database import async_session_factory
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_auth_service.app.database import get_async_session
from fastapi_auth_service.tests.db_waiter import wait_for_postgres
from fastapi_auth_service.cli import create_db

from typing import AsyncGenerator
from dotenv import load_dotenv

from sqlalchemy import select
from fastapi_auth_service.app.models.user import User
from contextlib import asynccontextmanager


load_dotenv()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """
    Creates tables in the DB before all tests. Waits until the DB is available.
    """
    await wait_for_postgres()
    create_db()  # Создаём таблицы


@pytest.fixture(scope="session")
def event_loop():
    """
    Explicitly define event loop to avoid conflicts with uvloop.
    Uses pytest-asyncio.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="function")
async def wait_for_db():
    """
    Wait for PostgreSQL to be available before running tests.
    Used when starting a test environment, especially with Docker.
    """
    await wait_for_postgres()


@pytest_asyncio.fixture(scope="function")
async def async_client():
    """
    An asynchronous client that works directly with a FastAPI application via ASGITransport.
    This is an integration test without a real server.
    """
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    client.headers.clear()
    yield client
    await client.aclose()


@pytest_asyncio.fixture(scope="function")
async def registered_user(async_client):
    """
    Registers a user and returns their data.
    Convenient for reuse in other tests.
    """
    email = f"{uuid.uuid4().hex}@example.com"
    user_data = {
        "email": email,
        "password": "StrongPass123!"
    }

    response = await async_client.post("/auth/register", json=user_data)
    assert response.status_code in (200, 201)
    return user_data


@pytest_asyncio.fixture(scope="function")
async def authorized_client(async_client):
    # Dynamic email
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "StrongPass123!"
    user_data = {"email": email, "password": password}

    # Registration
    reg_response = await async_client.post("/auth/register", json=user_data)
    print("📨 REGISTER STATUS:", reg_response.status_code)
    print("📨 REGISTER JSON:", reg_response.json())
    assert reg_response.status_code in (200, 201), "❌ Registration failed"

    # ⛏️ Login as form-data
    login_response = await async_client.post(
        "/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    print("🔐 LOGIN STATUS:", login_response.status_code)
    print("🔐 LOGIN JSON:", login_response.json())
    assert login_response.status_code == 200, "❌ Login failed"
    assert "access_token" in login_response.json()

    token = login_response.json()["access_token"]
    async_client.headers.update({"Authorization": f"Bearer {token}"})

    return async_client


@pytest_asyncio.fixture(scope="function")
async def changed_password(async_client):
    """
    Registers a user, changes their password, returns their email and new password.
    Used for password change and re-login tests.
    """
    email = "testuser@example.com"
    old_password = "StrongPass123!"
    new_password = "NewPass123!"

    # Registration
    await async_client.post("/auth/register", json={
        "email": email,
        "password": old_password
    })

    # Change password
    await async_client.post("/auth/change-password", json={
        "email": email,
        "old_password": old_password,
        "new_password": new_password
    })

    return {
        "email": email,
        "password": new_password
    }


@pytest_asyncio.fixture
@asynccontextmanager
async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture for overriding get_async_session in tests
    """
    async def _get_session() -> AsyncGenerator[AsyncSession, None]:
        async with async_session_factory() as session:
            yield session

    app.dependency_overrides[get_async_session] = _get_session
    yield _get_session
    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture for passing session directly to unit tests
    """
    async with async_session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def admin_client(async_client: AsyncClient) -> AsyncClient:
    register_data = {
        "email": "admin@test.com",
        "password": "Admin1234",
        "first_name": "Admin",
        "last_name": "Test"
    }

    # ⛏️ Delete the user directly if it already exists
    from sqlalchemy import delete, select
    from fastapi_auth_service.app.database import async_session_factory
    from fastapi_auth_service.app.models.user import User

    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == register_data["email"]))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            await session.delete(existing_user)
            await session.commit()

    # ✅ Registering an admin
    response = await async_client.post("/auth/register", json=register_data)
    assert response.status_code in (
        200, 201), f"Registration failed: {response.text}"

    # 👑 Change the role to admin
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == register_data["email"]))
        user = result.scalar_one()
        user.role = "admin"
        await session.commit()

    # 🔐 We get an access token
    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }
    login_response = await async_client.post("/auth/login", data=login_data)
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"

    access_token = login_response.json()["access_token"]
    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    return async_client

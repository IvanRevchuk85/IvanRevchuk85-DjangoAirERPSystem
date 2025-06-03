"""
Asynchronous connection initialization module to PostreSQL database
using SQLAlchemy and Pydantic Settings.
"""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase
from contextlib import asynccontextmanager
from fastapi_auth_service.app.core.settings import settings


# Forming a database connection string from environment variables
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

# Building an Asynchronous Engine for SQLAlchemy
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,  # connection line
    echo=True,  # SQL query log (turn True if debugging)
)

# Create an asynchronous session factory
async_session_factory = async_sessionmaker(
    engine,  # binding to the engine
    expire_on_commit=False  # objects will not be reset after commit
)

# Base class for ORM models


class Base(DeclarativeBase):
    pass

# Dependency для FastAPI - creates and automatically closes a session


async def get_async_session() -> AsyncSession:
    """
    Context manager for creating and closing a database session.
    Used as a dependency in endpoints and services.
    """
    async with async_session_factory() as session:
        yield session

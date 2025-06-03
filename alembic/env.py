"""Async Alembic environment config for autogenerate migrations."""

import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import pool
from alembic import context

import os
import sys

#  Add the path to the repository so that the import works
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

#  Import settings and models
from fastapi_auth_service.app.database import Base
from fastapi_auth_service.app import models  # needed for Alembic
from fastapi_auth_service.app.core.settings import settings  # variable source

#  Alembic config
config = context.config

#  Setting up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

#  Model metadata
target_metadata = Base.metadata

#  Connection URL from Pydantic Settings
DATABASE_URL = settings.db_url

def get_async_engine() -> AsyncEngine:
    """
    Creates an asynchronous SQLAlchemy engine for migrations.
    """
    return create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool
    )

def run_migrations_offline() -> None:
    """
    OFFLINE mode: generates SQL without connecting to the database.
    """
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """
    Performs migrations ONLINE over a live connection.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """
    ONLINE mode: Runs Alembic over an asynchronous connection.
    """
    connectable = get_async_engine()

    async with connectable.begin() as connection:
        await connection.run_sync(do_run_migrations)

#  Launch depending on the mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

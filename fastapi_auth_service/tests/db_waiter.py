# db_waiter.py

import asyncio
import asyncpg
import os

from dotenv import load_dotenv

load_dotenv()


async def wait_for_postgres(retries: int = 10, delay: float = 1.0):
    """
    Attempts to connect to the DB, pauses between attempts.
    Used to wait for PostgreSQL when running tests.
    """
    for i in range(retries):
        try:
            conn = await asyncpg.connect(
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                database=os.getenv("POSTGRES_DB"),
                host=os.getenv("POSTGRES_HOST"),
                port=int(os.getenv("POSTGRES_PORT", 5432))
            )
            await conn.close()
            print("✅ PostgreSQL is available")
            return
        except Exception as e:
            print(f"⏳ Waiting for PostgreSQL... ({i + 1}/{retries}) — {e}")
            await asyncio.sleep(delay)
    raise RuntimeError("🚫 Could not connect to PostgreSQL")

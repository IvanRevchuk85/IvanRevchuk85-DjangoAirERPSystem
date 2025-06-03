from fastapi import FastAPI
from fastapi_auth_service.app.routers.auth_routers import router as auth_router
from fastapi_auth_service.app.routers.user_routers import router as user_router
from fastapi_auth_service.app.routers.admin_routes import router as admin_router

from fastapi_auth_service.app.core.redis import redis_cache
import logging
import uvloop
import asyncio

from fastapi_auth_service.app.logging_config import configure_logging

# Activate logging
configure_logging()

# Setting up logging
logging.basicConfig(level=logging.DEBUG)

# Set uvloop as the main event loop (speeds up asynchrony)
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Create a FastAPI application
app = FastAPI(
    title="FastAPI Auth Service",
    description="User authentication API with registration, login, logout, and password change",
    version="1.0.0",
)

# Connecting authorization routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])

# ⚙️ Initializing Redis on application startup


@app.on_event("startup")
async def startup():
    try:
        await redis_cache.ping()  # Checking the connection
        logging.info("✅ Redis connected successfully")
    except Exception as e:
        logging.error(f"❌ Error connecting to Redis: {e}")

# Root endpoint (for checking API operation)


@app.get("/")
def read_root():
    return {"message": "FastAPI Auth Service is running"}


logger = logging.getLogger("app.test")


@app.get("/crash")
def crash():
    logger.error("🔥 CRITICAL: Something went wrong!")
    return {"error": "Simulated error logged"}

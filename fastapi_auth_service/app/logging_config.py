import logging
import os

from fastapi.logger import logger as fastapi_logger


APP_ENV = os.getenv("APP_ENV", "local")  # Get the current environment


def configure_logging():
    # Basic logging level by default
    logging_level = logging.INFO

    # Default logger settings
    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # SQLAlchemy logger
    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")

    # Setting by environment
    if APP_ENV == "local":
        # In local turn everything on
        sqlalchemy_logger.setLevel(logging.INFO)

    elif APP_ENV == "dev":
        # In dev, disable SQL, leave only the necessary loggers
        sqlalchemy_logger.setLevel(logging.WARNING)
        fastapi_logger.setLevel(logging.INFO)

    elif APP_ENV == "prod":
        # In prod only errors
        sqlalchemy_logger.setLevel(logging.ERROR)
        fastapi_logger.setLevel(logging.ERROR)
        logging.getLogger().setLevel(logging.ERROR)  # Global level

    # Clearly show what level of logging is enabled
    print(
        f"[LOGGING CONFIG] Environment: {APP_ENV.upper()}, Logging level set")

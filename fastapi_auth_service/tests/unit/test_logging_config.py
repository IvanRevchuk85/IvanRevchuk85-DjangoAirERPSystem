import logging
import os
import importlib

import pytest

from fastapi_auth_service.app import logging_config


@pytest.mark.parametrize("env, expected_sqlalchemy_level, expected_root_level", [
    ("local", logging.INFO, logging.INFO),
    ("dev", logging.WARNING, logging.INFO),
    ("prod", logging.ERROR, logging.ERROR),
])
def test_logging_levels(monkeypatch, env, expected_sqlalchemy_level, expected_root_level):
    # Substitute the environment variable
    monkeypatch.setenv("APP_ENV", env)

    # Reload the module taking into account the new APP_ENV
    importlib.reload(logging_config)

    #  Resetting the root logger
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Start configuring logs
    logging_config.configure_logging()

    # Checking the levels
    sqlalchemy_level = logging.getLogger("sqlalchemy.engine").level
    root_level = logging.getLogger().level

    assert sqlalchemy_level == expected_sqlalchemy_level
    assert root_level == expected_root_level

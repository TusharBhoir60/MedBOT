"""
Unit tests for core/config.py — Pydantic Settings loading.

These tests run without any database connection.
They verify that settings are loaded correctly with sensible defaults
and that environment-based discriminators work as intended.
"""
import os
import pytest
from unittest.mock import patch


def test_settings_default_values() -> None:
    """Settings should load with sensible development defaults."""
    from core.config import settings

    assert settings.APP_TITLE == "AarogyaAgent API"
    assert settings.APP_VERSION == "0.1.0"
    assert settings.APP_ENV in ("development", "staging", "production")
    assert settings.log.level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    assert settings.security.max_request_size > 0


def test_settings_database_url_has_asyncpg() -> None:
    """The async database URL must use an async-compatible driver.
    
    In testing, the default is SQLite (aiosqlite). In production, asyncpg is required.
    """
    from core.config import settings

    # Either aiosqlite (test) or asyncpg (production) is acceptable
    assert "aiosqlite" in settings.db.url or "asyncpg" in settings.db.url, (
        f"Database URL must use an async driver, got: {settings.db.url}"
    )


def test_settings_sync_url_has_psycopg2() -> None:
    """The sync (Alembic) database URL must use a sync driver.
    
    In testing, the default is SQLite. In production, psycopg2 is required.
    """
    from core.config import settings

    # Either sqlite (test) or psycopg2 (production) is acceptable
    assert "sqlite" in settings.db.sync_url or "psycopg2" in settings.db.sync_url or "psycopg" in settings.db.sync_url, (
        f"Sync database URL must use a sync driver, got: {settings.db.sync_url}"
    )


def test_settings_pool_size_positive() -> None:
    """Pool size must be a positive integer."""
    from core.config import settings

    assert settings.db.pool_size > 0
    assert settings.db.max_overflow >= 0


def test_settings_max_request_size_default() -> None:
    """Default max request size should be positive and within a reasonable range."""
    from core.config import settings

    # Config default is 5MB (5242880); env may override to 10MB (10485760)
    assert 1 * 1024 * 1024 <= settings.security.max_request_size <= 20 * 1024 * 1024, (
        f"max_request_size should be between 1MB and 20MB, got: {settings.security.max_request_size}"
    )


def test_api_v1_prefix_constant() -> None:
    """API v1 prefix constant must follow the correct format."""
    from core.constants import API_V1_STR

    assert API_V1_STR.startswith("/api/")
    assert "v1" in API_V1_STR
    assert not API_V1_STR.endswith("/")

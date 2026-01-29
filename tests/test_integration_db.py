"""Integration tests with PostgreSQL and migrations."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import get_settings
from src.database import get_db
from src.main import app

BASE_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def postgres_url():
    """Get PostgreSQL URL from environment or skip."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        pytest.skip("DATABASE_URL is not set for PostgreSQL integration tests")
    if not db_url.startswith("postgres"):
        pytest.skip("DATABASE_URL is not a PostgreSQL URL")
    return db_url


@pytest.fixture
def db_session_factory(postgres_url):
    """Run migrations and return a session factory bound to PostgreSQL."""

    env_backup: Dict[str, Optional[str]] = {
        "DATABASE_URL": os.environ.get("DATABASE_URL"),
        "SECRET_KEY": os.environ.get("SECRET_KEY"),
        "GOOGLE_CLIENT_ID": os.environ.get("GOOGLE_CLIENT_ID"),
        "GOOGLE_CLIENT_SECRET": os.environ.get("GOOGLE_CLIENT_SECRET"),
        "GOOGLE_REDIRECT_URI": os.environ.get("GOOGLE_REDIRECT_URI"),
    }

    os.environ["DATABASE_URL"] = postgres_url
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
    os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")
    os.environ.setdefault(
        "GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"
    )

    get_settings.cache_clear()

    alembic_cfg = Config(str(BASE_DIR / "alembic.ini"))
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(postgres_url)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    try:
        yield TestingSessionLocal
    finally:
        engine.dispose()
        for key, value in env_backup.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        get_settings.cache_clear()


@pytest.fixture
def client(db_session_factory):
    """Test client wired to the temporary database."""
    def override_get_db():
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_register_login_and_profile(client):
    """Full DB-backed auth flow: register -> login -> /me."""
    register = client.post(
        "/auth/register",
        json={"email": "testuser@example.com", "password": "test1234", "full_name": "Test User"},
    )
    if register.status_code != 200:
        print(f"ERROR: {register.json()}")
    assert register.status_code == 200
    assert "access_token" in register.json()

    login = client.post(
        "/auth/login",
        json={"email": "testuser@example.com", "password": "test1234"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    profile = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert profile.status_code == 200
    assert profile.json()["email"] == "testuser@example.com"




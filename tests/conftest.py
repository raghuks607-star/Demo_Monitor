"""Shared pytest fixtures."""

import pytest
from werkzeug.security import generate_password_hash

from app import create_app


@pytest.fixture
def app(tmp_path):
    """Flask app configured for tests (temp DB, no real secrets)."""
    test_hash = generate_password_hash("test-password")
    db_path = tmp_path / "test_servers.db"
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key-for-fernet-derive",
            "ADMIN_USERNAME": "admin",
            "ADMIN_PASSWORD_HASH": test_hash,
            "DATABASE_PATH": str(db_path),
            "WTF_CSRF_ENABLED": False,
            "SSH_AUTO_ADD_HOST_KEYS": False,
        }
    )
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """Logged-in test client."""
    client.post(
        "/login",
        data={"username": "admin", "password": "test-password"},
    )
    return client

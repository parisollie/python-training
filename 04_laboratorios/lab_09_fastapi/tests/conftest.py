"""Fixtures para tests de la API.

Usa una base de datos SQLite en memoria y sobreescribe la dependencia
get_db para que los tests no toquen la DB real.
"""

import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import Base, get_db  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """TestClient con DB SQLite en memoria aislada."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def auth_client(client: TestClient) -> TestClient:
    """TestClient con un usuario ya creado y autenticado (header listo)."""
    client.post(
        "/users/",
        json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User",
        },
    )

    response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "password123"},
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

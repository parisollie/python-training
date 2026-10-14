"""Fixtures compartidas para los tests de SQLAlchemy.

Usa SQLite en memoria con StaticPool para que todas las conexiones
compartan la misma base de datos durante el test.
"""

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).parent.parent))

from repository import init_db  # noqa: E402


@pytest.fixture
def engine() -> Iterator[Engine]:
    """Engine SQLite en memoria con tablas creadas.

    StaticPool mantiene la misma conexion en memoria durante todo el test,
    evitando que cada conexion cree una base de datos nueva.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    init_db(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    """Session abierta para tests que necesitan acceso directo."""
    with Session(engine) as session:
        yield session

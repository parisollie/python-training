"""Configuracion de la base de datos con SQLAlchemy 2.0.

Usa SQLite para simplificar (sin servidor de BD).
En produccion se reemplazaria por PostgreSQL, MySQL, etc.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# SQLite en archivo (para la app real)
DATABASE_URL = "sqlite:///./app.db"

# echo=False en produccion, True para ver SQL en consola
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos."""


def get_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI que provee una sesion por request.

    Yields:
        Session: sesion SQLAlchemy que se cierra al finalizar el request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

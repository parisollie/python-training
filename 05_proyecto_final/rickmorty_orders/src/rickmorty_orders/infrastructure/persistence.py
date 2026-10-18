"""Configuracion de la base de datos con SQLAlchemy 2.0.

- Engine (SQLite en desarrollo, PostgreSQL en produccion)
- SessionLocal (factory de sesiones)
- Base (DeclarativeBase para los modelos)
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from rickmorty_orders.infrastructure.config import get_settings


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos SQLAlchemy."""


def create_db_engine(database_url: str | None = None, echo: bool = False) -> Engine:
    """Crea un engine de SQLAlchemy.

    Args:
        database_url: URL de conexion. Si no se provee, usa la configuracion.
        echo: si True, imprime SQL generado.

    Returns:
        Engine configurado.
    """
    settings = get_settings()
    url = database_url or settings.database_url
    show_sql = echo or settings.database_echo

    # SQLite requiere check_same_thread=False para FastAPI (multi-thread)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}

    return create_engine(url, connect_args=connect_args, echo=show_sql)


# ============================================
# Instancia global (lazy, para produccion)
# ============================================

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    """Devuelve el engine global (lo crea si no existe)."""
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """Devuelve el SessionLocal global (lo crea si no existe)."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _session_factory


def get_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI que provee una sesion por request.

    Yields:
        Session de SQLAlchemy (se cierra al finalizar el request).
    """
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def init_db(engine: Engine | None = None) -> None:
    """Inicializa la base de datos (solo importa modelos).

    Args:
        engine: engine opcional (no se usa, se mantiene por compatibilidad).

    Nota: las tablas se crean via Alembic (alembic upgrade head).
    Esta funcion es un no-op que asegura que los modelos esten importados
    (util para que Base.metadata tenga todas las tablas registradas).
    """
    # Importar modelos para que Base los conozca
    from rickmorty_orders.infrastructure import orm_models  # noqa: F401

    _ = engine  # parametro mantenido por compatibilidad

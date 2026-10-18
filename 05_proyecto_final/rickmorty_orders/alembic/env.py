"""Alembic env.py configurado para rickmorty_orders.

- Importa Base y orm_models para autogenerate
- Lee database_url desde Settings (pydantic-settings)
"""

from logging.config import fileConfig

from alembic import context

# Importar TODOS los modelos para que Base.metadata los conozca
from rickmorty_orders.infrastructure import orm_models  # noqa: F401

# ==== Importar metadata y settings del proyecto ====
from rickmorty_orders.infrastructure.config import get_settings
from rickmorty_orders.infrastructure.persistence import Base
from sqlalchemy import create_engine, pool

# Config de Alembic
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata que Alembic comparara contra la DB real
target_metadata = Base.metadata

# Leer la URL real desde Settings (no desde alembic.ini)
settings = get_settings()
DATABASE_URL = settings.database_url


def run_migrations_offline() -> None:
    """Modo offline: genera SQL sin conectar a la DB."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Modo online: conecta a la DB y aplica migraciones."""
    connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

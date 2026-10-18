"""Fixtures compartidas para los tests del proyecto final."""

from collections.abc import Iterator

import pytest
from rickmorty_orders.domain.character import Character, CharacterStatus
from rickmorty_orders.domain.order import Order, OrderItem
from rickmorty_orders.domain.value_objects import (
    CharacterId,
    Email,
    Money,
)
from rickmorty_orders.infrastructure.in_memory import (
    FakeEventBus,
    FakeNotifier,
    InMemoryCharacterRepository,
    InMemoryOrderRepository,
)
from rickmorty_orders.infrastructure.orm_models import (  # noqa: F401
    OrderItemModel,
    OrderModel,
)
from rickmorty_orders.infrastructure.persistence import Base
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# ============================================
# Base de datos (SQLite en memoria)
# ============================================


@pytest.fixture
def engine() -> Iterator[Engine]:
    """Engine SQLite en memoria con todas las tablas creadas."""
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=eng)
    yield eng
    eng.dispose()


@pytest.fixture
def session_factory(engine: Engine) -> sessionmaker[Session]:
    """Session factory para el SQLOrderRepository."""
    return sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    """Session abierta (para tests de integracion)."""
    with Session(engine) as s:
        yield s


# ============================================
# Adaptadores en memoria
# ============================================


@pytest.fixture
def memory_repo() -> InMemoryOrderRepository:
    return InMemoryOrderRepository()


@pytest.fixture
def memory_chars() -> InMemoryCharacterRepository:
    """Repositorio de personajes con 3 personajes precargados."""
    repo = InMemoryCharacterRepository()
    repo.add(
        Character(
            id=CharacterId(1),
            name="Rick Sanchez",
            species="Human",
            status=CharacterStatus.ALIVE,
        )
    )
    repo.add(
        Character(
            id=CharacterId(2),
            name="Morty Smith",
            species="Human",
            status=CharacterStatus.ALIVE,
        )
    )
    repo.add(
        Character(
            id=CharacterId(3),
            name="Birdperson",
            species="Alien",
            status=CharacterStatus.DEAD,
        )
    )
    return repo


@pytest.fixture
def fake_notifier() -> FakeNotifier:
    return FakeNotifier()


@pytest.fixture
def fake_event_bus() -> FakeEventBus:
    return FakeEventBus()


# ============================================
# Entidades de dominio (para tests unit)
# ============================================


@pytest.fixture
def sample_items() -> list[OrderItem]:
    """Dos OrderItem válidos."""
    return [
        OrderItem(
            character_id=CharacterId(1),
            character_name="Rick Sanchez",
            quantity=1,
            unit_price=Money(50.0),
        ),
        OrderItem(
            character_id=CharacterId(2),
            character_name="Morty Smith",
            quantity=2,
            unit_price=Money(50.0),
        ),
    ]


@pytest.fixture
def sample_order(sample_items: list[OrderItem]) -> Order:
    """Order en estado PENDING."""
    return Order.create(
        customer_email=Email("paul@example.com"),
        items=sample_items,
    )

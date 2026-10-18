"""Tests de contrato para OrderRepository.

Garantizan que TODOS los adaptadores de OrderRepository se comporten
igual (Liskov Substitution Principle).

Adaptadores probados:
- InMemoryOrderRepository
- SQLOrderRepository (con SQLite en memoria)
"""

from collections.abc import Callable

import pytest
from rickmorty_orders.domain.order import Order, OrderItem
from rickmorty_orders.domain.ports import OrderRepository
from rickmorty_orders.domain.value_objects import (
    CharacterId,
    Email,
    Money,
)
from rickmorty_orders.infrastructure.in_memory import InMemoryOrderRepository
from rickmorty_orders.infrastructure.sql_repositories import SQLOrderRepository
from sqlalchemy.orm import Session, sessionmaker

# ============================================
# Fixtures
# ============================================


@pytest.fixture
def memory_repo_contract() -> OrderRepository:
    """Adaptador en memoria."""
    return InMemoryOrderRepository()


@pytest.fixture
def sql_repo_contract(
    session_factory: sessionmaker[Session],
) -> OrderRepository:
    """Adaptador SQL con SQLite en memoria."""
    return SQLOrderRepository(session_factory)


@pytest.fixture
def order_factory() -> Callable[..., Order]:
    """Factory de ordenes para tests."""

    def make(email: str = "paul@example.com") -> Order:
        return Order.create(
            customer_email=Email(email),
            items=[
                OrderItem(
                    character_id=CharacterId(1),
                    character_name="Rick Sanchez",
                    quantity=1,
                    unit_price=Money(50.0),
                ),
            ],
        )

    return make


# ============================================
# Contrato: parametrizado sobre implementaciones
# ============================================


@pytest.fixture(params=["memory", "sql"])
def repo(request: pytest.FixtureRequest) -> OrderRepository:
    """Devuelve cada implementacion de OrderRepository."""
    if request.param == "memory":
        return request.getfixturevalue("memory_repo_contract")  # type: ignore[no-any-return]
    return request.getfixturevalue("sql_repo_contract")  # type: ignore[no-any-return]


# ============================================
# Tests de contrato (LSP)
# ============================================


def test_save_y_find_by_id(
    repo: OrderRepository,
    order_factory: Callable[..., Order],
) -> None:
    """save guarda, find_by_id recupera."""
    order = order_factory()
    repo.save(order)

    found = repo.find_by_id(order.id)
    assert found is not None
    assert found.id == order.id
    assert found.customer_email == order.customer_email
    assert len(found.items) == len(order.items)


def test_find_by_id_inexistente(repo: OrderRepository) -> None:
    """find_by_id devuelve None si no existe."""
    from rickmorty_orders.domain.value_objects import OrderId

    assert repo.find_by_id(OrderId.generate()) is None


def test_list_all_vacio(repo: OrderRepository) -> None:
    """list_all en repo vacio devuelve []."""
    assert repo.list_all() == []


def test_list_all_con_datos(
    repo: OrderRepository,
    order_factory: Callable[..., Order],
) -> None:
    """list_all devuelve todas las ordenes."""
    o1 = order_factory("a@b.com")
    o2 = order_factory("c@d.com")
    repo.save(o1)
    repo.save(o2)
    orders = repo.list_all()
    assert len(orders) == 2


def test_find_by_customer(
    repo: OrderRepository,
    order_factory: Callable[..., Order],
) -> None:
    """find_by_customer filtra por email."""
    o1 = order_factory("paul@example.com")
    o2 = order_factory("paul@example.com")
    o3 = order_factory("ana@example.com")
    repo.save(o1)
    repo.save(o2)
    repo.save(o3)

    paul_orders = repo.find_by_customer(Email("paul@example.com"))
    ana_orders = repo.find_by_customer(Email("ana@example.com"))

    assert len(paul_orders) == 2
    assert len(ana_orders) == 1


def test_find_by_customer_sin_resultados(repo: OrderRepository) -> None:
    """find_by_customer devuelve [] si no hay ordenes."""
    assert repo.find_by_customer(Email("nadie@example.com")) == []


def test_save_actualiza_orden_existente(
    repo: OrderRepository,
    order_factory: Callable[..., Order],
) -> None:
    """save sobre una orden existente la actualiza (no duplica)."""
    order = order_factory()
    repo.save(order)

    # Modificar estado
    order.confirm()
    repo.save(order)

    all_orders = repo.list_all()
    assert len(all_orders) == 1

    found = repo.find_by_id(order.id)
    assert found is not None
    assert found.status.value == "confirmed"


def test_save_preserva_items(
    repo: OrderRepository,
) -> None:
    """save guarda los items correctamente."""
    order = Order.create(
        customer_email=Email("a@b.com"),
        items=[
            OrderItem(
                character_id=CharacterId(1),
                character_name="Rick",
                quantity=2,
                unit_price=Money(50.0),
            ),
            OrderItem(
                character_id=CharacterId(2),
                character_name="Morty",
                quantity=3,
                unit_price=Money(25.0),
            ),
        ],
    )
    repo.save(order)

    found = repo.find_by_id(order.id)
    assert found is not None
    assert len(found.items) == 2
    # Verificar totales
    assert found.subtotal.amount == 2 * 50.0 + 3 * 25.0  # 175.0
    assert found.total.amount == pytest.approx(175.0 * 1.16, abs=0.01)

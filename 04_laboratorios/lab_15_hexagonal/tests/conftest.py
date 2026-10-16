"""Fixtures compartidas para tests."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from application.create_order import CreateOrderService  # noqa: E402
from application.dtos import CreateOrderInput, OrderItemInput  # noqa: E402
from domain.order import Order, OrderItem  # noqa: E402
from domain.value_objects import Email, Money  # noqa: E402
from infrastructure.memory import (  # noqa: E402
    FakeNotifier,
    InMemoryOrderRepository,
)


@pytest.fixture
def repo() -> InMemoryOrderRepository:
    return InMemoryOrderRepository()


@pytest.fixture
def notifier() -> FakeNotifier:
    return FakeNotifier()


@pytest.fixture
def service(
    repo: InMemoryOrderRepository,
    notifier: FakeNotifier,
) -> CreateOrderService:
    return CreateOrderService(repository=repo, notifier=notifier)


@pytest.fixture
def valid_input() -> CreateOrderInput:
    """DTO de entrada valido."""
    return CreateOrderInput(
        customer_email="paul@example.com",
        items=[
            OrderItemInput(product="Teclado", quantity=2, unit_price=25.0),
            OrderItemInput(product="Mouse", quantity=1, unit_price=15.5),
        ],
    )


@pytest.fixture
def order() -> Order:
    """Entidad Order para tests de dominio."""
    return Order.create(
        customer_email=Email("paul@example.com"),
        items=[
            OrderItem(product="X", quantity=2, unit_price=Money(10.0)),
        ],
    )

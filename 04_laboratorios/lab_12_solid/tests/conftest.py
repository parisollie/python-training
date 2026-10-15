"""Fixtures compartidas para los tests."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.notifiers import ConsoleNotifier, FakeNotifier  # noqa: E402
from infrastructure.payments import FakePayment, StripePayment  # noqa: E402
from infrastructure.repositories import (  # noqa: E402
    InMemoryOrderRepository,
    SQLOrderRepository,
)
from services.order_service import OrderService  # noqa: E402


@pytest.fixture(autouse=True)
def _clear_sql_db() -> None:
    """Limpia la 'DB' compartida del SQLOrderRepository antes de cada test."""
    SQLOrderRepository.clear()


@pytest.fixture
def memory_repo() -> InMemoryOrderRepository:
    return InMemoryOrderRepository()


@pytest.fixture
def sql_repo() -> SQLOrderRepository:
    return SQLOrderRepository()


@pytest.fixture
def console_notifier() -> ConsoleNotifier:
    return ConsoleNotifier()


@pytest.fixture
def fake_notifier() -> FakeNotifier:
    return FakeNotifier()


@pytest.fixture
def fake_payment() -> FakePayment:
    return FakePayment()


@pytest.fixture
def stripe_payment() -> StripePayment:
    return StripePayment()


@pytest.fixture
def memory_service(
    memory_repo: InMemoryOrderRepository,
    fake_notifier: FakeNotifier,
    fake_payment: FakePayment,
) -> OrderService:
    """Servicio con implementaciones en memoria (rapido, para la mayoria de tests)."""
    return OrderService(repository=memory_repo, notifier=fake_notifier, payment=fake_payment)

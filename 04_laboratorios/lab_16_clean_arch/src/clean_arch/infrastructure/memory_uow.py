"""Implementaciones en memoria para el lab 16.

- InMemoryOrderRepository
- InMemoryUnitOfWork (coordina el repo + eventos)
- FakeEventBus (guarda eventos publicados)
- FakeNotifier (guarda notificaciones)
"""

from types import TracebackType
from typing import Self

from clean_arch.domain.events import DomainEvent
from clean_arch.domain.order import Order
from clean_arch.domain.ports import OrderRepository
from clean_arch.domain.value_objects import Email, OrderId


class InMemoryOrderRepository:
    """Repositorio en memoria."""

    def __init__(self) -> None:
        self._store: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self._store[str(order.id)] = order

    def find_by_id(self, order_id: OrderId) -> Order | None:
        return self._store.get(str(order_id))

    def find_by_customer(self, email: Email) -> list[Order]:
        return [o for o in self._store.values() if o.customer_email == email]

    def list_all(self) -> list[Order]:
        return list(self._store.values())


class FakeEventBus:
    """Event bus que guarda eventos para tests."""

    def __init__(self) -> None:
        self.published: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self.published.append(event)


class InMemoryUnitOfWork:
    """Unit of Work en memoria.

    Coordina el repositorio en memoria + los eventos pendientes.
    Al hacer commit, publica los eventos via el EventBus.
    """

    def __init__(self, event_bus: FakeEventBus | None = None) -> None:
        self.orders: OrderRepository = InMemoryOrderRepository()
        self.events: list[DomainEvent] = []
        self._event_bus = event_bus or FakeEventBus()
        self._committed = False

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        # En memoria no hay DB real, solo publicamos eventos
        for event in self.events:
            self._event_bus.publish(event)
        self.events.clear()
        self._committed = True

    def rollback(self) -> None:
        self.events.clear()
        self._committed = False

    def collect_event(self, event: DomainEvent) -> None:
        self.events.append(event)

    @property
    def event_bus(self) -> FakeEventBus:
        return self._event_bus

    @property
    def committed(self) -> bool:
        return self._committed


class FakeNotifier:
    """Notificador que guarda notificaciones para tests."""

    def __init__(self) -> None:
        self.created: list[str] = []
        self.confirmed: list[str] = []

    def notify_order_created(self, order: Order) -> None:
        self.created.append(str(order.id))

    def notify_order_confirmed(self, order: Order) -> None:
        self.confirmed.append(str(order.id))

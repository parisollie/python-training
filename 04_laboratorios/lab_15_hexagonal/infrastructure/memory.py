"""Adaptador en memoria del puerto OrderRepository.

Util para tests rapidos y desarrollo.
"""

from domain.order import Order
from domain.value_objects import OrderId


class InMemoryOrderRepository:
    """Implementacion en memoria del puerto OrderRepository."""

    def __init__(self) -> None:
        self._store: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        """Guarda la orden en memoria."""
        self._store[str(order.id)] = order

    def find_by_id(self, order_id: OrderId) -> Order | None:
        """Busca por id."""
        return self._store.get(str(order_id))

    def list_all(self) -> list[Order]:
        """Lista todas."""
        return list(self._store.values())


class FakeNotifier:
    """Implementacion simple del puerto Notifier para tests/dev."""

    def __init__(self) -> None:
        self.notified: list[str] = []

    def notify_order_created(self, order: Order) -> None:
        """Registra el id de la orden notificada."""
        self.notified.append(str(order.id))

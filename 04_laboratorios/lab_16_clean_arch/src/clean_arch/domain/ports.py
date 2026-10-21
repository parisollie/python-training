"""Puertos del dominio del lab 16."""

from typing import Protocol

from clean_arch.domain.events import DomainEvent
from clean_arch.domain.order import Order
from clean_arch.domain.value_objects import Email, OrderId


class OrderRepository(Protocol):
    """Puerto para persistir ordenes."""

    def save(self, order: Order) -> None: ...

    def find_by_id(self, order_id: OrderId) -> Order | None: ...

    def find_by_customer(self, email: Email) -> list[Order]: ...

    def list_all(self) -> list[Order]: ...


class Notifier(Protocol):
    """Puerto para notificaciones."""

    def notify_order_created(self, order: Order) -> None: ...

    def notify_order_confirmed(self, order: Order) -> None: ...


class EventBus(Protocol):
    """Puerto para publicar eventos de dominio."""

    def publish(self, event: DomainEvent) -> None: ...

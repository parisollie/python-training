"""Eventos de dominio.

Un evento de dominio representa algo que YA paso en el dominio.
- Son inmutables
- Se nombran en pasado (OrderCreated, no CreateOrder)
- Se publican despues de que la transaccion es exitosa
- Permiten desacoplar efectos secundarios (email, auditoria, cache)

En este proyecto:
- OrderCreated: una orden fue creada
- OrderConfirmed: una orden fue confirmada
- OrderCancelled: una orden fue cancelada
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from rickmorty_orders.domain.value_objects import OrderId


@dataclass(frozen=True)
class DomainEvent:
    """Base de todos los eventos de dominio."""

    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class OrderCreated(DomainEvent):
    """Evento: una orden fue creada.

    Attributes:
        order_id: id de la orden creada.
        customer_email: email del cliente.
        total: monto total de la orden.
    """

    order_id: OrderId = field(default_factory=OrderId.generate)
    customer_email: str = ""
    total: float = 0.0


@dataclass(frozen=True)
class OrderConfirmed(DomainEvent):
    """Evento: una orden fue confirmada."""

    order_id: OrderId = field(default_factory=OrderId.generate)


@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    """Evento: una orden fue cancelada."""

    order_id: OrderId = field(default_factory=OrderId.generate)
    reason: str = ""

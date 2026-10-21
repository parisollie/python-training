"""Eventos de dominio del lab 16."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from clean_arch.domain.value_objects import OrderId


@dataclass(frozen=True)
class DomainEvent:
    """Base de todos los eventos de dominio."""

    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class OrderCreated(DomainEvent):
    """Evento: se creo una orden."""

    order_id: OrderId = field(default_factory=OrderId.generate)
    customer_email: str = ""
    total: float = 0.0


@dataclass(frozen=True)
class OrderConfirmed(DomainEvent):
    """Evento: se confirmo una orden."""

    order_id: OrderId = field(default_factory=OrderId.generate)

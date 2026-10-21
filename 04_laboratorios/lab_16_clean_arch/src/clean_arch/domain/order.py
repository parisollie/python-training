"""Entidad Order del lab 16 (simplificada)."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from clean_arch.domain.errors import (
    InvalidOrderError,
    InvalidStatusTransitionError,
)
from clean_arch.domain.value_objects import Email, Money, OrderId

TAX_RATE = 0.16


class OrderStatus(StrEnum):
    """Estados de una orden."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class OrderItem:
    """Item de una orden."""

    product: str
    quantity: int
    unit_price: Money

    def __post_init__(self) -> None:
        if not self.product.strip():
            raise InvalidOrderError("El producto no puede estar vacio")
        if self.quantity < 1:
            raise InvalidOrderError(f"quantity debe ser >= 1 (recibido: {self.quantity})")

    @property
    def subtotal(self) -> Money:
        return self.unit_price * self.quantity


@dataclass
class Order:
    """Entidad Order con transiciones de estado."""

    id: OrderId
    customer_email: Email
    items: list[OrderItem]
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.items:
            raise InvalidOrderError("La orden debe tener al menos un item")

    @classmethod
    def create(
        cls,
        customer_email: Email,
        items: list[OrderItem],
    ) -> "Order":
        return cls(
            id=OrderId.generate(),
            customer_email=customer_email,
            items=items,
        )

    @property
    def subtotal(self) -> Money:
        total = Money(0.0)
        for item in self.items:
            total = total + item.subtotal
        return total

    @property
    def tax(self) -> Money:
        return self.subtotal * TAX_RATE

    @property
    def total(self) -> Money:
        return self.subtotal + self.tax

    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items)

    def confirm(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise InvalidStatusTransitionError(
                f"Solo se puede confirmar desde PENDING (actual: {self.status.value})"
            )
        self.status = OrderStatus.CONFIRMED

    def cancel(self) -> None:
        if self.status == OrderStatus.CANCELLED:
            raise InvalidStatusTransitionError("La orden ya esta cancelada")
        self.status = OrderStatus.CANCELLED

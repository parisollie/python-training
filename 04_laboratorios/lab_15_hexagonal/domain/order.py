"""Entidad Order con logica de negocio pura.

Una entidad:
- Tiene identidad (OrderId)
- Tiene invariantes (siempre al menos 1 item)
- Expone comportamiento que refleja reglas del negocio
- NO conoce infraestructura

Reglas de negocio:
- Una orden tiene un OrderId unico
- Tiene un email de cliente
- Tiene al menos 1 item
- Subtotal = suma de Money de los items
- Tax = 16% del subtotal
- Total = subtotal + tax
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from domain.value_objects import Email, Money, OrderId

TAX_RATE = 0.16


class OrderStatus(StrEnum):
    """Estados posibles de una orden."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class OrderItem:
    """Item de una orden.

    Value Object inmutable.
    """

    product: str
    quantity: int
    unit_price: Money

    def __post_init__(self) -> None:
        if not self.product.strip():
            raise ValueError("El producto no puede estar vacio")
        if self.quantity < 1:
            raise ValueError(f"quantity debe ser >= 1 (recibido: {self.quantity})")

    @property
    def subtotal(self) -> Money:
        """Subtotal del item."""
        return self.unit_price * self.quantity


@dataclass
class Order:
    """Entidad Order con comportamiento de negocio."""

    id: OrderId
    customer_email: Email
    items: list[OrderItem]
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("La orden debe tener al menos un item")

    @classmethod
    def create(
        cls,
        customer_email: Email,
        items: list[OrderItem],
    ) -> "Order":
        """Factory method que asigna un nuevo OrderId."""
        return cls(
            id=OrderId.generate(),
            customer_email=customer_email,
            items=items,
        )

    @property
    def subtotal(self) -> Money:
        """Suma de subtotales de los items."""
        total = Money(0.0)
        for item in self.items:
            total = total + item.subtotal
        return total

    @property
    def tax(self) -> Money:
        """IVA (16%) del subtotal."""
        return self.subtotal * TAX_RATE

    @property
    def total(self) -> Money:
        """Total a pagar (subtotal + tax)."""
        return self.subtotal + self.tax

    @property
    def total_items(self) -> int:
        """Cantidad total de unidades."""
        return sum(item.quantity for item in self.items)

    def confirm(self) -> None:
        """Confirma la orden.

        Raises:
            ValueError: Si la orden no esta en PENDING.
        """
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Solo se pueden confirmar ordenes PENDING (actual: {self.status})")
        self.status = OrderStatus.CONFIRMED

    def cancel(self) -> None:
        """Cancela la orden.

        Raises:
            ValueError: Si la orden ya fue enviada.
        """
        if self.status == OrderStatus.SHIPPED:
            raise ValueError("No se puede cancelar una orden ya enviada")
        self.status = OrderStatus.CANCELLED

    def add_item(self, item: OrderItem) -> None:
        """Agrega un item.

        Raises:
            ValueError: Si la orden ya fue confirmada o enviada.
        """
        if self.status in (OrderStatus.CONFIRMED, OrderStatus.SHIPPED):
            raise ValueError(f"No se pueden agregar items a una orden {self.status}")
        self.items.append(item)

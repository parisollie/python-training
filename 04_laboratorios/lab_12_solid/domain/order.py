"""Entidades de dominio con validaciones y reglas de negocio.

Este modulo NO conoce nada de DB, HTTP, emails, etc.
Es puro Python con reglas de negocio.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime

TAX_RATE = 0.16


@dataclass
class OrderItem:
    """Item de una orden."""

    product: str
    quantity: int
    unit_price: float

    def __post_init__(self) -> None:
        if self.quantity < 1:
            raise ValueError(f"quantity debe ser >= 1 (recibido: {self.quantity})")
        if self.unit_price < 0:
            raise ValueError(f"unit_price debe ser >= 0 (recibido: {self.unit_price})")

    @property
    def subtotal(self) -> float:
        """Subtotal del item."""
        return round(self.quantity * self.unit_price, 2)


@dataclass
class Order:
    """Orden de compra.

    Reglas de negocio:
        - No se puede crear sin items.
        - Cada item se valida (quantity >= 1, unit_price >= 0).
        - El total incluye IVA.
    """

    user_id: str
    items: list[OrderItem] = field(default_factory=list)
    status: str = "pending"
    id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.user_id:
            raise ValueError("user_id no puede estar vacio")
        if not self.items:
            raise ValueError("la orden debe tener al menos un item")

    @property
    def subtotal(self) -> float:
        """Suma de subtotales."""
        return round(sum(item.subtotal for item in self.items), 2)

    @property
    def tax(self) -> float:
        """IVA sobre subtotal."""
        return round(self.subtotal * TAX_RATE, 2)

    @property
    def total(self) -> float:
        """Total a pagar (subtotal + IVA)."""
        return round(self.subtotal + self.tax, 2)

    @property
    def total_items(self) -> int:
        """Cantidad total de unidades."""
        return sum(item.quantity for item in self.items)

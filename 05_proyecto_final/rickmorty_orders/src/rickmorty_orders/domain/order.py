"""Entidad Order y OrderItem.

Order es la entidad raiz del agregado. Contiene:
- Identidad (OrderId)
- Value Objects (Email, Money)
- Items (OrderItem) con referencias a personajes
- Estado (OrderStatus) con transiciones controladas
- Reglas de negocio puras

Reglas de negocio:
- Una orden tiene al menos 1 item
- No se pueden modificar items si status != PENDING
- Transiciones: PENDING -> CONFIRMED -> SHIPPED
                PENDING -> CANCELLED
                CONFIRMED -> CANCELLED
                SHIPPED -> (terminal)
- Subtotal = suma de subtotales de items
- Tax = 16% del subtotal
- Total = subtotal + tax
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from rickmorty_orders.domain.errors import (
    InvalidOrderError,
    InvalidStatusTransitionError,
)
from rickmorty_orders.domain.value_objects import (
    CharacterId,
    Email,
    Money,
    OrderId,
)

TAX_RATE = 0.16


class OrderStatus(StrEnum):
    """Estados de una orden."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class OrderItem:
    """Item de una orden.

    Value Object inmutable. Cada item referencia un personaje
    de Rick and Morty.
    """

    character_id: CharacterId
    character_name: str
    quantity: int
    unit_price: Money

    def __post_init__(self) -> None:
        if not self.character_name.strip():
            raise InvalidOrderError("El nombre del personaje no puede estar vacio")
        if self.quantity < 1:
            raise InvalidOrderError(f"quantity debe ser >= 1 (recibido: {self.quantity})")

    @property
    def subtotal(self) -> Money:
        """Subtotal del item (unit_price * quantity)."""
        return self.unit_price * self.quantity


@dataclass
class Order:
    """Entidad Order (raiz del agregado)."""

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
        """Factory method que asigna un nuevo OrderId."""
        return cls(
            id=OrderId.generate(),
            customer_email=customer_email,
            items=items,
        )

    # ============================================
    # Calculos derivados
    # ============================================

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

    # ============================================
    # Comportamiento del dominio
    # ============================================

    def add_item(self, item: OrderItem) -> None:
        """Agrega un item a la orden.

        Raises:
            InvalidStatusTransitionError: Si la orden no esta PENDING.
        """
        if self.status != OrderStatus.PENDING:
            raise InvalidStatusTransitionError(
                f"No se pueden agregar items a una orden {self.status.value}"
            )
        self.items.append(item)

    def remove_item(self, character_id: CharacterId) -> None:
        """Remueve el item con el character_id dado.

        Raises:
            InvalidStatusTransitionError: Si la orden no esta PENDING.
            InvalidOrderError: Si el item no existe o quedaria vacia.
        """
        if self.status != OrderStatus.PENDING:
            raise InvalidStatusTransitionError(
                f"No se pueden remover items de una orden {self.status.value}"
            )
        items_filtrados = [i for i in self.items if i.character_id != character_id]
        if len(items_filtrados) == len(self.items):
            raise InvalidOrderError(f"No existe un item con character_id {character_id}")
        if not items_filtrados:
            raise InvalidOrderError("La orden no puede quedar vacia")
        self.items = items_filtrados

    def confirm(self) -> None:
        """Confirma la orden (PENDING -> CONFIRMED).

        Raises:
            InvalidStatusTransitionError: Si no esta PENDING.
        """
        if self.status != OrderStatus.PENDING:
            raise InvalidStatusTransitionError(
                f"Solo se puede confirmar desde PENDING (actual: {self.status.value})"
            )
        self.status = OrderStatus.CONFIRMED

    def ship(self) -> None:
        """Marca como enviada (CONFIRMED -> SHIPPED).

        Raises:
            InvalidStatusTransitionError: Si no esta CONFIRMED.
        """
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidStatusTransitionError(
                f"Solo se puede enviar desde CONFIRMED (actual: {self.status.value})"
            )
        self.status = OrderStatus.SHIPPED

    def cancel(self) -> None:
        """Cancela la orden.

        Raises:
            InvalidStatusTransitionError: Si ya fue enviada.
        """
        if self.status == OrderStatus.SHIPPED:
            raise InvalidStatusTransitionError("No se puede cancelar una orden ya enviada")
        if self.status == OrderStatus.CANCELLED:
            raise InvalidStatusTransitionError("La orden ya esta cancelada")
        self.status = OrderStatus.CANCELLED

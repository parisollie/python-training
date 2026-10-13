"""Modelos de dominio con tipado estatico avanzado.

Demuestra:
- Literal para valores restringidos
- TypedDict para JSON crudo
- Final para constantes
- Annotated para metadatos
"""

from dataclasses import dataclass, field
from typing import Annotated, Final, Literal, TypedDict

# ============================================
# Tipos avanzados
# ============================================

# Literal: solo estos valores son validos
OrderStatus = Literal["pending", "confirmed", "shipped", "delivered", "cancelled"]

# Final: constante que no debe reasignarse
TAX_RATE: Final[float] = 0.16
MAX_ITEMS_PER_ORDER: Final[int] = 100

# Annotated: metadatos sobre un tipo (usado por Pydantic, FastAPI, etc.)
Quantity = Annotated[int, "cantidad >= 1"]
UnitPrice = Annotated[float, "precio >= 0"]


# ============================================
# TypedDict: estructura de JSON crudo
# ============================================


class OrderItemJSON(TypedDict):
    """Estructura JSON de un item de orden."""

    name: str
    quantity: int
    unit_price: float


class OrderJSON(TypedDict):
    """Estructura JSON de una orden cruda."""

    id: str
    customer: str
    status: str
    items: list[OrderItemJSON]


# ============================================
# Entidades de dominio (dataclasses)
# ============================================


@dataclass(order=True)
class OrderItem:
    """Item individual dentro de una orden.

    Attributes:
        name: Nombre del producto.
        quantity: Cantidad pedida. Debe ser >= 1.
        unit_price: Precio unitario. Debe ser >= 0.
    """

    name: str
    quantity: Quantity
    unit_price: UnitPrice

    def __post_init__(self) -> None:
        """Valida los campos."""
        if self.quantity < 1:
            raise ValueError(f"quantity debe ser >= 1 (recibido: {self.quantity})")
        if self.unit_price < 0:
            raise ValueError(f"unit_price debe ser >= 0 (recibido: {self.unit_price})")

    @property
    def subtotal(self) -> float:
        """Subtotal del item (quantity * unit_price)."""
        return self.quantity * self.unit_price


@dataclass
class Order:
    """Orden de compra con tipado avanzado.

    Attributes:
        id: Identificador unico.
        customer: Nombre del cliente.
        items: Lista de items.
        status: Estado de la orden (Literal).
    """

    id: str
    customer: str
    status: OrderStatus = "pending"
    items: list[OrderItem] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Valida los campos."""
        if not self.id:
            raise ValueError("id no puede estar vacio")
        if not self.customer:
            raise ValueError("customer no puede estar vacio")
        if len(self.items) > MAX_ITEMS_PER_ORDER:
            raise ValueError(f"no se permiten mas de {MAX_ITEMS_PER_ORDER} items")

    @property
    def subtotal(self) -> float:
        """Suma de subtotales."""
        return sum(item.subtotal for item in self.items)

    @property
    def tax(self) -> float:
        """IVA sobre subtotal."""
        return round(self.subtotal * TAX_RATE, 2)

    @property
    def total(self) -> float:
        """Total a pagar."""
        return round(self.subtotal + self.tax, 2)

    @property
    def total_items(self) -> int:
        """Cantidad total de unidades."""
        return sum(item.quantity for item in self.items)

    def add_item(self, item: OrderItem) -> None:
        """Agrega un item validando el limite."""
        if len(self.items) >= MAX_ITEMS_PER_ORDER:
            raise ValueError(f"limite de {MAX_ITEMS_PER_ORDER} items alcanzado")
        self.items.append(item)

    def change_status(self, new_status: OrderStatus) -> None:
        """Cambia el estado de la orden.

        Args:
            new_status: Nuevo estado (Literal, mypy valida).
        """
        self.status = new_status


def order_from_json(data: OrderJSON) -> Order:
    """Construye una Order a partir de un OrderJSON (TypedDict).

    Args:
        data: Diccionario con estructura conocida (TypedDict).

    Returns:
        Entidad Order.

    Note:
        Si el status del JSON no es valido, se lanza ValueError.
    """
    valid_statuses: set[str] = {"pending", "confirmed", "shipped", "delivered", "cancelled"}
    if data["status"] not in valid_statuses:
        raise ValueError(f"status invalido: {data['status']}")

    order = Order(
        id=data["id"],
        customer=data["customer"],
        status=data["status"],  # type: ignore[arg-type]  # validado arriba
    )
    for item_data in data["items"]:
        order.add_item(
            OrderItem(
                name=item_data["name"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
            )
        )
    return order

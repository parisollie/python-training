"""Schemas Pydantic para validacion de entrada/salida.

Los schemas Pydantic validan datos externos (JSON, formularios, APIs)
y los convierten en entidades de dominio (dataclasses).
"""

from models import Order, OrderItem
from pydantic import BaseModel, Field, field_validator


class OrderItemIn(BaseModel):
    """Item de entrada (sin subtotal, se calcula)."""

    name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0.0)


class OrderItemOut(BaseModel):
    """Item de salida (incluye subtotal calculado)."""

    name: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderIn(BaseModel):
    """Orden de entrada (sin id, sin calculos)."""

    customer: str = Field(min_length=1, max_length=100)
    items: list[OrderItemIn] = Field(min_length=1)

    @field_validator("customer")
    @classmethod
    def customer_no_vacio(cls, v: str) -> str:
        """Valida que el customer no sea solo espacios."""
        if not v.strip():
            raise ValueError("customer no puede ser vacio")
        return v.strip()


class OrderOut(BaseModel):
    """Orden de salida (con id, calculos y totales)."""

    id: str
    customer: str
    items: list[OrderItemOut]
    subtotal: float
    tax: float
    total: float
    total_items: int


def order_from_in(order_in: OrderIn, order_id: str) -> Order:
    """Convierte un OrderIn (Pydantic) en una entidad Order (dataclass).

    Args:
        order_in: Schema de entrada validado.
        order_id: Identificador a asignar a la orden.

    Returns:
        Entidad Order lista para usar en el dominio.
    """
    order = Order(id=order_id, customer=order_in.customer)
    for item_in in order_in.items:
        order.add_item(
            OrderItem(
                name=item_in.name,
                quantity=item_in.quantity,
                unit_price=item_in.unit_price,
            )
        )
    return order


def order_to_out(order: Order) -> OrderOut:
    """Convierte una entidad Order (dataclass) en un OrderOut (Pydantic).

    Args:
        order: Entidad de dominio.

    Returns:
        Schema de salida listo para serializar a JSON.
    """
    return OrderOut(
        id=order.id,
        customer=order.customer,
        items=[
            OrderItemOut(
                name=item.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            for item in order.items
        ],
        subtotal=order.subtotal,
        tax=order.tax,
        total=order.total,
        total_items=order.total_items,
    )

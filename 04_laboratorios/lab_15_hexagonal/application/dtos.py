"""DTOs (Data Transfer Objects) de la capa de aplicacion.

Los DTOs:
- Son objetos planos para transportar datos entre capas
- NO son entidades del dominio
- Se validan con Pydantic (en el borde de la aplicacion)
- Evitan exponer entidades crudas al exterior

CreateOrderInput: entrada al caso de uso
OrderOutput: salida del caso de uso
"""

from domain.order import Order
from pydantic import BaseModel, Field


class OrderItemInput(BaseModel):
    """DTO de entrada: un item de la orden."""

    product: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0.0)


class CreateOrderInput(BaseModel):
    """DTO de entrada al caso de uso CreateOrder."""

    customer_email: str = Field(min_length=5, max_length=255)
    items: list[OrderItemInput] = Field(min_length=1)


class OrderItemOutput(BaseModel):
    """DTO de salida: un item con su subtotal."""

    product: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderOutput(BaseModel):
    """DTO de salida del caso de uso."""

    id: str
    customer_email: str
    status: str
    items: list[OrderItemOutput]
    subtotal: float
    tax: float
    total: float
    total_items: int

    @classmethod
    def from_entity(cls, order: Order) -> "OrderOutput":
        """Convierte una entidad Order al DTO de salida."""
        return cls(
            id=str(order.id),
            customer_email=str(order.customer_email),
            status=order.status.value,
            items=[
                OrderItemOutput(
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.unit_price.amount,
                    subtotal=item.subtotal.amount,
                )
                for item in order.items
            ],
            subtotal=order.subtotal.amount,
            tax=order.tax.amount,
            total=order.total.amount,
            total_items=order.total_items,
        )

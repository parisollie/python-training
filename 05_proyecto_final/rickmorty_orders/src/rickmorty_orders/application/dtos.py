"""DTOs (Data Transfer Objects) de la capa de aplicacion.

Los DTOs:
- Transportan datos entre el exterior y los casos de uso
- Se validan con Pydantic (en el borde de la aplicacion)
- Evitan exponer entidades del dominio al exterior
- No contienen logica de negocio
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from rickmorty_orders.domain.order import Order


class OrderItemInput(BaseModel):
    """DTO de entrada: un item de la orden."""

    character_id: int = Field(ge=1, description="ID de personaje de R&M")
    quantity: int = Field(ge=1, le=100, description="Cantidad (1-100)")


class CreateOrderInput(BaseModel):
    """DTO de entrada al caso de uso CreateOrder."""

    customer_email: EmailStr = Field(description="Email del cliente")
    items: list[OrderItemInput] = Field(
        min_length=1,
        max_length=50,
        description="Items de la orden (1-50)",
    )


class OrderItemOutput(BaseModel):
    """DTO de salida: un item con su subtotal."""

    model_config = ConfigDict(from_attributes=True)

    character_id: int
    character_name: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderOutput(BaseModel):
    """DTO de salida del caso de uso."""

    model_config = ConfigDict(from_attributes=True)

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
                    character_id=item.character_id.value,
                    character_name=item.character_name,
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

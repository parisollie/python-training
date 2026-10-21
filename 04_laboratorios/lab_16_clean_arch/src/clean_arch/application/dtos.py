"""DTOs de entrada/salida del lab 16."""

from pydantic import BaseModel, EmailStr, Field


class OrderItemInput(BaseModel):
    """DTO de entrada: un item de la orden."""

    product: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=1, le=100)
    unit_price: float = Field(ge=0.0)


class CreateOrderInput(BaseModel):
    """DTO de entrada: crear una orden."""

    customer_email: EmailStr
    items: list[OrderItemInput] = Field(min_length=1, max_length=50)


class OrderItemOutput(BaseModel):
    """DTO de salida: un item."""

    product: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderOutput(BaseModel):
    """DTO de salida: una orden."""

    id: str
    customer_email: str
    status: str
    items: list[OrderItemOutput]
    subtotal: float
    tax: float
    total: float
    total_items: int

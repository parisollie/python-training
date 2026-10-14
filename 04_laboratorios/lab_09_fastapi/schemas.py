"""Schemas Pydantic para la API.

Separacion de responsabilidades:
- XxxIn: entrada (validacion de request)
- XxxOut: salida (serializacion de response)
- Token: respuesta de login
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ============================================
# USER
# ============================================


class UserIn(BaseModel):
    """Datos para crear un usuario."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    name: str = Field(min_length=1, max_length=100)


class UserOut(BaseModel):
    """Datos publicos del usuario (sin password)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    created_at: datetime


# ============================================
# AUTH
# ============================================


class Token(BaseModel):
    """Respuesta del endpoint /token."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Datos extraidos del JWT (para uso interno)."""

    email: str | None = None


# ============================================
# ORDER
# ============================================


class OrderItemIn(BaseModel):
    """Item de entrada (sin subtotal)."""

    product: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0.0)


class OrderItemOut(BaseModel):
    """Item de salida (con subtotal calculado)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    product: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderIn(BaseModel):
    """Datos para crear una orden."""

    items: list[OrderItemIn] = Field(min_length=1)


class OrderOut(BaseModel):
    """Datos de una orden (salida)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: str
    created_at: datetime
    items: list[OrderItemOut]
    total: float

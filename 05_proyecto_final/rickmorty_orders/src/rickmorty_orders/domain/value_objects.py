"""Value Objects del dominio.

Un Value Object:
- No tiene identidad (dos con el mismo valor son iguales)
- Es inmutable (frozen dataclass)
- Tiene invariantes en __post_init__
- Puede tener comportamiento

Value Objects del dominio rickmorty_orders:
- OrderId: identificador unico de orden (UUID)
- CharacterId: identificador de personaje de Rick and Morty
- Money: cantidad monetaria con moneda
- Email: email validado
"""

from dataclasses import dataclass
from re import compile as re_compile
from uuid import uuid4

_EMAIL_RE = re_compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass(frozen=True)
class OrderId:
    """Identificador unico de una orden."""

    value: str

    @classmethod
    def generate(cls) -> "OrderId":
        """Genera un OrderId nuevo (UUID4)."""
        return cls(value=str(uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CharacterId:
    """Identificador de un personaje de Rick and Morty."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 1:
            raise ValueError(f"CharacterId debe ser >= 1 (recibido: {self.value})")

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Money:
    """Cantidad monetaria con su moneda."""

    amount: float
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"Money no puede ser negativo (recibido: {self.amount})")
        if len(self.currency) != 3:
            raise ValueError(f"Currency debe ser de 3 letras (recibido: {self.currency})")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"No se pueden sumar {self.currency} y {other.currency}")
        return Money(amount=round(self.amount + other.amount, 2), currency=self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"No se pueden restar {self.currency} y {other.currency}")
        return Money(amount=round(self.amount - other.amount, 2), currency=self.currency)

    def __mul__(self, factor: int | float) -> "Money":
        if factor < 0:
            raise ValueError(f"Factor no puede ser negativo (recibido: {factor})")
        return Money(amount=round(self.amount * factor, 2), currency=self.currency)

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"


@dataclass(frozen=True)
class Email:
    """Email validado y normalizado."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not _EMAIL_RE.match(normalized):
            raise ValueError(f"Email invalido (recibido: {self.value})")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value

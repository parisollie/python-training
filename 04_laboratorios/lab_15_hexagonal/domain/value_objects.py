"""Value Objects del dominio.

Un Value Object:
- No tiene identidad (dos con el mismo valor son iguales)
- Es inmutable (frozen dataclass)
- Tiene invariantes en __post_init__
- Puede tener comportamiento (metodos)

Ejemplos: Money, Email, OrderId.
"""

from dataclasses import dataclass
from re import compile as re_compile
from uuid import uuid4

# Regex simple para email
_EMAIL_RE = re_compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass(frozen=True)
class OrderId:
    """Identificador unico de una orden."""

    value: str

    @classmethod
    def generate(cls) -> "OrderId":
        """Genera un nuevo OrderId aleatorio."""
        return cls(value=str(uuid4()))

    def __str__(self) -> str:
        return self.value


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
        """Suma dos Money del mismo tipo."""
        if self.currency != other.currency:
            raise ValueError(f"No se pueden sumar {self.currency} y {other.currency}")
        return Money(amount=round(self.amount + other.amount, 2), currency=self.currency)

    def __mul__(self, factor: int | float) -> "Money":
        """Multiplica Money por un escalar."""
        if factor < 0:
            raise ValueError(f"Factor no puede ser negativo (recibido: {factor})")
        return Money(amount=round(self.amount * factor, 2), currency=self.currency)

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"


@dataclass(frozen=True)
class Email:
    """Direccion de email validada."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not _EMAIL_RE.match(normalized):
            raise ValueError(f"Email invalido (recibido: {self.value})")
        # frozen dataclass: usamos object.__setattr__ para normalizar
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value

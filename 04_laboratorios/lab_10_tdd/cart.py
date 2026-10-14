"""Carrito de compras con descuentos.

Implementado con TDD (Test-Driven Development):
- RED: escribimos el test, falla porque no existe el codigo
- GREEN: implementamos lo minimo para que pase
- REFACTOR: mejoramos sin romper tests

Reglas de negocio:
- Subtotal: suma de precios de los items
- Descuento por monto:
  * 0% si subtotal <= 100
  * 10% si 100 < subtotal <= 500
  * 20% si subtotal > 500
- Descuento extra: 5% adicional si el usuario es premium
- Total = subtotal - descuento total
"""

from typing import Protocol


class UserService(Protocol):
    """Interfaz para consultar si un usuario es premium.

    Permite inyectar una implementacion real (DB, API) o un mock en tests.
    """

    def is_premium(self, user_id: str) -> bool:
        """Devuelve True si el usuario es premium."""
        ...


class InMemoryUserService:
    """Implementacion en memoria de UserService (para pruebas)."""

    def __init__(self, premium_users: set[str] | None = None) -> None:
        self._premium: set[str] = premium_users or set()

    def is_premium(self, user_id: str) -> bool:
        """Devuelve True si el user_id esta en el set de premium."""
        return user_id in self._premium


class Cart:
    """Carrito de compras con descuentos por monto y por usuario premium.

    Attributes:
        items: Lista de precios unitarios de los productos.
        user_id: Identificador del usuario (opcional).
        user_service: Servicio para consultar si es premium.

    Examples:
        >>> cart = Cart()
        >>> cart.add_item(50.0)
        >>> cart.add_item(100.0)
        >>> cart.subtotal()
        150.0
        >>> cart.discount()
        15.0
        >>> cart.total()
        135.0
    """

    def __init__(
        self,
        user_id: str | None = None,
        user_service: UserService | None = None,
    ) -> None:
        """Inicializa el carrito.

        Args:
            user_id: Identificador del usuario (opcional).
            user_service: Servicio para consultar premium (opcional).
        """
        self.items: list[float] = []
        self.user_id = user_id
        self.user_service = user_service

    def add_item(self, price: float) -> None:
        """Agrega un item al carrito.

        Args:
            price: Precio del item.

        Raises:
            ValueError: Si el precio es negativo.
        """
        if price < 0:
            raise ValueError(f"El precio no puede ser negativo (recibido: {price})")
        self.items.append(price)

    def subtotal(self) -> float:
        """Suma de los precios de los items."""
        return round(sum(self.items), 2)

    def discount(self) -> float:
        """Descuento total (por monto + premium)."""
        subtotal = self.subtotal()

        # Descuento por monto
        if subtotal > 500:
            base_discount = 0.20
        elif subtotal > 100:
            base_discount = 0.10
        else:
            base_discount = 0.0

        # Descuento extra por premium
        premium_discount = 0.0
        if (
            self.user_id is not None
            and self.user_service is not None
            and self.user_service.is_premium(self.user_id)
        ):
            premium_discount = 0.05

        total_discount = base_discount + premium_discount
        return round(subtotal * total_discount, 2)

    def total(self) -> float:
        """Total a pagar (subtotal - descuento)."""
        return round(self.subtotal() - self.discount(), 2)

    def clear(self) -> None:
        """Vacia el carrito."""
        self.items.clear()

    def __len__(self) -> int:
        return len(self.items)

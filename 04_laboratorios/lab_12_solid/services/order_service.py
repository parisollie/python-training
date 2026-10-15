"""Servicio de ordenes que depende de Protocols (DIP).

Demuestra los 5 principios SOLID:
- SRP: solo orquesta el caso de uso (no hace DB, ni email, ni cobro)
- OCP: agregar un nuevo PaymentProcessor no requiere tocar este archivo
- LSP: cualquier implementacion de los Protocols es aceptada
- ISP: usa 3 interfaces pequenas y especificas
- DIP: depende de abstracciones (Protocols), no de clases concretas
"""

from typing import TypedDict

from domain.order import Order, OrderItem
from domain.protocols import Notifier, OrderRepository, PaymentProcessor


class ItemInput(TypedDict):
    """Shape del dict de entrada para crear items."""

    product: str
    quantity: int
    unit_price: float


class PaymentError(Exception):
    """Error de pago."""


class OrderService:
    """Servicio de creacion y consulta de ordenes.

    Depende de 3 abstracciones (Protocols):
    - OrderRepository
    - Notifier
    - PaymentProcessor

    Inyeccion por constructor: el servicio no sabe si la DB es en memoria,
    SQL, Mongo, ni si el notifier es email o consola.
    """

    def __init__(
        self,
        repository: OrderRepository,
        notifier: Notifier,
        payment: PaymentProcessor,
    ) -> None:
        """Inyecta las dependencias.

        Args:
            repository: Implementacion de OrderRepository.
            notifier: Implementacion de Notifier.
            payment: Implementacion de PaymentProcessor.
        """
        self._repository = repository
        self._notifier = notifier
        self._payment = payment

    def create_order(
        self,
        user_id: str,
        items: list[ItemInput],
    ) -> Order:
        """Crea una orden: valida, cobra, guarda y notifica.

        Args:
            user_id: ID del usuario.
            items: Lista de dicts con product, quantity, unit_price.

        Returns:
            Orden creada con id asignado.

        Raises:
            PaymentError: Si el cobro falla.
            ValueError: Si los items son invalidos.
        """
        order_items = [
            OrderItem(
                product=item["product"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
            )
            for item in items
        ]

        order = Order(user_id=user_id, items=order_items)

        # Cobrar ANTES de guardar (si falla, no se guarda)
        if not self._payment.charge(order.total, user_id):
            raise PaymentError(f"Fallo el cobro de {order.total} para {user_id}")

        # Persistir
        self._repository.save(order)

        # Notificar
        self._notifier.notify_order_created(order)

        return order

    def get_order(self, order_id: str) -> Order | None:
        """Obtiene una orden por id."""
        return self._repository.get(order_id)

    def list_user_orders(self, user_id: str) -> list[Order]:
        """Lista las ordenes de un usuario."""
        return self._repository.list_by_user(user_id)

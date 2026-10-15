"""Protocols (puertos) del dominio.

Define las interfaces que el dominio necesita del exterior:
- OrderRepository: guardar y recuperar ordenes
- Notifier: notificar eventos
- PaymentProcessor: cobrar

El dominio NO conoce implementaciones concretas, solo interfaces.
"""

from typing import Protocol

from domain.order import Order


class OrderRepository(Protocol):
    """Interfaz para guardar/recuperar ordenes.

    Implementaciones posibles:
    - InMemoryOrderRepository (tests)
    - SQLOrderRepository (produccion)
    - MongoOrderRepository (alternativa)
    """

    def save(self, order: Order) -> None:
        """Guarda una orden (crea o actualiza)."""
        ...

    def get(self, order_id: str) -> Order | None:
        """Obtiene una orden por id, o None si no existe."""
        ...

    def list_by_user(self, user_id: str) -> list[Order]:
        """Lista las ordenes de un usuario."""
        ...


class Notifier(Protocol):
    """Interfaz para notificar eventos.

    Implementaciones posibles:
    - EmailNotifier (produccion)
    - ConsoleNotifier (dev)
    - FakeNotifier (tests)
    """

    def notify_order_created(self, order: Order) -> None:
        """Notifica que se creo una orden."""
        ...


class PaymentProcessor(Protocol):
    """Interfaz para procesar pagos.

    Implementaciones posibles:
    - StripePayment (produccion)
    - FakePayment (tests)
    """

    def charge(self, amount: float, user_id: str) -> bool:
        """Cobra el monto al usuario.

        Returns:
            True si el cobro fue exitoso.
        """
        ...

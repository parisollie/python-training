"""Puertos (interfaces) que el dominio necesita del exterior.

Los puertos son Protocols. Definen el CONTRATO que los adaptadores
deben cumplir, sin acoplarse a implementaciones concretas.

Puertos secundarios (driven): el dominio los USA
- OrderRepository: persistencia
- Notifier: notificaciones

Los adaptadores concretos viven en infrastructure/.
"""

from typing import Protocol

from domain.order import Order
from domain.value_objects import OrderId


class OrderRepository(Protocol):
    """Puerto para persistir ordenes.

    Contrato:
        - save: guarda o actualiza una orden
        - find_by_id: recupera por id, o None si no existe
        - list_all: lista todas las ordenes
    """

    def save(self, order: Order) -> None:
        """Guarda o actualiza una orden."""
        ...

    def find_by_id(self, order_id: OrderId) -> Order | None:
        """Recupera una orden por id."""
        ...

    def list_all(self) -> list[Order]:
        """Lista todas las ordenes."""
        ...


class Notifier(Protocol):
    """Puerto para notificar eventos del dominio.

    Contrato:
        - notify_order_created: notifica que se creo una orden
    """

    def notify_order_created(self, order: Order) -> None:
        """Notifica la creacion de una orden."""
        ...

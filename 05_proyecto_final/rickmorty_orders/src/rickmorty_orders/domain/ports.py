"""Puertos del dominio (interfaces).

Los puertos definen los CONTRATOS que el dominio necesita del exterior:

Puertos secundarios (driven, salida):
- OrderRepository: persistencia de ordenes
- CharacterRepository: consulta a la API externa de R&M
- Notifier: notificaciones al cliente
- EventBus: publicacion de eventos de dominio

Los adaptadores concretos viven en infrastructure/ y cumplen estos Protocols.
"""

from typing import Protocol

from rickmorty_orders.domain.character import Character
from rickmorty_orders.domain.events import DomainEvent
from rickmorty_orders.domain.order import Order
from rickmorty_orders.domain.value_objects import CharacterId, Email, OrderId


class OrderRepository(Protocol):
    """Puerto para persistir ordenes."""

    def save(self, order: Order) -> None:
        """Guarda o actualiza una orden."""
        ...

    def find_by_id(self, order_id: OrderId) -> Order | None:
        """Recupera una orden por id, o None si no existe."""
        ...

    def find_by_customer(self, email: Email) -> list[Order]:
        """Lista las ordenes de un cliente."""
        ...

    def list_all(self) -> list[Order]:
        """Lista todas las ordenes."""
        ...


class CharacterRepository(Protocol):
    """Puerto para consultar personajes de la API externa."""

    def find_by_id(self, character_id: CharacterId) -> Character | None:
        """Obtiene un personaje por id, o None si no existe."""
        ...

    def list_by_ids(self, character_ids: list[CharacterId]) -> list[Character]:
        """Obtiene multiples personajes."""
        ...


class Notifier(Protocol):
    """Puerto para notificar eventos al cliente."""

    def notify_order_created(self, order: Order) -> None:
        """Notifica que se creo una orden."""
        ...

    def notify_order_confirmed(self, order: Order) -> None:
        """Notifica que se confirmo una orden."""
        ...

    def notify_order_cancelled(self, order: Order) -> None:
        """Notifica que se cancelo una orden."""
        ...


class EventBus(Protocol):
    """Puerto para publicar eventos de dominio."""

    def publish(self, event: DomainEvent) -> None:
        """Publica un evento de dominio."""
        ...

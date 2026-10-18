"""Adaptadores en memoria para desarrollo y tests.

Implementan los puertos del dominio sin dependencias externas.
"""

from rickmorty_orders.domain.character import Character
from rickmorty_orders.domain.events import DomainEvent
from rickmorty_orders.domain.order import Order
from rickmorty_orders.domain.value_objects import CharacterId, Email, OrderId


class InMemoryOrderRepository:
    """Repositorio en memoria de ordenes."""

    def __init__(self) -> None:
        self._store: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self._store[str(order.id)] = order

    def find_by_id(self, order_id: OrderId) -> Order | None:
        return self._store.get(str(order_id))

    def find_by_customer(self, email: Email) -> list[Order]:
        return [o for o in self._store.values() if o.customer_email == email]

    def list_all(self) -> list[Order]:
        return list(self._store.values())


class InMemoryCharacterRepository:
    """Repositorio en memoria de personajes (para tests)."""

    def __init__(self, characters: list[Character] | None = None) -> None:
        self._store: dict[int, Character] = {}
        for c in characters or []:
            self._store[c.id.value] = c

    def add(self, character: Character) -> None:
        """Agrega un personaje al repositorio."""
        self._store[character.id.value] = character

    def find_by_id(self, character_id: CharacterId) -> Character | None:
        return self._store.get(character_id.value)

    def list_by_ids(self, character_ids: list[CharacterId]) -> list[Character]:
        result = []
        for cid in character_ids:
            c = self._store.get(cid.value)
            if c is not None:
                result.append(c)
        return result


class FakeNotifier:
    """Notificador que guarda las notificaciones (para tests)."""

    def __init__(self) -> None:
        self.created: list[str] = []
        self.confirmed: list[str] = []
        self.cancelled: list[str] = []

    def notify_order_created(self, order: Order) -> None:
        self.created.append(str(order.id))

    def notify_order_confirmed(self, order: Order) -> None:
        self.confirmed.append(str(order.id))

    def notify_order_cancelled(self, order: Order) -> None:
        self.cancelled.append(str(order.id))


class FakeEventBus:
    """Event bus que guarda los eventos publicados (para tests)."""

    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self.events.append(event)

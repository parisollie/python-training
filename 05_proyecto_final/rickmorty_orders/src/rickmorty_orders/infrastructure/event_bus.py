"""Adaptador EventBus in-memory.

Publica eventos llamando a los handlers registrados.

En produccion se reemplazaria por RabbitMQ, Kafka, Redis Streams, etc.
"""

import logging
from collections import defaultdict
from collections.abc import Callable

from rickmorty_orders.domain.events import DomainEvent

logger = logging.getLogger(__name__)


class InMemoryEventBus:
    """Event bus simple en memoria.

    Uso:
        bus = InMemoryEventBus()
        bus.subscribe(OrderCreated, handler_fn)
        bus.publish(OrderCreated(...))
    """

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[Callable[[DomainEvent], None]]] = defaultdict(
            list
        )
        self._published: list[DomainEvent] = []

    def subscribe(
        self,
        event_type: type[DomainEvent],
        handler: Callable[[DomainEvent], None],
    ) -> None:
        """Registra un handler para un tipo de evento."""
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        """Publica un evento a todos los handlers registrados."""
        logger.debug("Publicando evento: %s", type(event).__name__)
        self._published.append(event)
        for handler in self._handlers.get(type(event), []):
            try:
                handler(event)
            except Exception as e:
                logger.exception(
                    "Error en handler %s para %s: %s",
                    handler.__name__,
                    type(event).__name__,
                    e,
                )

    @property
    def published_events(self) -> list[DomainEvent]:
        """Devuelve los eventos publicados (util para tests)."""
        return list(self._published)

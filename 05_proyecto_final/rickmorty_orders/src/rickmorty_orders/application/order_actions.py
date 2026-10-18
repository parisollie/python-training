"""Casos de uso de acciones: ConfirmOrder y CancelOrder."""

import logging

from rickmorty_orders.application.dtos import OrderOutput
from rickmorty_orders.domain.errors import OrderNotFoundError
from rickmorty_orders.domain.events import OrderCancelled, OrderConfirmed
from rickmorty_orders.domain.ports import EventBus, Notifier, OrderRepository
from rickmorty_orders.domain.value_objects import OrderId

logger = logging.getLogger(__name__)


class ConfirmOrderService:
    """Caso de uso: confirmar una orden."""

    def __init__(
        self,
        repository: OrderRepository,
        notifier: Notifier,
        event_bus: EventBus,
    ) -> None:
        self._repository = repository
        self._notifier = notifier
        self._event_bus = event_bus

    def execute(self, order_id: str) -> OrderOutput:
        """Ejecuta el caso de uso.

        Raises:
            OrderNotFoundError: si la orden no existe.
            InvalidStatusTransitionError: si la transicion es invalida.
        """
        order = self._repository.find_by_id(OrderId(order_id))
        if order is None:
            raise OrderNotFoundError(f"Orden {order_id} no existe")

        order.confirm()
        self._repository.save(order)
        self._notifier.notify_order_confirmed(order)
        self._event_bus.publish(OrderConfirmed(order_id=order.id))

        logger.info("Orden confirmada: %s", order.id)
        return OrderOutput.from_entity(order)


class CancelOrderService:
    """Caso de uso: cancelar una orden."""

    def __init__(
        self,
        repository: OrderRepository,
        notifier: Notifier,
        event_bus: EventBus,
    ) -> None:
        self._repository = repository
        self._notifier = notifier
        self._event_bus = event_bus

    def execute(self, order_id: str, reason: str = "") -> OrderOutput:
        """Ejecuta el caso de uso.

        Args:
            order_id: id de la orden.
            reason: motivo de cancelacion (opcional).

        Raises:
            OrderNotFoundError: si la orden no existe.
            InvalidStatusTransitionError: si la transicion es invalida.
        """
        order = self._repository.find_by_id(OrderId(order_id))
        if order is None:
            raise OrderNotFoundError(f"Orden {order_id} no existe")

        order.cancel()
        self._repository.save(order)
        self._notifier.notify_order_cancelled(order)
        self._event_bus.publish(OrderCancelled(order_id=order.id, reason=reason))

        logger.info("Orden cancelada: %s (razon: %s)", order.id, reason or "N/A")
        return OrderOutput.from_entity(order)

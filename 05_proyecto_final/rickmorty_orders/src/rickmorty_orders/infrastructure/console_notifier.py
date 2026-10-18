"""Adaptador ConsoleNotifier del puerto Notifier.

Simula notificaciones imprimiendo en consola.
En produccion se reemplazaria por EmailNotifier, SlackNotifier, etc.
"""

import logging

from rickmorty_orders.domain.order import Order

logger = logging.getLogger(__name__)


class ConsoleNotifier:
    """Notificador que escribe en logs y consola."""

    def notify_order_created(self, order: Order) -> None:
        """Notifica creacion de orden."""
        msg = (
            f"[NOTIFY] Order created: {order.id} "
            f"for {order.customer_email} "
            f"(total: {order.total})"
        )
        logger.info(msg)
        print(msg)

    def notify_order_confirmed(self, order: Order) -> None:
        """Notifica confirmacion de orden."""
        msg = f"[NOTIFY] Order confirmed: {order.id}"
        logger.info(msg)
        print(msg)

    def notify_order_cancelled(self, order: Order) -> None:
        """Notifica cancelacion de orden."""
        msg = f"[NOTIFY] Order cancelled: {order.id}"
        logger.info(msg)
        print(msg)

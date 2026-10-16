"""Adaptador HTTP del puerto Notifier.

Demuestra que podemos cambiar la implementacion sin tocar
ni el dominio ni el caso de uso.

Usa httpx (ya instalado en el proyecto) con timeout y manejo de errores.
"""

import logging

import httpx
from domain.order import Order

logger = logging.getLogger(__name__)


class HttpNotifier:
    """Notificador via HTTP POST.

    Envia un JSON con los datos de la orden a una URL configurable.

    Uso:
        notifier = HttpNotifier("https://api.example.com/notify")
        notifier.notify_order_created(order)
    """

    def __init__(
        self,
        url: str,
        timeout: float = 5.0,
        client: httpx.Client | None = None,
    ) -> None:
        """Inicializa el notificador.

        Args:
            url: URL a la que enviar el POST.
            timeout: Timeout en segundos.
            client: Cliente httpx opcional (para tests).
        """
        self.url = url
        self.timeout = timeout
        self._client = client or httpx.Client(timeout=timeout)

    def notify_order_created(self, order: Order) -> None:
        """Envia la orden via HTTP POST.

        Si falla, registra el error pero NO relanza (notificacion no critica).
        """
        payload = {
            "event": "order_created",
            "order_id": str(order.id),
            "customer_email": str(order.customer_email),
            "total": order.total.amount,
            "currency": order.total.currency,
        }
        try:
            response = self._client.post(self.url, json=payload)
            response.raise_for_status()
            logger.info("Notificacion enviada para orden %s", order.id)
        except httpx.HTTPError as e:
            logger.error("Fallo notificacion para orden %s: %s", order.id, e)

    def close(self) -> None:
        """Cierra el cliente HTTP."""
        self._client.close()

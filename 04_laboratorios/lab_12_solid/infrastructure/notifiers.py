"""Implementaciones de Notifier."""

from domain.order import Order


class ConsoleNotifier:
    """Notificador que imprime en consola (dev)."""

    def __init__(self) -> None:
        self.notified: list[str] = []

    def notify_order_created(self, order: Order) -> None:
        """Imprime el evento y guarda el id notificado."""
        assert order.id is not None
        print(f"📧 Orden creada: {order.id} para {order.user_id} (total {order.total})")
        self.notified.append(order.id)


class EmailNotifier:
    """Simulacion de notificador por email (produccion).

    En produccion enviaria un email real con SMTP o un servicio como SendGrid.
    Aqui solo guarda los envios en memoria para poder testear.
    """

    def __init__(self, smtp_server: str = "smtp.example.com") -> None:
        self.smtp_server = smtp_server
        self.sent_emails: list[dict[str, str]] = []

    def notify_order_created(self, order: Order) -> None:
        """Registra el email que se habria enviado."""
        assert order.id is not None
        self.sent_emails.append(
            {
                "to": f"{order.user_id}@example.com",
                "subject": f"Orden {order.id} creada",
                "body": f"Tu orden tiene un total de ${order.total}",
            }
        )


class FakeNotifier:
    """Notificador que no hace nada (util en tests que no verifican notificaciones)."""

    def notify_order_created(self, order: Order) -> None:
        """No hace nada."""

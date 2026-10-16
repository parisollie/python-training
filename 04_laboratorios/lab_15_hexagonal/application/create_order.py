"""Caso de uso: CreateOrder.

Orquesta el dominio y los puertos. No conoce adaptadores concretos.
"""

from domain.order import Order, OrderItem
from domain.ports import Notifier, OrderRepository
from domain.value_objects import Email, Money, OrderId

from application.dtos import CreateOrderInput, OrderOutput


class OrderNotFoundError(Exception):
    """La orden no existe."""


class CreateOrderService:
    """Caso de uso para crear ordenes.

    Depende de 2 puertos (Protocols):
    - OrderRepository
    - Notifier

    No conoce implementaciones concretas (SQL, HTTP, Memory).
    """

    def __init__(
        self,
        repository: OrderRepository,
        notifier: Notifier,
    ) -> None:
        """Inyecta las dependencias via constructor."""
        self._repository = repository
        self._notifier = notifier

    def execute(self, input_dto: CreateOrderInput) -> OrderOutput:
        """Ejecuta el caso de uso.

        Args:
            input_dto: DTO validado de entrada.

        Returns:
            DTO con la orden creada.
        """
        # Convertir DTO -> entidades del dominio
        email = Email(input_dto.customer_email)
        items = [
            OrderItem(
                product=item.product,
                quantity=item.quantity,
                unit_price=Money(item.unit_price),
            )
            for item in input_dto.items
        ]

        # Crear la entidad (aplica invariantes)
        order = Order.create(customer_email=email, items=items)

        # Persistir via puerto
        self._repository.save(order)

        # Notificar via puerto
        self._notifier.notify_order_created(order)

        # Convertir entidad -> DTO de salida
        return OrderOutput.from_entity(order)

    def get(self, order_id: str) -> OrderOutput:
        """Obtiene una orden existente.

        Args:
            order_id: id de la orden.

        Returns:
            DTO de la orden.

        Raises:
            OrderNotFoundError: si no existe.
        """
        order = self._repository.find_by_id(OrderId(order_id))
        if order is None:
            raise OrderNotFoundError(f"Orden {order_id} no existe")
        return OrderOutput.from_entity(order)

    def list_all(self) -> list[OrderOutput]:
        """Lista todas las ordenes."""
        return [OrderOutput.from_entity(o) for o in self._repository.list_all()]

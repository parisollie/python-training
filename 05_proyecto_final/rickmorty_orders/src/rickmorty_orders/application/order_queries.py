"""Casos de uso de consulta: GetOrder y ListOrders."""

import logging

from rickmorty_orders.application.dtos import OrderOutput
from rickmorty_orders.domain.errors import OrderNotFoundError
from rickmorty_orders.domain.ports import OrderRepository
from rickmorty_orders.domain.value_objects import Email, OrderId

logger = logging.getLogger(__name__)


class GetOrderService:
    """Caso de uso: obtener una orden por id."""

    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def execute(self, order_id: str) -> OrderOutput:
        """Ejecuta el caso de uso.

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


class ListOrdersService:
    """Caso de uso: listar ordenes (todas o por cliente)."""

    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def execute(self, customer_email: str | None = None) -> list[OrderOutput]:
        """Ejecuta el caso de uso.

        Args:
            customer_email: si se provee, filtra por cliente.

        Returns:
            Lista de DTOs de ordenes.
        """
        if customer_email is not None:
            orders = self._repository.find_by_customer(Email(customer_email))
        else:
            orders = self._repository.list_all()
        return [OrderOutput.from_entity(o) for o in orders]

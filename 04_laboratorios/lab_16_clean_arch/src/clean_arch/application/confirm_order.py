"""Caso de uso: ConfirmOrderService con Unit of Work."""

from clean_arch.application.unit_of_work import UnitOfWork
from clean_arch.domain.errors import OrderNotFoundError
from clean_arch.domain.events import OrderConfirmed
from clean_arch.domain.order import Order
from clean_arch.domain.value_objects import OrderId


class ConfirmOrderService:
    """Caso de uso: confirmar una orden."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, order_id: str) -> Order:
        """Confirma la orden y devuelve la entidad."""
        order = self._uow.orders.find_by_id(OrderId(order_id))
        if order is None:
            raise OrderNotFoundError(f"Orden {order_id} no existe")

        order.confirm()

        with self._uow:
            self._uow.orders.save(order)
            self._uow.collect_event(OrderConfirmed(order_id=order.id))
            self._uow.commit()

        return order

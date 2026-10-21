"""Caso de uso: CreateOrderService con Unit of Work.

Demuestra:
- El caso de uso abre el UoW explicitamente (with self.uow)
- Persiste via uow.orders.save()
- Registra eventos via uow.collect_event()
- Al hacer commit, el UoW publica los eventos via el EventBus
- Devuelve la entidad (el presenter se encarga de convertirla)
"""

from clean_arch.application.dtos import CreateOrderInput
from clean_arch.application.unit_of_work import UnitOfWork
from clean_arch.domain.events import OrderCreated
from clean_arch.domain.order import Order, OrderItem
from clean_arch.domain.value_objects import Email, Money


class CreateOrderService:
    """Caso de uso: crear una orden.

    Depende del UnitOfWork (Protocol). No conoce adaptadores concretos.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, input_dto: CreateOrderInput) -> Order:
        """Ejecuta el caso de uso y devuelve la entidad (no el DTO)."""
        items = [
            OrderItem(
                product=item.product,
                quantity=item.quantity,
                unit_price=Money(item.unit_price),
            )
            for item in input_dto.items
        ]

        order = Order.create(
            customer_email=Email(input_dto.customer_email),
            items=items,
        )

        with self._uow:
            self._uow.orders.save(order)
            self._uow.collect_event(
                OrderCreated(
                    order_id=order.id,
                    customer_email=str(order.customer_email),
                    total=order.total.amount,
                )
            )
            self._uow.commit()

        return order

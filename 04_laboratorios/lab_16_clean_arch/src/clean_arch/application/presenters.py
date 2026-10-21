"""Presenters del lab 16.

Un Presenter convierte una entidad del dominio en un DTO de salida.
Esta separado del caso de uso: el caso de uso devuelve la entidad,
el presenter decide COMO presentarla.

Ventajas:
- Multiples formatos (JSON, HTML, XML) sin tocar el caso de uso
- Testeable de forma aislada
- El router/controller no sabe nada de la entidad
"""

from clean_arch.application.dtos import OrderItemOutput, OrderOutput
from clean_arch.domain.order import Order


class OrderPresenter:
    """Convierte una Order en un OrderOutput."""

    def present(self, order: Order) -> OrderOutput:
        """Convierte la entidad en DTO de salida."""
        return OrderOutput(
            id=str(order.id),
            customer_email=str(order.customer_email),
            status=order.status.value,
            items=[
                OrderItemOutput(
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.unit_price.amount,
                    subtotal=item.subtotal.amount,
                )
                for item in order.items
            ],
            subtotal=order.subtotal.amount,
            tax=order.tax.amount,
            total=order.total.amount,
            total_items=order.total_items,
        )

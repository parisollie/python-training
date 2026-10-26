"""Conversores entre mensajes Protobuf y DTOs de la capa de aplicacion.

Los conversores son funciones puras (sin estado, sin I/O). Su unico
trabajo es traducir entre el mundo gRPC (mensajes protobuf) y el mundo
de la aplicacion (DTOs Pydantic).

Esto mantiene el servicer (OrderServicer) delgado y testeable.
"""

from rickmorty_orders.application.dtos import (
    CreateOrderInput,
    OrderItemInput,
    OrderItemOutput,
    OrderOutput,
)
from rickmorty_orders.grpc import orders_pb2


def proto_to_create_order_input(request: orders_pb2.CreateOrderRequest) -> CreateOrderInput:
    """Convierte un CreateOrderRequest de protobuf al DTO de entrada.

    Args:
        request: mensaje protobuf recibido por gRPC.

    Returns:
        DTO validado de entrada al caso de uso.

    Raises:
        pydantic.ValidationError: si los datos no cumplen las reglas del DTO.
    """
    return CreateOrderInput(
        customer_email=request.customer_email,
        items=[
            OrderItemInput(character_id=item.character_id, quantity=item.quantity)
            for item in request.items
        ],
    )


def order_item_output_to_proto(item: OrderItemOutput) -> orders_pb2.OrderItemOutput:
    """Convierte un OrderItemOutput (DTO) a un OrderItemOutput (protobuf).

    Args:
        item: DTO del item de la orden.

    Returns:
        Mensaje protobuf equivalente.
    """
    return orders_pb2.OrderItemOutput(
        character_id=item.character_id,
        character_name=item.character_name,
        quantity=item.quantity,
        unit_price=item.unit_price,
        subtotal=item.subtotal,
    )


def order_output_to_proto(order: OrderOutput) -> orders_pb2.OrderResponse:
    """Convierte un OrderOutput (DTO) a un OrderResponse (protobuf).

    Args:
        order: DTO de la orden.

    Returns:
        Mensaje protobuf equivalente.
    """
    return orders_pb2.OrderResponse(
        id=order.id,
        customer_email=order.customer_email,
        status=order.status,
        items=[order_item_output_to_proto(item) for item in order.items],
        subtotal=order.subtotal,
        tax=order.tax,
        total=order.total,
        total_items=order.total_items,
    )


def order_outputs_to_list_proto(
    orders: list[OrderOutput],
) -> orders_pb2.ListOrdersResponse:
    """Convierte una lista de OrderOutput a ListOrdersResponse (protobuf).

    Args:
        orders: lista de DTOs.

    Returns:
        Mensaje protobuf con la lista envuelta.
    """
    return orders_pb2.ListOrdersResponse(
        orders=[order_output_to_proto(o) for o in orders],
    )

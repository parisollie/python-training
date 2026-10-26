"""Tests unitarios de los conversores proto <-> DTO.

No levantan gRPC ni red: solo validan que las traducciones entre
mensajes protobuf y DTOs Pydantic preservan los datos.
"""

import pytest
from rickmorty_orders.application.dtos import (
    OrderItemOutput,
    OrderOutput,
)
from rickmorty_orders.grpc import orders_pb2
from rickmorty_orders.grpc.converters import (
    order_item_output_to_proto,
    order_output_to_proto,
    order_outputs_to_list_proto,
    proto_to_create_order_input,
)

# ============================================
# proto_to_create_order_input
# ============================================


def test_proto_to_create_order_input_convierte_campos():
    """Verifica que el DTO refleja los datos del mensaje protobuf."""
    request = orders_pb2.CreateOrderRequest(
        customer_email="test@example.com",
        items=[
            orders_pb2.OrderItemInput(character_id=1, quantity=2),
            orders_pb2.OrderItemInput(character_id=3, quantity=1),
        ],
    )

    dto = proto_to_create_order_input(request)

    assert dto.customer_email == "test@example.com"
    assert len(dto.items) == 2
    assert dto.items[0].character_id == 1
    assert dto.items[0].quantity == 2
    assert dto.items[1].character_id == 3
    assert dto.items[1].quantity == 1


def test_proto_to_create_order_input_con_email_invalido_falla():
    """Pydantic valida el email; protobuf no. El DTO debe fallar."""
    request = orders_pb2.CreateOrderRequest(
        customer_email="esto-no-es-un-email",
        items=[orders_pb2.OrderItemInput(character_id=1, quantity=1)],
    )

    with pytest.raises(ValueError):
        proto_to_create_order_input(request)


# ============================================
# order_item_output_to_proto
# ============================================


def test_order_item_output_to_proto_preserva_campos():
    dto = OrderItemOutput(
        character_id=1,
        character_name="Rick Sanchez",
        quantity=2,
        unit_price=50.0,
        subtotal=100.0,
    )

    proto = order_item_output_to_proto(dto)

    assert proto.character_id == 1
    assert proto.character_name == "Rick Sanchez"
    assert proto.quantity == 2
    assert proto.unit_price == 50.0
    assert proto.subtotal == 100.0


# ============================================
# order_output_to_proto
# ============================================


def _sample_order_output() -> OrderOutput:
    return OrderOutput(
        id="abc-123",
        customer_email="paul@example.com",
        status="pending",
        items=[
            OrderItemOutput(
                character_id=1,
                character_name="Rick Sanchez",
                quantity=2,
                unit_price=50.0,
                subtotal=100.0,
            ),
            OrderItemOutput(
                character_id=2,
                character_name="Morty Smith",
                quantity=1,
                unit_price=50.0,
                subtotal=50.0,
            ),
        ],
        subtotal=150.0,
        tax=24.0,
        total=174.0,
        total_items=3,
    )


def test_order_output_to_proto_preserva_todos_los_campos():
    dto = _sample_order_output()

    proto = order_output_to_proto(dto)

    assert proto.id == "abc-123"
    assert proto.customer_email == "paul@example.com"
    assert proto.status == "pending"
    assert proto.subtotal == 150.0
    assert proto.tax == 24.0
    assert proto.total == 174.0
    assert proto.total_items == 3
    assert len(proto.items) == 2
    assert proto.items[0].character_name == "Rick Sanchez"
    assert proto.items[1].character_name == "Morty Smith"


# ============================================
# order_outputs_to_list_proto
# ============================================


def test_order_outputs_to_list_proto_envuelve_lista():
    orders = [_sample_order_output(), _sample_order_output()]

    response = order_outputs_to_list_proto(orders)

    assert len(response.orders) == 2
    assert response.orders[0].id == "abc-123"
    assert response.orders[1].id == "abc-123"


def test_order_outputs_to_list_proto_lista_vacia():
    response = order_outputs_to_list_proto([])

    assert len(response.orders) == 0

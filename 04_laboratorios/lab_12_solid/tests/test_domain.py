"""Tests del dominio (Order y OrderItem)."""

import pytest
from domain.order import TAX_RATE, Order, OrderItem


def test_order_item_subtotal() -> None:
    """subtotal = quantity * unit_price."""
    item = OrderItem(product="Teclado", quantity=2, unit_price=25.0)
    assert item.subtotal == 50.0


def test_order_item_quantity_invalida() -> None:
    """quantity < 1 lanza ValueError."""
    with pytest.raises(ValueError, match="quantity"):
        OrderItem(product="X", quantity=0, unit_price=10.0)


def test_order_item_unit_price_negativo() -> None:
    """unit_price < 0 lanza ValueError."""
    with pytest.raises(ValueError, match="unit_price"):
        OrderItem(product="X", quantity=1, unit_price=-5.0)


def test_order_totales() -> None:
    """Subtotal, tax y total correctos."""
    order = Order(
        user_id="user-1",
        items=[
            OrderItem(product="A", quantity=2, unit_price=25.0),
            OrderItem(product="B", quantity=1, unit_price=15.5),
        ],
    )
    assert order.subtotal == 65.5
    assert order.tax == round(65.5 * TAX_RATE, 2)  # 10.48
    assert order.total == 75.98


def test_order_sin_user_id() -> None:
    """user_id vacio lanza ValueError."""
    with pytest.raises(ValueError, match="user_id"):
        Order(
            user_id="",
            items=[OrderItem(product="X", quantity=1, unit_price=1.0)],
        )


def test_order_sin_items() -> None:
    """Sin items lanza ValueError."""
    with pytest.raises(ValueError, match="al menos un item"):
        Order(user_id="user-1", items=[])


def test_order_total_items() -> None:
    """total_items suma quantities."""
    order = Order(
        user_id="user-1",
        items=[
            OrderItem(product="A", quantity=3, unit_price=1.0),
            OrderItem(product="B", quantity=2, unit_price=1.0),
        ],
    )
    assert order.total_items == 5


def test_order_status_default() -> None:
    """Status default es pending."""
    order = Order(
        user_id="user-1",
        items=[OrderItem(product="X", quantity=1, unit_price=1.0)],
    )
    assert order.status == "pending"


def test_order_created_at_utc() -> None:
    """created_at se inicializa en UTC."""
    order = Order(
        user_id="user-1",
        items=[OrderItem(product="X", quantity=1, unit_price=1.0)],
    )
    assert order.created_at is not None
    assert order.created_at.tzinfo is not None

"""Tests del dominio del lab 16."""

import pytest
from clean_arch.domain.errors import (
    InvalidOrderError,
    InvalidStatusTransitionError,
)
from clean_arch.domain.order import Order, OrderItem, OrderStatus
from clean_arch.domain.value_objects import Email, Money, OrderId

# ============================================
# Value Objects
# ============================================


def test_money_suma() -> None:
    """Money + Money del mismo tipo."""
    assert (Money(100.0) + Money(50.0)).amount == 150.0


def test_money_negativo_falla() -> None:
    """Money negativo lanza."""
    with pytest.raises(ValueError, match="negativo"):
        Money(-1.0)


def test_email_normaliza() -> None:
    """Email normaliza (strip + lowercase)."""
    assert Email("  PAUL@Example.COM  ").value == "paul@example.com"


def test_email_invalido_falla() -> None:
    """Email invalido lanza."""
    with pytest.raises(ValueError, match="Email invalido"):
        Email("no-es-email")


def test_order_id_generate() -> None:
    """OrderId.generate() crea UUID unicos."""
    oid1 = OrderId.generate()
    oid2 = OrderId.generate()
    assert oid1 != oid2


# ============================================
# OrderItem
# ============================================


def test_order_item_subtotal() -> None:
    """subtotal = unit_price * quantity."""
    item = OrderItem(product="X", quantity=3, unit_price=Money(10.0))
    assert item.subtotal.amount == 30.0


def test_order_item_producto_vacio_falla() -> None:
    """Producto vacio lanza."""
    with pytest.raises(InvalidOrderError, match="producto"):
        OrderItem(product="", quantity=1, unit_price=Money(10.0))


def test_order_item_quantity_invalida_falla() -> None:
    """quantity < 1 lanza."""
    with pytest.raises(InvalidOrderError, match="quantity"):
        OrderItem(product="X", quantity=0, unit_price=Money(10.0))


# ============================================
# Order
# ============================================


def test_order_create() -> None:
    """Order.create asigna id y status PENDING."""
    order = Order.create(
        customer_email=Email("a@b.com"),
        items=[OrderItem(product="X", quantity=1, unit_price=Money(10.0))],
    )
    assert order.id is not None
    assert order.status == OrderStatus.PENDING


def test_order_sin_items_falla() -> None:
    """Sin items lanza."""
    with pytest.raises(InvalidOrderError, match="al menos un item"):
        Order.create(customer_email=Email("a@b.com"), items=[])


def test_order_totales() -> None:
    """subtotal, tax, total correctos."""
    order = Order.create(
        customer_email=Email("a@b.com"),
        items=[
            OrderItem(product="A", quantity=2, unit_price=Money(50.0)),
            OrderItem(product="B", quantity=1, unit_price=Money(25.0)),
        ],
    )
    assert order.subtotal.amount == 125.0
    assert order.tax.amount == 20.0
    assert order.total.amount == 145.0
    assert order.total_items == 3


# ============================================
# Transiciones de estado
# ============================================


def test_order_confirm() -> None:
    """confirm() cambia PENDING -> CONFIRMED."""
    order = Order.create(
        customer_email=Email("a@b.com"),
        items=[OrderItem(product="X", quantity=1, unit_price=Money(10.0))],
    )
    order.confirm()
    assert order.status == OrderStatus.CONFIRMED


def test_order_confirm_dos_veces_falla() -> None:
    """No se puede confirmar dos veces."""
    order = Order.create(
        customer_email=Email("a@b.com"),
        items=[OrderItem(product="X", quantity=1, unit_price=Money(10.0))],
    )
    order.confirm()
    with pytest.raises(InvalidStatusTransitionError, match="PENDING"):
        order.confirm()


def test_order_cancel() -> None:
    """cancel() cambia a CANCELLED."""
    order = Order.create(
        customer_email=Email("a@b.com"),
        items=[OrderItem(product="X", quantity=1, unit_price=Money(10.0))],
    )
    order.cancel()
    assert order.status == OrderStatus.CANCELLED


def test_order_cancel_dos_veces_falla() -> None:
    """No se puede cancelar dos veces."""
    order = Order.create(
        customer_email=Email("a@b.com"),
        items=[OrderItem(product="X", quantity=1, unit_price=Money(10.0))],
    )
    order.cancel()
    with pytest.raises(InvalidStatusTransitionError, match="ya esta cancelada"):
        order.cancel()

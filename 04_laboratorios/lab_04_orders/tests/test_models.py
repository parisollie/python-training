"""Tests para las dataclasses Order y OrderItem."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Order, OrderItem  # noqa: E402

# ============================================
# Tests de OrderItem
# ============================================


def test_order_item_subtotal() -> None:
    """subtotal = quantity * unit_price."""
    item = OrderItem(name="Teclado", quantity=2, unit_price=25.0)
    assert item.subtotal == 50.0


def test_order_item_quantity_invalida() -> None:
    """quantity < 1 lanza ValueError."""
    with pytest.raises(ValueError, match="quantity"):
        OrderItem(name="X", quantity=0, unit_price=10.0)


def test_order_item_precio_negativo() -> None:
    """unit_price < 0 lanza ValueError."""
    with pytest.raises(ValueError, match="unit_price"):
        OrderItem(name="X", quantity=1, unit_price=-5.0)


def test_order_item_eq() -> None:
    """Dos items con mismos valores son iguales."""
    a = OrderItem(name="X", quantity=2, unit_price=10.0)
    b = OrderItem(name="X", quantity=2, unit_price=10.0)
    assert a == b


def test_order_item_order() -> None:
    """Items se ordenan por (name, quantity, unit_price)."""
    a = OrderItem(name="A", quantity=1, unit_price=10.0)
    b = OrderItem(name="B", quantity=1, unit_price=10.0)
    assert a < b


# ============================================
# Tests de Order (construccion)
# ============================================


def test_order_vacia() -> None:
    """Order vacia tiene subtotal 0, tax 0, total 0."""
    order = Order(id="ORD-001", customer="Paul")
    assert order.subtotal == 0.0
    assert order.tax == 0.0
    assert order.total == 0.0
    assert order.total_items == 0


def test_order_add_item() -> None:
    """add_item agrega items a la lista."""
    order = Order(id="ORD-001", customer="Paul")
    item = OrderItem(name="Teclado", quantity=1, unit_price=25.0)
    order.add_item(item)
    assert len(order.items) == 1
    assert order.items[0] == item


def test_order_id_vacio() -> None:
    """id vacio lanza ValueError."""
    with pytest.raises(ValueError, match="id"):
        Order(id="", customer="Paul")


def test_order_customer_vacio() -> None:
    """customer vacio lanza ValueError."""
    with pytest.raises(ValueError, match="customer"):
        Order(id="ORD-001", customer="")


# ============================================
# Tests de Order (calculos derivados)
# ============================================


def test_order_subtotal() -> None:
    """subtotal suma los subtotales de los items."""
    order = Order(id="ORD-001", customer="Paul")
    order.add_item(OrderItem(name="Teclado", quantity=2, unit_price=25.0))
    order.add_item(OrderItem(name="Mouse", quantity=1, unit_price=15.5))
    assert order.subtotal == 65.5


def test_order_tax() -> None:
    """tax = subtotal * 0.16, redondeado a 2 decimales."""
    order = Order(id="ORD-001", customer="Paul")
    order.add_item(OrderItem(name="X", quantity=1, unit_price=100.0))
    assert order.tax == 16.0


def test_order_total() -> None:
    """total = subtotal + tax."""
    order = Order(id="ORD-001", customer="Paul")
    order.add_item(OrderItem(name="Teclado", quantity=2, unit_price=25.0))
    order.add_item(OrderItem(name="Mouse", quantity=1, unit_price=15.5))
    assert order.total == 75.98


def test_order_total_items() -> None:
    """total_items suma las quantities."""
    order = Order(id="ORD-001", customer="Paul")
    order.add_item(OrderItem(name="A", quantity=3, unit_price=1.0))
    order.add_item(OrderItem(name="B", quantity=2, unit_price=1.0))
    assert order.total_items == 5


# ============================================
# Tests de Order (comparaciones)
# ============================================


def test_order_eq() -> None:
    """Dos ordenes con mismos valores son iguales."""
    a = Order(id="ORD-001", customer="Paul")
    b = Order(id="ORD-001", customer="Paul")
    assert a == b


def test_order_lt_por_total() -> None:
    """o1 < o2 se compara por total."""
    o1 = Order(id="ORD-001", customer="Paul")
    o1.add_item(OrderItem(name="X", quantity=1, unit_price=10.0))

    o2 = Order(id="ORD-002", customer="Ana")
    o2.add_item(OrderItem(name="Y", quantity=1, unit_price=100.0))

    assert o1 < o2
    assert o2 > o1


def test_order_sorted_por_total() -> None:
    """sorted() ordena las ordenes por total."""
    o1 = Order(id="ORD-001", customer="Paul")
    o1.add_item(OrderItem(name="X", quantity=1, unit_price=50.0))

    o2 = Order(id="ORD-002", customer="Ana")
    o2.add_item(OrderItem(name="Y", quantity=1, unit_price=150.0))

    o3 = Order(id="ORD-003", customer="Luis")

    ordenadas = sorted([o2, o1, o3])
    assert [o.id for o in ordenadas] == ["ORD-003", "ORD-001", "ORD-002"]

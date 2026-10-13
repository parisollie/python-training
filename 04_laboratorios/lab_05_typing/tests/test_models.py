"""Tests para models.py (tipado avanzado)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (  # noqa: E402
    MAX_ITEMS_PER_ORDER,
    TAX_RATE,
    Order,
    OrderItem,
    order_from_json,
)

# ============================================
# Constantes
# ============================================


def test_constantes() -> None:
    """Constantes tienen los valores esperados."""
    assert TAX_RATE == 0.16
    assert MAX_ITEMS_PER_ORDER == 100


# ============================================
# OrderItem
# ============================================


def test_order_item_subtotal() -> None:
    """subtotal = quantity * unit_price."""
    item = OrderItem(name="Teclado", quantity=2, unit_price=25.0)
    assert item.subtotal == 50.0


def test_order_item_validaciones() -> None:
    """quantity < 1 y unit_price < 0 fallan."""
    with pytest.raises(ValueError, match="quantity"):
        OrderItem(name="X", quantity=0, unit_price=10.0)

    with pytest.raises(ValueError, match="unit_price"):
        OrderItem(name="X", quantity=1, unit_price=-5.0)


# ============================================
# Order
# ============================================


def test_order_status_default() -> None:
    """Status default es 'pending'."""
    order = Order(id="ORD-001", customer="Paul")
    assert order.status == "pending"


def test_order_change_status() -> None:
    """change_status actualiza el estado."""
    order = Order(id="ORD-001", customer="Paul")
    order.change_status("confirmed")
    assert order.status == "confirmed"

    order.change_status("shipped")
    # mypy no sigue mutaciones; comparamos via variable intermedia
    nuevo_estado: str = order.status
    assert nuevo_estado == "shipped"


def test_order_totales() -> None:
    """Subtotal, tax, total, total_items se calculan bien."""
    order = Order(id="ORD-001", customer="Paul")
    order.add_item(OrderItem(name="Teclado", quantity=2, unit_price=25.0))
    order.add_item(OrderItem(name="Mouse", quantity=1, unit_price=15.5))
    assert order.subtotal == 65.5
    assert order.tax == 10.48
    assert order.total == 75.98
    assert order.total_items == 3


def test_order_limite_items() -> None:
    """No se permiten mas de MAX_ITEMS_PER_ORDER items."""
    order = Order(id="ORD-001", customer="Paul")
    # Agregar MAX_ITEMS_PER_ORDER items
    for i in range(MAX_ITEMS_PER_ORDER):
        order.add_item(OrderItem(name=f"Item {i}", quantity=1, unit_price=1.0))

    # El siguiente debe fallar
    with pytest.raises(ValueError, match="limite"):
        order.add_item(OrderItem(name="Extra", quantity=1, unit_price=1.0))


# ============================================
# order_from_json (TypedDict)
# ============================================


def test_order_from_json() -> None:
    """Construye una Order desde un TypedDict valido."""
    from models import OrderJSON

    data: OrderJSON = {
        "id": "ORD-002",
        "customer": "Ana",
        "status": "pending",
        "items": [
            {"name": "Monitor", "quantity": 1, "unit_price": 130.0},
        ],
    }
    order = order_from_json(data)
    assert order.id == "ORD-002"
    assert order.customer == "Ana"
    assert order.status == "pending"
    assert order.total == 150.8


def test_order_from_json_status_invalido() -> None:
    """Status invalido en JSON lanza ValueError."""
    from models import OrderJSON

    data: OrderJSON = {
        "id": "ORD-003",
        "customer": "Luis",
        "status": "inventado",
        "items": [{"name": "X", "quantity": 1, "unit_price": 1.0}],
    }
    with pytest.raises(ValueError, match="status invalido"):
        order_from_json(data)

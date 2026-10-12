"""Tests para los schemas Pydantic y la conversion a/desde entidades."""

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parent.parent))

from schemas import OrderIn, order_from_in, order_to_out  # noqa: E402

# ============================================
# Tests de OrderIn (validacion)
# ============================================


def test_order_in_valido() -> None:
    """JSON valido se convierte en OrderIn."""
    order_in = OrderIn.model_validate(
        {
            "customer": "Paul",
            "items": [
                {"name": "Teclado", "quantity": 2, "unit_price": 25.0},
            ],
        }
    )
    assert order_in.customer == "Paul"
    assert len(order_in.items) == 1


def test_order_in_customer_vacio() -> None:
    """customer vacio falla validacion."""
    with pytest.raises(ValidationError):
        OrderIn.model_validate(
            {
                "customer": "",
                "items": [{"name": "X", "quantity": 1, "unit_price": 1.0}],
            }
        )


def test_order_in_customer_solo_espacios() -> None:
    """customer con solo espacios falla validacion."""
    with pytest.raises(ValidationError, match="customer"):
        OrderIn.model_validate(
            {"customer": "   ", "items": [{"name": "X", "quantity": 1, "unit_price": 1.0}]}
        )


def test_order_in_customer_hace_strip() -> None:
    """customer se limpia con strip."""
    order_in = OrderIn.model_validate(
        {"customer": "  Paul  ", "items": [{"name": "X", "quantity": 1, "unit_price": 1.0}]}
    )
    assert order_in.customer == "Paul"


def test_order_in_items_vacio() -> None:
    """items debe tener al menos 1 elemento."""
    with pytest.raises(ValidationError):
        OrderIn.model_validate({"customer": "Paul", "items": []})


def test_order_in_quantity_invalida() -> None:
    """quantity < 1 falla validacion."""
    with pytest.raises(ValidationError):
        OrderIn.model_validate(
            {"customer": "Paul", "items": [{"name": "X", "quantity": 0, "unit_price": 1.0}]}
        )


def test_order_in_unit_price_negativo() -> None:
    """unit_price < 0 falla validacion."""
    with pytest.raises(ValidationError):
        OrderIn.model_validate(
            {"customer": "Paul", "items": [{"name": "X", "quantity": 1, "unit_price": -1.0}]}
        )


# ============================================
# Tests de conversion OrderIn -> Order
# ============================================


def test_order_from_in() -> None:
    """OrderIn se convierte correctamente a Order."""
    order_in = OrderIn.model_validate(
        {
            "customer": "Paul",
            "items": [
                {"name": "Teclado", "quantity": 2, "unit_price": 25.0},
                {"name": "Mouse", "quantity": 1, "unit_price": 15.5},
            ],
        }
    )
    order = order_from_in(order_in, order_id="ORD-001")
    assert order.id == "ORD-001"
    assert order.customer == "Paul"
    assert len(order.items) == 2
    assert order.subtotal == 65.5
    assert order.total == 75.98


# ============================================
# Tests de conversion Order -> OrderOut
# ============================================


def test_order_to_out() -> None:
    """Order se convierte correctamente a OrderOut."""
    order_in = OrderIn.model_validate(
        {
            "customer": "Paul",
            "items": [
                {"name": "Teclado", "quantity": 2, "unit_price": 25.0},
            ],
        }
    )
    order = order_from_in(order_in, order_id="ORD-001")
    order_out = order_to_out(order)

    assert order_out.id == "ORD-001"
    assert order_out.customer == "Paul"
    assert order_out.subtotal == 50.0
    assert order_out.tax == 8.0
    assert order_out.total == 58.0
    assert order_out.total_items == 2
    assert order_out.items[0].subtotal == 50.0


def test_order_to_out_serializa_json() -> None:
    """OrderOut puede serializarse a JSON."""
    order_in = OrderIn.model_validate(
        {
            "customer": "Paul",
            "items": [{"name": "X", "quantity": 1, "unit_price": 100.0}],
        }
    )
    order = order_from_in(order_in, order_id="ORD-001")
    order_out = order_to_out(order)

    json_str = order_out.model_dump_json()
    assert '"id":"ORD-001"' in json_str
    assert '"total":116.0' in json_str


def test_flujo_completo() -> None:
    """JSON -> OrderIn -> Order -> OrderOut -> JSON."""
    json_entrada = {
        "customer": "Ana",
        "items": [
            {"name": "Monitor", "quantity": 1, "unit_price": 130.0},
            {"name": "Cable", "quantity": 2, "unit_price": 5.0},
        ],
    }

    order_in = OrderIn.model_validate(json_entrada)
    order = order_from_in(order_in, order_id="ORD-999")
    order_out = order_to_out(order)
    json_salida = order_out.model_dump_json()

    # Verificar montos
    assert order_out.subtotal == 140.0
    assert order_out.tax == 22.4
    assert order_out.total == 162.4
    assert order_out.total_items == 3

    # Verificar serializacion
    assert '"id":"ORD-999"' in json_salida
    assert '"customer":"Ana"' in json_salida

"""Tests para Cart (TDD)."""

import pytest
from cart import Cart, InMemoryUserService

# ============================================
# Subtotal
# ============================================


def test_cart_vacio(cart: Cart) -> None:
    """Carrito vacio: subtotal = 0."""
    assert cart.subtotal() == 0.0
    assert cart.total() == 0.0
    assert len(cart) == 0


def test_add_item(cart: Cart) -> None:
    """add_item agrega el precio."""
    cart.add_item(50.0)
    assert cart.subtotal() == 50.0
    assert len(cart) == 1


def test_subtotal_suma(cart: Cart) -> None:
    """subtotal es la suma de los precios."""
    cart.add_item(10.0)
    cart.add_item(20.5)
    cart.add_item(30.25)
    assert cart.subtotal() == 60.75


def test_precio_negativo_falla(cart: Cart) -> None:
    """Precio negativo lanza ValueError."""
    with pytest.raises(ValueError, match="negativo"):
        cart.add_item(-10.0)


# ============================================
# Descuento por monto
# ============================================


@pytest.mark.parametrize(
    "items,expected_discount",
    [
        ([50.0], 0.0),  # subtotal 50 -> 0%
        ([100.0], 0.0),  # subtotal 100 -> 0% (limite exacto)
        ([150.0], 15.0),  # subtotal 150 -> 10%
        ([500.0], 50.0),  # subtotal 500 -> 10% (limite exacto)
        ([501.0], 100.2),  # subtotal 501 -> 20%
        ([1000.0], 200.0),  # subtotal 1000 -> 20%
    ],
)
def test_descuento_por_monto(cart: Cart, items: list[float], expected_discount: float) -> None:
    """Descuento por monto: 0% <=100, 10% <=500, 20% >500."""
    for price in items:
        cart.add_item(price)
    assert cart.discount() == expected_discount


# ============================================
# Descuento premium
# ============================================


def test_premium_sin_monto(premium_cart: Cart) -> None:
    """Premium con subtotal bajo: solo 5%."""
    premium_cart.add_item(50.0)
    assert premium_cart.discount() == 2.5  # 50 * 0.05


def test_premium_con_monto(premium_cart: Cart) -> None:
    """Premium + monto: 10% + 5% = 15%."""
    premium_cart.add_item(200.0)
    assert premium_cart.discount() == 30.0  # 200 * 0.15


def test_premium_con_monto_alto(premium_cart: Cart) -> None:
    """Premium + monto alto: 20% + 5% = 25%."""
    premium_cart.add_item(1000.0)
    assert premium_cart.discount() == 250.0  # 1000 * 0.25


def test_no_premium(cart: Cart) -> None:
    """Usuario no premium: sin descuento extra."""
    service = InMemoryUserService(premium_users={"user-99"})
    cart_with_service = Cart(user_id="user-1", user_service=service)
    cart_with_service.add_item(200.0)
    assert cart_with_service.discount() == 20.0  # solo 10%


def test_sin_user_service(cart: Cart) -> None:
    """Sin user_service no consulta premium."""
    cart.add_item(200.0)
    assert cart.discount() == 20.0


# ============================================
# Total
# ============================================


def test_total_basico(cart: Cart) -> None:
    """Total = subtotal - descuento."""
    cart.add_item(50.0)
    cart.add_item(100.0)
    assert cart.subtotal() == 150.0
    assert cart.discount() == 15.0
    assert cart.total() == 135.0


def test_total_premium(premium_cart: Cart) -> None:
    """Total con premium."""
    premium_cart.add_item(200.0)
    assert premium_cart.total() == 170.0


# ============================================
# Clear
# ============================================


def test_clear(cart: Cart) -> None:
    """clear vacia el carrito."""
    cart.add_item(10.0)
    cart.add_item(20.0)
    cart.clear()
    assert cart.subtotal() == 0.0
    assert len(cart) == 0

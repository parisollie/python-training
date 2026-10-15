"""Tests del patron Strategy."""

import pytest
from strategy import (
    Cart,
    NormalPricing,
    PremiumPricing,
    SeasonalPricing,
    VipPricing,
)

# ============================================
# Cart
# ============================================


def test_cart_vacio() -> None:
    """Carrito vacio subtotal 0."""
    cart = Cart()
    assert cart.subtotal() == 0.0
    assert cart.total() == 0.0


def test_cart_add_item() -> None:
    """add_item agrega precios."""
    cart = Cart()
    cart.add_item(10.0)
    cart.add_item(20.0)
    assert cart.subtotal() == 30.0


def test_cart_precio_negativo() -> None:
    """Precio negativo falla."""
    cart = Cart()
    with pytest.raises(ValueError, match="Precio negativo"):
        cart.add_item(-10.0)


# ============================================
# Strategies
# ============================================


@pytest.mark.parametrize(
    "strategy,subtotal,expected",
    [
        (NormalPricing(), 100.0, 100.0),
        (PremiumPricing(), 100.0, 90.0),
        (VipPricing(), 100.0, 80.0),
        (SeasonalPricing(), 50.0, 47.5),  # 5% off
        (SeasonalPricing(), 200.0, 170.0),  # 15% off
        (SeasonalPricing(), 1000.0, 750.0),  # 25% off
    ],
)
def test_strategy_calculate(strategy: object, subtotal: float, expected: float) -> None:
    """Cada Strategy calcula el descuento correcto."""
    assert strategy.calculate(subtotal) == expected  # type: ignore[attr-defined]


# ============================================
# Cambio de Strategy en runtime
# ============================================


def test_cart_cambia_strategy() -> None:
    """El carrito puede cambiar de Strategy en runtime."""
    cart = Cart()
    cart.add_item(100.0)

    assert cart.total() == 100.0  # Normal (default)

    cart.change_pricing(PremiumPricing())
    assert cart.total() == 90.0

    cart.change_pricing(VipPricing())
    assert cart.total() == 80.0


def test_cart_con_strategy_inicial() -> None:
    """Se puede pasar la Strategy al constructor."""
    cart = Cart(pricing=VipPricing())
    cart.add_item(100.0)
    assert cart.total() == 80.0


# ============================================
# LSP: cualquier Strategy funciona igual
# ============================================


@pytest.mark.parametrize(
    "pricing",
    [NormalPricing(), PremiumPricing(), VipPricing(), SeasonalPricing()],
)
def test_lsp_todas_las_strategies(pricing: object) -> None:
    """Todas las Strategies devuelven float >= 0."""
    result = pricing.calculate(100.0)  # type: ignore[attr-defined]
    assert isinstance(result, float)
    assert result >= 0

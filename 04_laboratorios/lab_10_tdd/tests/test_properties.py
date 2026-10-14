"""Tests de propiedades con Hypothesis.

Property-based testing:
- En lugar de probar casos especificos, se describen INVARIANTES
- Hypothesis genera cientos de casos aleatorios y busca contraejemplos
- Si encuentra un caso que viola la propiedad, lo "encoge" al minimo
"""

from cart import Cart, InMemoryUserService
from hypothesis import given, settings
from hypothesis import strategies as st

# Estrategia: precios positivos razonables
prices = st.lists(
    st.floats(min_value=0.01, max_value=10_000.0, allow_nan=False, allow_infinity=False),
    min_size=0,
    max_size=50,
)


# ============================================
# Invariantes del subtotal
# ============================================


@given(prices)
@settings(max_examples=100)
def test_subtotal_nunca_negativo(items: list[float]) -> None:
    """El subtotal siempre es >= 0 (invariante)."""
    cart = Cart()
    for price in items:
        cart.add_item(price)
    assert cart.subtotal() >= 0


@given(prices)
@settings(max_examples=100)
def test_subtotal_es_suma(items: list[float]) -> None:
    """El subtotal es la suma de los precios (dentro del redondeo)."""
    cart = Cart()
    for price in items:
        cart.add_item(price)
    assert abs(cart.subtotal() - sum(items)) < 0.01


@given(st.floats(min_value=0.01, max_value=10_000.0, allow_nan=False))
@settings(max_examples=100)
def test_un_item_solo(price: float) -> None:
    """Con un solo item, subtotal == precio."""
    cart = Cart()
    cart.add_item(price)
    assert abs(cart.subtotal() - price) < 0.01


# ============================================
# Invariantes del descuento
# ============================================


@given(prices)
@settings(max_examples=100)
def test_descuento_nunca_mayor_que_subtotal(items: list[float]) -> None:
    """El descuento nunca puede ser mayor que el subtotal."""
    cart = Cart()
    for price in items:
        cart.add_item(price)
    assert cart.discount() <= cart.subtotal()


@given(prices)
@settings(max_examples=100)
def test_total_nunca_negativo(items: list[float]) -> None:
    """El total siempre es >= 0."""
    cart = Cart()
    for price in items:
        cart.add_item(price)
    assert cart.total() >= 0


@given(prices)
@settings(max_examples=100)
def test_total_menor_o_igual_subtotal(items: list[float]) -> None:
    """Total <= subtotal (porque descuento >= 0)."""
    cart = Cart()
    for price in items:
        cart.add_item(price)
    assert cart.total() <= cart.subtotal() + 0.001


# ============================================
# Invariantes del premium
# ============================================


@given(prices)
@settings(max_examples=50)
def test_premium_descuento_mayor_o_igual(items: list[float]) -> None:
    """Un usuario premium siempre tiene descuento >= que uno normal."""
    normal = Cart()
    premium = Cart(
        user_id="user-1",
        user_service=InMemoryUserService(premium_users={"user-1"}),
    )
    for price in items:
        normal.add_item(price)
        premium.add_item(price)

    assert premium.discount() >= normal.discount() - 0.001


# ============================================
# Idempotencia
# ============================================


@given(prices)
@settings(max_examples=50)
def test_subtotal_idempotente(items: list[float]) -> None:
    """Llamar subtotal() multiples veces devuelve lo mismo."""
    cart = Cart()
    for price in items:
        cart.add_item(price)
    assert cart.subtotal() == cart.subtotal() == cart.subtotal()

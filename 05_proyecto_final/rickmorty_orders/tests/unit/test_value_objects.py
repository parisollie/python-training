"""Tests de Value Objects (dominio puro, sin dependencias externas)."""

from dataclasses import FrozenInstanceError

import pytest
from rickmorty_orders.domain.value_objects import (
    CharacterId,
    Email,
    Money,
    OrderId,
)

# ============================================
# OrderId
# ============================================


def test_order_id_generate() -> None:
    """generate() crea un UUID unico."""
    oid1 = OrderId.generate()
    oid2 = OrderId.generate()
    assert oid1 != oid2
    assert len(oid1.value) == 36


def test_order_id_igualdad_por_valor() -> None:
    """OrderId compara por valor."""
    assert OrderId("abc") == OrderId("abc")
    assert OrderId("abc") != OrderId("xyz")


def test_order_id_str() -> None:
    """str devuelve el value."""
    assert str(OrderId("test-123")) == "test-123"


def test_order_id_inmutable() -> None:
    """OrderId es inmutable."""
    oid = OrderId("abc")
    with pytest.raises(FrozenInstanceError):
        oid.value = "xyz"  # type: ignore[misc]


# ============================================
# CharacterId
# ============================================


def test_character_id_valido() -> None:
    """CharacterId con id positivo."""
    cid = CharacterId(1)
    assert cid.value == 1


def test_character_id_cero_falla() -> None:
    """CharacterId(0) lanza."""
    with pytest.raises(ValueError, match=">= 1"):
        CharacterId(0)


def test_character_id_negativo_falla() -> None:
    """CharacterId negativo lanza."""
    with pytest.raises(ValueError, match=">= 1"):
        CharacterId(-5)


def test_character_id_igualdad() -> None:
    """Igualdad por valor."""
    assert CharacterId(1) == CharacterId(1)
    assert CharacterId(1) != CharacterId(2)


def test_character_id_str() -> None:
    """str devuelve el numero."""
    assert str(CharacterId(42)) == "42"


# ============================================
# Money
# ============================================


def test_money_creacion() -> None:
    """Money con amount y currency."""
    m = Money(100.0)
    assert m.amount == 100.0
    assert m.currency == "USD"


def test_money_negativo_falla() -> None:
    """Money negativo lanza."""
    with pytest.raises(ValueError, match="negativo"):
        Money(-1.0)


def test_money_currency_invalida_falla() -> None:
    """Currency debe tener 3 letras."""
    with pytest.raises(ValueError, match="3 letras"):
        Money(100.0, currency="US")


def test_money_suma() -> None:
    """Suma de Money del mismo tipo."""
    result = Money(100.0) + Money(50.5)
    assert result.amount == 150.5
    assert result.currency == "USD"


def test_money_suma_currency_distinta_falla() -> None:
    """No se pueden sumar monedas distintas."""
    with pytest.raises(ValueError, match="No se pueden sumar"):
        Money(100.0, "USD") + Money(50.0, "EUR")


def test_money_resta() -> None:
    """Resta de Money."""
    result = Money(100.0) - Money(30.0)
    assert result.amount == 70.0


def test_money_multiplicar() -> None:
    """Multiplicar Money por escalar."""
    assert (Money(100.0) * 2).amount == 200.0
    assert (Money(100.0) * 0.5).amount == 50.0


def test_money_multiplicar_negativo_falla() -> None:
    """Factor negativo lanza."""
    with pytest.raises(ValueError, match="Factor"):
        Money(100.0) * -1


def test_money_igualdad() -> None:
    """Igualdad por valor."""
    assert Money(100.0) == Money(100.0)
    assert Money(100.0) != Money(100.01)
    assert Money(100.0, "USD") != Money(100.0, "EUR")


def test_money_inmutable() -> None:
    """Money es inmutable."""
    m = Money(100.0)
    with pytest.raises(FrozenInstanceError):
        m.amount = 200.0  # type: ignore[misc]


def test_money_str() -> None:
    """Formato legible."""
    assert str(Money(100.5)) == "100.50 USD"
    assert str(Money(100.5, "EUR")) == "100.50 EUR"


# ============================================
# Email
# ============================================


def test_email_valido() -> None:
    """Email valido."""
    e = Email("paul@example.com")
    assert e.value == "paul@example.com"


def test_email_normaliza() -> None:
    """strip + lowercase."""
    e = Email("  PAUL@Example.COM  ")
    assert e.value == "paul@example.com"


def test_email_invalido_sin_arroba() -> None:
    """Email sin @ lanza."""
    with pytest.raises(ValueError, match="Email invalido"):
        Email("no-es-email")


def test_email_invalido_sin_dominio() -> None:
    """Email sin dominio valido lanza."""
    with pytest.raises(ValueError):
        Email("a@b")


def test_email_invalido_sin_usuario() -> None:
    """Email sin usuario lanza."""
    with pytest.raises(ValueError):
        Email("@example.com")


def test_email_invalido_dominio_sin_punto() -> None:
    """Dominio sin punto TLD lanza."""
    with pytest.raises(ValueError):
        Email("user@localhost")


def test_email_igualdad_normalizada() -> None:
    """Igualdad tras normalizar."""
    assert Email("PAUL@example.com") == Email("paul@EXAMPLE.com")


def test_email_inmutable() -> None:
    """Email es inmutable."""
    e = Email("a@b.com")
    with pytest.raises(FrozenInstanceError):
        e.value = "otro@b.com"  # type: ignore[misc]

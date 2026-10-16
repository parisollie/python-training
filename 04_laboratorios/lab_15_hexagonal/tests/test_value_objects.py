"""Tests de Value Objects (dominio puro, sin mocks)."""

import pytest
from domain.value_objects import Email, Money, OrderId

# ============================================
# Money
# ============================================


def test_money_creacion() -> None:
    """Money con amount y currency."""
    m = Money(100.0)
    assert m.amount == 100.0
    assert m.currency == "USD"


def test_money_negativo_falla() -> None:
    """Money negativo lanza ValueError."""
    with pytest.raises(ValueError, match="negativo"):
        Money(-1.0)


def test_money_currency_invalida() -> None:
    """Currency debe tener 3 letras."""
    with pytest.raises(ValueError, match="3 letras"):
        Money(100.0, currency="US")


def test_money_suma() -> None:
    """Suma de Money del mismo tipo."""
    result = Money(100.0) + Money(50.0)
    assert result.amount == 150.0
    assert result.currency == "USD"


def test_money_suma_currency_distinta_falla() -> None:
    """No se pueden sumar monedas distintas."""
    with pytest.raises(ValueError, match="No se pueden sumar"):
        Money(100.0, "USD") + Money(50.0, "EUR")


def test_money_multiplicar() -> None:
    """Multiplicar por escalar."""
    assert (Money(100.0) * 2).amount == 200.0
    assert (Money(100.0) * 0.5).amount == 50.0


def test_money_multiplicar_negativo_falla() -> None:
    """Multiplicar por negativo lanza."""
    with pytest.raises(ValueError, match="Factor"):
        Money(100.0) * -1


def test_money_igualdad_por_valor() -> None:
    """Dos Money con mismo valor son iguales."""
    assert Money(100.0) == Money(100.0)
    assert Money(100.0) != Money(100.01)


def test_money_inmutable() -> None:
    """Money es inmutable (frozen)."""
    from dataclasses import FrozenInstanceError

    m = Money(100.0)
    with pytest.raises(FrozenInstanceError):
        m.amount = 200.0  # type: ignore[misc]


def test_money_str() -> None:
    """Formato legible."""
    assert str(Money(100.5)) == "100.50 USD"


# ============================================
# Email
# ============================================


def test_email_ok() -> None:
    """Email valido."""
    e = Email("paul@example.com")
    assert e.value == "paul@example.com"


def test_email_normaliza() -> None:
    """strip + lowercase."""
    e = Email("  PAUL@Example.COM  ")
    assert e.value == "paul@example.com"


def test_email_invalido() -> None:
    """Email sin @ o dominio lanza."""
    with pytest.raises(ValueError, match="Email invalido"):
        Email("no-es-email")

    with pytest.raises(ValueError):
        Email("a@b")

    with pytest.raises(ValueError):
        Email("@example.com")


def test_email_igualdad_por_valor() -> None:
    """Igualdad por valor (normalizado)."""
    assert Email("PAUL@example.com") == Email("paul@EXAMPLE.com")


# ============================================
# OrderId
# ============================================


def test_order_id_generate() -> None:
    """generate crea un id unico."""
    oid1 = OrderId.generate()
    oid2 = OrderId.generate()
    assert oid1 != oid2
    assert len(oid1.value) == 36  # UUID4


def test_order_id_igualdad_por_valor() -> None:
    """Igualdad por valor."""
    assert OrderId("abc") == OrderId("abc")
    assert OrderId("abc") != OrderId("xyz")


def test_order_id_str() -> None:
    """str devuelve el value."""
    oid = OrderId("abc-123")
    assert str(oid) == "abc-123"

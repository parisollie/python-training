"""Tests del patron Adapter."""

from adapter import (
    CheckoutService,
    FailingPaymentAPI,
    ModernPaymentAdapter,
    ModernPaymentAPI,
    OldPaymentAdapter,
    OldPaymentAPI,
)

# ============================================
# OldPaymentAdapter
# ============================================


def test_old_adapter_exito() -> None:
    """Convierte float->cents y dict->bool."""
    api = OldPaymentAPI()
    adapter = OldPaymentAdapter(api)

    assert adapter.pay(10.50, "user-1") is True
    assert api.calls == [{"cents": 1050, "customer": "user-1"}]


def test_old_adapter_falla() -> None:
    """Detecta status error."""
    adapter = OldPaymentAdapter(FailingPaymentAPI())
    assert adapter.pay(10.0, "user-1") is False


def test_old_adapter_redondeo() -> None:
    """Convierte correctamente decimales a centavos."""
    api = OldPaymentAPI()
    adapter = OldPaymentAdapter(api)

    adapter.pay(9.999, "u")
    assert api.calls[0]["cents"] == 1000  # redondea

    adapter.pay(0.01, "u")
    assert api.calls[1]["cents"] == 1


# ============================================
# ModernPaymentAdapter
# ============================================


def test_modern_adapter_exito() -> None:
    """Delega y captura sin excepcion."""
    api = ModernPaymentAPI()
    adapter = ModernPaymentAdapter(api)

    assert adapter.pay(20.0, "user-2") is True
    assert api.calls == [(20.0, "user-2")]


def test_modern_adapter_error() -> None:
    """Convierte exception -> False."""
    adapter = ModernPaymentAdapter(ModernPaymentAPI())
    assert adapter.pay(-1.0, "user") is False


# ============================================
# CheckoutService (agnostico)
# ============================================


def test_checkout_con_old_adapter() -> None:
    """CheckoutService acepta OldPaymentAdapter."""
    service = CheckoutService(OldPaymentAdapter(OldPaymentAPI()))
    result = service.checkout(10.0, "u1")
    assert "exitoso" in result


def test_checkout_con_modern_adapter() -> None:
    """CheckoutService acepta ModernPaymentAdapter."""
    service = CheckoutService(ModernPaymentAdapter(ModernPaymentAPI()))
    result = service.checkout(20.0, "u2")
    assert "exitoso" in result


def test_checkout_fallido() -> None:
    """CheckoutService reporta pago fallido."""
    service = CheckoutService(OldPaymentAdapter(FailingPaymentAPI()))
    result = service.checkout(5.0, "u")
    assert "fallido" in result


# ============================================
# LSP: cualquier Adapter es equivalente
# ============================================


def test_lsp_adapters_equivalentes() -> None:
    """Todos los adapters cumplen el mismo Protocol."""
    old = OldPaymentAdapter(OldPaymentAPI())
    modern = ModernPaymentAdapter(ModernPaymentAPI())

    for adapter in (old, modern):
        result = adapter.pay(10.0, "user")
        assert isinstance(result, bool)
        assert result is True

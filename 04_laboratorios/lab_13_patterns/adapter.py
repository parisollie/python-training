"""Patron Adapter: adaptar APIs externas a una interfaz interna.

Demuestra:
- Protocol: define la interfaz que el dominio espera
- Adapter: traduce entre dos interfaces incompatibles
- Sin acoplamiento: el dominio no conoce la API externa
"""

from typing import Protocol

# ============================================
# Interfaz que el dominio espera
# ============================================


class PaymentGateway(Protocol):
    """Interfaz que el dominio espera para cobrar."""

    def pay(self, amount: float, user_id: str) -> bool:
        """Cobra el monto al usuario. Devuelve True si exito."""
        ...


# ============================================
# APIs externas (con interfaces distintas)
# ============================================


class OldPaymentAPI:
    """API vieja que cobra en centavos y devuelve un dict."""

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def make_payment(self, cents: int, customer: str) -> dict[str, object]:
        """Cobra en centavos. Devuelve {'status': 'ok'|'error', 'cents': int}."""
        self.calls.append({"cents": cents, "customer": customer})
        return {"status": "ok", "cents": cents}


class ModernPaymentAPI:
    """API moderna con metodo process() que lanza excepciones."""

    def __init__(self) -> None:
        self.calls: list[tuple[float, str]] = []

    def process(self, amount: float, user: str) -> None:
        """Procesa el pago. Lanza si falla."""
        if amount <= 0:
            raise ValueError("Monto invalido")
        self.calls.append((amount, user))


class FailingPaymentAPI(OldPaymentAPI):
    """API que siempre falla (para tests).

    Hereda de OldPaymentAPI para cumplir con el tipo (LSP).
    """

    def make_payment(self, cents: int, customer: str) -> dict[str, object]:
        """Devuelve status error siempre."""
        return {"status": "error", "cents": cents}


# ============================================
# Adapters
# ============================================


class OldPaymentAdapter:
    """Adapta OldPaymentAPI a la interfaz PaymentGateway.

    Traduce:
    - float (dolares) -> int (centavos)
    - dict -> bool
    """

    def __init__(self, api: OldPaymentAPI) -> None:
        self._api = api

    def pay(self, amount: float, user_id: str) -> bool:
        """Convierte y delega a la API vieja."""
        cents = int(round(amount * 100))
        result = self._api.make_payment(cents, user_id)
        return result.get("status") == "ok"


class ModernPaymentAdapter:
    """Adapta ModernPaymentAPI a la interfaz PaymentGateway.

    Traduce:
    - manejo de excepciones -> bool
    """

    def __init__(self, api: ModernPaymentAPI) -> None:
        self._api = api

    def pay(self, amount: float, user_id: str) -> bool:
        """Delega y captura excepciones."""
        try:
            self._api.process(amount, user_id)
            return True
        except (ValueError, RuntimeError):
            return False


# ============================================
# Servicio que usa la interfaz (sin conocer adapters)
# ============================================


class CheckoutService:
    """Servicio de checkout que usa cualquier PaymentGateway."""

    def __init__(self, gateway: PaymentGateway) -> None:
        self._gateway = gateway

    def checkout(self, amount: float, user_id: str) -> str:
        """Cobra y devuelve un mensaje."""
        if self._gateway.pay(amount, user_id):
            return f"Pago exitoso de ${amount} para {user_id}"
        return f"Pago fallido de ${amount} para {user_id}"

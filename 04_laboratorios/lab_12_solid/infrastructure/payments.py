"""Implementaciones de PaymentProcessor."""


class StripePayment:
    """Simulacion de procesador de pago real (Stripe).

    En produccion llamaria a la API de Stripe.
    Aqui registra los cobros para poder testear.
    """

    def __init__(self, api_key: str = "sk_test_fake") -> None:
        self.api_key = api_key
        self.charges: list[dict[str, object]] = []

    def charge(self, amount: float, user_id: str) -> bool:
        """Registra un cobro exitoso."""
        self.charges.append({"amount": amount, "user_id": user_id, "status": "ok"})
        return True


class FakePayment:
    """Procesador de pago falso (tests).

    Se puede configurar para fallar (util para testear error handling).
    """

    def __init__(self, should_succeed: bool = True) -> None:
        self.should_succeed = should_succeed
        self.calls: list[tuple[float, str]] = []

    def charge(self, amount: float, user_id: str) -> bool:
        """Devuelve el resultado configurado."""
        self.calls.append((amount, user_id))
        return self.should_succeed

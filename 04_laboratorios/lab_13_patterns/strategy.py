"""Patron Strategy: calculadoras de precio intercambiables.

Demuestra:
- Strategy: distintos algoritmos de precio con la misma interfaz
- Protocol: define el contrato
- Sin herencia: cada Strategy es independiente
"""

from typing import Protocol


class PricingStrategy(Protocol):
    """Interfaz del algoritmo de precio."""

    def calculate(self, subtotal: float) -> float:
        """Calcula el total a partir del subtotal.

        Args:
            subtotal: Suma de los precios sin descuento.

        Returns:
            Precio final con descuento aplicado.
        """
        ...


class NormalPricing:
    """Sin descuento (cliente comun)."""

    def calculate(self, subtotal: float) -> float:
        """Devuelve el subtotal sin cambios."""
        return round(subtotal, 2)


class PremiumPricing:
    """10% de descuento (cliente premium)."""

    DISCOUNT = 0.10

    def calculate(self, subtotal: float) -> float:
        """Aplica 10% de descuento."""
        return round(subtotal * (1 - self.DISCOUNT), 2)


class VipPricing:
    """20% de descuento (cliente VIP)."""

    DISCOUNT = 0.20

    def calculate(self, subtotal: float) -> float:
        """Aplica 20% de descuento."""
        return round(subtotal * (1 - self.DISCOUNT), 2)


class SeasonalPricing:
    """Descuento escalonado en rebajas.

    - 5% si subtotal <= 100
    - 15% si 100 < subtotal <= 500
    - 25% si subtotal > 500
    """

    def calculate(self, subtotal: float) -> float:
        """Aplica descuento escalonado."""
        if subtotal > 500:
            discount = 0.25
        elif subtotal > 100:
            discount = 0.15
        else:
            discount = 0.05
        return round(subtotal * (1 - discount), 2)


# ============================================
# Context: usa una Strategy
# ============================================


class Cart:
    """Carrito que usa una PricingStrategy para calcular el total."""

    def __init__(self, pricing: PricingStrategy | None = None) -> None:
        self.items: list[float] = []
        self.pricing: PricingStrategy = pricing or NormalPricing()

    def add_item(self, price: float) -> None:
        """Agrega un item al carrito."""
        if price < 0:
            raise ValueError(f"Precio negativo: {price}")
        self.items.append(price)

    def subtotal(self) -> float:
        """Suma de precios."""
        return round(sum(self.items), 2)

    def total(self) -> float:
        """Precio final segun la Strategy activa."""
        return self.pricing.calculate(self.subtotal())

    def change_pricing(self, pricing: PricingStrategy) -> None:
        """Cambia la Strategy en runtime."""
        self.pricing = pricing

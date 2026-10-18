"""Errores de dominio.

Los errores de dominio:
- Representan violaciones de reglas de negocio
- NO conocen HTTP, SQL ni frameworks
- Se lanzan desde el dominio y la aplicación
- La infraestructura los traduce a respuestas HTTP
"""


class DomainError(Exception):
    """Base de todos los errores de dominio."""


class InvalidOrderError(DomainError):
    """La orden es invalida (regla de negocio)."""


class InvalidStatusTransitionError(DomainError):
    """Transicion de estado no permitida."""


class OrderNotFoundError(DomainError):
    """La orden no existe."""


class CharacterNotFoundError(DomainError):
    """El personaje no existe en la API externa."""


class CharacterServiceError(DomainError):
    """La API externa de Rick and Morty fallo."""


class PaymentFailedError(DomainError):
    """El cobro de la orden fallo."""

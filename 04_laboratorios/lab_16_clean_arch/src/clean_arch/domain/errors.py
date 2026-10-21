"""Errores de dominio del lab 16."""


class DomainError(Exception):
    """Base de todos los errores de dominio."""


class InvalidOrderError(DomainError):
    """La orden es invalida (regla de negocio)."""


class InvalidStatusTransitionError(DomainError):
    """Transicion de estado no permitida."""


class OrderNotFoundError(DomainError):
    """La orden no existe."""

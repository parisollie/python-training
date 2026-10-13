"""Repositorio de ordenes usando Protocol.

Demuestra:
- Protocol: interfaces estructurales (duck typing con tipos)
- Polimorfismo sin herencia
- Inversion de dependencias
"""

from typing import Protocol

from models import Order


class OrderRepository(Protocol):
    """Interfaz (puerto) para repositorios de ordenes.

    Cualquier clase que tenga estos metodos cumple el Protocol,
    sin necesidad de heredar de una clase base.
    """

    def save(self, order: Order) -> None:
        """Guarda o actualiza una orden."""
        ...

    def get(self, order_id: str) -> Order | None:
        """Obtiene una orden por id, o None si no existe."""
        ...

    def list_all(self) -> list[Order]:
        """Devuelve todas las ordenes."""
        ...

    def delete(self, order_id: str) -> bool:
        """Elimina una orden. Devuelve True si existia."""
        ...


class InMemoryOrderRepository:
    """Implementacion en memoria del OrderRepository.

    Cumple el Protocol sin heredar de nada.
    """

    def __init__(self) -> None:
        self._store: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        """Guarda la orden en memoria."""
        self._store[order.id] = order

    def get(self, order_id: str) -> Order | None:
        """Obtiene una orden por id."""
        return self._store.get(order_id)

    def list_all(self) -> list[Order]:
        """Lista todas las ordenes."""
        return list(self._store.values())

    def delete(self, order_id: str) -> bool:
        """Elimina una orden. Devuelve True si existia."""
        return self._store.pop(order_id, None) is not None


# ============================================
# Servicio que usa el repositorio
# ============================================


class OrderService:
    """Servicio de ordenes que depende del Protocol, no de la implementacion.

    Esto permite cambiar la implementacion (memoria, SQL, API) sin
    modificar el servicio.
    """

    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def create(self, order: Order) -> None:
        """Crea una nueva orden."""
        if self._repository.get(order.id) is not None:
            raise ValueError(f"Ya existe una orden con id {order.id}")
        self._repository.save(order)

    def get(self, order_id: str) -> Order | None:
        """Obtiene una orden por id."""
        return self._repository.get(order_id)

    def count(self) -> int:
        """Cuenta cuantas ordenes hay."""
        return len(self._repository.list_all())

    def delete(self, order_id: str) -> bool:
        """Elimina una orden."""
        return self._repository.delete(order_id)

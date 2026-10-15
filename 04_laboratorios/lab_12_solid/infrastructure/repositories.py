"""Implementaciones concretas del OrderRepository.

- InMemoryOrderRepository: para tests y desarrollo
- SQLOrderRepository: simulacion simple (dict compartido como "DB")

Ambas cumplen el Protocol sin heredar de nada.
"""

from uuid import uuid4

from domain.order import Order


class InMemoryOrderRepository:
    """Repositorio en memoria que cumple OrderRepository (Protocol).

    Cumple el contrato sin heredar de una clase base.
    """

    def __init__(self) -> None:
        self._store: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        """Guarda la orden (asigna id si no tiene)."""
        if order.id is None:
            order.id = str(uuid4())
        self._store[order.id] = order

    def get(self, order_id: str) -> Order | None:
        """Obtiene una orden por id."""
        return self._store.get(order_id)

    def list_by_user(self, user_id: str) -> list[Order]:
        """Lista ordenes del usuario."""
        return [o for o in self._store.values() if o.user_id == user_id]


class SQLOrderRepository:
    """Simulacion de un repositorio SQL.

    En produccion usaria SQLAlchemy, pero para el laboratorio simulamos
    con un dict de clase (compartido entre instancias).
    """

    _shared_db: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        """Guarda en la 'DB' compartida."""
        if order.id is None:
            order.id = str(uuid4())
        self._shared_db[order.id] = order

    def get(self, order_id: str) -> Order | None:
        """Obtiene de la 'DB' compartida."""
        return self._shared_db.get(order_id)

    def list_by_user(self, user_id: str) -> list[Order]:
        """Lista de la 'DB' compartida."""
        return [o for o in self._shared_db.values() if o.user_id == user_id]

    @classmethod
    def clear(cls) -> None:
        """Limpia la 'DB' (util para tests aislados)."""
        cls._shared_db.clear()

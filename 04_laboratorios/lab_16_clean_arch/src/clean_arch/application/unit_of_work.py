"""Unit of Work del lab 16.

El Unit of Work (UoW) coordina:
- Repositorios (orders)
- Transacciones (commit/rollback)
- Eventos pendientes (que se publican al hacer commit)

Patron: el caso de uso envuelve la operacion en `with uow:`.
Si todo va bien -> commit (persiste + publica eventos).
Si algo falla -> rollback (descarta todo).
"""

from types import TracebackType
from typing import Protocol, Self

from clean_arch.domain.events import DomainEvent
from clean_arch.domain.ports import OrderRepository


class UnitOfWork(Protocol):
    """Puerto del Unit of Work."""

    orders: OrderRepository
    events: list[DomainEvent]

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def collect_event(self, event: DomainEvent) -> None:
        """Registra un evento para publicar al hacer commit."""
        ...

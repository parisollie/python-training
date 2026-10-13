"""Tests para repository.py (Protocol y OrderService)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Order, OrderItem  # noqa: E402
from repository import InMemoryOrderRepository, OrderService  # noqa: E402

# ============================================
# InMemoryOrderRepository
# ============================================


def test_repo_save_y_get() -> None:
    """save guarda y get recupera."""
    repo = InMemoryOrderRepository()
    order = Order(id="ORD-001", customer="Paul")
    repo.save(order)
    assert repo.get("ORD-001") is order


def test_repo_get_inexistente() -> None:
    """get de id inexistente devuelve None."""
    repo = InMemoryOrderRepository()
    assert repo.get("NO-EXISTE") is None


def test_repo_list_all_vacio() -> None:
    """list_all en repo vacio devuelve []."""
    repo = InMemoryOrderRepository()
    assert repo.list_all() == []


def test_repo_list_all() -> None:
    """list_all devuelve todas las ordenes guardadas."""
    repo = InMemoryOrderRepository()
    repo.save(Order(id="ORD-001", customer="Paul"))
    repo.save(Order(id="ORD-002", customer="Ana"))
    assert len(repo.list_all()) == 2


def test_repo_delete_existente() -> None:
    """delete devuelve True si la orden existia."""
    repo = InMemoryOrderRepository()
    repo.save(Order(id="ORD-001", customer="Paul"))
    assert repo.delete("ORD-001") is True
    assert repo.get("ORD-001") is None


def test_repo_delete_inexistente() -> None:
    """delete devuelve False si no existia."""
    repo = InMemoryOrderRepository()
    assert repo.delete("NO-EXISTE") is False


def test_repo_save_actualiza() -> None:
    """save sobre el mismo id actualiza (no duplica)."""
    repo = InMemoryOrderRepository()
    o1 = Order(id="ORD-001", customer="Paul")
    repo.save(o1)

    o1_updated = Order(id="ORD-001", customer="Paul Actualizado")
    repo.save(o1_updated)

    assert len(repo.list_all()) == 1
    assert repo.get("ORD-001") is o1_updated


# ============================================
# OrderService
# ============================================


def test_service_create() -> None:
    """create guarda la orden."""
    service = OrderService(InMemoryOrderRepository())
    order = Order(id="ORD-001", customer="Paul")
    service.create(order)
    assert service.get("ORD-001") is order


def test_service_create_duplicado() -> None:
    """create con id existente lanza ValueError."""
    service = OrderService(InMemoryOrderRepository())
    service.create(Order(id="ORD-001", customer="Paul"))

    with pytest.raises(ValueError, match="Ya existe"):
        service.create(Order(id="ORD-001", customer="Otro"))


def test_service_count() -> None:
    """count devuelve cuantas ordenes hay."""
    service = OrderService(InMemoryOrderRepository())
    assert service.count() == 0
    service.create(Order(id="ORD-001", customer="Paul"))
    service.create(Order(id="ORD-002", customer="Ana"))
    assert service.count() == 2


def test_service_delete() -> None:
    """delete devuelve True y reduce count."""
    service = OrderService(InMemoryOrderRepository())
    service.create(Order(id="ORD-001", customer="Paul"))
    assert service.delete("ORD-001") is True
    assert service.count() == 0


def test_service_get_inexistente() -> None:
    """get de id inexistente devuelve None."""
    service = OrderService(InMemoryOrderRepository())
    assert service.get("NO-EXISTE") is None


def test_service_polimorfismo() -> None:
    """OrderService acepta cualquier implementacion del Protocol.

    Aqui usamos InMemoryOrderRepository, pero podria ser cualquier clase
    que cumpla el Protocol (SQL, API, mock, etc.).
    """

    # Mock minimo que cumple el Protocol
    class FakeRepo:
        def __init__(self) -> None:
            self._data: dict[str, Order] = {}

        def save(self, order: Order) -> None:
            self._data[order.id] = order

        def get(self, order_id: str) -> Order | None:
            return self._data.get(order_id)

        def list_all(self) -> list[Order]:
            return list(self._data.values())

        def delete(self, order_id: str) -> bool:
            return self._data.pop(order_id, None) is not None

    # OrderService funciona igual con el FakeRepo
    service = OrderService(FakeRepo())
    service.create(Order(id="ORD-001", customer="Paul"))
    assert service.count() == 1


def test_service_con_ordenes_con_items() -> None:
    """Flujo completo: crear orden con items, consultar totales."""
    service = OrderService(InMemoryOrderRepository())

    order = Order(id="ORD-001", customer="Paul")
    order.add_item(OrderItem(name="Teclado", quantity=2, unit_price=25.0))
    order.add_item(OrderItem(name="Mouse", quantity=1, unit_price=15.5))

    service.create(order)

    recuperada = service.get("ORD-001")
    assert recuperada is not None
    assert recuperada.total == 75.98
    assert recuperada.total_items == 3

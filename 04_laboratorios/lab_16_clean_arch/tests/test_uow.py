"""Tests del Unit of Work del lab 16."""

import pytest
from clean_arch.domain.events import OrderCreated
from clean_arch.domain.order import Order, OrderItem
from clean_arch.domain.value_objects import Email, Money, OrderId
from clean_arch.infrastructure.memory_uow import InMemoryUnitOfWork


def _make_order() -> Order:
    return Order.create(
        customer_email=Email("a@b.com"),
        items=[OrderItem(product="X", quantity=1, unit_price=Money(10.0))],
    )


# ============================================
# Context manager
# ============================================


def test_uow_context_manager() -> None:
    """with uow: ... funciona."""
    uow = InMemoryUnitOfWork()
    with uow:
        pass


def test_uow_rollback_en_excepcion() -> None:
    """Si hay excepcion en el with, se hace rollback (no commit)."""
    uow = InMemoryUnitOfWork()
    order = _make_order()

    with pytest.raises(RuntimeError), uow:
        uow.orders.save(order)
        uow.collect_event(OrderCreated(order_id=order.id))
        raise RuntimeError("boom")

    # El evento NO se publico (rollback)
    assert len(uow.event_bus.published) == 0
    assert uow.committed is False


# ============================================
# commit
# ============================================


def test_uow_commit_publica_eventos() -> None:
    """Al commit, se publican los eventos pendientes."""
    uow = InMemoryUnitOfWork()
    order = _make_order()

    with uow:
        uow.orders.save(order)
        uow.collect_event(OrderCreated(order_id=order.id))
        uow.commit()

    assert len(uow.event_bus.published) == 1
    assert isinstance(uow.event_bus.published[0], OrderCreated)
    assert uow.committed is True


def test_uow_commit_limpia_eventos() -> None:
    """Despues de commit, la lista de events queda vacia."""
    uow = InMemoryUnitOfWork()
    order = _make_order()

    with uow:
        uow.orders.save(order)
        uow.collect_event(OrderCreated(order_id=order.id))
        uow.commit()

    assert uow.events == []


def test_uow_sin_commit_no_publica() -> None:
    """Sin llamar a commit, los eventos no se publican."""
    uow = InMemoryUnitOfWork()
    order = _make_order()

    with uow:
        uow.orders.save(order)
        uow.collect_event(OrderCreated(order_id=order.id))
        # NO commit

    assert len(uow.event_bus.published) == 0


# ============================================
# persistencia
# ============================================


def test_uow_save_y_find() -> None:
    """save y find_by_id funcionan."""
    uow = InMemoryUnitOfWork()
    order = _make_order()

    with uow:
        uow.orders.save(order)
        uow.commit()

    found = uow.orders.find_by_id(order.id)
    assert found is order


def test_uow_find_by_id_inexistente() -> None:
    """find_by_id de id inexistente devuelve None."""
    uow = InMemoryUnitOfWork()
    assert uow.orders.find_by_id(OrderId.generate()) is None


def test_uow_find_by_customer() -> None:
    """find_by_customer filtra."""
    uow = InMemoryUnitOfWork()
    o1 = Order.create(
        customer_email=Email("paul@example.com"),
        items=[OrderItem(product="X", quantity=1, unit_price=Money(10.0))],
    )
    o2 = Order.create(
        customer_email=Email("ana@example.com"),
        items=[OrderItem(product="Y", quantity=1, unit_price=Money(20.0))],
    )

    with uow:
        uow.orders.save(o1)
        uow.orders.save(o2)
        uow.commit()

    paul_orders = uow.orders.find_by_customer(Email("paul@example.com"))
    ana_orders = uow.orders.find_by_customer(Email("ana@example.com"))
    assert len(paul_orders) == 1
    assert len(ana_orders) == 1

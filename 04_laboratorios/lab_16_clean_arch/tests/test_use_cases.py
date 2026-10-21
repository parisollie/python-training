"""Tests de casos de uso y controller del lab 16."""

import pytest
from clean_arch.application.confirm_order import ConfirmOrderService
from clean_arch.application.controllers import CreateOrderController
from clean_arch.application.create_order import CreateOrderService
from clean_arch.application.dtos import CreateOrderInput, OrderItemInput
from clean_arch.application.presenters import OrderPresenter
from clean_arch.domain.errors import OrderNotFoundError
from clean_arch.domain.events import OrderConfirmed, OrderCreated
from clean_arch.domain.value_objects import OrderId
from clean_arch.infrastructure.memory_uow import InMemoryUnitOfWork

# ============================================
# CreateOrderService
# ============================================


def test_create_order_service() -> None:
    """CreateOrderService crea la orden y publica OrderCreated."""
    uow = InMemoryUnitOfWork()
    service = CreateOrderService(uow)

    order = service.execute(
        CreateOrderInput(
            customer_email="paul@example.com",
            items=[OrderItemInput(product="Rick", quantity=2, unit_price=50.0)],
        )
    )

    assert order.id is not None
    assert order.total.amount == 116.0  # 100 + 16%
    assert len(uow.orders.list_all()) == 1
    assert len(uow.event_bus.published) == 1
    assert isinstance(uow.event_bus.published[0], OrderCreated)


def test_create_order_email_invalido() -> None:
    """Email invalido es rechazado por Pydantic (antes del Value Object)."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="email"):
        CreateOrderInput(
            customer_email="no-es-email",
            items=[OrderItemInput(product="X", quantity=1, unit_price=1.0)],
        )


# ============================================
# ConfirmOrderService
# ============================================


def test_confirm_order_service() -> None:
    """ConfirmOrderService cambia a CONFIRMED y publica OrderConfirmed."""
    uow = InMemoryUnitOfWork()
    create = CreateOrderService(uow)
    confirm = ConfirmOrderService(uow)

    order = create.execute(
        CreateOrderInput(
            customer_email="a@b.com",
            items=[OrderItemInput(product="X", quantity=1, unit_price=10.0)],
        )
    )
    uow.event_bus.published.clear()

    confirmed = confirm.execute(str(order.id))

    assert confirmed.status.value == "confirmed"
    assert len(uow.event_bus.published) == 1
    assert isinstance(uow.event_bus.published[0], OrderConfirmed)


def test_confirm_order_inexistente() -> None:
    """Confirmar orden inexistente lanza OrderNotFoundError."""
    uow = InMemoryUnitOfWork()
    confirm = ConfirmOrderService(uow)

    with pytest.raises(OrderNotFoundError, match="no existe"):
        confirm.execute(str(OrderId.generate()))


# ============================================
# Controller + Presenter
# ============================================


def test_controller_flujo_completo() -> None:
    """Controller -> Use Case -> UoW -> Presenter."""
    uow = InMemoryUnitOfWork()
    service = CreateOrderService(uow)
    presenter = OrderPresenter()
    controller = CreateOrderController(service, presenter)

    output = controller.handle(
        CreateOrderInput(
            customer_email="a@b.com",
            items=[OrderItemInput(product="X", quantity=2, unit_price=50.0)],
        )
    )

    assert output.id is not None
    assert output.customer_email == "a@b.com"
    assert output.subtotal == 100.0
    assert output.tax == 16.0
    assert output.total == 116.0
    assert len(output.items) == 1
    assert output.items[0].subtotal == 100.0


def test_presenter_convierte_correctamente() -> None:
    """OrderPresenter convierte Order a OrderOutput."""
    uow = InMemoryUnitOfWork()
    service = CreateOrderService(uow)
    order = service.execute(
        CreateOrderInput(
            customer_email="a@b.com",
            items=[OrderItemInput(product="X", quantity=1, unit_price=10.0)],
        )
    )

    presenter = OrderPresenter()
    output = presenter.present(order)

    assert output.id == str(order.id)
    assert output.status == "pending"
    assert output.total == 11.6

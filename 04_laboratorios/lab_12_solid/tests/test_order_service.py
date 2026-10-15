"""Tests del OrderService (con DIP: se inyectan fakes)."""

import pytest
from infrastructure.notifiers import ConsoleNotifier, EmailNotifier, FakeNotifier
from infrastructure.payments import FakePayment, StripePayment
from infrastructure.repositories import InMemoryOrderRepository, SQLOrderRepository
from services.order_service import OrderService, PaymentError

# ============================================
# Casos basicos
# ============================================


def test_create_order_ok(memory_service: OrderService) -> None:
    """Crear una orden exitosamente."""
    order = memory_service.create_order(
        user_id="user-1",
        items=[{"product": "Teclado", "quantity": 2, "unit_price": 25.0}],
    )
    assert order.id is not None
    assert order.user_id == "user-1"
    assert order.subtotal == 50.0
    assert order.total == 58.0


def test_create_order_cobra_antes_de_guardar(
    memory_repo: InMemoryOrderRepository,
    fake_notifier: FakeNotifier,
    fake_payment: FakePayment,
) -> None:
    """El cobro ocurre ANTES de guardar (si falla, no se persiste)."""
    service = OrderService(memory_repo, fake_notifier, fake_payment)
    order = service.create_order(
        user_id="user-1",
        items=[{"product": "X", "quantity": 1, "unit_price": 100.0}],
    )

    assert fake_payment.calls == [(116.0, "user-1")]
    assert memory_repo.get(order.id) is not None  # type: ignore[arg-type]


def test_create_order_pago_falla_no_persiste(
    memory_repo: InMemoryOrderRepository,
    fake_notifier: FakeNotifier,
) -> None:
    """Si el pago falla, no se persiste la orden."""
    failing_payment = FakePayment(should_succeed=False)
    service = OrderService(memory_repo, fake_notifier, failing_payment)

    with pytest.raises(PaymentError, match="Fallo el cobro"):
        service.create_order(
            user_id="user-1",
            items=[{"product": "X", "quantity": 1, "unit_price": 10.0}],
        )

    assert memory_repo.list_by_user("user-1") == []


def test_create_order_notifica(
    memory_repo: InMemoryOrderRepository,
    fake_payment: FakePayment,
) -> None:
    """Al crear una orden, se notifica."""
    notifier = ConsoleNotifier()
    service = OrderService(memory_repo, notifier, fake_payment)
    order = service.create_order(
        user_id="user-1",
        items=[{"product": "X", "quantity": 1, "unit_price": 10.0}],
    )
    assert order.id in notifier.notified


def test_create_order_item_invalido(memory_service: OrderService) -> None:
    """Item invalido lanza ValueError."""
    with pytest.raises(ValueError, match="quantity"):
        memory_service.create_order(
            user_id="user-1",
            items=[{"product": "X", "quantity": 0, "unit_price": 10.0}],
        )


def test_create_order_sin_items(memory_service: OrderService) -> None:
    """Sin items lanza ValueError."""
    with pytest.raises(ValueError, match="al menos un item"):
        memory_service.create_order(user_id="user-1", items=[])


# ============================================
# Consultas
# ============================================


def test_get_order(memory_service: OrderService) -> None:
    """get_order recupera la orden creada."""
    order = memory_service.create_order(
        user_id="user-1",
        items=[{"product": "X", "quantity": 1, "unit_price": 10.0}],
    )
    assert memory_service.get_order(order.id) is order  # type: ignore[arg-type]


def test_get_order_inexistente(memory_service: OrderService) -> None:
    """get_order con id inexistente devuelve None."""
    assert memory_service.get_order("no-existe") is None


def test_list_user_orders(memory_service: OrderService) -> None:
    """list_user_orders filtra por usuario."""
    memory_service.create_order(
        user_id="user-1",
        items=[{"product": "A", "quantity": 1, "unit_price": 10.0}],
    )
    memory_service.create_order(
        user_id="user-1",
        items=[{"product": "B", "quantity": 1, "unit_price": 20.0}],
    )
    memory_service.create_order(
        user_id="user-2",
        items=[{"product": "C", "quantity": 1, "unit_price": 30.0}],
    )

    assert len(memory_service.list_user_orders("user-1")) == 2
    assert len(memory_service.list_user_orders("user-2")) == 1


# ============================================
# DIP: cambiar implementaciones sin tocar el servicio
# ============================================


def test_service_con_sql_repository(
    sql_repo: SQLOrderRepository,
    fake_notifier: FakeNotifier,
    fake_payment: FakePayment,
) -> None:
    """El mismo servicio funciona con SQLOrderRepository."""
    service = OrderService(sql_repo, fake_notifier, fake_payment)
    order = service.create_order(
        user_id="user-1",
        items=[{"product": "X", "quantity": 1, "unit_price": 10.0}],
    )
    assert order.id is not None
    assert service.get_order(order.id) is order


def test_service_con_email_notifier(
    memory_repo: InMemoryOrderRepository,
    fake_payment: FakePayment,
) -> None:
    """El mismo servicio funciona con EmailNotifier."""
    notifier = EmailNotifier()
    service = OrderService(memory_repo, notifier, fake_payment)
    order = service.create_order(
        user_id="user-1",
        items=[{"product": "X", "quantity": 1, "unit_price": 10.0}],
    )
    assert len(notifier.sent_emails) == 1
    assert notifier.sent_emails[0]["to"] == "user-1@example.com"
    assert str(order.id) in notifier.sent_emails[0]["subject"]


def test_service_con_stripe_payment(
    memory_repo: InMemoryOrderRepository,
    fake_notifier: FakeNotifier,
) -> None:
    """El mismo servicio funciona con StripePayment."""
    payment = StripePayment()
    service = OrderService(memory_repo, fake_notifier, payment)
    service.create_order(
        user_id="user-1",
        items=[{"product": "X", "quantity": 1, "unit_price": 100.0}],
    )
    assert len(payment.charges) == 1
    assert payment.charges[0]["amount"] == 116.0
    assert payment.charges[0]["user_id"] == "user-1"


# ============================================
# LSP: sustitucion de implementaciones
# ============================================


@pytest.mark.parametrize("repo_type", ["memory", "sql"])
def test_lsp_mismo_comportamiento(
    repo_type: str,
    fake_notifier: FakeNotifier,
    fake_payment: FakePayment,
) -> None:
    """Ambos repositorios se comportan igual (LSP)."""
    repo = InMemoryOrderRepository() if repo_type == "memory" else SQLOrderRepository()
    service = OrderService(repo, fake_notifier, fake_payment)

    order = service.create_order(
        user_id="user-1",
        items=[{"product": "X", "quantity": 1, "unit_price": 10.0}],
    )

    assert service.get_order(order.id) is not None  # type: ignore[arg-type]
    assert len(service.list_user_orders("user-1")) == 1
    assert service.list_user_orders("user-2") == []

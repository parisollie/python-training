"""Tests del caso de uso CreateOrderService.

Unit (con fakes) + Contract (adaptadores cumplen puerto) + E2E.
"""

import httpx
import pytest
from application.create_order import CreateOrderService, OrderNotFoundError
from application.dtos import CreateOrderInput, OrderItemInput
from domain.order import Order, OrderItem
from domain.ports import Notifier, OrderRepository
from domain.value_objects import Email, Money, OrderId
from infrastructure.http_notifier import HttpNotifier
from infrastructure.memory import FakeNotifier, InMemoryOrderRepository

# ============================================
# Unit: caso de uso con fakes
# ============================================


def test_create_order_ok(service: CreateOrderService, valid_input: CreateOrderInput) -> None:
    """Caso de uso basico."""
    result = service.execute(valid_input)
    assert result.id is not None
    assert result.customer_email == "paul@example.com"
    assert result.subtotal == 65.5
    assert result.tax == 10.48
    assert result.total == 75.98
    assert result.status == "pending"
    assert result.total_items == 3


def test_create_order_notifica(
    service: CreateOrderService,
    valid_input: CreateOrderInput,
    notifier: FakeNotifier,
) -> None:
    """El caso de uso notifica."""
    result = service.execute(valid_input)
    assert result.id in notifier.notified


def test_create_order_persiste(
    service: CreateOrderService,
    valid_input: CreateOrderInput,
    repo: InMemoryOrderRepository,
) -> None:
    """El caso de uso persiste."""
    result = service.execute(valid_input)
    order = repo.find_by_id(OrderId(result.id))
    assert order is not None


def test_create_order_email_invalido(service: CreateOrderService) -> None:
    """Email invalido lanza."""
    with pytest.raises(ValueError, match="Email invalido"):
        service.execute(
            CreateOrderInput(
                customer_email="no-es-email",
                items=[OrderItemInput(product="X", quantity=1, unit_price=1.0)],
            )
        )


def test_get_order_ok(service: CreateOrderService, valid_input: CreateOrderInput) -> None:
    """get recupera la orden creada."""
    created = service.execute(valid_input)
    result = service.get(created.id)
    assert result.id == created.id


def test_get_order_inexistente(service: CreateOrderService) -> None:
    """get con id inexistente lanza OrderNotFoundError."""
    with pytest.raises(OrderNotFoundError, match="no existe"):
        service.get("no-existe")


def test_list_all(
    service: CreateOrderService,
    valid_input: CreateOrderInput,
) -> None:
    """list_all devuelve todas las ordenes."""
    service.execute(valid_input)
    service.execute(valid_input)
    assert len(service.list_all()) == 2


# ============================================
# Contract: los adaptadores cumplen el puerto
# ============================================


def test_inmemory_cumple_repository_protocol(repo: InMemoryOrderRepository) -> None:
    """InMemoryOrderRepository cumple OrderRepository."""
    # mypy verifica en tiempo de compilacion; aqui verificamos runtime
    assert hasattr(repo, "save")
    assert hasattr(repo, "find_by_id")
    assert hasattr(repo, "list_all")


def test_fake_notifier_cumple_notifier_protocol(notifier: FakeNotifier) -> None:
    """FakeNotifier cumple Notifier."""
    assert hasattr(notifier, "notify_order_created")


def test_http_notifier_cumple_notifier_protocol() -> None:
    """HttpNotifier cumple Notifier."""
    notifier = HttpNotifier("https://example.com/notify")
    assert hasattr(notifier, "notify_order_created")
    notifier.close()


@pytest.mark.parametrize("repo_type", ["memory"])
def test_contract_repositorio_comportamiento(repo_type: str) -> None:
    """Todos los repositorios se comportan igual (LSP)."""
    if repo_type == "memory":
        repo: OrderRepository = InMemoryOrderRepository()

    order = Order.create(
        customer_email=Email("a@b.com"),
        items=[OrderItem(product="X", quantity=1, unit_price=Money(1.0))],
    )

    # save + find_by_id
    repo.save(order)
    found = repo.find_by_id(order.id)
    assert found is order

    # list_all
    assert len(repo.list_all()) == 1

    # id inexistente
    assert repo.find_by_id(OrderId("no-existe")) is None


@pytest.mark.parametrize("notifier_type", ["fake"])
def test_contract_notifier_comportamiento(notifier_type: str) -> None:
    """Todos los notifiers se comportan igual."""
    if notifier_type == "fake":
        notif: Notifier = FakeNotifier()

    order = Order.create(
        customer_email=Email("a@b.com"),
        items=[OrderItem(product="X", quantity=1, unit_price=Money(1.0))],
    )
    # No debe lanzar
    notif.notify_order_created(order)


# ============================================
# E2E: flujo completo con adaptadores reales
# ============================================


def test_e2e_flujo_completo_con_http_notifier() -> None:
    """E2E: crear orden con notifier HTTP simulado."""
    captured: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(
            {
                "url": str(request.url),
                "body": request.content.decode(),
            }
        )
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)

    repo = InMemoryOrderRepository()
    notifier = HttpNotifier("https://api.example.com/notify", client=client)
    service = CreateOrderService(repository=repo, notifier=notifier)

    result = service.execute(
        CreateOrderInput(
            customer_email="paul@example.com",
            items=[OrderItemInput(product="X", quantity=1, unit_price=100.0)],
        )
    )

    # Verificar el flujo
    assert result.total == 116.0
    assert len(captured) == 1
    assert "order_created" in str(captured[0]["body"])
    assert result.id in str(captured[0]["body"])

    # La orden quedo en el repo
    saved = repo.find_by_id(OrderId(result.id))
    assert saved is not None

    notifier.close()


def test_e2e_http_notifier_falla_silenciosamente() -> None:
    """El notifier HTTP no propaga errores (no rompe el flujo)."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)

    repo = InMemoryOrderRepository()
    notifier = HttpNotifier("https://api.example.com/notify", client=client)
    service = CreateOrderService(repository=repo, notifier=notifier)

    # No debe lanzar aunque el notifier falle
    result = service.execute(
        CreateOrderInput(
            customer_email="paul@example.com",
            items=[OrderItemInput(product="X", quantity=1, unit_price=10.0)],
        )
    )
    assert result.id is not None
    assert len(repo.list_all()) == 1

    notifier.close()

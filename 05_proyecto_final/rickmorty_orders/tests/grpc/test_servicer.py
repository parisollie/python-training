"""Tests del OrderServicer gRPC sin levantar red.

Estrategia: instanciamos OrderServicer y sobrescribimos sus 5 servicios
con versiones que usan fixtures en memoria (memory_repo, memory_chars,
fake_notifier, fake_event_bus). Asi probamos el servicer completo
(conversion + traduccion de errores + delegacion a casos de uso)
sin depender de red, SQLite ni servidor levantado.

El context de gRPC se simula con un FakeContext que captura abort().
"""

from typing import Any

import grpc
import pytest
from rickmorty_orders.application.create_order import CreateOrderService
from rickmorty_orders.application.order_actions import (
    CancelOrderService,
    ConfirmOrderService,
)
from rickmorty_orders.application.order_queries import (
    GetOrderService,
    ListOrdersService,
)
from rickmorty_orders.grpc import orders_pb2
from rickmorty_orders.grpc.server import OrderServicer
from rickmorty_orders.infrastructure.in_memory import (
    FakeEventBus,
    FakeNotifier,
    InMemoryCharacterRepository,
    InMemoryOrderRepository,
)
from rickmorty_orders.infrastructure.persistence import Base, get_engine

# ============================================
# Fake gRPC context
# ============================================


class FakeContext(grpc.ServicerContext):
    """Context fake que captura el abort() como una excepcion controlada."""

    def __init__(self) -> None:
        self.aborted: tuple[grpc.StatusCode, str] | None = None

    def abort(self, code: grpc.StatusCode, details: str) -> None:
        self.aborted = (code, details)
        raise _AbortError(code, details)

    def abort_with_status(self, status: grpc.Status) -> None:  # pragma: no cover
        raise NotImplementedError

    def set_trailing_metadata(self, trailing_metadata: Any) -> None:  # pragma: no cover
        pass

    def invocation_metadata(self) -> Any:  # pragma: no cover
        return ()

    def peer(self) -> str:  # pragma: no cover
        return "fake"

    def peer_identities(self) -> Any:  # pragma: no cover
        return None

    def peer_identity_key(self) -> Any:  # pragma: no cover
        return None

    def auth_context(self) -> dict[str, Any]:  # pragma: no cover
        return {}

    def send_initial_metadata(self, initial_metadata: Any) -> None:  # pragma: no cover
        pass

    def set_code(self, code: grpc.StatusCode) -> None:  # pragma: no cover
        pass

    def set_details(self, details: str) -> None:  # pragma: no cover
        pass

    def code(self) -> grpc.StatusCode | None:  # pragma: no cover
        return None

    def details(self) -> str | None:  # pragma: no cover
        return None

    def trailing_metadata(self) -> Any:  # pragma: no cover
        return ()

    def add_callback(self, callback: Any) -> bool:  # pragma: no cover
        """No-op: el servicer no usa callbacks."""
        return False

    def cancel(self) -> None:  # pragma: no cover
        """No-op: el servicer no cancela el contexto."""

    def is_active(self) -> bool:  # pragma: no cover
        """El contexto siempre esta activo en tests."""
        return True

    def time_remaining(self) -> float | None:  # pragma: no cover
        """Sin limite de tiempo en tests."""
        return None


class _AbortError(Exception):
    """Excepcion interna para simular el abort() de gRPC."""

    def __init__(self, code: grpc.StatusCode, details: str) -> None:
        super().__init__(details)
        self.code = code
        self.details = details


# ============================================
# Fixture: servicer con servicios en memoria
# ============================================


@pytest.fixture
def servicer(
    memory_repo: InMemoryOrderRepository,
    memory_chars: InMemoryCharacterRepository,
    fake_notifier: FakeNotifier,
    fake_event_bus: FakeEventBus,
) -> OrderServicer:
    """OrderServicer con servicios cableados a adaptadores en memoria.

    Sobrescribe los atributos privados del servicer DESPUES de instanciarlo,
    para no tocar la DB real (SQLite). El __init__ original corre create_all
    contra get_engine(), que es idempotente y no afecta los tests.
    """
    svc = OrderServicer()
    svc._create = CreateOrderService(  # type: ignore[attr-defined]
        memory_repo, memory_chars, fake_notifier, fake_event_bus
    )
    svc._get = GetOrderService(memory_repo)  # type: ignore[attr-defined]
    svc._list = ListOrdersService(memory_repo)  # type: ignore[attr-defined]
    svc._confirm = ConfirmOrderService(  # type: ignore[attr-defined]
        memory_repo, fake_notifier, fake_event_bus
    )
    svc._cancel = CancelOrderService(  # type: ignore[attr-defined]
        memory_repo, fake_notifier, fake_event_bus
    )
    return svc


def _create_request(email: str = "test@example.com") -> orders_pb2.CreateOrderRequest:
    return orders_pb2.CreateOrderRequest(
        customer_email=email,
        items=[
            orders_pb2.OrderItemInput(character_id=1, quantity=2),
            orders_pb2.OrderItemInput(character_id=2, quantity=1),
        ],
    )


# ============================================
# CreateOrder
# ============================================


def test_create_order_ok(servicer: OrderServicer) -> None:
    ctx = FakeContext()

    response = servicer.CreateOrder(_create_request(), ctx)

    assert response.customer_email == "test@example.com"
    assert response.status == "pending"
    assert response.total > 0
    assert len(response.items) == 2
    assert response.items[0].character_name == "Rick Sanchez"
    assert response.items[1].character_name == "Morty Smith"
    assert ctx.aborted is None


def test_create_order_personaje_inexistente_aborta_not_found(
    servicer: OrderServicer,
) -> None:
    ctx = FakeContext()
    request = orders_pb2.CreateOrderRequest(
        customer_email="test@example.com",
        items=[orders_pb2.OrderItemInput(character_id=9999, quantity=1)],
    )

    with pytest.raises(_AbortError):
        servicer.CreateOrder(request, ctx)

    assert ctx.aborted is not None
    assert ctx.aborted[0] == grpc.StatusCode.NOT_FOUND


def test_create_order_email_invalido_aborta_invalid_argument(
    servicer: OrderServicer,
) -> None:
    ctx = FakeContext()
    request = orders_pb2.CreateOrderRequest(
        customer_email="no-es-email",
        items=[orders_pb2.OrderItemInput(character_id=1, quantity=1)],
    )

    with pytest.raises(_AbortError):
        servicer.CreateOrder(request, ctx)

    assert ctx.aborted is not None
    assert ctx.aborted[0] == grpc.StatusCode.INVALID_ARGUMENT


# ============================================
# GetOrder
# ============================================


def test_get_order_ok(servicer: OrderServicer) -> None:
    ctx = FakeContext()
    created = servicer.CreateOrder(_create_request(), FakeContext())

    response = servicer.GetOrder(orders_pb2.GetOrderRequest(order_id=created.id), ctx)

    assert response.id == created.id
    assert response.customer_email == created.customer_email


def test_get_order_inexistente_aborta_not_found(servicer: OrderServicer) -> None:
    ctx = FakeContext()

    with pytest.raises(_AbortError):
        servicer.GetOrder(orders_pb2.GetOrderRequest(order_id="no-existe"), ctx)

    assert ctx.aborted is not None
    assert ctx.aborted[0] == grpc.StatusCode.NOT_FOUND


# ============================================
# ListOrders
# ============================================


def test_list_orders_vacio(servicer: OrderServicer) -> None:
    ctx = FakeContext()

    response = servicer.ListOrders(orders_pb2.ListOrdersRequest(), ctx)

    assert len(response.orders) == 0


def test_list_orders_todas(servicer: OrderServicer) -> None:
    servicer.CreateOrder(_create_request("a@example.com"), FakeContext())
    servicer.CreateOrder(_create_request("b@example.com"), FakeContext())

    response = servicer.ListOrders(orders_pb2.ListOrdersRequest(), FakeContext())

    assert len(response.orders) == 2


def test_list_orders_filtra_por_email(servicer: OrderServicer) -> None:
    servicer.CreateOrder(_create_request("a@example.com"), FakeContext())
    servicer.CreateOrder(_create_request("b@example.com"), FakeContext())

    response = servicer.ListOrders(
        orders_pb2.ListOrdersRequest(customer_email="a@example.com"), FakeContext()
    )

    assert len(response.orders) == 1
    assert response.orders[0].customer_email == "a@example.com"


# ============================================
# ConfirmOrder
# ============================================


def test_confirm_order_ok(servicer: OrderServicer) -> None:
    created = servicer.CreateOrder(_create_request(), FakeContext())

    response = servicer.ConfirmOrder(orders_pb2.OrderIdRequest(order_id=created.id), FakeContext())

    assert response.status == "confirmed"


def test_confirm_order_inexistente_aborta_not_found(servicer: OrderServicer) -> None:
    ctx = FakeContext()

    with pytest.raises(_AbortError):
        servicer.ConfirmOrder(orders_pb2.OrderIdRequest(order_id="no-existe"), ctx)

    assert ctx.aborted is not None
    assert ctx.aborted[0] == grpc.StatusCode.NOT_FOUND


def test_confirm_order_ya_confirmada_aborta_failed_precondition(
    servicer: OrderServicer,
) -> None:
    created = servicer.CreateOrder(_create_request(), FakeContext())
    servicer.ConfirmOrder(orders_pb2.OrderIdRequest(order_id=created.id), FakeContext())

    ctx = FakeContext()
    with pytest.raises(_AbortError):
        servicer.ConfirmOrder(orders_pb2.OrderIdRequest(order_id=created.id), ctx)

    assert ctx.aborted is not None
    assert ctx.aborted[0] == grpc.StatusCode.FAILED_PRECONDITION


# ============================================
# CancelOrder
# ============================================


def test_cancel_order_ok_desde_pending(servicer: OrderServicer) -> None:
    created = servicer.CreateOrder(_create_request(), FakeContext())

    response = servicer.CancelOrder(
        orders_pb2.CancelOrderRequest(order_id=created.id, reason="test"), FakeContext()
    )

    assert response.status == "cancelled"


def test_cancel_order_ok_desde_confirmed(servicer: OrderServicer) -> None:
    """Regla de negocio: CONFIRMED -> CANCELLED esta permitida."""
    created = servicer.CreateOrder(_create_request(), FakeContext())
    servicer.ConfirmOrder(orders_pb2.OrderIdRequest(order_id=created.id), FakeContext())

    response = servicer.CancelOrder(
        orders_pb2.CancelOrderRequest(order_id=created.id), FakeContext()
    )

    assert response.status == "cancelled"


def test_cancel_order_inexistente_aborta_not_found(servicer: OrderServicer) -> None:
    ctx = FakeContext()

    with pytest.raises(_AbortError):
        servicer.CancelOrder(orders_pb2.CancelOrderRequest(order_id="no-existe"), ctx)

    assert ctx.aborted is not None
    assert ctx.aborted[0] == grpc.StatusCode.NOT_FOUND


def test_cancel_order_ya_cancelada_aborta_failed_precondition(
    servicer: OrderServicer,
) -> None:
    created = servicer.CreateOrder(_create_request(), FakeContext())
    servicer.CancelOrder(orders_pb2.CancelOrderRequest(order_id=created.id), FakeContext())

    ctx = FakeContext()
    with pytest.raises(_AbortError):
        servicer.CancelOrder(orders_pb2.CancelOrderRequest(order_id=created.id), ctx)

    assert ctx.aborted is not None
    assert ctx.aborted[0] == grpc.StatusCode.FAILED_PRECONDITION
    assert "cancelada" in ctx.aborted[1].lower()


# ============================================
# Sanity: el engine global quedo consistente
# ============================================


def test_create_all_no_rompe_metadata() -> None:
    """create_all es idempotente y no destruye datos existentes."""
    Base.metadata.create_all(get_engine())
    assert "orders" in Base.metadata.tables
    assert "order_items" in Base.metadata.tables

"""Servidor gRPC que expone los casos de uso de Orders.

Este servidor es un ADAPTADOR DELGADO: su unico trabajo es:
1. Recibir mensajes protobuf
2. Convertirlos a DTOs (converters.py)
3. Llamar al caso de uso REAL (application/)
4. Convertir la respuesta a protobuf
5. Traducir errores de dominio a status codes de gRPC

NO contiene logica de negocio. Los casos de uso hacen ese trabajo.
"""

from __future__ import annotations

import logging
from concurrent import futures

import grpc
import pydantic

from rickmorty_orders.application.create_order import CreateOrderService
from rickmorty_orders.application.order_actions import (
    CancelOrderService,
    ConfirmOrderService,
)
from rickmorty_orders.application.order_queries import (
    GetOrderService,
    ListOrdersService,
)
from rickmorty_orders.domain.errors import (
    CharacterNotFoundError,
    InvalidStatusTransitionError,
    OrderNotFoundError,
)
from rickmorty_orders.grpc import orders_pb2, orders_pb2_grpc
from rickmorty_orders.grpc.converters import (
    order_output_to_proto,
    order_outputs_to_list_proto,
    proto_to_create_order_input,
)
from rickmorty_orders.infrastructure import orm_models  # noqa: F401 — registra modelos
from rickmorty_orders.infrastructure.console_notifier import ConsoleNotifier
from rickmorty_orders.infrastructure.event_bus import InMemoryEventBus
from rickmorty_orders.infrastructure.persistence import (
    Base,
    get_engine,
    get_session_factory,
)
from rickmorty_orders.infrastructure.rickmorty_client import RickMortyApiClient
from rickmorty_orders.infrastructure.sql_repositories import SQLOrderRepository

logger = logging.getLogger(__name__)


# OrderServiceServicer viene de codigo generado por protoc (sin tipos).
# Heredar de Any es intencional: mypy no debe chequear los metodos
# que protoc genera, solo los que escribimos nosotros.
# OrderServiceServicer viene de codigo generado por protoc (sin tipos).
# Heredar de Any es intencional: mypy no debe chequear los metodos
# que protoc genera, solo los que escribimos nosotros.
class OrderServicer(orders_pb2_grpc.OrderServiceServicer):  # type: ignore[misc]
    """Implementacion gRPC del servicio OrderService.

    Construye las dependencias igual que `infrastructure/dependencies.py`,
    pero sin FastAPI `Depends` (no aplica en gRPC).
    """

    def __init__(self) -> None:
        # Creamos las tablas si no existen (idempotente, sin tocar Alembic).
        # Esto hace al servidor gRPC autosuficiente: no requiere CWD
        # especifico ni correr 'alembic upgrade head' antes.
        Base.metadata.create_all(get_engine())
        self._repo = SQLOrderRepository(get_session_factory())
        self._characters = RickMortyApiClient()
        self._notifier = ConsoleNotifier()
        self._event_bus = InMemoryEventBus()

        self._create = CreateOrderService(
            self._repo, self._characters, self._notifier, self._event_bus
        )
        self._get = GetOrderService(self._repo)
        self._list = ListOrdersService(self._repo)
        self._confirm = ConfirmOrderService(self._repo, self._notifier, self._event_bus)
        self._cancel = CancelOrderService(self._repo, self._notifier, self._event_bus)

    # ------------------------------------------------------------------
    # RPC handlers
    # ------------------------------------------------------------------

    def CreateOrder(
        self,
        request: orders_pb2.CreateOrderRequest,
        context: grpc.ServicerContext,
    ) -> orders_pb2.OrderResponse:
        """RPC: crear una orden."""
        try:
            input_dto = proto_to_create_order_input(request)
        except pydantic.ValidationError as exc:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))

        try:
            output = self._create.execute(input_dto)
        except CharacterNotFoundError as exc:
            context.abort(grpc.StatusCode.NOT_FOUND, str(exc))
        except pydantic.ValidationError as exc:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))
        except Exception as exc:  # noqa: BLE001 - red de seguridad
            logger.exception("Error inesperado en CreateOrder")
            context.abort(grpc.StatusCode.INTERNAL, f"Error interno: {exc}")

        return order_output_to_proto(output)

    def GetOrder(
        self,
        request: orders_pb2.GetOrderRequest,
        context: grpc.ServicerContext,
    ) -> orders_pb2.OrderResponse:
        """RPC: obtener una orden por id."""
        try:
            output = self._get.execute(request.order_id)
        except OrderNotFoundError as exc:
            context.abort(grpc.StatusCode.NOT_FOUND, str(exc))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error inesperado en GetOrder")
            context.abort(grpc.StatusCode.INTERNAL, f"Error interno: {exc}")
        return order_output_to_proto(output)

    def ListOrders(
        self,
        request: orders_pb2.ListOrdersRequest,
        context: grpc.ServicerContext,
    ) -> orders_pb2.ListOrdersResponse:
        """RPC: listar ordenes (todas o por cliente)."""
        try:
            email = request.customer_email or None
            outputs = self._list.execute(email)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error inesperado en ListOrders")
            context.abort(grpc.StatusCode.INTERNAL, f"Error interno: {exc}")
        return order_outputs_to_list_proto(outputs)

    def ConfirmOrder(
        self,
        request: orders_pb2.OrderIdRequest,
        context: grpc.ServicerContext,
    ) -> orders_pb2.OrderResponse:
        """RPC: confirmar una orden."""
        try:
            output = self._confirm.execute(request.order_id)
        except OrderNotFoundError as exc:
            context.abort(grpc.StatusCode.NOT_FOUND, str(exc))
        except InvalidStatusTransitionError as exc:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, str(exc))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error inesperado en ConfirmOrder")
            context.abort(grpc.StatusCode.INTERNAL, f"Error interno: {exc}")
        return order_output_to_proto(output)

    def CancelOrder(
        self,
        request: orders_pb2.CancelOrderRequest,
        context: grpc.ServicerContext,
    ) -> orders_pb2.OrderResponse:
        """RPC: cancelar una orden."""
        try:
            output = self._cancel.execute(request.order_id, request.reason)
        except OrderNotFoundError as exc:
            context.abort(grpc.StatusCode.NOT_FOUND, str(exc))
        except InvalidStatusTransitionError as exc:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, str(exc))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error inesperado en CancelOrder")
            context.abort(grpc.StatusCode.INTERNAL, f"Error interno: {exc}")
        return order_output_to_proto(output)


def serve(port: int = 50051) -> None:
    """Arranca el servidor gRPC (bloqueante)."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    orders_pb2_grpc.add_OrderServiceServicer_to_server(OrderServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info("gRPC server escuchando en puerto %d", port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve()

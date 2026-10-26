"""Cliente gRPC de prueba para interactuar con OrderService.

Uso manual:

    # En una terminal:
    poetry run python -m rickmorty_orders.grpc.server

    # En otra terminal:
    poetry run python -m rickmorty_orders.grpc.client

Este modulo NO se usa en produccion: es una herramienta de desarrollo
y base para los tests de integracion.
"""

from __future__ import annotations

import argparse
import logging
import sys
import uuid

import grpc

from rickmorty_orders.grpc import orders_pb2, orders_pb2_grpc

logger = logging.getLogger(__name__)


def _print_response(label: str, response: orders_pb2.OrderResponse) -> None:
    """Imprime una respuesta de orden legible."""
    print(f"\n=== {label} ===")
    print(f"  id:          {response.id}")
    print(f"  email:       {response.customer_email}")
    print(f"  status:      {response.status}")
    print(f"  subtotal:    {response.subtotal:.2f}")
    print(f"  tax:         {response.tax:.2f}")
    print(f"  total:       {response.total:.2f}")
    print(f"  total_items: {response.total_items}")
    for item in response.items:
        print(
            f"    - [{item.character_id}] {item.character_name} "
            f"x{item.quantity} @ {item.unit_price:.2f} = {item.subtotal:.2f}"
        )


def _handle_grpc_error(exc: grpc.RpcError, action: str) -> None:
    """Imprime el error de gRPC de forma consistente."""
    code = exc.code().name if exc.code() else "UNKNOWN"
    details = exc.details() or "(sin detalles)"
    print(f"\n[ERROR] {action} -> {code}: {details}", file=sys.stderr)


def run_demo(target: str) -> None:
    """Corre un flujo de demo: create -> get -> list -> confirm -> cancel."""
    print(f"Conectando a {target} ...")
    with grpc.insecure_channel(target) as channel:
        stub = orders_pb2_grpc.OrderServiceStub(channel)

        email = f"demo-{uuid.uuid4().hex[:8]}@example.com"

        # 1. CreateOrder
        try:
            created = stub.CreateOrder(
                orders_pb2.CreateOrderRequest(
                    customer_email=email,
                    items=[
                        orders_pb2.OrderItemInput(character_id=1, quantity=2),
                        orders_pb2.OrderItemInput(character_id=2, quantity=1),
                    ],
                ),
                timeout=10,
            )
            _print_response("CreateOrder", created)
        except grpc.RpcError as exc:
            _handle_grpc_error(exc, "CreateOrder")
            return

        # 2. GetOrder
        try:
            fetched = stub.GetOrder(
                orders_pb2.GetOrderRequest(order_id=created.id),
                timeout=10,
            )
            _print_response("GetOrder", fetched)
        except grpc.RpcError as exc:
            _handle_grpc_error(exc, "GetOrder")

        # 3. ListOrders
        try:
            listed = stub.ListOrders(
                orders_pb2.ListOrdersRequest(customer_email=email),
                timeout=10,
            )
            print(f"\n=== ListOrders ===\n  total encontradas: {len(listed.orders)}")
        except grpc.RpcError as exc:
            _handle_grpc_error(exc, "ListOrders")

        # 4. ConfirmOrder
        try:
            confirmed = stub.ConfirmOrder(
                orders_pb2.OrderIdRequest(order_id=created.id),
                timeout=10,
            )
            _print_response("ConfirmOrder", confirmed)
        except grpc.RpcError as exc:
            _handle_grpc_error(exc, "ConfirmOrder")

        # 5. CancelOrder (permitido desde CONFIRMED por regla de negocio)
        try:
            cancelled = stub.CancelOrder(
                orders_pb2.CancelOrderRequest(
                    order_id=created.id,
                    reason="Cancelacion post-confirmacion",
                ),
                timeout=10,
            )
            _print_response("CancelOrder", cancelled)
        except grpc.RpcError as exc:
            _handle_grpc_error(exc, "CancelOrder")

        # 6. CancelOrder de nuevo (DEBE fallar: ya esta cancelada)
        try:
            stub.CancelOrder(
                orders_pb2.CancelOrderRequest(
                    order_id=created.id,
                    reason="Segundo intento (esperado fallar)",
                ),
                timeout=10,
            )
            print("\n[!] Inesperado: se permitio cancelar 2 veces")
        except grpc.RpcError as exc:
            _handle_grpc_error(exc, "CancelOrder x2 (esperado: FAILED_PRECONDITION)")


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cliente gRPC de demo para Orders")
    parser.add_argument(
        "--target",
        default="localhost:50051",
        help="Host:puerto del servidor gRPC (default: localhost:50051)",
    )
    return parser


def main() -> None:
    logging.basicConfig(level=logging.WARNING)
    args = _build_arg_parser().parse_args()
    run_demo(args.target)


if __name__ == "__main__":
    main()

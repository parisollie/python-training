"""CLI principal de rickmorty_orders (Typer).

Uso:
    rickmorty-orders --help
    rickmorty-orders orders list
    rickmorty-orders orders create --email X --item Y --quantity 2 --price 50
    rickmorty-orders orders get <id>
    rickmorty-orders orders confirm <id>
    rickmorty-orders orders cancel <id> --reason "motivo"
"""

from typing import Annotated

import httpx
import typer

from rickmorty_orders.cli.client import ApiClient
from rickmorty_orders.cli.formatters import (
    error,
    print_order_detail,
    print_orders_table,
    success,
)

app = typer.Typer(
    help="CLI para gestionar ordenes de rickmorty_orders",
    no_args_is_help=True,
)

orders_app = typer.Typer(help="Gestionar ordenes")
app.add_typer(orders_app, name="orders")


# ============================================
# Helpers
# ============================================


def _get_api_url() -> str:
    """URL de la API (configurable via env var CLI_API_URL)."""
    import os

    return os.environ.get("CLI_API_URL", "http://localhost:8000")


def _handle_error(e: Exception) -> None:
    """Muestra errores de HTTP de forma amigable."""
    if isinstance(e, httpx.HTTPStatusError):
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        error(f"HTTP {e.response.status_code}: {detail}")
    elif isinstance(e, httpx.RequestError):
        error(f"No se pudo conectar a la API: {e}")
        error("Asegurate de que la API este corriendo (uvicorn ...)")
    else:
        error(str(e))
    raise typer.Exit(code=1)


# ============================================
# Comandos de orders
# ============================================


@orders_app.command("list")
def orders_list(
    customer_email: Annotated[
        str | None,
        typer.Option("--email", "-e", help="Filtrar por email del cliente"),
    ] = None,
) -> None:
    """Lista todas las ordenes (opcionalmente filtradas por cliente)."""
    try:
        with ApiClient(_get_api_url()) as client:
            orders = client.list_orders(customer_email)
        print_orders_table(orders)
    except Exception as e:
        _handle_error(e)


@orders_app.command("get")
def orders_get(
    order_id: Annotated[str, typer.Argument(help="ID de la orden")],
) -> None:
    """Obtiene una orden por ID."""
    try:
        with ApiClient(_get_api_url()) as client:
            order = client.get_order(order_id)
        if order is None:
            error(f"Orden {order_id} no encontrada")
            raise typer.Exit(code=1)
        print_order_detail(order)
    except typer.Exit:
        raise
    except Exception as e:
        _handle_error(e)


@orders_app.command("create")
def orders_create(
    email: Annotated[str, typer.Option("--email", "-e", help="Email del cliente")],
    character_id: Annotated[int, typer.Option("--character", "-c", help="ID del personaje")],
    quantity: Annotated[int, typer.Option("--quantity", "-q", help="Cantidad")] = 1,
) -> None:
    """Crea una orden con un item."""
    try:
        with ApiClient(_get_api_url()) as client:
            order = client.create_order(
                customer_email=email,
                items=[{"character_id": character_id, "quantity": quantity}],
            )
        success(f"Orden creada: {order.get('id')}")
        print_order_detail(order)
    except Exception as e:
        _handle_error(e)


@orders_app.command("confirm")
def orders_confirm(
    order_id: Annotated[str, typer.Argument(help="ID de la orden")],
) -> None:
    """Confirma una orden (PENDING -> CONFIRMED)."""
    try:
        with ApiClient(_get_api_url()) as client:
            order = client.confirm_order(order_id)
        success(f"Orden confirmada: {order.get('id')}")
    except Exception as e:
        _handle_error(e)


@orders_app.command("cancel")
def orders_cancel(
    order_id: Annotated[str, typer.Argument(help="ID de la orden")],
    reason: Annotated[
        str,
        typer.Option("--reason", "-r", help="Motivo de cancelacion"),
    ] = "",
) -> None:
    """Cancela una orden."""
    if not typer.confirm(f"Cancelar la orden {order_id}?"):
        warning_msg = "Operacion cancelada por el usuario"
        typer.echo(warning_msg)
        raise typer.Exit(code=0)
    try:
        with ApiClient(_get_api_url()) as client:
            order = client.cancel_order(order_id, reason=reason)
        success(f"Orden cancelada: {order.get('id')}")
    except Exception as e:
        _handle_error(e)


# ============================================
# Comando raiz
# ============================================


@app.command("health")
def health() -> None:
    """Verifica que la API este corriendo."""
    try:
        with ApiClient(_get_api_url()) as client:
            response = client._request("GET", "/health")
        if response.status_code == 200:
            success(f"API OK en {_get_api_url()}")
        else:
            error(f"API respondio {response.status_code}")
            raise typer.Exit(code=1)
    except Exception as e:
        _handle_error(e)


if __name__ == "__main__":
    app()

"""Tests del CLI con Typer CliRunner.

Usa httpx.MockTransport para no depender de la API real.
"""

import sys
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from rickmorty_orders.cli.main import app  # noqa: E402

runner = CliRunner()


# ============================================
# Helpers
# ============================================


def _sample_order_dict(order_id: str = "test-id") -> dict[str, object]:
    return {
        "id": order_id,
        "customer_email": "paul@example.com",
        "status": "pending",
        "items": [
            {
                "character_id": 1,
                "character_name": "Rick",
                "quantity": 1,
                "unit_price": 50.0,
                "subtotal": 50.0,
            }
        ],
        "subtotal": 50.0,
        "tax": 8.0,
        "total": 58.0,
        "total_items": 1,
    }


@pytest.fixture
def mock_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reemplaza httpx.Client por uno con MockTransport."""

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        method = request.method

        # GET /health
        if path == "/health" and method == "GET":
            return httpx.Response(200, json={"status": "healthy"})

        # GET /orders/
        if path == "/orders/" and method == "GET":
            return httpx.Response(200, json=[_sample_order_dict()])

        # POST /orders/
        if path == "/orders/" and method == "POST":
            return httpx.Response(201, json=_sample_order_dict())

        # GET /orders/{id}
        if (
            path.startswith("/orders/")
            and method == "GET"
            and "/confirm" not in path
            and "/cancel" not in path
        ):
            return httpx.Response(200, json=_sample_order_dict())

        # PATCH /orders/{id}/confirm
        if "/confirm" in path and method == "PATCH":
            order = _sample_order_dict()
            order["status"] = "confirmed"
            return httpx.Response(200, json=order)

        # PATCH /orders/{id}/cancel
        if "/cancel" in path and method == "PATCH":
            order = _sample_order_dict()
            order["status"] = "cancelled"
            return httpx.Response(200, json=order)

        return httpx.Response(404)

    original_client = httpx.Client

    def mock_client_factory(*args: object, **kwargs: object) -> httpx.Client:
        return original_client(transport=httpx.MockTransport(handler))

    monkeypatch.setattr(httpx, "Client", mock_client_factory)


# ============================================
# Tests
# ============================================


def test_help() -> None:
    """rickmorty-orders --help muestra los comandos."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "orders" in result.stdout
    assert "health" in result.stdout


def test_orders_help() -> None:
    """orders --help muestra los subcomandos."""
    result = runner.invoke(app, ["orders", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout
    assert "create" in result.stdout
    assert "confirm" in result.stdout


def test_health_ok(mock_transport: None) -> None:
    """health responde OK cuando la API esta corriendo."""
    result = runner.invoke(app, ["health"])
    assert result.exit_code == 0
    assert "API OK" in result.stdout


def test_orders_list(mock_transport: None) -> None:
    """orders list muestra la tabla de ordenes."""
    result = runner.invoke(app, ["orders", "list"])
    assert result.exit_code == 0
    assert "paul@example.com" in result.stdout
    assert "pending" in result.stdout


def test_orders_get(mock_transport: None) -> None:
    """orders get muestra el detalle."""
    result = runner.invoke(app, ["orders", "get", "test-id"])
    assert result.exit_code == 0
    assert "test-id" in result.stdout
    assert "Rick" in result.stdout


def test_orders_create(mock_transport: None) -> None:
    """orders create crea una orden."""
    result = runner.invoke(
        app,
        ["orders", "create", "--email", "paul@example.com", "--character", "1"],
    )
    assert result.exit_code == 0
    assert "Orden creada" in result.stdout


def test_orders_confirm(mock_transport: None) -> None:
    """orders confirm confirma la orden."""
    result = runner.invoke(app, ["orders", "confirm", "test-id"])
    assert result.exit_code == 0
    assert "confirmada" in result.stdout


def test_orders_cancel_con_confirmacion(mock_transport: None) -> None:
    """orders cancel pide confirmacion y cancela con y."""
    result = runner.invoke(app, ["orders", "cancel", "test-id"], input="y\n")
    assert result.exit_code == 0
    assert "cancelada" in result.stdout


def test_orders_cancel_sin_confirmacion(mock_transport: None) -> None:
    """orders cancel no cancela si el usuario dice n."""
    result = runner.invoke(app, ["orders", "cancel", "test-id"], input="n\n")
    # Sale con codigo 0
    assert result.exit_code == 0
    # NO debe aparecer el mensaje de exito "Orden cancelada"
    assert "OK Orden cancelada" not in result.stdout
    # SI debe aparecer el aviso de que el usuario cancelo la operacion
    assert "Operacion cancelada por el usuario" in result.stdout


def test_health_api_caida() -> None:
    """health muestra error cuando la API no responde."""
    # Sin mock: la API no esta corriendo en tests
    result = runner.invoke(app, ["health"])
    assert result.exit_code == 1
    assert "No se pudo conectar" in result.stdout or "ERROR" in result.stdout

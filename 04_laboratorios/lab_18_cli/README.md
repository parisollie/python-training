# Laboratorio 18 — CLI con Typer

CLI (`rickmorty-orders`) que consume la API del proyecto final para gestionar órdenes.

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1
- typer 0.27.3, rich 15.0.0
- La API del proyecto final corriendo en `http://localhost:8000`

## Estructura

El CLI vive dentro del paquete del proyecto final:

    rickmorty_orders/
    └── cli/
        ├── __init__.py
        ├── client.py       # Cliente HTTP hacia la API
        ├── formatters.py   # Tablas y colores con rich
        └── main.py         # App Typer + subcomandos

Entry point registrado en `pyproject.toml`:

    [tool.poetry.scripts]
    rickmorty-orders = "rickmorty_orders.cli.main:app"

## Instalación

    poetry install

Esto registra el comando `rickmorty-orders` en el venv.

## Comandos disponibles

    rickmorty-orders --help
    rickmorty-orders orders --help
    rickmorty-orders health
    rickmorty-orders orders list [--email EMAIL]
    rickmorty-orders orders get ORDER_ID
    rickmorty-orders orders create --email EMAIL --character ID [--quantity N]
    rickmorty-orders orders confirm ORDER_ID
    rickmorty-orders orders cancel ORDER_ID [--reason MOTIVO]

## Cómo usar (paso a paso)

### 1. Arrancar la API (en una terminal)

    cd 05_proyecto_final/rickmorty_orders
    poetry run alembic upgrade head
    poetry run uvicorn rickmorty_orders.infrastructure.api_app:app --host 127.0.0.1 --port 8000

Dejar esta terminal abierta.

### 2. Probar el CLI (en otra terminal)

    # Health check
    poetry run rickmorty-orders health

Salida esperada:

    OK API OK en http://localhost:8000

    # Crear una orden
    poetry run rickmorty-orders orders create \
      --email "paul@example.com" --character 1 --quantity 1

Salida esperada (tabla rich con Rick Sanchez, $58.00 total):

    OK Orden creada: XXXX-XXXX-...
    Orden: XXXX-XXXX-...
    Cliente: paul@example.com
    Status: pending
    ┏━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┓
    ┃ Producto     ┃ Cantidad ┃ Precio unit. ┃ Subtotal ┃
    ...
    Total: $58.00

    # Listar
    poetry run rickmorty-orders orders list

Salida esperada: tabla con todas las órdenes.

    # Obtener detalle (usar el ID del paso anterior)
    poetry run rickmorty-orders orders get <ID>

    # Confirmar
    poetry run rickmorty-orders orders confirm <ID>

    # Cancelar (pide confirmación interactiva y/n)
    poetry run rickmorty-orders orders cancel <ID> --reason "test"

## Variables de entorno

El CLI lee `CLI_API_URL` para apuntar a otra URL de API:

    CLI_API_URL=http://mi-api.com poetry run rickmorty-orders health

Default: `http://localhost:8000`

## Tests del CLI

Los tests usan `typer.testing.CliRunner` + `httpx.MockTransport` (sin API real).

    poetry run pytest 05_proyecto_final/rickmorty_orders/tests/cli/ -v

Salida esperada: `10 passed`.

| Archivo | Qué cubre | Tests |
|---------|-----------|-------|
| test_cli.py | help, health, list, get, create, confirm, cancel | 10 |

## Verificación de calidad

    poetry run ruff check 05_proyecto_final/rickmorty_orders/
    poetry run mypy 05_proyecto_final/rickmorty_orders/

## Estado

- [x] Estructura del CLI (client, formatters, main)
- [x] Subcomandos: health, list, get, create, confirm, cancel
- [x] Entry point `rickmorty-orders`
- [x] Output formateado con rich (tablas, colores)
- [x] Configuración por env var (`CLI_API_URL`)
- [x] 10 tests con CliRunner
- [x] ruff + mypy OK
- [x] Documentación completa

## Referencias

- Typer docs: https://typer.tiangolo.com/
- Rich docs: https://rich.readthedocs.io/
- CliRunner: https://typer.tiangolo.com/tutorial/testing/

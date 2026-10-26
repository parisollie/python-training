# Módulo 20 — Interoperabilidad y ecosistema mixto

## Objetivos
- Definir contratos neutrales entre servicios (Protobuf, OpenAPI)
- Comunicarse entre servicios heterogeneos (gRPC)
- Integrar mensajeria para eventos asincronos (Redis pub/sub)
- Serializar datos con formatos eficientes

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1
- Docker Desktop (opcional, para Redis)
- Dependencias instaladas:
  - `grpcio 1.85.0`
  - `grpcio-tools 1.85.0` (incluye `protoc`)
  - `redis 8.1.0`
  - `types-grpcio` (dev, solo para mypy)

## Estructura

    rickmorty_orders/
    ├── proto/
    │   └── orders.proto              # Contrato neutral (5 RPCs)
    ├── fix_grpc_imports.py           # Idempotente: arregla imports de protoc
    └── src/rickmorty_orders/grpc/
        ├── __init__.py
        ├── orders_pb2.py             # Generado por protoc (mensajes)
        ├── orders_pb2_grpc.py        # Generado por protoc (stub + servicer)
        ├── converters.py             # proto <-> DTO (funciones puras)
        ├── server.py                 # OrderServicer (adaptador delgado)
        └── client.py                 # Cliente de demo

    tests/grpc/
    ├── test_converters.py            # 6 tests (conversiones puras)
    └── test_servicer.py              # 16 tests (5 RPCs + errores)

## El contrato `.proto`

El archivo `proto/orders.proto` define el contrato neutral del servicio.
Cualquier lenguaje (Python, Java, Go, etc.) puede generar stubs a partir
de este archivo y comunicarse con nuestro servidor:

    service OrderService {
      rpc CreateOrder (CreateOrderRequest) returns (OrderResponse);
      rpc GetOrder (GetOrderRequest) returns (OrderResponse);
      rpc ListOrders (ListOrdersRequest) returns (ListOrdersResponse);
      rpc ConfirmOrder (OrderIdRequest) returns (OrderResponse);
      rpc CancelOrder (CancelOrderRequest) returns (OrderResponse);
    }

El servicio **reutiliza los casos de uso reales** del proyecto
(`CreateOrderService`, `GetOrderService`, etc.). El servicer gRPC es
solo un adaptador: convierte proto → DTO, delega al caso de uso,
convierte DTO → proto.

## Regenerar stubs (después de editar el `.proto`)

Si modificas `orders.proto` (agregar un RPC, cambiar un mensaje), hay
que regenerar los stubs de Python:

    cd 05_proyecto_final/rickmorty_orders
    poetry run python -m grpc_tools.protoc \
      -I ./proto \
      --python_out=./src/rickmorty_orders/grpc \
      --grpc_python_out=./src/rickmorty_orders/grpc \
      ./proto/orders.proto
    poetry run python fix_grpc_imports.py
    cd ../..

**¿Por qué `fix_grpc_imports.py`?**

`protoc` genera `orders_pb2_grpc.py` con un import absoluto:

    import orders_pb2 as orders__pb2

Pero nuestro paquete se llama `rickmorty_orders.grpc`, así que ese
import falla en runtime. El script reescribe el import a:

    from rickmorty_orders.grpc import orders_pb2 as orders__pb2

Es **idempotente**: si ya está arreglado, no hace nada.

## Cómo usar (paso a paso)

Este módulo necesita **dos terminales al mismo tiempo**: una para el
servidor gRPC (que se queda escuchando) y otra para el cliente de demo.

### Cómo abrir dos terminales en macOS

**Opción 1 — dos pestañas en Terminal.app:**

1. `⌘ + Espacio` → escribe `Terminal` → Enter
2. `⌘ + T` → nueva pestaña (ahora tienes 2)
3. Cambiar entre pestañas: `⌘ + ⇧ + ]` y `⌘ + ⇧ + [`

**Opción 2 — dos ventanas:**

1. Terminal.app → `⌘ + N` → nueva ventana

**Opción 3 — VS Code / iTerm2:**

Abrir una pestaña nueva de terminal (`⌘ + ` ` en VS Code).

En **ambas terminales** debes estar en la raíz del repo
(`~/Desktop/python-training`).

### 1. Arrancar el servidor gRPC (Terminal 1)

    cd ~/Desktop/python-training
    poetry run python -m rickmorty_orders.grpc.server

Salida esperada:

    INFO:__main__:gRPC server escuchando en puerto 50051

**Dejar esta terminal abierta.** El servidor se queda bloqueado
(igual que `uvicorn`). No es un error, es lo esperado.

Al arrancar, el servidor crea las tablas en SQLite si no existen
(`Base.metadata.create_all`). Es idempotente: no borra datos existentes.

### 2. Probar el cliente de demo (en otra terminal)

    cd ~/Desktop/python-training
    poetry run python -m rickmorty_orders.grpc.client

Salida esperada (flujo completo, ~40 líneas):

    Conectando a localhost:50051 ...

    === CreateOrder ===
      id:          <uuid>
      email:       demo-xxxxxxxx@example.com
      status:      pending
      subtotal:    150.00
      tax:         24.00
      total:       174.00
      total_items: 3
        - [1] Rick Sanchez x2 @ 50.00 = 100.00
        - [2] Morty Smith x1 @ 50.00 = 50.00

    === GetOrder ===
      ... (mismos datos)

    === ListOrders ===
      total encontradas: 1

    === ConfirmOrder ===
      ...
      status:      confirmed

    === CancelOrder ===
      ...
      status:      cancelled

    [ERROR] CancelOrder x2 (esperado: FAILED_PRECONDITION) -> FAILED_PRECONDITION: La orden ya esta cancelada

**La última línea es la prueba de que funciona.** El "error" es
intencional: el dominio rechaza cancelar una orden ya cancelada. La
regla `CONFIRMED -> CANCELLED` sí está permitida; `CANCELLED -> CANCELLED`
no.

### 3. Apagar el servidor

En **Terminal 1**: `Ctrl + C`.

## Manejo de errores: dominio -> status codes gRPC

El servicer traduce errores de dominio a **status codes de gRPC**,
que cualquier cliente (Python, Java, Go) puede interpretar:

| Error de dominio | Status code gRPC |
|---|---|
| `OrderNotFoundError` | `NOT_FOUND` |
| `CharacterNotFoundError` | `NOT_FOUND` |
| `InvalidStatusTransitionError` | `FAILED_PRECONDITION` |
| `pydantic.ValidationError` | `INVALID_ARGUMENT` |
| `Exception` (catch-all) | `INTERNAL` |

## Decisiones de diseño

**1. Adaptador delgado, casos de uso intactos.**

`OrderServicer` no reimplementa nada: convierte proto → DTO, delega al
caso de uso real, convierte DTO → proto, traduce errores. Toda la lógica
vive en `application/` y `domain/`, igual que en FastAPI y CLI.

**2. `create_all` en vez de Alembic en el servicer.**

El `init_db()` del proyecto es **no-op** por diseño (las tablas se
crean vía Alembic). Como el servidor gRPC debe ser **autosuficiente**
(no depender del CWD ni de correr migraciones antes), en
`OrderServicer.__init__` hacemos:

    Base.metadata.create_all(get_engine())

`create_all` es idempotente. Alembic sigue siendo el camino de
producción para migraciones futuras.

**3. La URL de SQLite es relativa al CWD.**

`database_url = "sqlite:///./rickmorty_orders.db"` es **relativa al
CWD**. Si corres el server desde la raíz del repo, la DB vive en
`./rickmorty_orders.db`. Para producción, usar `RMO_DATABASE_URL` con
una URL absoluta o PostgreSQL.

**4. Excepciones de ruff y mypy para los stubs generados.**

`orders_pb2.py` y `orders_pb2_grpc.py` no tienen tipos (los genera
protoc). En `pyproject.toml`:

    [tool.ruff.lint.per-file-ignores]
    "**/orders_pb2.py" = ["E501"]
    "**/orders_pb2_grpc.py" = ["N802", "E501"]
    "**/grpc/server.py" = ["N802"]

    [[tool.mypy.overrides]]
    module = ["rickmorty_orders.grpc.orders_pb2", "rickmorty_orders.grpc.orders_pb2_grpc"]
    ignore_missing_imports = true
    follow_imports = "skip"

En `server.py`, un `# type: ignore[misc]` justificado:

    class OrderServicer(orders_pb2_grpc.OrderServiceServicer):  # type: ignore[misc]

`N802` en `server.py` está ignorado porque gRPC **obliga** a CamelCase
en los nombres de RPC (los define el `.proto`). Renombrarlos rompería
el `stub.CreateOrder(...)` del cliente.

## Tests

Los tests no necesitan red, ni servidor levantado, ni SQLite real:
usan las fixtures en memoria del `conftest.py` (`memory_repo`,
`memory_chars`, `fake_notifier`, `fake_event_bus`) y un `FakeContext`
que captura `abort()`.

    poetry run pytest 05_proyecto_final/rickmorty_orders/tests/grpc/ -v

Salida esperada: `22 passed`.

| Archivo | Qué cubre | Tests |
|---------|-----------|-------|
| test_converters.py | proto ↔ DTO, email inválido | 6 |
| test_servicer.py | 5 RPCs (OK + errores) | 16 |

Total en el proyecto: **162 tests** (antes 140, +22 de este módulo).

## Verificación de calidad

    poetry run ruff check 05_proyecto_final/rickmorty_orders/src/rickmorty_orders/grpc/
    poetry run mypy 05_proyecto_final/rickmorty_orders/src/rickmorty_orders/grpc/server.py \
                   05_proyecto_final/rickmorty_orders/src/rickmorty_orders/grpc/converters.py \
                   05_proyecto_final/rickmorty_orders/src/rickmorty_orders/grpc/client.py

Ambos deben reportar "All checks passed!" / "Success: no issues found".

## Estado

- [x] Instalar `grpcio`, `grpcio-tools`, `redis`, `types-grpcio`
- [x] Definir `proto/orders.proto` (5 RPCs)
- [x] Generar stubs con `protoc`
- [x] Script `fix_grpc_imports.py` para arreglar imports
- [x] `converters.py` (proto ↔ DTO)
- [x] `OrderServicer` (adaptador delgado, 5 RPCs)
- [x] `client.py` (cliente de demo end-to-end)
- [x] `create_all` en `__init__` (servidor autosuficiente)
- [x] Manejo de errores dominio → gRPC (NOT_FOUND, INVALID_ARGUMENT, FAILED_PRECONDITION, INTERNAL)
- [x] 22 tests (sin red, sin SQLite real)
- [x] Excepciones de ruff/mypy documentadas
- [x] ruff + mypy OK
- [x] Documentación completa

## Qué quedó pendiente (fuera de alcance)

- **Redis pub/sub**: se instaló `redis` y se documentó el patrón, pero
  no se implementó el publicador ni el consumidor. El proyecto ya
  publica eventos con `InMemoryEventBus` (ver
  `infrastructure/event_bus.py`); migrar a Redis sería un módulo extra.
- **Autenticación gRPC**: los RPCs no piden credenciales. En producción
  se usaría un interceptor con JWT (el proyecto ya tiene `secret_key`
  en config).
- **Streaming bidireccional**: el contrato define solo unary RPCs. El
  protocolo soporta streaming, pero no lo ejercitamos.

## Referencias

- gRPC Python docs: https://grpc.io/docs/languages/python/
- Protobuf docs: https://protobuf.dev/
- redis-py: https://redis-py.readthedocs.io/
- grpc_testing: https://grpc.github.io/grpc/python/grpc_testing.html
- RabbitMQ: https://www.rabbitmq.com/
- Kafka: https://kafka.apache.org/

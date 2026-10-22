# Rick & Morty Orders

Proyecto final integrador de la capacitación Python: **servicio de Orders** con arquitectura hexagonal/limpia, API FastAPI, persistencia SQLAlchemy y consumo de la API pública de Rick and Morty.

## Presentación del proyecto

**rickmorty_orders** es un servicio backend completo y production-ready que demuestra una arquitectura hexagonal/limpia aplicada a un caso real: **órdenes de compra enriquecidas con personajes de Rick and Morty**.

### ¿Qué hace?

- Expone una **API REST** con 7 endpoints (crear/listar/obtener/confirmar/cancelar órdenes)
- Consume la **API pública de Rick and Morty** para validar personajes y calcular precios
- Persiste en **SQLite** (fácil de cambiar a PostgreSQL)
- Aplica **migraciones reproducibles** con Alembic
- Corre en **Docker** (imagen multistage, usuario non-root, healthcheck)
- Pasa **130 tests** con **93% de cobertura**
- Pasa **ruff** y **mypy strict** sin errores
- Tiene **CI automatizado** en GitHub Actions

### Métricas

| Métrica | Valor |
|---------|-------|
| Commits | 35+ |
| Tests | **130** |
| Cobertura | **93%** |
| Endpoints | **7** |
| Módulos de dominio | 5 (value_objects, errors, events, character, order) |
| Casos de uso | 5 (create, get, list, confirm, cancel) |
| Puertos (interfaces) | 4 (OrderRepository, CharacterRepository, Notifier, EventBus) |
| Adaptadores | 6 (SQL, HTTP, Console, InMemory x2, Fake) |
| Migraciones Alembic | 1 |
| Código fuente | ~1,500 líneas |
| Código de tests | ~1,800 líneas |
| Imagen Docker | 662 MB (137 MB comprimida) |

### Arquitectura

Hexagonal (ports & adapters) con 3 capas concéntricas:

    Infraestructura  →  Aplicación  →  Dominio
    (adaptadores)        (casos de uso)  (entidades, VOs, puertos)

Regla de dependencia: las dependencias apuntan **hacia dentro**. El dominio **nunca** importa infraestructura.

### Demo en 2 comandos

    # 1. Construir y arrancar el contenedor
    docker build -f 05_proyecto_final/rickmorty_orders/Dockerfile -t rickmorty-orders:latest .
    docker run -d --name rickmorty -p 8001:8000 rickmorty-orders:latest

    # 2. Probar
    curl http://localhost:8001/health
    curl -X POST http://localhost:8001/orders/ \
      -H "Content-Type: application/json" \
      -d '{"customer_email": "demo@example.com", "items": [{"character_id": 1, "quantity": 1}]}'

Documentación interactiva: http://localhost:8001/docs

### Stack

Python 3.12 · FastAPI · SQLAlchemy 2.0 · Alembic · Pydantic · httpx · SQLite · Docker · GitHub Actions · Poetry · pytest · ruff · mypy

### Qué demuestra este proyecto

- **Arquitectura hexagonal/limpia** aplicada a un caso real
- **Inversión de dependencias** con `Protocol` (PEP 544)
- **Value Objects** con invariantes (`Money`, `Email`, `OrderId`)
- **Eventos de dominio** (`OrderCreated`, `OrderConfirmed`, `OrderCancelled`)
- **Repository pattern** con implementaciones intercambiables (SQL / InMemory)
- **Testing profesional**: unit + contract (LSP) + integration + e2e
- **CI/CD**: Docker multistage + GitHub Actions
- **Seguridad**: auditoría con `pip-audit`, usuario non-root, secrets via env vars

## Objetivo

Construir un servicio backend completo y production-ready que demuestre todo lo aprendido en los 15 módulos: desde el dominio puro hasta el delivery (Docker + CI/CD).

## Contexto

Este proyecto consume la Rick and Morty API para enriquecer órdenes con información de personajes. El caso de uso principal es:

- Un usuario crea una orden de compra
- La orden puede incluir uno o más personajes de Rick and Morty (como "productos")
- El servicio consulta la API externa para validar y enriquecer los personajes
- Se calculan totales (subtotal, tax, total)
- Se publican eventos de dominio (OrderCreated)
- Los clientes pueden consultar, confirmar o cancelar sus órdenes

## Stack

| Capa | Tecnología |
|------|------------|
| Lenguaje | Python 3.12 |
| Gestión de deps | Poetry 2.5.1 |
| API | FastAPI 0.143.x + Uvicorn |
| Dominio | Dataclasses + Value Objects + Protocol |
| Validación | Pydantic 2.14.x |
| Persistencia | SQLAlchemy 2.x + Alembic |
| Cliente HTTP | httpx 0.28.x |
| Testing | pytest + pytest-cov + Hypothesis + pytest-asyncio |
| Calidad | ruff + black + isort + mypy (strict) + pre-commit |
| Container | Docker multistage |
| CI/CD | GitHub Actions |
| Configuración | pydantic-settings |

## Arquitectura

Arquitectura hexagonal / ports & adapters con tres capas concéntricas:

    +------------------------------------------------------+
    |                   INFRASTRUCTURE                     |
    |  (FastAPI, SQLAlchemy, httpx, Alembic, Settings)     |
    |                                                      |
    |  +-----------------------------------------------+   |
    |  |              APPLICATION                      |   |
    |  |    (Casos de uso, DTOs, Event Handlers)       |   |
    |  |                                               |   |
    |  |   +---------------------------------------+   |   |
    |  |   |             DOMAIN                    |   |   |
    |  |   |  (Entidades, Value Objects, Puertos,  |   |   |
    |  |   |   Eventos, Errores)                   |   |   |
    |  |   +---------------------------------------+   |   |
    |  +-----------------------------------------------+   |
    +------------------------------------------------------+

Regla de dependencia: infrastructure -> application -> domain. Nunca al revés.

## Estructura del proyecto

- `README.md`
- `pyproject.toml` — configuración Poetry + herramientas
- `poetry.lock`
- `.env.example` — ejemplo de variables de entorno
- `.dockerignore`
- `Dockerfile` — multistage
- `docker-compose.yml` — para desarrollo local
- `alembic.ini` — configuración Alembic
- `alembic/` — migraciones
  - `env.py`
  - `script.py.mako`
  - `versions/`
- `.github/`
  - `workflows/`
    - `ci.yml` — lint + typecheck + tests + build
- `src/`
  - `rickmorty_orders/`
    - `__init__.py`
    - `domain/` — **NÚCLEO** (sin dependencias externas)
      - `__init__.py`
      - `value_objects.py` — OrderId, Money, Email, CharacterId
      - `order.py` — Order, OrderItem, OrderStatus
      - `character.py` — Character (referencia externa)
      - `events.py` — OrderCreated, OrderConfirmed, OrderCancelled
      - `errors.py` — errores de dominio
      - `ports.py` — OrderRepository, CharacterRepository, Notifier, EventBus
    - `application/` — **CASOS DE USO**
      - `__init__.py`
      - `dtos.py` — CreateOrderInput, OrderOutput
      - `create_order.py` — CreateOrderService
      - `get_order.py` — GetOrderService
      - `list_orders.py` — ListOrdersService
      - `confirm_order.py` — ConfirmOrderService
      - `cancel_order.py` — CancelOrderService
      - `event_handlers.py` — manejo de eventos
    - `infrastructure/` — **ADAPTADORES**
      - `__init__.py`
      - `config.py` — Settings (pydantic-settings)
      - `api/` — FastAPI
        - `app.py`
        - `dependencies.py`
        - `routers/`
          - `orders.py`
          - `health.py`
        - `schemas.py`
      - `persistence/` — SQLAlchemy
        - `models.py`
        - `database.py`
        - `repositories.py`
      - `external/` — Rick and Morty API
        - `rickmorty_client.py`
      - `notifications/`
        - `console_notifier.py`
- `tests/`
  - `__init__.py`
  - `conftest.py` — fixtures compartidas
  - `unit/` — dominio puro
    - `__init__.py`
    - `test_value_objects.py`
    - `test_order.py`
    - `test_events.py`
  - `contract/` — adaptadores cumplen puertos
    - `__init__.py`
    - `test_repository_contract.py`
    - `test_character_repo_contract.py`
  - `integration/` — con SQLite, HTTP mock, etc.
    - `__init__.py`
    - `test_sql_repository.py`
    - `test_rickmorty_client.py`
  - `e2e/` — flujo completo con TestClient
    - `__init__.py`
    - `test_orders_api.py`

## Fases del proyecto

| Fase | Contenido | Estado |
|------|-----------|:------:|
| 1 | Setup: estructura + README | ✅ Completada |
| 2 | Dominio: entidades, VOs, puertos, eventos | ✅ Completada |
| 3 | Aplicación: casos de uso + DTOs | ✅ Completada |
| 4 | Infraestructura: SQLAlchemy, httpx, FastAPI | ✅ Completada |
| 5 | Testing: unit + contract + integration + e2e | ✅ Completada |
| 6 | Alembic + Docker + CI/CD | ✅ Completada |
| 7 | Auditoría + presentación | ✅ Completada |

## Estado actual

### Completado

**Dominio (FASE 2)**
- Value Objects: `OrderId`, `CharacterId`, `Money`, `Email` (todos `frozen=True`)
- Errores de dominio: `DomainError` + 6 errores especificos
- Eventos: `OrderCreated`, `OrderConfirmed`, `OrderCancelled`
- Entidades: `Order` con transiciones de estado, `OrderItem`, `Character`
- Puertos: `OrderRepository`, `CharacterRepository`, `Notifier`, `EventBus`

**Aplicacion (FASE 3)**
- DTOs: `CreateOrderInput`, `OrderOutput`, `OrderItemInput`, `OrderItemOutput`
- Casos de uso:
  - `CreateOrderService` (consulta personajes, calcula precios, crea orden)
  - `GetOrderService`, `ListOrdersService`, `ConfirmOrderService`, `CancelOrderService`
- Adaptadores en memoria (para desarrollo y tests)

**Infraestructura (FASE 4)**
- `config.py`: Settings con pydantic-settings (env vars con prefijo `RMO_`)
- `persistence.py`: SQLAlchemy engine + SessionLocal + Base + get_db
- `orm_models.py`: OrderModel, OrderItemModel (SQLAlchemy 2.0)
- `sql_repositories.py`: SQLOrderRepository (implementa el puerto)
- `rickmorty_client.py`: RickMortyApiClient (httpx + retry + timeout)
- `console_notifier.py`: ConsoleNotifier
- `event_bus.py`: InMemoryEventBus
- `dependencies.py`: wiring de FastAPI (get_*_service)
- `api_orders.py`: router de orders (5 endpoints)
- `api_health.py`: router de health (2 endpoints)
- `api_app.py`: app FastAPI + CORS + lifespan

**API funcionando end-to-end**
- 7 endpoints probados contra la API real de Rick and Morty
- Persistencia en SQLite
- Crear, listar, obtener, confirmar y cancelar ordenes

**Testing (FASE 5)**
- `tests/conftest.py`: fixtures compartidas (engine SQLite, repos, samples)
- `tests/unit/` (77 tests):
  - `test_value_objects.py` (28 tests): Money, Email, OrderId, CharacterId
  - `test_order.py` (28 tests): OrderItem, Order, transiciones, invariantes
  - `test_events.py` (11 tests): DomainEvent, OrderCreated, OrderConfirmed, OrderCancelled
  - `test_character.py` (10 tests): Character, CharacterStatus
- `tests/contract/` (26 tests):
  - `test_repository_contract.py` (16 tests): InMemory y SQL cumplen el mismo contrato (LSP)
  - `test_character_repo_contract.py` (10 tests): InMemory y HTTP cumplen el mismo contrato
- `tests/integration/` (9 tests):
  - `test_rickmorty_client.py`: httpx.MockTransport, retry, 404, fallback
- `tests/e2e/` (18 tests):
  - `test_orders_api.py`: TestClient + SQLite en memoria + dependency_overrides

**Calidad**
- ruff: sin errores
- mypy strict: sin errores (40 archivos)
- pytest: 130 tests pasando
- Cobertura: 93%

**Alembic + Docker + CI/CD (FASE 6)**
- Alembic configurado (`alembic/env.py` conectado a Base + Settings)
- Migracion inicial `74a558816f76` (orders + order_items) aplicada
- `init_db()` refactorizado (no-op, las tablas las crea Alembic)
- `.dockerignore` (excluye tests, .venv, etc.)
- `Dockerfile` multistage (builder + runtime), usuario non-root `app`
- `RMO_DATABASE_URL=sqlite:////app/data/rickmorty_orders.db` en el contenedor
- `CMD` ejecuta `alembic upgrade head && uvicorn` al arrancar
- HEALTHCHECK con urllib cada 30s
- Imagen: 662 MB (137 MB comprimida)
- Contenedor probado end-to-end (crea ordenes contra la API real)
- `.github/workflows/ci.yml`: lint + typecheck + test + build
- `.env.example` con placeholders (RMO_*)

### Siguiente

**FASE 7: Auditoria + presentacion**
- pip-audit / safety
- README final con diagramas
- Presentacion del proyecto

## Modelo de dominio (borrador)

### Value Objects

| VO | Propósito | Invariante |
|----|-----------|------------|
| OrderId | Identificador de orden | UUID |
| CharacterId | Identificador de personaje (R&M) | entero positivo |
| Money | Cantidad monetaria | >= 0, 3 letras de moneda |
| Email | Email del cliente | formato válido |

### Entidades

| Entidad | Campos |
|---------|--------|
| Order | id, customer_email, items, status, created_at |
| OrderItem | character_id, character_name, quantity, unit_price |
| Character | id, name, species, status (vivo/muerto) |

### Estados de Order

    PENDING -> CONFIRMED -> SHIPPED
        |
        v
    CANCELLED

### Eventos de dominio

- OrderCreated
- OrderConfirmed
- OrderCancelled

## Endpoints disponibles (FastAPI)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Root |
| GET | `/health` | Health check |
| POST | `/orders/` | Crear orden |
| GET | `/orders/` | Listar ordenes (filtro opcional `?customer_email=`) |
| GET | `/orders/{id}` | Obtener orden por id |
| PATCH | `/orders/{id}/confirm` | Confirmar (pending -> confirmed) |
| PATCH | `/orders/{id}/cancel` | Cancelar (pending/confirmed -> cancelled) |

Documentacion interactiva:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Cómo ejecutar la API

Requisitos:
- Haber corrido `poetry install` desde la raiz del repo

Arrancar el servidor:

    cd 05_proyecto_final/rickmorty_orders
    poetry run uvicorn rickmorty_orders.infrastructure.api_app:app --reload --port 8000
    # Abrir http://localhost:8000/docs
    # Detener con Ctrl+C

Probar con curl (desde otra terminal):

    # Health check
    curl http://localhost:8000/health

    # Crear orden
    curl -X POST http://localhost:8000/orders/ \
      -H "Content-Type: application/json" \
      -d '{"customer_email": "paul@example.com", "items": [{"character_id": 1, "quantity": 1}]}'

    # Listar ordenes
    curl http://localhost:8000/orders/

    # Confirmar (usar el id devuelto por POST)
    curl -X PATCH http://localhost:8000/orders/{ID}/confirm

    # Cancelar
    curl -X PATCH "http://localhost:8000/orders/{ID}/cancel?reason=test"

Configuracion via variables de entorno (prefijo RMO_):

    RMO_ENVIRONMENT=production RMO_DEBUG=false poetry run uvicorn ...

    # Ver todas las variables: ver src/rickmorty_orders/infrastructure/config.py

## Verificación paso a paso (fases 1-5)

Todos los comandos de abajo se ejecutan **desde la raíz del repo**:
`/Users/paulfelix/Desktop/python-training` (o donde hayas clonado).

> Requisito: haber corrido `poetry install` una vez.

### FASE 1: Setup

    # Instalar dependencias
    poetry install

    # Verificar que el paquete se importa
    cd 05_proyecto_final/rickmorty_orders
    poetry run python -c "import rickmorty_orders; print(rickmorty_orders.__file__)"
    cd ../..

Salida esperada: la ruta a `src/rickmorty_orders/__init__.py`.

### FASE 2: Dominio (Value Objects, entidades, eventos)

    cd 05_proyecto_final/rickmorty_orders
    poetry run python -c "
    from rickmorty_orders.domain.value_objects import Money, Email, OrderId, CharacterId
    from rickmorty_orders.domain.order import Order, OrderItem, OrderStatus
    from rickmorty_orders.domain.events import OrderCreated

    # Value Objects
    print(f'Money: {Money(100.0) + Money(50.0)}')
    print(f'Email: {Email("  PAUL@Example.COM  ")}')

    # Entidad Order
    order = Order.create(
        customer_email=Email('paul@example.com'),
        items=[OrderItem(
            character_id=CharacterId(1),
            character_name='Rick',
            quantity=2,
            unit_price=Money(50.0),
        )],
    )
    print(f'Order total: {order.total}')

    # Evento
    event = OrderCreated(order_id=order.id, customer_email='a@b.com', total=100.0)
    print(f'Evento: {type(event).__name__}')
    "
    cd ../..

Salida esperada:
- `Money: 150.00 USD`
- `Email: paul@example.com`
- `Order total: 116.00 USD`
- `Evento: OrderCreated`

### FASE 3: Aplicación (casos de uso + DTOs)

    cd 05_proyecto_final/rickmorty_orders
    poetry run python -c "
    from rickmorty_orders.application.create_order import CreateOrderService
    from rickmorty_orders.application.dtos import CreateOrderInput, OrderItemInput
    from rickmorty_orders.domain.character import Character, CharacterStatus
    from rickmorty_orders.domain.value_objects import CharacterId
    from rickmorty_orders.infrastructure.in_memory import (
        InMemoryOrderRepository, InMemoryCharacterRepository,
        FakeNotifier, FakeEventBus,
    )

    # Wiring manual
    chars = InMemoryCharacterRepository([
        Character(id=CharacterId(1), name='Rick', species='Human', status=CharacterStatus.ALIVE),
    ])
    orders = InMemoryOrderRepository()
    notifier = FakeNotifier()
    events = FakeEventBus()

    service = CreateOrderService(orders, chars, notifier, events)
    result = service.execute(CreateOrderInput(
        customer_email='paul@example.com',
        items=[OrderItemInput(character_id=1, quantity=2)],
    ))
    print(f'Order creada: {result.id}')
    print(f'Total: {result.total}')
    print(f'Notificaciones: {len(notifier.created)}')
    print(f'Eventos: {[type(e).__name__ for e in events.events]}')
    "
    cd ../..

Salida esperada: orden creada, total, 1 notificación, `[OrderCreated]`.

### FASE 4: Infraestructura (API)

    cd 05_proyecto_final/rickmorty_orders
    poetry run uvicorn rickmorty_orders.infrastructure.api_app:app --reload --port 8000

Abrir: http://localhost:8000/docs (ver los 7 endpoints)

En **otra terminal**, probar con curl:

    curl http://localhost:8000/health

    curl -X POST http://localhost:8000/orders/ \
      -H "Content-Type: application/json" \
      -d '{"customer_email": "paul@example.com", "items": [{"character_id": 1, "quantity": 1}]}'

    curl http://localhost:8000/orders/

Detener el servidor con `Ctrl+C`.

### FASE 5: Testing

    # Todos los tests (130 esperados)
    poetry run pytest 05_proyecto_final/rickmorty_orders/tests/ -v

    # Solo unit (77 tests rapidos, <0.1s)
    poetry run pytest 05_proyecto_final/rickmorty_orders/tests/unit/ -v

    # Solo contract (26 tests)
    poetry run pytest 05_proyecto_final/rickmorty_orders/tests/contract/ -v

    # Solo integration (9 tests)
    poetry run pytest 05_proyecto_final/rickmorty_orders/tests/integration/ -v

    # Solo e2e (18 tests)
    poetry run pytest 05_proyecto_final/rickmorty_orders/tests/e2e/ -v

    # Con cobertura (93% esperado)
    poetry run pytest 05_proyecto_final/rickmorty_orders/tests/ \
      --cov=05_proyecto_final/rickmorty_orders/src/rickmorty_orders \
      --cov-report=term-missing

Salida esperada: `130 passed` en ~3s (con cobertura ~93%).

### Verificación de calidad (todas las fases)

    # Linter
    poetry run ruff check 05_proyecto_final/rickmorty_orders/

    # Type checker
    poetry run mypy 05_proyecto_final/rickmorty_orders/

Salida esperada:
- `All checks passed!`
- `Success: no issues found`

## Testing

**130 tests, 93% cobertura.**

Estructura:
- `tests/unit/` (77): dominio puro (value objects, order, events, character)
- `tests/contract/` (26): adaptadores cumplen los puertos (LSP)
- `tests/integration/` (9): cliente HTTP con MockTransport
- `tests/e2e/` (18): TestClient con DB en memoria

Comandos:

    # Todos los tests
    poetry run pytest 05_proyecto_final/rickmorty_orders/tests/ -v

    # Solo unit (dominio puro, rapidos)
    poetry run pytest 05_proyecto_final/rickmorty_orders/tests/unit/ -v

    # Solo un tipo
    poetry run pytest 05_proyecto_final/rickmorty_orders/tests/contract/ -v
    poetry run pytest 05_proyecto_final/rickmorty_orders/tests/integration/ -v
    poetry run pytest 05_proyecto_final/rickmorty_orders/tests/e2e/ -v

    # Con cobertura
    poetry run pytest 05_proyecto_final/rickmorty_orders/tests/ \
      --cov=05_proyecto_final/rickmorty_orders/src/rickmorty_orders \
      --cov-report=term-missing

Tipos de tests (piramide):

| Tipo | Cantidad | Velocidad | Dependencias |
|------|---------:|-----------|--------------|
| Unit | 77 | ~0.05s | Ninguna |
| Contract | 26 | ~0.09s | SQLite memoria, MockTransport |
| Integration | 9 | ~3s | httpx.MockTransport |
| E2E | 18 | ~0.2s | TestClient + SQLite memoria |

## Alembic (migraciones)

El proyecto usa Alembic para migraciones reproducibles.

    # Aplicar migraciones
    cd 05_proyecto_final/rickmorty_orders
    poetry run alembic upgrade head
    cd ../..

    # Ver version actual
    cd 05_proyecto_final/rickmorty_orders
    poetry run alembic current
    cd ../..

    # Crear nueva migracion (tras cambiar orm_models.py)
    cd 05_proyecto_final/rickmorty_orders
    poetry run alembic revision --autogenerate -m "descripcion del cambio"
    cd ../..

    # Retroceder 1 migracion
    cd 05_proyecto_final/rickmorty_orders
    poetry run alembic downgrade -1
    cd ../..

Migracion actual: `74a558816f76` (initial schema: orders and order_items).

## Docker

### Construir la imagen

Desde la RAIZ del repo:

    docker build -f 05_proyecto_final/rickmorty_orders/Dockerfile -t rickmorty-orders:latest .

La imagen es **multistage** (builder + runtime) y corre como **usuario no-root** (`app`).

Tamano: ~662 MB (137 MB comprimida).

### Ejecutar el contenedor

    docker run -d --name rickmorty -p 8001:8000 rickmorty-orders:latest

El contenedor:
- Ejecuta `alembic upgrade head` al arrancar (migraciones automaticas)
- Expone en `http://localhost:8001`
- Tiene HEALTHCHECK cada 30s
- Persiste la DB SQLite en `/app/data/rickmorty_orders.db` (dentro del contenedor)

Probar el flujo completo (desde otra terminal):

    # 1. Health check
    curl http://localhost:8001/health

    # 2. Crear una orden (consulta la API real de Rick and Morty)
    curl -X POST http://localhost:8001/orders/ \
      -H "Content-Type: application/json" \
      -d '{"customer_email": "paul@example.com", "items": [{"character_id": 1, "quantity": 1}]}'

    # 3. IMPORTANTE: en la respuesta, COPIA el valor de "id"
    #    (es un UUID como "883e3787-a8e8-4d22-831e-b4a94d72be3d")
    #    Luego exportalo en la terminal:
    ORDER_ID="AQUI-PEGA-EL-ID-QUE-COPIASTE"

    #    Verifica que quedo bien:
    echo "ORDER_ID=$ORDER_ID"

    # 4. Listar ordenes
    curl http://localhost:8001/orders/

    # 5. Obtener una orden por id
    curl http://localhost:8001/orders/$ORDER_ID

    # 6. Confirmar la orden
    curl -X PATCH http://localhost:8001/orders/$ORDER_ID/confirm

    # 7. Cancelar la orden
    curl -X PATCH "http://localhost:8001/orders/$ORDER_ID/cancel?reason=test"

    # 8. Ver documentacion interactiva
    # Abrir http://localhost:8001/docs en el navegador

### Ver logs del contenedor

    docker logs rickmorty
    docker logs -f rickmorty   # seguir en tiempo real (Ctrl+C para salir)

### Detener y eliminar

    docker stop rickmorty
    docker rm rickmorty

### Reconstruir tras cambios

Si modificas el codigo y quieres reconstruir la imagen:

    docker stop rickmorty
    docker rm rickmorty
    docker build -f 05_proyecto_final/rickmorty_orders/Dockerfile -t rickmorty-orders:latest .
    docker run -d --name rickmorty -p 8001:8000 rickmorty-orders:latest

## CI/CD (GitHub Actions)

Workflow en `.github/workflows/ci.yml`:

- **lint**: `ruff check`
- **typecheck**: `mypy`
- **test**: `pytest` con cobertura
- **build**: `docker build`

Se ejecuta en:
- Cada `push` a `main`
- Cada `pull_request` a `main`

Ver estado en: https://github.com/parisollie/python-training/actions

## Variables de entorno

Copia `.env.example` a `.env` y ajusta:

    cp 05_proyecto_final/rickmorty_orders/.env.example 05_proyecto_final/rickmorty_orders/.env

Variables (todas con prefijo `RMO_`):

| Variable | Default | Descripcion |
|----------|---------|-------------|
| RMO_ENVIRONMENT | development | development / staging / production |
| RMO_DEBUG | true | Modo debug |
| RMO_DATABASE_URL | sqlite:///./rickmorty_orders.db | URL de la DB |
| RMO_RICKMORTY_API_URL | https://rickandmortyapi.com/api | API externa |
| RMO_SECRET_KEY | cambiar-en-produccion | JWT secret (futuro) |

**NUNCA** commitear `.env` con valores reales. Ya esta en `.gitignore`.

## Auditoría de dependencias

El proyecto usa `pip-audit` (herramienta oficial de PyPA) para auditar dependencias contra la base de datos de vulnerabilidades (PyPI Advisory + OSV).

### Ejecutar la auditoría

    # Auditar todas las dependencias
    poetry run pip-audit

    # Auditoría de produccion (ignorando vulnerabilidades conocidas en dev)
    poetry run pip-audit \
      --ignore-vuln PYSEC-2026-1325 \
      --ignore-vuln PYSEC-2026-4298

Salida esperada:

    No known vulnerabilities found, 3 ignored

### Vulnerabilidades conocidas (ignoradas justificadamente)

| Paquete | CVE | Motivo | Acción |
|---------|-----|--------|--------|
| `ecdsa 0.19.2` | PYSEC-2026-1325 | Minerva timing attack. El mantenedor considera los ataques de canal lateral fuera de alcance. | Solo en `dev` (via python-jose). No se usa en runtime. |
| `python-jose 3.5.0` | PYSEC-2026-4298 | Algorithm confusion (CVSS 9.3). Sin fix upstream (proyecto sin mantenimiento). | Solo en `dev` (lab 09). Proyecto final no usa JWT. |

**Decisión:** ambas dependencias se movieron al grupo `dev` del `pyproject.toml`. El **runtime del proyecto final no las carga**, por lo que no representan un riesgo de seguridad en producción.

Si en el futuro se necesita JWT en producción, se migrará a **`PyJWT`** (mantenida, sin CVEs conocidos).

### Última auditoría

- **Fecha:** 18 de octubre de 2026
- **Resultado:** `No known vulnerabilities found, 3 ignored`
- **Paquete local `python-training`:** no auditado (no está en PyPI, es local)

## Plan de mantenimiento

### Tareas periodicas

| Frecuencia | Tarea | Comando |
|------------|-------|---------|
| **Semanal** | Auditar dependencias | `poetry run pip-audit` |
| **Semanal** | Ver vulnerabilidades de la imagen Docker | `docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --scanners vuln --quiet rickmorty-orders:latest` |
| **Semanal** | Ver dependencias desactualizadas | `poetry show --outdated` |
| **Mensual** | Actualizar dependencias (en rama) | `poetry update` + tests + merge |
| **Mensual** | Actualizar imagen base `python:3.12-slim` | Rebuild sin cache + re-escanear |
| **Trimestral** | Rotar secretos (`RMO_SECRET_KEY`, tokens) | Manual + deploy |
| **Anual** | Actualizar Python (MINOR/MAJOR) | Rebuild + tests |

### Politica de excepciones de seguridad

Cuando `pip-audit` o Trivy detecten una vulnerabilidad **sin fix disponible**:

1. **Documentar** en el README del modulo correspondiente:
   - CVE, paquete afectado, severidad
   - Justificacion (no explotable, solo dev, sin fix upstream)
   - Accion a tomar (rotar, migrar, aceptar)
2. **Ignorar explicitamente** en la herramienta:
   - `pip-audit --ignore-vuln CVE-XXXX-YYYY`
   - Trivy: `--ignore-unfixed` o `.trivyignore`
3. **Revisar** en la siguiente auditoria trimestral

### Vulnerabilidades conocidas aceptadas

| Paquete | CVE | Severidad | Motivo | Accion |
|---------|-----|-----------|--------|--------|
| `python-jose 3.5.0` | CVE-2026-85394 | CRITICAL | Sin fix upstream. Movido al grupo dev. No se usa en runtime. | Migrar a PyJWT si se necesita JWT en prod |
| `ecdsa 0.19.2` | PYSEC-2026-1325 | HIGH | Minerva timing attack. Sin fix. Dependencia de `python-jose`. | Solo en dev |
| Paquetes del OS (Debian) | Varios | HIGH/MEDIUM | Imagen base `python:3.12-slim`. No explotables desde el codigo. | Actualizar imagen base mensualmente |

### Comandos de auditoria (resumen)

    # Dependencias Python
    poetry run pip-audit

    # Imagen Docker (Trivy)
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
      aquasec/trivy:latest image --scanners vuln --quiet rickmorty-orders:latest

    # Dependencias desactualizadas
    poetry show --outdated

    # Actualizar (en rama)
    poetry update
    poetry run pytest 05_proyecto_final/rickmorty_orders/tests/ -q
    poetry run ruff check 05_proyecto_final/rickmorty_orders/
    poetry run mypy 05_proyecto_final/rickmorty_orders/

## Criterios de éxito (rúbrica)

- [ ] Arquitectura: capas separadas, regla de dependencia respetada
- [ ] Dominio: entidades + VOs + invariantes + eventos
- [ ] Puertos y adaptadores: intercambiables, contract tests
- [ ] API: endpoints documentados, validados, con JWT
- [ ] Testing: unit + contract + integration + e2e; cobertura > 85%
- [ ] Calidad: ruff + mypy strict sin errores
- [ ] CI/CD: pipeline en verde (lint + tests + build)
- [ ] Seguridad: pydantic-settings, pip-audit sin hallazgos críticos
- [ ] Observabilidad: logging estructurado
- [ ] Rendimiento: endpoints < 200ms p95
- [ ] Documentación: README + diagramas

## Referencias

- Rick and Morty API: https://rickandmortyapi.com/documentation
- Cosmic Python (arquitectura hexagonal en Python): https://www.cosmicpython.com/
- Alistair Cockburn — Hexagonal Architecture: https://alistair.cockburn.us/hexagonal-architecture/
- FastAPI docs: https://fastapi.tiangolo.com/
- SQLAlchemy 2.0 docs: https://docs.sqlalchemy.org/en/20/

## Autor

parisollie - pjff18@gmail.com

## Licencia

Uso educativo.

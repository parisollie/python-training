# Rick & Morty Orders

Proyecto final integrador de la capacitación Python: **servicio de Orders** con arquitectura hexagonal/limpia, API FastAPI, persistencia SQLAlchemy y consumo de la API pública de Rick and Morty.

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

rickmorty_orders/
├── README.md
├── pyproject.toml              <- configuración Poetry + herramientas
├── poetry.lock
├── .env.example                <- ejemplo de variables de entorno
├── .dockerignore
├── Dockerfile                  <- multistage
├── docker-compose.yml          <- para desarrollo local
├── alembic.ini                 <- configuración Alembic
├── alembic/                    <- migraciones
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── .github/
│   └── workflows/
│       └── ci.yml              <- lint + typecheck + tests + build
├── src/
│   └── rickmorty_orders/
│       ├── __init__.py
│       ├── domain/             <- NÚCLEO (sin dependencias externas)
│       │   ├── __init__.py
│       │   ├── value_objects.py    <- OrderId, Money, Email, CharacterId
│       │   ├── order.py            <- Order, OrderItem, OrderStatus
│       │   ├── character.py        <- Character (referencia externa)
│       │   ├── events.py           <- OrderCreated, OrderConfirmed, ...
│       │   ├── errors.py           <- errores de dominio
│       │   └── ports.py            <- OrderRepository, CharacterRepository,
│       │                              Notifier, EventBus
│       ├── application/        <- CASOS DE USO
│       │   ├── __init__.py
│       │   ├── dtos.py             <- CreateOrderInput, OrderOutput
│       │   ├── create_order.py     <- CreateOrderService
│       │   ├── get_order.py        <- GetOrderService
│       │   ├── list_orders.py      <- ListOrdersService
│       │   ├── confirm_order.py    <- ConfirmOrderService
│       │   ├── cancel_order.py     <- CancelOrderService
│       │   └── event_handlers.py   <- manejo de eventos
│       └── infrastructure/     <- ADAPTADORES
│           ├── __init__.py
│           ├── config.py           <- Settings (pydantic-settings)
│           ├── api/                <- FastAPI
│           │   ├── app.py
│           │   ├── dependencies.py
│           │   ├── routers/
│           │   │   ├── orders.py
│           │   │   └── health.py
│           │   └── schemas.py
│           ├── persistence/        <- SQLAlchemy
│           │   ├── models.py
│           │   ├── database.py
│           │   └── repositories.py
│           ├── external/           <- Rick and Morty API
│           │   └── rickmorty_client.py
│           └── notifications/
│               └── console_notifier.py
└── tests/
    ├── __init__.py
    ├── conftest.py             <- fixtures compartidas
    ├── unit/                   <- dominio puro
    │   ├── __init__.py
    │   ├── test_value_objects.py
    │   ├── test_order.py
    │   └── test_events.py
    ├── contract/               <- adaptadores cumplen puertos
    │   ├── __init__.py
    │   ├── test_repository_contract.py
    │   └── test_character_repo_contract.py
    ├── integration/            <- con SQLite, HTTP mock, etc.
    │   ├── __init__.py
    │   ├── test_sql_repository.py
    │   └── test_rickmorty_client.py
    └── e2e/                    <- flujo completo con TestClient
        ├── __init__.py
        └── test_orders_api.py

## Fases del proyecto

| Fase | Contenido | Estado |
|------|-----------|:------:|
| 1 | Setup: estructura + README | ✅ Completada |
| 2 | Dominio: entidades, VOs, puertos, eventos | ✅ Completada |
| 3 | Aplicación: casos de uso + DTOs | ✅ Completada |
| 4 | Infraestructura: SQLAlchemy, httpx, FastAPI | ✅ Completada |
| 5 | Testing: unit + contract + integration + e2e | ✅ Completada |
| 6 | Alembic + Docker + CI/CD | 🔄 Siguiente |
| 7 | Auditoría + presentación | ⬜ Pendiente |

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

### Siguiente

**FASE 6: Alembic + Docker + CI/CD**
- Alembic (init + migracion inicial + upgrade)
- Dockerfile multistage
- GitHub Actions (lint + typecheck + tests + build)

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

## Docker (cuando esté listo)

    # Construir
    docker build -t rickmorty-orders:latest .

    # Ejecutar
    docker run -p 8000:8000 rickmorty-orders:latest

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

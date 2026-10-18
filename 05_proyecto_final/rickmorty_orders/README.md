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
| 4 | Infraestructura: SQLAlchemy, httpx, FastAPI | 🔄 Siguiente |
| 5 | Testing: unit + contract + integration + e2e | ⬜ Pendiente |
| 6 | Alembic + Docker + CI/CD | ⬜ Pendiente |
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
  - `GetOrderService` (obtener por id)
  - `ListOrdersService` (listar por cliente o todas)
  - `ConfirmOrderService` (pending -> confirmed)
  - `CancelOrderService` (pending/confirmed -> cancelled)
- Adaptadores en memoria (para desarrollo y tests)

**Calidad**
- ruff: sin errores
- mypy strict: sin errores
- 20 archivos Python verificados

### Siguiente

**FASE 4: Infraestructura**
- SQLAlchemy (OrderRepository)
- httpx (CharacterRepository contra la API real)
- FastAPI (routers, dependencias, JWT)
- pydantic-settings (configuracion)

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

## Endpoints planeados (FastAPI)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /characters/{id} | Consulta a la API R&M (proxy) |
| POST | /orders | Crear una orden |
| GET | /orders | Listar órdenes del usuario |
| GET | /orders/{id} | Obtener una orden |
| PATCH | /orders/{id}/confirm | Confirmar |
| PATCH | /orders/{id}/cancel | Cancelar |

## Cómo se ejecutará (cuando esté listo)

    # Instalar dependencias
    poetry install

    # Aplicar migraciones
    poetry run alembic upgrade head

    # Arrancar servidor de desarrollo
    poetry run uvicorn rickmorty_orders.infrastructure.api.app:app --reload

    # Abrir documentación
    # http://localhost:8000/docs

## Testing (cuando esté listo)

    # Todos los tests
    poetry run pytest tests/ -v

    # Solo unit
    poetry run pytest tests/unit/ -v

    # Con cobertura
    poetry run pytest tests/ --cov=src/rickmorty_orders --cov-report=term-missing

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

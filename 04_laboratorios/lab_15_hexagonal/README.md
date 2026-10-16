# Laboratorio 15 — Arquitectura Hexagonal

Sistema de órdenes con **Ports & Adapters**: dominio puro, puertos estables y adaptadores intercambiables.

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1
- Pydantic 2.14.1, httpx 0.28.1

## Estructura

lab_15_hexagonal/
├── README.md              ← este archivo
├── domain/                ← núcleo (puro Python)
│   ├── __init__.py
│   ├── value_objects.py   ← Money, Email, OrderId
│   ├── order.py           ← entidad Order + OrderItem + OrderStatus
│   └── ports.py           ← OrderRepository, Notifier (Protocols)
├── application/           ← casos de uso
│   ├── __init__.py
│   ├── dtos.py            ← CreateOrderInput, OrderOutput (Pydantic)
│   └── create_order.py    ← CreateOrderService
├── infrastructure/        ← adaptadores
│   ├── __init__.py
│   ├── memory.py          ← InMemoryOrderRepository, FakeNotifier
│   └── http_notifier.py   ← HttpNotifier (httpx)
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_value_objects.py       ← 18 tests
    ├── test_order_entity.py        ← 17 tests
    └── test_create_order_service.py ← 13 tests

## Diagrama de capas

    Infraestructura  →  Aplicación  →  Dominio
    (adaptadores)        (casos de uso)  (entidades, VOs, puertos)

**Regla de dependencia**: las dependencias apuntan **hacia dentro**.
El dominio **nunca** importa infraestructura.

## Dominio

### Value Objects (`domain/value_objects.py`)

| VO | Invariante |
|----|-----------|
| `Money` | `amount >= 0`, `currency` de 3 letras |
| `Email` | Formato válido, normaliza (strip + lowercase) |
| `OrderId` | UUID generable o custom |

Son `frozen=True` (inmutables) y comparan por **valor**.

### Entidad (`domain/order.py`)

| Clase | Rol |
|-------|-----|
| `OrderItem` | Value Object (product, quantity, unit_price) |
| `Order` | Entidad (id, customer_email, items, status) |
| `OrderStatus` | `StrEnum`: PENDING, CONFIRMED, SHIPPED, CANCELLED |

**Reglas de negocio en la entidad:**
- `Order.create(...)` genera un `OrderId` nuevo
- Al menos 1 item (`__post_init__`)
- `confirm()` solo desde `PENDING`
- `cancel()` no permitido desde `SHIPPED`
- `add_item()` bloqueado si `CONFIRMED` o `SHIPPED`
- `subtotal`, `tax` (16%), `total` calculados con `Money`

### Puertos (`domain/ports.py`)

    class OrderRepository(Protocol):
        def save(self, order: Order) -> None: ...
        def find_by_id(self, order_id: OrderId) -> Order | None: ...
        def list_all(self) -> list[Order]: ...

    class Notifier(Protocol):
        def notify_order_created(self, order: Order) -> None: ...

## Aplicación

### DTOs (`application/dtos.py`)

- `OrderItemInput` / `CreateOrderInput` → entrada validada con Pydantic
- `OrderItemOutput` / `OrderOutput` → salida con `from_entity(order)`

### Caso de uso (`application/create_order.py`)

    service = CreateOrderService(repository=repo, notifier=notifier)
    result = service.execute(CreateOrderInput(...))

El servicio:
1. Convierte DTO → entidades del dominio
2. Aplica invariantes (via `Order.create`)
3. Persiste via puerto
4. Notifica via puerto
5. Convierte entidad → DTO de salida

**No conoce** si el repo es memoria, SQL o Mongo. Ni si el notifier es fake o HTTP.

## Infraestructura

### Adaptadores

| Adaptador | Puerto | Uso |
|-----------|--------|-----|
| `InMemoryOrderRepository` | `OrderRepository` | tests, dev |
| `FakeNotifier` | `Notifier` | tests |
| `HttpNotifier` | `Notifier` | notificación HTTP real |

## Ejemplo: flujo completo

    cd 04_laboratorios/lab_15_hexagonal
    poetry run python -c "
    from application.create_order import CreateOrderService
    from application.dtos import CreateOrderInput
    from infrastructure.memory import InMemoryOrderRepository, FakeNotifier

    # Wiring manual
    repo = InMemoryOrderRepository()
    notifier = FakeNotifier()
    service = CreateOrderService(repository=repo, notifier=notifier)

    # Ejecutar caso de uso
    result = service.execute(CreateOrderInput(
        customer_email='paul@example.com',
        items=[
            {'product': 'Teclado', 'quantity': 2, 'unit_price': 25.0},
            {'product': 'Mouse', 'quantity': 1, 'unit_price': 15.5},
        ],
    ))

    print(f'Orden: {result.id}')
    print(f'Subtotal: {result.subtotal}')
    print(f'Tax: {result.tax}')
    print(f'Total: {result.total}')
    print(f'Notificaciones: {notifier.notified}')
    "
    cd ../..

Salida esperada:

    Orden: XXXX-XXXX-...
    Subtotal: 65.5
    Tax: 10.48
    Total: 75.98
    Notificaciones: ['XXXX-XXXX-...']

## Ejemplo: intercambiar adaptadores sin tocar el caso de uso

    cd 04_laboratorios/lab_15_hexagonal
    poetry run python -c "
    import httpx
    from application.create_order import CreateOrderService
    from application.dtos import CreateOrderInput
    from infrastructure.memory import InMemoryOrderRepository
    from infrastructure.http_notifier import HttpNotifier

    captured = []

    def handler(request):
        captured.append(str(request.content))
        return httpx.Response(200, json={'ok': True})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)

    # Mismo caso de uso, distinto notifier
    service = CreateOrderService(
        repository=InMemoryOrderRepository(),
        notifier=HttpNotifier('https://api.example.com/notify', client=client),
    )

    service.execute(CreateOrderInput(
        customer_email='paul@example.com',
        items=[{'product': 'X', 'quantity': 1, 'unit_price': 100.0}],
    ))

    print(f'HTTP capturado: {captured}')
    "
    cd ../..

Salida esperada:

    HTTP capturado: ['{"event":"order_created","order_id":"...","customer_email":"paul@example.com","total":116.0,"currency":"USD"}']

## Cómo ejecutar los tests

    poetry run pytest 04_laboratorios/lab_15_hexagonal/tests/ -v

Salida esperada:

    48 passed in 0.09s

### Con cobertura

    poetry run pytest 04_laboratorios/lab_15_hexagonal/tests/ --cov=04_laboratorios/lab_15_hexagonal --cov-report=term-missing

### Archivos de tests

| Archivo | Qué cubre | Tests |
|---------|-----------|-------|
| test_value_objects.py | Money, Email, OrderId | 18 |
| test_order_entity.py | Order, OrderItem, estados | 17 |
| test_create_order_service.py | Caso de uso + contract + e2e | 13 |

### Tipos de tests

- **Unit**: dominio puro (Value Objects, entidad Order)
- **Unit con fakes**: caso de uso con `InMemoryOrderRepository` + `FakeNotifier`
- **Contract**: adaptadores cumplen los puertos (`hasattr` de métodos)
- **E2E**: flujo completo con `HttpNotifier` simulado via `MockTransport`

## Verificación de calidad

    poetry run ruff check 04_laboratorios/lab_15_hexagonal/
    poetry run mypy 04_laboratorios/lab_15_hexagonal/
    poetry run pre-commit run --all-files

## Comparación con SOLID (Módulo 12)

| Aspecto | SOLID (M12) | Hexagonal (M15) |
|---------|-------------|-----------------|
| Enfoque | Principios de diseño de clases | Estructura de capas del sistema |
| Dominio | `Order` con validaciones | `Order` + Value Objects + `OrderId` |
| Interfaces | 3 Protocols (Repo, Notifier, Payment) | 2 Protocols (Repo, Notifier) |
| Organización | domain/services/infrastructure | domain/application/infrastructure |
| Dinero | `float` plano | Value Object `Money` |
| Email | `str` validado con Pydantic | Value Object `Email` |
| Caso de uso | `OrderService.create_order` | `CreateOrderService.execute` con DTOs |
| Testing | 23 tests | 48 tests (con Value Objects) |

**Hexagonal agrega respecto a SOLID:**
- Value Objects con invariantes propias
- Capa explícita de **aplicación** (casos de uso)
- DTOs de entrada/salida (no expone entidades)
- Regla de dependencia formal

## Notas de implementación

### Value Objects con `frozen=True`

    @dataclass(frozen=True)
    class Money:
        amount: float
        currency: str = "USD"

Inmutables por diseño → seguros para compartir y comparar por valor.

### `StrEnum` para estados

    class OrderStatus(StrEnum):
        PENDING = "pending"
        ...

Python 3.11+. Se serializa como string natural, útil con Pydantic y JSON.

### `Email` normaliza con `object.__setattr__`

    @dataclass(frozen=True)
    class Email:
        def __post_init__(self):
            normalized = self.value.strip().lower()
            object.__setattr__(self, "value", normalized)

Permite normalizar dentro de un `frozen=True` (truco avanzado pero idiomático).

### `HttpNotifier` no propaga errores

    try:
        response = self._client.post(...)
        response.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(...)

La notificación **no debe romper el flujo principal**. Si el cliente quiere garantías, se debe implementar retry o una cola.

### Wiring manual

El `wiring` se hace **fuera** del caso de uso, en la capa de infraestructura. En un proyecto real podría ser una función `get_order_service()` en un módulo `dependencies.py` de FastAPI.

### DTOs con Pydantic en el borde

`CreateOrderInput` valida la entrada con Pydantic. Esto **no contamina el dominio**: Pydantic vive en la capa de aplicación (o en `api/`), nunca en `domain/`.

## Comandos rápidos (resumen)

    # Ejemplos
    cd 04_laboratorios/lab_15_hexagonal
    poetry run python -c "
    from application.create_order import CreateOrderService
    from application.dtos import CreateOrderInput
    from infrastructure.memory import InMemoryOrderRepository, FakeNotifier
    s = CreateOrderService(InMemoryOrderRepository(), FakeNotifier())
    r = s.execute(CreateOrderInput(
        customer_email='a@b.com',
        items=[{'product': 'X', 'quantity': 1, 'unit_price': 10.0}],
    ))
    print(r.total)
    "
    cd ../..

    # Tests
    poetry run pytest 04_laboratorios/lab_15_hexagonal/tests/ -v

    # Calidad
    poetry run ruff check 04_laboratorios/lab_15_hexagonal/
    poetry run mypy 04_laboratorios/lab_15_hexagonal/

## Estado

- [x] Estructura (domain/application/infrastructure/tests)
- [x] Value Objects (Money, Email, OrderId)
- [x] Entidad Order con lógica pura
- [x] Puertos (OrderRepository, Notifier)
- [x] DTOs con Pydantic
- [x] Caso de uso CreateOrderService
- [x] Adaptadores (InMemory, Fake, Http)
- [x] Tests: unit + contract + e2e
- [x] ruff + mypy OK
- [x] Documentación completa

## Clonar este laboratorio

    git clone https://github.com/parisollie/python-training.git
    cd python-training
    poetry install

    # Tests
    poetry run pytest 04_laboratorios/lab_15_hexagonal/tests/ -v

    # Ejemplos
    cd 04_laboratorios/lab_15_hexagonal
    poetry run python -c "from domain.value_objects import Money; print(Money(100) + Money(50))"
    cd ../..

## Referencias

- Alistair Cockburn — Hexagonal Architecture: https://alistair.cockburn.us/hexagonal-architecture/
- Robert C. Martin — Clean Architecture (libro)
- Cosmic Python (gratis online): https://www.cosmicpython.com/
- Python `typing.Protocol`: https://docs.python.org/3/library/typing.html#typing.Protocol
- PEP 544 — Protocols: https://peps.python.org/pep-0544/
- Python `enum.StrEnum`: https://docs.python.org/3/library/enum.html#enum.StrEnum
- Real Python — Python Architecture: https://realpython.com/python-architecture/

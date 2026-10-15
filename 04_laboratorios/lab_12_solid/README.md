# Laboratorio 12 — Principios SOLID aplicados

Refactor de un servicio de órdenes aplicando los 5 principios SOLID, con inyección de dependencias mediante Protocols.

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1

## Estructura

lab_12_solid/
├── README.md              ← este archivo
├── domain/                ← reglas de negocio (puro Python)
│   ├── __init__.py
│   ├── order.py           ← Order + OrderItem con validaciones
│   └── protocols.py       ← OrderRepository, Notifier, PaymentProcessor
├── services/              ← alto nivel (orquestación)
│   ├── __init__.py
│   └── order_service.py   ← OrderService + ItemInput (TypedDict)
├── infrastructure/        ← bajo nivel (implementaciones)
│   ├── __init__.py
│   ├── repositories.py    ← InMemoryOrderRepository, SQLOrderRepository
│   ├── notifiers.py       ← ConsoleNotifier, EmailNotifier, FakeNotifier
│   └── payments.py        ← StripePayment, FakePayment
└── tests/
    ├── __init__.py
    ├── conftest.py        ← fixtures
    ├── test_domain.py     ← 9 tests
    └── test_order_service.py ← 14 tests

## Los 5 principios SOLID

### S — Single Responsibility

Cada clase tiene **una razón para cambiar**:

| Clase | Responsabilidad |
|-------|-----------------|
| `Order` | Reglas de negocio (subtotal, tax, total) |
| `OrderRepository` | Persistencia |
| `Notifier` | Notificaciones |
| `PaymentProcessor` | Cobro |
| `OrderService` | Orquestar el caso de uso |

### O — Open/Closed

**Abierto a extensión, cerrado a modificación.**

Agregar `PayPalPayment` no requiere tocar `OrderService`:

    class PayPalPayment:
        def charge(self, amount: float, user_id: str) -> bool:
            ...  # nueva implementación

    service = OrderService(repo, notifier, PayPalPayment())  # funciona igual

### L — Liskov Substitution

Cualquier implementación de un Protocol puede sustituir a otra sin romper.

Test parametrizado que verifica esto:

    @pytest.mark.parametrize("repo_type", ["memory", "sql"])
    def test_lsp_mismo_comportamiento(repo_type):
        repo = InMemoryOrderRepository() if repo_type == "memory" else SQLOrderRepository()
        service = OrderService(repo, ...)
        # mismas aserciones pasan con ambos

### I — Interface Segregation

3 interfaces pequeñas y específicas en lugar de una grande:

- `OrderRepository` (solo persistencia)
- `Notifier` (solo notificaciones)
- `PaymentProcessor` (solo cobro)

Ninguna implementación está obligada a tener métodos que no usa.

### D — Dependency Inversion

`OrderService` depende de **abstracciones** (Protocols), no de implementaciones concretas.

    class OrderService:
        def __init__(
            self,
            repository: OrderRepository,   # Protocol
            notifier: Notifier,            # Protocol
            payment: PaymentProcessor,     # Protocol
        ) -> None:
            ...

Esto permite:
- **Tests rápidos** con implementaciones en memoria
- **Producción** con SQL/email/Stripe
- **Cambiar cualquier pieza** sin tocar el servicio

## Ejemplo: crear orden

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_12_solid')
    from infrastructure.repositories import InMemoryOrderRepository
    from infrastructure.notifiers import ConsoleNotifier
    from infrastructure.payments import FakePayment
    from services.order_service import OrderService

    service = OrderService(
        repository=InMemoryOrderRepository(),
        notifier=ConsoleNotifier(),
        payment=FakePayment(),
    )

    order = service.create_order(
        user_id='user-1',
        items=[
            {'product': 'Teclado', 'quantity': 2, 'unit_price': 25.0},
            {'product': 'Mouse', 'quantity': 1, 'unit_price': 15.5},
        ],
    )
    print(f'Orden creada: {order.id}')
    print(f'Total: {order.total}')
    "

Salida esperada:

    📧 Orden creada: 64f3203a-... para user-1 (total 75.98)

    Orden creada: 64f3203a-...
    Total: 75.98

## Ejemplo: cambiar implementaciones sin tocar el servicio

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_12_solid')
    from infrastructure.repositories import InMemoryOrderRepository, SQLOrderRepository
    from infrastructure.notifiers import ConsoleNotifier, EmailNotifier
    from infrastructure.payments import FakePayment, StripePayment
    from services.order_service import OrderService

    # Producción: SQL + Email + Stripe
    prod_service = OrderService(
        repository=SQLOrderRepository(),
        notifier=EmailNotifier(),
        payment=StripePayment(),
    )

    # Tests: Memory + Console + Fake
    test_service = OrderService(
        repository=InMemoryOrderRepository(),
        notifier=ConsoleNotifier(),
        payment=FakePayment(),
    )

    # MISMO OrderService, sin cambios en su código
    print('Ambos servicios creados sin cambiar OrderService')
    "

Salida esperada:

    Ambos servicios creados sin cambiar OrderService

## Ejemplo: fallo de pago no persiste

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_12_solid')
    from infrastructure.repositories import InMemoryOrderRepository
    from infrastructure.notifiers import FakeNotifier
    from infrastructure.payments import FakePayment
    from services.order_service import OrderService, PaymentError

    repo = InMemoryOrderRepository()
    service = OrderService(repo, FakeNotifier(), FakePayment(should_succeed=False))

    try:
        service.create_order(
            user_id='user-1',
            items=[{'product': 'X', 'quantity': 1, 'unit_price': 10.0}],
        )
    except PaymentError as e:
        print(f'Pago fallo: {e}')
        print(f'Ordenes persistidas: {len(repo.list_by_user(\"user-1\"))}')
    "

Salida esperada:

    Pago fallo: Fallo el cobro de 11.6 para user-1
    Ordenes persistidas: 0

## Cómo ejecutar los tests

    poetry run pytest 04_laboratorios/lab_12_solid/tests/ -v

Salida esperada:

    23 passed in 0.08s

### Con cobertura

    poetry run pytest 04_laboratorios/lab_12_solid/tests/ --cov=04_laboratorios/lab_12_solid --cov-report=term-missing

### Archivos de tests

| Archivo | Qué cubre | Tests |
|---------|-----------|-------|
| test_domain.py | Order, OrderItem, validaciones | 9 |
| test_order_service.py | OrderService, DIP, LSP, OCP | 14 |

## Verificación de calidad

    poetry run ruff check 04_laboratorios/lab_12_solid/
    poetry run mypy 04_laboratorios/lab_12_solid/
    poetry run pre-commit run --all-files

## Notas de implementación

### Protocol vs ABC

Se usa `Protocol` (PEP 544) en lugar de `ABC` porque:

- **Duck typing tipado**: cualquier clase con los métodos correctos cumple
- **Sin acoplamiento**: `InMemoryOrderRepository` no hereda de nada
- **Mocks triviales**: `Mock()` cumple el Protocol sin herencia
- **Retrocompatible**: si mañana se quiere heredar, se puede

### Wiring manual vs DI framework

En este laboratorio, el "wiring" es **manual** (pasamos las dependencias al `__init__`). Esto es suficiente para proyectos pequeños y medianos.

Para proyectos grandes, se pueden usar frameworks de DI como:
- `dependency-injector`
- `punq`
- `python-inject`

Pero **no son necesarios**: el wiring manual es simple y explícito (PEP 20: "Explícito es mejor que implícito").

### ¿Por qué el cobro va antes del save?

    if not self._payment.charge(order.total, user_id):
        raise PaymentError(...)
    self._repository.save(order)

Si el cobro falla, **no se persiste** la orden. Esto evita órdenes fantasma en la DB.

En producción real, con transacciones, se podría hacer al revés (save + charge + rollback si falla). Depende del caso.

### Tests sin tocar la red ni la DB real

Gracias al DIP, todos los tests usan:
- `InMemoryOrderRepository` (no DB)
- `FakeNotifier` (no email)
- `FakePayment` (no Stripe)

Resultado: **23 tests en 0.08s**.

### TypedDict para entrada

`create_order` acepta `list[ItemInput]` donde `ItemInput` es un `TypedDict`:

    class ItemInput(TypedDict):
        product: str
        quantity: int
        unit_price: float

Esto da autocompletado y verificación de tipos sin sacrificar la flexibilidad del dict.

## Comandos rápidos (resumen)

    # Tests
    poetry run pytest 04_laboratorios/lab_12_solid/tests/ -v

    # Calidad
    poetry run ruff check 04_laboratorios/lab_12_solid/
    poetry run mypy 04_laboratorios/lab_12_solid/

    # Ejemplo
    poetry run python -c "
    import sys; sys.path.insert(0, '04_laboratorios/lab_12_solid')
    from infrastructure.repositories import InMemoryOrderRepository
    from infrastructure.notifiers import ConsoleNotifier
    from infrastructure.payments import FakePayment
    from services.order_service import OrderService
    s = OrderService(InMemoryOrderRepository(), ConsoleNotifier(), FakePayment())
    o = s.create_order('u1', [{'product': 'X', 'quantity': 1, 'unit_price': 10.0}])
    print(o.total)
    "

## Estado

- [x] Estructura del laboratorio (domain/services/infrastructure)
- [x] Dominio con validaciones
- [x] Protocols (OrderRepository, Notifier, PaymentProcessor)
- [x] OrderService dependiendo de Protocols
- [x] Implementaciones memory + SQL
- [x] Notifiers (Console, Email, Fake)
- [x] Payments (Stripe, Fake)
- [x] 23 tests
- [x] ruff + mypy OK
- [x] Documentación completa

## Clonar este laboratorio

    git clone https://github.com/parisollie/python-training.git
    cd python-training
    poetry install

    # Tests
    poetry run pytest 04_laboratorios/lab_12_solid/tests/ -v

## Referencias

- SOLID (Wikipedia): https://en.wikipedia.org/wiki/SOLID
- Robert C. Martin — Clean Architecture (libro)
- Python typing.Protocol: https://docs.python.org/3/library/typing.html#typing.Protocol
- PEP 544 — Protocols: https://peps.python.org/pep-0544/
- Real Python — SOLID: https://realpython.com/solid-principles-python/

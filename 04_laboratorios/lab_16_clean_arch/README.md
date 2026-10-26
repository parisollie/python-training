# Laboratorio 16 — Arquitectura Limpia

Demuestra los conceptos de **Clean Architecture** aplicados a un caso real
(crear y confirmar ordenes), con enfasis en los 4 componentes nuevos:

1. **Unit of Work** explicito (transacciones + coordinacion de repos)
2. **Event Handlers** via `collect_event` + commit
3. **Presenter** que convierte entidades en DTOs
4. **Controller** puro (sin FastAPI), testeable de forma aislada

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1

## Estructura

```text
lab_16_clean_arch/
├── README.md              <- este archivo
├── src/
│   └── clean_arch/
│       ├── __init__.py
│       ├── domain/                    <- Entidades (nucleo)
│       │   ├── __init__.py
│       │   ├── value_objects.py       (OrderId, Money, Email)
│       │   ├── errors.py              (DomainError + 3 errores)
│       │   ├── events.py              (OrderCreated, OrderConfirmed)
│       │   ├── order.py               (Order, OrderItem, OrderStatus)
│       │   └── ports.py               (OrderRepository, Notifier, EventBus)
│       ├── application/               <- Casos de uso + UoW + Presenter
│       │   ├── __init__.py
│       │   ├── dtos.py                (CreateOrderInput, OrderOutput)
│       │   ├── unit_of_work.py        (Protocol UnitOfWork)
│       │   ├── presenters.py          (OrderPresenter)
│       │   ├── create_order.py        (CreateOrderService)
│       │   ├── confirm_order.py       (ConfirmOrderService)
│       │   └── controllers.py         (CreateOrderController)
│       └── infrastructure/            <- Adaptadores (en memoria)
│           ├── __init__.py
│           └── memory_uow.py          (InMemoryUnitOfWork, FakeEventBus, FakeNotifier)
└── tests/
    └── __init__.py
```

## Los 4 componentes clave

### 1. Unit of Work (UoW)

El UoW coordina repositorios, transacciones y eventos pendientes.

    with self._uow:
        self._uow.orders.save(order)
        self._uow.collect_event(OrderCreated(...))
        self._uow.commit()   # <- publica eventos, marca como committed

**Ventajas:**
- Una sola transaccion para multiples repos
- Rollback automatico si algo falla
- Eventos publicados solo si el commit tuvo exito

### 2. Event Handlers (via collect_event)

El caso de uso **NO publica eventos directamente**. Los deja en el UoW:

    self._uow.collect_event(OrderCreated(order_id=order.id, ...))

Al hacer `commit()`, el UoW los publica en el `EventBus`. Los handlers
registrados en el bus reaccionan (enviar email, actualizar cache, etc.).

### 3. Presenter

Convierte la entidad del dominio en un DTO de salida.

    presenter = OrderPresenter()
    output = presenter.present(order)  # Order -> OrderOutput

**Ventajas:**
- El caso de uso devuelve la **entidad** (no el DTO)
- El presenter decide **como** presentarla
- Multiples formatos (JSON, HTML, XML) sin tocar el caso de uso

### 4. Controller (puro)

    class CreateOrderController:
        def __init__(self, service: CreateOrderService, presenter: OrderPresenter):
            self._service = service
            self._presenter = presenter

        def handle(self, input_dto: CreateOrderInput) -> OrderOutput:
            order = self._service.execute(input_dto)
            return self._presenter.present(order)

**Ventajas:**
- Sin FastAPI: testeable con pytest puro
- Flujo claro: input -> use case -> presenter -> output
- Facil de migrar a otro framework (no estas atado a FastAPI)

## Ejemplo: flujo completo

    poetry run python -c "
    from clean_arch.application.controllers import CreateOrderController
    from clean_arch.application.create_order import CreateOrderService
    from clean_arch.application.dtos import CreateOrderInput
    from clean_arch.application.presenters import OrderPresenter
    from clean_arch.infrastructure.memory_uow import InMemoryUnitOfWork

    # Wiring manual
    uow = InMemoryUnitOfWork()
    service = CreateOrderService(uow)
    presenter = OrderPresenter()
    controller = CreateOrderController(service, presenter)

    # Ejecutar flujo completo
    result = controller.handle(CreateOrderInput(
        customer_email='paul@example.com',
        items=[
            {'product': 'Rick', 'quantity': 2, 'unit_price': 50.0},
            {'product': 'Morty', 'quantity': 1, 'unit_price': 25.0},
        ],
    ))

    print(f'Order ID: {result.id}')
    print(f'Total: \${result.total}')
    print(f'Eventos: {[type(e).__name__ for e in uow.event_bus.published]}')
    "

Salida esperada:

    Order ID: XXXX-XXXX-...
    Total: $145.0
    Eventos: ['OrderCreated']

## Diferencias con el lab 15 (Hexagonal)

| Aspecto | Hexagonal (lab 15) | Clean Architecture (lab 16) |
|---------|-------------------|----------------------------|
| Transacciones | Cada repo abre sesion | Unit of Work explicito |
| Eventos | Publicados directos | collect_event + commit |
| Presentacion | Router devuelve DTO | Presenter separado |
| Controller | Router FastAPI | Controller puro (sin FastAPI) |
| Testeabilidad | Requiere TestClient | pytest puro |

## Comparacion con el proyecto final

El proyecto final (`rickmorty_orders`) usa **Hexagonal** con algunas
practicas de Clean (repositorios por entidad, eventos en el bus).
El lab 16 va **un paso mas alla** con:
- UoW explicito (aunque en memoria)
- Presenter separado del router
- Controller puro

En un proyecto real, la migracion a Clean Architecture implica:

1. Extraer el presenter de los routers FastAPI
2. Introducir un UoW que coordine transacciones
3. Mover los event handlers fuera del caso de uso
4. (Opcional) Separar controllers de routers

## Verificación paso a paso

Todos los comandos se ejecutan **desde la raíz del repo** (`python-training/`).

### Setup

    poetry install

### Flujo completo (demo)

    poetry run python -c "
    from clean_arch.application.controllers import CreateOrderController
    from clean_arch.application.create_order import CreateOrderService
    from clean_arch.application.dtos import CreateOrderInput
    from clean_arch.application.presenters import OrderPresenter
    from clean_arch.infrastructure.memory_uow import InMemoryUnitOfWork

    uow = InMemoryUnitOfWork()
    service = CreateOrderService(uow)
    presenter = OrderPresenter()
    controller = CreateOrderController(service, presenter)

    result = controller.handle(CreateOrderInput(
        customer_email='paul@example.com',
        items=[
            {'product': 'Rick', 'quantity': 2, 'unit_price': 50.0},
            {'product': 'Morty', 'quantity': 1, 'unit_price': 25.0},
        ],
    ))

    print(f'Order ID: {result.id}')
    print(f'Status: {result.status}')
    print(f'Subtotal: \${result.subtotal}')
    print(f'Tax: \${result.tax}')
    print(f'Total: \${result.total}')
    print(f'Items: {len(result.items)}')
    print(f'Eventos publicados: {[type(e).__name__ for e in uow.event_bus.published]}')
    print(f'UoW committed: {uow.committed}')
    "

Salida esperada:

    Order ID: XXXX-XXXX-...
    Status: pending
    Subtotal: $125.0
    Tax: $20.0
    Total: $145.0
    Items: 2
    Eventos publicados: ['OrderCreated']
    UoW committed: True

### Tests

    # Todos los tests (29 esperados)
    poetry run pytest 04_laboratorios/lab_16_clean_arch/tests/ -v

    # Solo dominio
    poetry run pytest 04_laboratorios/lab_16_clean_arch/tests/test_domain.py -v

    # Solo UoW
    poetry run pytest 04_laboratorios/lab_16_clean_arch/tests/test_uow.py -v

    # Solo casos de uso
    poetry run pytest 04_laboratorios/lab_16_clean_arch/tests/test_use_cases.py -v

    # Con cobertura (97% esperado)
    poetry run pytest 04_laboratorios/lab_16_clean_arch/tests/ \
      --cov=04_laboratorios/lab_16_clean_arch/src/clean_arch \
      --cov-report=term-missing

### Calidad

    # Linter
    poetry run ruff check 04_laboratorios/lab_16_clean_arch/

    # Type checker
    poetry run mypy 04_laboratorios/lab_16_clean_arch/

Salida esperada:

    All checks passed!
    Success: no issues found

### Archivos de tests

| Archivo | Qué cubre | Tests |
|---------|-----------|-------|
| test_domain.py | Value Objects, OrderItem, Order, transiciones | 15 |
| test_uow.py | UnitOfWork: context manager, commit, rollback, persistencia | 8 |
| test_use_cases.py | CreateOrderService, ConfirmOrderService, Controller, Presenter | 6 |

**Total: 29 tests, 97% cobertura.**

## Verificacion de calidad

    poetry run ruff check 04_laboratorios/lab_16_clean_arch/
    poetry run mypy 04_laboratorios/lab_16_clean_arch/

## Estado

- [x] Dominio (VOs, entidad, eventos, errores, puertos)
- [x] Aplicacion (DTOs, UoW Protocol, Presenter, casos de uso, Controller)
- [x] Infraestructura (InMemoryUnitOfWork, FakeEventBus, FakeNotifier)
- [x] Flujo completo funcionando (controller -> use case -> UoW -> presenter)
- [x] Tests (29 tests: 15 domain + 8 uow + 6 use cases)
- [x] Cobertura 97%
- [x] ruff + mypy OK
- [ ] Commit final

## Clonar este laboratorio

    git clone https://github.com/parisollie/python-training.git
    cd python-training
    poetry install

    # Flujo completo
    cd 04_laboratorios/lab_16_clean_arch
    poetry run python -c "
    from clean_arch.application.controllers import CreateOrderController
    from clean_arch.application.create_order import CreateOrderService
    from clean_arch.application.dtos import CreateOrderInput
    from clean_arch.application.presenters import OrderPresenter
    from clean_arch.infrastructure.memory_uow import InMemoryUnitOfWork
    uow = InMemoryUnitOfWork()
    c = CreateOrderController(CreateOrderService(uow), OrderPresenter())
    r = c.handle(CreateOrderInput(customer_email='a@b.com', items=[{'product': 'X', 'quantity': 1, 'unit_price': 10.0}]))
    print(r.total)
    "
    cd ../..

## Referencias

- Robert C. Martin — Clean Architecture (libro, 2017)
- Cosmic Python: https://www.cosmicpython.com/
- Martin Fowler — Unit of Work: https://martinfowler.com/eaaCatalog/unitOfWork.html
- Martin Fowler — Domain Events: https://martinfowler.com/eaaDev/DomainEvent.html
- Alistair Cockburn — Hexagonal Architecture: https://alistair.cockburn.us/hexagonal-architecture/

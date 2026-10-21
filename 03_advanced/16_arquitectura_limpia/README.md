# Módulo 16 — Arquitectura Limpia

## Objetivos
- Estructurar un servicio con capas independientes y reglas claras
- Gestionar transacciones con Unit of Work
- Publicar y manejar eventos de dominio
- Separar la presentacion (presenters) de los controllers

## Contenidos clave

### Que es Arquitectura Limpia
Propuesta por Robert C. Martin ("Uncle Bob"). Es una evolucion de la
Arquitectura Hexagonal que formaliza las capas y agrega componentes
explicitos para transacciones, eventos y presentacion.

### Las 4 capas (de dentro hacia fuera)

    +-------------------------------------------------------------+
    |  4. Frameworks & Drivers                                    |
    |     FastAPI, SQLAlchemy, httpx, Alembic, Docker             |
    |                                                             |
    |  +-------------------------------------------------------+  |
    |  |  3. Interface Adapters                                |  |
    |  |     Controllers, Presenters, Gateways, Repositories   |  |
    |  |                                                       |  |
    |  |  +-------------------------------------------------+  |  |
    |  |  |  2. Use Cases (Application)                     |  |  |
    |  |  |     CreateOrder, ConfirmOrder, ...              |  |  |
    |  |  |     Unit of Work, Event Handlers                |  |  |
    |  |  |                                                 |  |  |
    |  |  |  +-------------------------------------------+  |  |  |
    |  |  |  |  1. Entities (Domain)                     |  |  |  |
    |  |  |  |     Order, OrderItem, Money, Email        |  |  |  |
    |  |  |  |     Puertos, Eventos, Errores             |  |  |  |
    |  |  |  +-------------------------------------------+  |  |  |
    |  |  +-------------------------------------------------+  |  |
    |  +-------------------------------------------------------+  |
    +-------------------------------------------------------------+

Regla de dependencia: las dependencias apuntan HACIA DENTRO.
Las capas externas conocen a las internas, nunca al reves.

### Diferencias con Hexagonal (Módulo 15)

| Aspecto | Hexagonal | Clean Architecture |
|---------|-----------|-------------------|
| Capas | domain / application / infrastructure | entities / use cases / interface adapters / frameworks |
| Transacciones | Implicitas (cada repo abre sesion) | Explicit Unit of Work |
| Eventos | Publicados directos al bus | Event Handlers registrados |
| Presentacion | Routers devuelven DTOs | Presenters separados de controllers |
| Controllers | Routers FastAPI hacen todo | Controller -> Use Case -> Presenter |
| Gateways | Repositorios por entidad | Gateways + UoW coordinando |

### Componentes clave

**Unit of Work (UoW)**
- Coordina transacciones entre multiples repositorios
- Asegura atomicidad: si un paso falla, se hace rollback de todo
- API tipica: `with uow: uow.orders.add(order); uow.commit()`

**Eventos de dominio + Handlers**
- Los casos de uso publican eventos (`OrderCreated`)
- Los handlers reaccionan de forma desacoplada (enviar email, actualizar cache)
- Se registran en un EventBus o en el UoW

**Presenters**
- Convierten entidades del dominio a DTOs (formato de salida)
- Separan la logica de presentacion del controller
- Permiten tener multiples formatos (JSON, HTML, XML) sin tocar el caso de uso

**Controllers**
- Reciben el request, validan (Pydantic), invocan el caso de uso, devuelven el presenter
- No contienen logica de negocio
- Se pueden testear sin FastAPI (puros)

### Cuando usar Clean Architecture

**Si:**
- Dominio complejo con muchas reglas e invariantes
- Vida util larga (cambiar DB/framework sin reescribir)
- Multiples formatos de salida (API + CLI + mensajeria)
- Testing prioritario del dominio
- Transacciones que tocan varias entidades

**No:**
- CRUD simple
- Prototipos o scripts
- Equipos pequenos con dominio trivial
- Proyectos de vida corta

## Laboratorio

Refactor del proyecto `rickmorty_orders` aplicando Clean Architecture:

1. **Unit of Work** explicito
2. **Event Handlers** para `OrderCreated` (enviar notificacion)
3. **Presenter** que convierte Order -> OrderOutput
4. **Controller** puro (sin FastAPI) que orquesta caso de uso + presenter
5. **Wiring** con FastAPI al final

El laboratorio vive en `04_laboratorios/lab_16_clean_arch/` y es una
reimplementacion pequena para comparar con el proyecto final.

## Conceptos clave

### ¿Por que PEP 20 importa aqui?
- "Simple es mejor que complejo" -> no sobre-ingenieria; UoW solo si hay transacciones multi-entidad
- "Explícito es mejor que implícito" -> el UoW se abre explicitamente, no se esconde en el repo
- "La legibilidad cuenta" -> el controller se lee como un flujo claro

### Flujo de una request en Clean Architecture

    HTTP Request
        |
        v
    Controller (valida input con Pydantic)
        |
        v
    Use Case (orquesta: abre UoW, llama a repos, publica eventos)
        |
        v
    UoW (coordina repos y transaccion)
        |
        v
    Repositories / Gateways (adaptadores)
        |
        v
    DB / API externa
        |
        v (back up)
    Use Case devuelve entidad
        |
        v
    Presenter (entidad -> DTO)
        |
        v
    Controller devuelve DTO
        |
        v
    HTTP Response

### Ejemplo: Unit of Work

    class UnitOfWork(Protocol):
        orders: OrderRepository
        def __enter__(self) -> "UnitOfWork": ...
        def __exit__(self, *args: object) -> None: ...
        def commit(self) -> None: ...
        def rollback(self) -> None: ...

    # Uso en un caso de uso:
    with self.uow:
        self.uow.orders.save(order)
        self.uow.commit()

### Ejemplo: Event Handler

    class SendEmailOnOrderCreated:
        def __init__(self, notifier: Notifier) -> None:
            self.notifier = notifier

        def __call__(self, event: OrderCreated) -> None:
            self.notifier.notify_order_created(event.order)

    # Registrar en el bus:
    bus.subscribe(OrderCreated, SendEmailOnOrderCreated(notifier))

### Ejemplo: Presenter

    class OrderPresenter:
        def present(self, order: Order) -> OrderOutput:
            return OrderOutput(
                id=str(order.id),
                customer_email=str(order.customer_email),
                total=order.total.amount,
                ...
            )

### Ejemplo: Controller

    class CreateOrderController:
        def __init__(
            self,
            use_case: CreateOrderService,
            presenter: OrderPresenter,
        ) -> None:
            self.use_case = use_case
            self.presenter = presenter

        def handle(self, input_dto: CreateOrderInput) -> OrderOutput:
            order = self.use_case.execute(input_dto)
            return self.presenter.present(order)

## Checklist
- [ ] Crear estructura del laboratorio (domain/application/infrastructure)
- [ ] Implementar Unit of Work (Protocol + implementaciones)
- [ ] Implementar Event Handlers
- [ ] Implementar Presenter
- [ ] Implementar Controller (puro, sin FastAPI)
- [ ] Reimplementar CreateOrderService usando UoW
- [ ] Wiring con FastAPI al final
- [ ] Tests: unit, integration, e2e
- [ ] Correr ruff y mypy
- [ ] Documentar en README del laboratorio
- [ ] Commit del modulo

## Referencias
- Robert C. Martin — Clean Architecture (libro, 2017)
- Robert C. Martin — The Clean Code Blog: https://blog.cleancoder.com/
- Cosmic Python (arquitectura hexagonal/limpia): https://www.cosmicpython.com/
- Alistair Cockburn — Hexagonal Architecture: https://alistair.cockburn.us/hexagonal-architecture/
- Martin Fowler — Unit of Work: https://martinfowler.com/eaaCatalog/unitOfWork.html
- Martin Fowler — Domain Events: https://martinfowler.com/eaaDev/DomainEvent.html

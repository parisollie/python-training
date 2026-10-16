# Módulo 15 — Arquitectura Hexagonal

## Objetivos
- Separar reglas de negocio de detalles de infraestructura
- Definir puertos estables y adaptadores intercambiables
- Orquestar casos de uso con dependencias invertidas

## Contenidos clave

### Que es Arquitectura Hexagonal
Tambien llamada "Ports and Adapters" (Alistair Cockburn, 2005).
Propone que el **dominio** (reglas de negocio) este en el centro, y
la **infraestructura** (DB, HTTP, mensajeria) en la periferia.

    +--------------------------------------------------+
    |                                                  |
    |               INFRAESTRUCTURA                    |
    |                                                  |
    |  +-------------------+   +-------------------+   |
    |  |   Adaptador       |   |   Adaptador       |   |
    |  |   HTTP            |   |   SQL             |   |
    |  +---------+---------+   +---------+---------+   |
    |            |                       |             |
    |            v                       v             |
    |       +---------+             +---------+        |
    |       | PUERTO  |             | PUERTO  |        |
    |       | Notifier|             | Repo    |        |
    |       +----+----+             +----+----+        |
    |            |                       |             |
    |            +-----------+-----------+             |
    |                        |                         |
    |                        v                         |
    |              +-------------------+               |
    |              |     APLICACION    |               |
    |              |   (Casos de uso)  |               |
    |              +---------+---------+               |
    |                        |                         |
    |                        v                         |
    |              +-------------------+               |
    |              |      DOMINIO      |               |
    |              |  (Entidades, VO)  |               |
    |              +-------------------+               |
    |                                                  |
    +--------------------------------------------------+

### Capas

**Dominio** (centro):
- Entidades y Value Objects (Money, OrderId, Email)
- Reglas de negocio puras (sin dependencias externas)
- Puertos (Protocols) que el dominio necesita
- NO conoce frameworks, DB, ni HTTP

**Aplicacion**:
- Casos de uso (CreateOrder, GetOrder, CancelOrder)
- Orquesta el dominio y los puertos
- DTOs de entrada/salida (no expone entidades crudas)
- NO conoce implementaciones concretas

**Infraestructura** (periferia):
- Adaptadores: repositorios (SQL, Memory), notificadores (HTTP, Email)
- API HTTP (FastAPI)
- Configuracion, wiring
- Depende del dominio y la aplicacion

### Puertos vs Adaptadores

| Concepto | Que es |
|----------|--------|
| Puerto | Interface (Protocol) que define el contrato |
| Adaptador | Implementacion concreta del puerto |
| Puerto primario | Lo que entra (API HTTP, CLI, mensajeria) |
| Puerto secundario | Lo que sale (DB, email, APIs externas) |

### Regla de dependencia
Las dependencias **apuntan hacia el dominio**:

    Infraestructura -> Aplicacion -> Dominio

Nunca al reves. El dominio no importa infraestructura.

### Value Objects vs Entidades

| Aspecto | Value Object | Entidad |
|---------|--------------|---------|
| Identidad | Por valor (Money(100) == Money(100)) | Por id (Order(1) != Order(2)) |
| Mutabilidad | Inmutable (frozen dataclass) | Mutable |
| Ejemplos | Money, Email, OrderId | Order, Customer, Product |
| Comparacion | Por valor | Por id |

### DTOs (Data Transfer Objects)
Objetos planos para transportar datos entre capas:
- `CreateOrderInput`: DTO de entrada (no es la entidad)
- `OrderOutput`: DTO de salida (evita exponer entidades)
- Se validan con Pydantic (en infraestructura)

### Inyeccion de dependencias
El wiring se hace en la **infraestructura**, no en el dominio:

    def get_order_service() -> OrderService:
        repo = SQLOrderRepository(engine)
        notifier = HttpNotifier(url)
        return OrderService(repo, notifier)

## Laboratorio

Sistema de ordenes con arquitectura hexagonal:

1. **Dominio**:
   - Value Objects: `OrderId`, `Money`, `Email`
   - Entidad: `Order` con lógica de negocio pura
   - Puertos: `OrderRepository`, `Notifier`

2. **Aplicacion**:
   - Caso de uso: `CreateOrderService`
   - DTOs: `CreateOrderInput`, `OrderOutput`

3. **Infraestructura**:
   - Adaptadores: `InMemoryOrderRepository`, `FakeNotifier`
   - Adaptador HTTP (opcional): `HttpNotifier` con httpx
   - Wiring con dependency injection

4. **Tests**:
   - Unit (dominio puro, sin mocks)
   - Contract (todos los adaptadores cumplen el puerto)
   - E2E (flujo completo con adaptador real)

## Conceptos clave

### ¿Por que PEP 20 importa aqui?
- "Simple es mejor que complejo" -> 3 capas, no 10
- "Explícito es mejor que implícito" -> el wiring está a la vista
- "Los errores nunca deben pasar silenciosamente" -> puertos que lanzan errores de dominio

### Diferencia con SOLID (Módulo 12)
- SOLID aplica **principios** a clases
- Hexagonal define **estructura** en capas
- Ambos se complementan: SOLID dentro de cada capa, Hexagonal entre capas

### Cuando usar Arquitectura Hexagonal

**Si**:
- Dominio complejo (muchas reglas, validaciones, invariantes)
- Vida útil larga (cambiar DB/framework sin reescribir)
- Múltiples clientes (API, CLI, mensajería)
- Testing prioritario del dominio

**No**:
- CRUD simple
- Prototipos o scripts
- Equipos chicos con dominio simple
- Proyectos de vida corta

### Ejemplo: Value Object

    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Money:
        amount: float
        currency: str = "USD"

        def __post_init__(self):
            if self.amount < 0:
                raise ValueError("Money no puede ser negativo")

        def __add__(self, other: "Money") -> "Money":
            if self.currency != other.currency:
                raise ValueError("No se pueden sumar monedas distintas")
            return Money(self.amount + other.amount, self.currency)

        def __str__(self) -> str:
            return f"{self.amount:.2f} {self.currency}"

### Ejemplo: Puerto

    from typing import Protocol

    class OrderRepository(Protocol):
        def save(self, order: Order) -> None: ...
        def find_by_id(self, order_id: OrderId) -> Order | None: ...

### Ejemplo: Caso de uso

    class CreateOrderService:
        def __init__(
            self,
            repository: OrderRepository,
            notifier: Notifier,
        ) -> None:
            self._repository = repository
            self._notifier = notifier

        def execute(self, input_dto: CreateOrderInput) -> OrderOutput:
            order = Order.create(
                customer_email=Email(input_dto.customer_email),
                items=input_dto.items,
            )
            self._repository.save(order)
            self._notifier.notify_order_created(order)
            return OrderOutput.from_entity(order)

### Ejemplo: Adaptador intercambiable

    # Test: en memoria
    service = CreateOrderService(InMemoryOrderRepository(), FakeNotifier())

    # Produccion: SQL + HTTP
    service = CreateOrderService(
        SQLOrderRepository(engine),
        HttpNotifier("https://api.example.com/notify"),
    )

    # El caso de uso NO cambia

## Checklist
- [ ] Crear estructura (domain/application/infrastructure/tests)
- [ ] Implementar Value Objects (OrderId, Money, Email)
- [ ] Implementar entidad Order (con logica pura)
- [ ] Definir puertos (OrderRepository, Notifier)
- [ ] Implementar caso de uso CreateOrderService
- [ ] DTOs con Pydantic (CreateOrderInput, OrderOutput)
- [ ] Adaptadores InMemory y Fake
- [ ] Adaptador HTTP con httpx (opcional)
- [ ] Tests: unit, contract, e2e
- [ ] Correr ruff y mypy
- [ ] Documentar en README del laboratorio
- [ ] Commit del modulo

## Referencias
- Alistair Cockburn — Hexagonal Architecture: https://alistair.cockburn.us/hexagonal-architecture/
- Robert C. Martin — Clean Architecture (libro)
- Python typing.Protocol: https://docs.python.org/3/library/typing.html#typing.Protocol
- PEP 544 — Protocols: https://peps.python.org/pep-0544/
- Real Python — Hexagonal Architecture: https://realpython.com/python-architecture/
- Cosmic Python (libro): https://www.cosmicpython.com/

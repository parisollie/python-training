# Módulo 12 — Principios SOLID aplicados en Python

## Objetivos
- Aplicar SOLID a servicios y dominio
- Reducir acoplamiento y mejorar extensibilidad
- Usar Protocols y factories para inyeccion de dependencias

## Contenidos clave

### Que es SOLID
Cinco principios de diseno orientado a objetos, formulados por Robert C. Martin:

- **S**RP: Single Responsibility Principle
- **O**CP: Open/Closed Principle
- **L**SP: Liskov Substitution Principle
- **I**SP: Interface Segregation Principle
- **D**IP: Dependency Inversion Principle

### SRP — Single Responsibility
Una clase debe tener **una sola razon para cambiar**.

Senales de violacion:
- La clase tiene mas de una responsabilidad ("y" en su descripcion)
- Los tests son dificiles porque mezclan cosas
- Un cambio en la DB obliga a tocar la logica de negocio

### OCP — Open/Closed
Abierto a extension, cerrado a modificacion.

- Se extiende con nuevas clases, no modificando las existentes
- Se logra con polimorfismo (herencia o Protocol)
- Ejemplo: agregar un metodo de pago sin tocar el servicio

### LSP — Liskov Substitution
Las subclases deben poder sustituir a sus clases base sin romper.

Senales de violacion:
- La subclase lanza excepciones que la base no lanza
- La subclase cambia el significado del metodo
- isinstance/type checks para decidir comportamiento

### ISP — Interface Segregation
Muchas interfaces pequenas son mejores que una grande.

- No obligar a implementar metodos que no se usan
- En Python: Protocols especificos por caso de uso

### DIP — Dependency Inversion
Depender de abstracciones, no de implementaciones.

- Los modulos de alto nivel no deben depender de los de bajo nivel
- Ambos deben depender de abstracciones (Protocols)
- Se logra con inyeccion de dependencias

## Laboratorio

Refactor de un servicio de ordenes aplicando SOLID.

**Antes (violando SOLID):**
- OrderService con logica + acceso a DB + envio de emails
- Sin interfaz, dificil de testear

**Despues (aplicando SOLID):**
1. **SRP**: separar en OrderService (logica) + OrderRepository (DB) + Notifier (email)
2. **OCP**: agregar metodos de pago sin tocar OrderService
3. **LSP**: OrderRepository (Protocol) implementado por InMemory y SQL sin cambiar el servicio
4. **ISP**: Protocols especificos (OrderRepository, Notifier, PaymentProcessor)
5. **DIP**: OrderService depende de Protocols, no de implementaciones concretas

## Conceptos clave

### ¿Por que PEP 20 importa aqui?
- "Explicito es mejor que implicito" -> declarar Protocols
- "Simple es mejor que complejo" -> 3 Protocol pequenos > 1 ABC grande
- "Los errores nunca deben pasar silenciosamente" -> validar en el dominio

### Estructura del refactor

    services/               <- alto nivel (logica)
      order_service.py      <- depende de Protocols
    domain/                 <- reglas de negocio
      order.py              <- entidad con validaciones
      protocols.py          <- OrderRepository, Notifier, PaymentProcessor
    infrastructure/         <- bajo nivel (detalles)
      repositories.py       <- InMemoryOrderRepository, SQLOrderRepository
      notifiers.py          <- EmailNotifier, ConsoleNotifier
      payments.py           <- StripePayment, FakePayment

### Ejemplo: SRP

**Mal (una clase hace todo):**

    class OrderService:
        def create_order(self, user_id, items):
            # validar
            # guardar en DB
            # enviar email
            # cobrar
            ...

**Bien (responsabilidades separadas):**

    class OrderService:
        def __init__(self, repo, notifier, payment):
            self.repo = repo
            self.notifier = notifier
            self.payment = payment

        def create_order(self, user_id, items):
            order = Order(user_id=user_id, items=items)
            self.payment.charge(order.total)
            self.repo.save(order)
            self.notifier.notify_order_created(order)
            return order

### Ejemplo: DIP con Protocol

    from typing import Protocol

    class OrderRepository(Protocol):
        def save(self, order: Order) -> None: ...
        def get(self, order_id: str) -> Order | None: ...

    class OrderService:
        def __init__(self, repo: OrderRepository):
            self.repo = repo

    # En produccion:
    service = OrderService(SQLOrderRepository(engine))

    # En tests:
    service = OrderService(InMemoryOrderRepository())

### Ejemplo: OCP con polimorfismo

    class PaymentProcessor(Protocol):
        def charge(self, amount: float) -> bool: ...

    class StripePayment:
        def charge(self, amount: float) -> bool:
            ... # API real

    class FakePayment:
        def charge(self, amount: float) -> bool:
            return True  # para tests

    # OrderService no cambia cuando se agrega PayPal, Crypto, etc.

## Checklist
- [x] Crear estructura del laboratorio
- [x] Identificar violaciones SOLID en codigo "malo"
- [x] Definir Protocols (Repository, Notifier, PaymentProcessor)
- [x] Implementar dominio (Order con validaciones)
- [x] Implementar OrderService dependiendo de Protocols
- [x] Implementaciones en memoria + SQL + Fake
- [x] Tests verificando LSP (mismas aserciones para todas las impl)
- [x] Correr ruff y mypy
- [x] Documentar en README del laboratorio
- [x] Commit del modulo

## Referencias
- Robert C. Martin — Clean Architecture (libro)
- SOLID (Wikipedia): https://en.wikipedia.org/wiki/SOLID
- Python typing.Protocol: https://docs.python.org/3/library/typing.html#typing.Protocol
- Real Python — SOLID: https://realpython.com/solid-principles-python/
- PEP 544 — Protocols: https://peps.python.org/pep-0544/

# Laboratorio 05 — Tipado estático avanzado

Demuestra el uso de tipado avanzado en Python 3.12 con mypy strict:

- **Literal**: valores restringidos a un conjunto
- **TypedDict**: diccionarios con estructura fija
- **Protocol**: interfaces estructurales (duck typing con tipos)
- **Final**: constantes no reasignables
- **Annotated**: metadatos sobre tipos

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1
- mypy en modo strict

## Estructura

```text
lab_05_typing/
├── README.md              ← este archivo
├── models.py              ← entidades con tipos avanzados
├── repository.py          ← Protocol + implementacion + servicio
└── tests/
    ├── test_models.py     ← 9 tests
    └── test_repository.py ← 14 tests
```

## Modelos de dominio (models.py)

### Tipos avanzados usados

| Tipo | Uso en el laboratorio |
|------|----------------------|
| Literal | `OrderStatus = Literal["pending", "confirmed", ...]` |
| Final | `TAX_RATE: Final[float] = 0.16` |
| Annotated | `Quantity = Annotated[int, "cantidad >= 1"]` |
| TypedDict | `OrderJSON`, `OrderItemJSON` |

### OrderItem

| Campo | Tipo | Validación |
|-------|------|------------|
| name | str | — |
| quantity | Annotated[int, ...] | >= 1 |
| unit_price | Annotated[float, ...] | >= 0.0 |

Propiedad derivada: `subtotal` = quantity × unit_price

### Order

| Campo | Tipo | Validación |
|-------|------|------------|
| id | str | no vacío |
| customer | str | no vacío |
| status | OrderStatus (Literal) | default: "pending" |
| items | list[OrderItem] | max: 100 |

Propiedades: `subtotal`, `tax`, `total`, `total_items`
Métodos: `add_item()`, `change_status()`

### order_from_json

Convierte un `OrderJSON` (TypedDict) en una entidad `Order`.

## Repositorio (repository.py)

### OrderRepository (Protocol)

Define la interfaz (puerto) para repositorios:

    class OrderRepository(Protocol):
        def save(self, order: Order) -> None: ...
        def get(self, order_id: str) -> Order | None: ...
        def list_all(self) -> list[Order]: ...
        def delete(self, order_id: str) -> bool: ...

### InMemoryOrderRepository

Implementación en memoria que cumple el Protocol **sin heredar**.

### OrderService

Depende del **Protocol**, no de la implementación. Esto permite cambiar
la implementación sin tocar el servicio (Inversión de Dependencias).

## Ejemplo: flujo completo

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_05_typing')
    from models import Order, OrderItem
    from repository import InMemoryOrderRepository, OrderService

    service = OrderService(InMemoryOrderRepository())

    order = Order(id='ORD-001', customer='Paul')
    order.add_item(OrderItem(name='Teclado', quantity=2, unit_price=25.0))
    service.create(order)

    order.change_status('confirmed')

    recuperada = service.get('ORD-001')
    print(f'Estado: {recuperada.status}')
    print(f'Total: {recuperada.total}')
    print(f'Ordenes: {service.count()}')
    "

Salida esperada:

    Estado: confirmed
    Total: 58.0
    Ordenes: 1

## Ejemplo: TypedDict y Literal

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_05_typing')
    from models import order_from_json, OrderJSON

    data: OrderJSON = {
        'id': 'ORD-002',
        'customer': 'Ana',
        'status': 'pending',
        'items': [{'name': 'Monitor', 'quantity': 1, 'unit_price': 130.0}],
    }

    order = order_from_json(data)
    print(f'Orden: {order.id} - {order.customer} - {order.status}')
    print(f'Total: {order.total}')
    "

Salida esperada:

    Orden: ORD-002 - Ana - pending
    Total: 150.8

## Cómo ejecutar los tests

### Todos los tests

    poetry run pytest 04_laboratorios/lab_05_typing/tests/ -v

Salida esperada:

    23 passed in 0.02s

### Con cobertura

    poetry run pytest 04_laboratorios/lab_05_typing/tests/ --cov=04_laboratorios/lab_05_typing --cov-report=term-missing

### Solo un archivo

    poetry run pytest 04_laboratorios/lab_05_typing/tests/test_models.py -v
    poetry run pytest 04_laboratorios/lab_05_typing/tests/test_repository.py -v

### Archivos de tests

| Archivo | Qué cubre | Tests |
|---------|-----------|-------|
| test_models.py | Order, OrderItem, order_from_json, validaciones | 9 |
| test_repository.py | Repositorio, Protocol, OrderService | 14 |

## Verificación de calidad

    poetry run ruff check 04_laboratorios/lab_05_typing/
    poetry run mypy 04_laboratorios/lab_05_typing/
    poetry run pre-commit run --all-files

## Notas de implementación

### mypy strict en acción

El proyecto usa mypy en modo `strict`. Esto significa que:
- Todas las funciones deben tener type hints
- Los `Optional` deben manejarse explícitamente
- No se permiten retornos `Any` implícitos
- `warn_return_any`, `warn_unused_configs` activos

### Sobre # type: ignore

En `models.py` hay un `# type: ignore[arg-type]` en `order_from_json`.
Está **justificado**: mypy no puede inferir que validamos `data["status"]`
antes de pasarlo a `Order`. La excepción local está documentada.

### Sobre Protocol

El `OrderRepository` es un **Protocol**, no una clase base. Esto significa:
- Cualquier clase con los métodos correctos lo cumple (duck typing tipado)
- No hay herencia explícita
- Es ideal para inyección de dependencias

## Comandos rápidos (resumen)

    # Tests
    poetry run pytest 04_laboratorios/lab_05_typing/tests/ -v

    # Cobertura
    poetry run pytest 04_laboratorios/lab_05_typing/tests/ --cov=04_laboratorios/lab_05_typing --cov-report=term-missing

    # Calidad
    poetry run ruff check 04_laboratorios/lab_05_typing/
    poetry run mypy 04_laboratorios/lab_05_typing/

## Estado

- [x] Crear estructura del laboratorio
- [x] Literal, Final, Annotated en models.py
- [x] TypedDict para JSON
- [x] Protocol para repositorio
- [x] OrderService con inyección de dependencias
- [x] 23 tests con pytest
- [x] ruff + mypy strict OK
- [x] Documentación completa

## Clonar este laboratorio

    git clone https://github.com/parisollie/python-training.git
    cd python-training
    poetry install

    # Ejecutar tests
    poetry run pytest 04_laboratorios/lab_05_typing/tests/ -v

## Referencias

- Python docs — typing: https://docs.python.org/3/library/typing.html
- PEP 484 — Type Hints: https://peps.python.org/pep-0484/
- PEP 604 — Union operator |: https://peps.python.org/pep-0604/
- PEP 695 — Type Parameter Syntax: https://peps.python.org/pep-0695/
- mypy docs: https://mypy.readthedocs.io/
- typing.Protocol: https://docs.python.org/3/library/typing.html#typing.Protocol
- typing.TypedDict: https://docs.python.org/3/library/typing.html#typing.TypedDict
- typing.Literal: https://docs.python.org/3/library/typing.html#typing.Literal

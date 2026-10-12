# Laboratorio 04 — Objetos y modelos de datos

Modela órdenes de compra con dos enfoques complementarios:
1. **dataclass** `Order` → entidad de dominio con lógica derivada
2. **Pydantic** `OrderIn` / `OrderOut` → validación y serialización

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1
- Pydantic (instalado en el proyecto)

## Estructura

lab_04_orders/
├── README.md              ← este archivo
├── models.py              ← dataclasses Order y OrderItem
├── schemas.py             ← modelos Pydantic y conversores
└── tests/
    ├── test_models.py     ← 16 tests
    └── test_schemas.py    ← 11 tests

## Instalación

Desde la raíz del proyecto:

    poetry install

## Modelos de dominio (models.py)

### OrderItem

| Campo | Tipo | Validación |
|-------|------|------------|
| name | str | — |
| quantity | int | >= 1 |
| unit_price | float | >= 0.0 |

Propiedad derivada: `subtotal` = quantity × unit_price

### Order

| Campo | Tipo | Validación |
|-------|------|------------|
| id | str | no vacío |
| customer | str | no vacío |
| items | list[OrderItem] | default: [] |

Propiedades derivadas:
- `subtotal` = suma de subtotales de items
- `tax` = subtotal × 0.16 (redondeado a 2 decimales)
- `total` = subtotal + tax
- `total_items` = suma de quantities

Métodos:
- `add_item(item)` → agrega un item
- `__lt__` → compara por `total` (para sorted, min, max)

## Schemas Pydantic (schemas.py)

### OrderItemIn / OrderItemOut

- `OrderItemIn` → entrada sin subtotal
- `OrderItemOut` → salida con subtotal calculado

### OrderIn / OrderOut

- `OrderIn` → entrada (customer + items), sin id ni totales
- `OrderOut` → salida completa (id, items, subtotal, tax, total, total_items)

### Conversores

- `order_from_in(order_in, order_id)` → OrderIn → Order (dataclass)
- `order_to_out(order)` → Order → OrderOut (Pydantic)

## Ejemplo: flujo completo

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_04_orders')
    from schemas import OrderIn, order_from_in, order_to_out

    json_entrada = {
        'customer': 'Paul',
        'items': [
            {'name': 'Teclado', 'quantity': 2, 'unit_price': 25.0},
            {'name': 'Mouse', 'quantity': 1, 'unit_price': 15.5},
        ],
    }

    # 1. Validar JSON con Pydantic
    order_in = OrderIn.model_validate(json_entrada)

    # 2. Convertir a entidad de dominio (dataclass)
    order = order_from_in(order_in, order_id='ORD-001')
    print(f'Subtotal: {order.subtotal}')
    print(f'IVA: {order.tax}')
    print(f'Total: {order.total}')

    # 3. Convertir a schema de salida
    order_out = order_to_out(order)
    print(order_out.model_dump_json(indent=2))
    "

Salida esperada (resumen):

    Subtotal: 65.5
    IVA: 10.48
    Total: 75.98
    {
      "id": "ORD-001",
      "customer": "Paul",
      "items": [...],
      "subtotal": 65.5,
      "tax": 10.48,
      "total": 75.98,
      "total_items": 3
    }

## Ejemplo: comparar órdenes por total

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_04_orders')
    from models import Order, OrderItem

    o1 = Order(id='ORD-001', customer='Paul')
    o1.add_item(OrderItem(name='Teclado', quantity=2, unit_price=25.0))

    o2 = Order(id='ORD-002', customer='Ana')
    o2.add_item(OrderItem(name='Monitor', quantity=1, unit_price=130.0))

    o3 = Order(id='ORD-003', customer='Luis')

    print(f'o1.total = {o1.total}')
    print(f'o2.total = {o2.total}')
    print(f'o3.total = {o3.total}')
    print(f'o1 < o2: {o1 < o2}')
    print(f'Ordenadas: {[o.id for o in sorted([o2, o1, o3])]}')
    "

Salida esperada:

    o1.total = 50.0
    o2.total = 150.8
    o3.total = 0.0
    o1 < o2: True
    Ordenadas: ['ORD-003', 'ORD-001', 'ORD-002']

## Ejemplo: validación fallida (Pydantic)

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_04_orders')
    from pydantic import ValidationError
    from schemas import OrderIn

    try:
        OrderIn.model_validate({
            'customer': '',
            'items': [{'name': 'X', 'quantity': 0, 'unit_price': -1.0}],
        })
    except ValidationError as e:
        print(f'Errores de validación: {e.error_count()}')
    "

Salida esperada:

    Errores de validación: 3

## Cómo ejecutar los tests

### Todos los tests

    poetry run pytest 04_laboratorios/lab_04_orders/tests/ -v

Salida esperada:

    27 passed in 0.04s

### Con cobertura

    poetry run pytest 04_laboratorios/lab_04_orders/tests/ --cov=04_laboratorios/lab_04_orders --cov-report=term-missing

### Solo un archivo

    poetry run pytest 04_laboratorios/lab_04_orders/tests/test_models.py -v
    poetry run pytest 04_laboratorios/lab_04_orders/tests/test_schemas.py -v

### Archivos de tests

| Archivo | Qué cubre | Tests |
|---------|-----------|-------|
| test_models.py | OrderItem, Order (subtotal, tax, total, comparaciones) | 16 |
| test_schemas.py | OrderIn, OrderOut, conversores, flujo completo | 11 |

## Verificación de calidad

    poetry run ruff check 04_laboratorios/lab_04_orders/
    poetry run mypy 04_laboratorios/lab_04_orders/
    poetry run pre-commit run --all-files

## Comandos rápidos (resumen)

    # Tests
    poetry run pytest 04_laboratorios/lab_04_orders/tests/ -v

    # Cobertura
    poetry run pytest 04_laboratorios/lab_04_orders/tests/ --cov=04_laboratorios/lab_04_orders --cov-report=term-missing

    # Calidad
    poetry run ruff check 04_laboratorios/lab_04_orders/
    poetry run mypy 04_laboratorios/lab_04_orders/

## Estado

- [x] Crear estructura del laboratorio
- [x] Implementar dataclass Order y OrderItem
- [x] Implementar modelos Pydantic (OrderIn/OrderOut)
- [x] Conversores order_from_in / order_to_out
- [x] 27 tests con pytest
- [x] ruff + mypy OK
- [x] Documentación completa

## Clonar este laboratorio

    git clone https://github.com/parisollie/python-training.git
    cd python-training
    poetry install

    # Ejecutar tests
    poetry run pytest 04_laboratorios/lab_04_orders/tests/ -v

## Referencias

- Python docs — dataclasses: https://docs.python.org/3/library/dataclasses.html
- Python docs — Modelo de datos (dunder methods): https://docs.python.org/3/reference/datamodel.html
- PEP 557 — Data Classes: https://peps.python.org/pep-0557/
- Pydantic docs: https://docs.pydantic.dev/

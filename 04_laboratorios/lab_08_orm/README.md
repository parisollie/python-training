# Laboratorio 08 — Acceso a datos y ORM (SQLAlchemy 2.0)

Modela usuarios, órdenes e items con SQLAlchemy 2.0 (estilo moderno) y prueba el CRUD con SQLite en memoria.

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1
- SQLAlchemy 2.1.4
- Alembic 1.20.0

## Estructura

lab_08_orm/
├── README.md              ← este archivo
├── models.py              ← User, Order, OrderItem (SQLAlchemy 2.0)
├── repository.py          ← CRUD con Session
└── tests/
    ├── conftest.py        ← fixture engine SQLite en memoria
    ├── test_models.py     ← 5 tests de modelos
    └── test_repository.py ← 17 tests de repositorio

## Modelos (models.py)

### User

| Campo | Tipo | Constraints |
|-------|------|-------------|
| id | int | primary key |
| email | str | unique, indexed |
| name | str | max 100 |
| created_at | datetime | UTC, default now |

Relación: `orders` (1-N con Order, cascade delete)

### Order

| Campo | Tipo | Constraints |
|-------|------|-------------|
| id | int | primary key |
| user_id | int | FK users.id, ondelete CASCADE |
| status | str | default "pending" |
| created_at | datetime | UTC, default now |

Relación: `user` (N-1 con User), `items` (1-N con OrderItem, cascade delete)
Propiedad: `total` = suma de subtotales de items

### OrderItem

| Campo | Tipo | Constraints |
|-------|------|-------------|
| id | int | primary key |
| order_id | int | FK orders.id, ondelete CASCADE |
| product | str | max 100 |
| quantity | int | default 1 |
| unit_price | float | default 0.0 |

Relación: `order` (N-1 con Order)
Propiedad: `subtotal` = quantity * unit_price

## Repositorio (repository.py)

### UserRepository

| Método | Descripción |
|--------|-------------|
| `create(email, name)` | Crea un usuario |
| `get(user_id)` | Obtiene por id |
| `get_by_email(email)` | Obtiene por email |
| `list_all()` | Lista todos |
| `update_name(user_id, name)` | Actualiza nombre |
| `delete(user_id)` | Elimina |

### OrderRepository

| Método | Descripción |
|--------|-------------|
| `create(user_id, items)` | Crea orden con items (eager loading) |
| `get(order_id)` | Obtiene con items cargados |
| `list_by_user(user_id)` | Lista las órdenes del usuario |
| `update_status(order_id, status)` | Cambia estado |
| `delete(order_id)` | Elimina (cascade borra items) |

## Ejemplo: crear usuario y orden

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_08_orm')
    from sqlalchemy import create_engine
    from repository import init_db, UserRepository, OrderRepository

    engine = create_engine('sqlite:///:memory:')
    init_db(engine)

    users = UserRepository(engine)
    orders = OrderRepository(engine)

    u = users.create(email='ana@example.com', name='Ana')
    print(f'Usuario: id={u.id}, email={u.email}')

    o = orders.create(user_id=u.id, items=[
        {'product': 'Monitor', 'quantity': 1, 'unit_price': 130.0},
        {'product': 'Cable', 'quantity': 2, 'unit_price': 5.0},
    ])
    print(f'Orden: id={o.id}, items={len(o.items)}, total={o.total}')
    "

Salida esperada:

    Usuario: id=1, email=ana@example.com
    Orden: id=1, items=2, total=140.0

## Ejemplo: listar órdenes de un usuario

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_08_orm')
    from sqlalchemy import create_engine
    from repository import init_db, UserRepository, OrderRepository

    engine = create_engine('sqlite:///:memory:')
    init_db(engine)

    users = UserRepository(engine)
    orders = OrderRepository(engine)

    u = users.create(email='paul@example.com', name='Paul')
    orders.create(user_id=u.id, items=[{'product': 'A', 'quantity': 1, 'unit_price': 10.0}])
    orders.create(user_id=u.id, items=[{'product': 'B', 'quantity': 1, 'unit_price': 20.0}])

    user_orders = orders.list_by_user(u.id)
    print(f'Ordenes: {len(user_orders)}')
    for o in user_orders:
        print(f'  - Orden {o.id}: total={o.total}, status={o.status}')
    "

Salida esperada:

    Ordenes: 2
      - Orden 1: total=10.0, status=pending
      - Orden 2: total=20.0, status=pending

## Ejemplo: cascade delete

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_08_orm')
    from sqlalchemy import create_engine
    from repository import init_db, UserRepository, OrderRepository

    engine = create_engine('sqlite:///:memory:')
    init_db(engine)

    users = UserRepository(engine)
    orders = OrderRepository(engine)

    u = users.create(email='x@y.com', name='X')
    o = orders.create(user_id=u.id, items=[{'product': 'P', 'quantity': 1, 'unit_price': 1.0}])

    print(f'Antes: ordenes={len(orders.list_by_user(u.id))}')
    users.delete(u.id)
    print(f'Despues: ordenes={len(orders.list_by_user(u.id))}')
    "

Salida esperada:

    Antes: ordenes=1
    Despues: ordenes=0

## Cómo ejecutar los tests

### Todos los tests

    poetry run pytest 04_laboratorios/lab_08_orm/tests/ -v

Salida esperada:

    22 passed in 0.06s

### Con cobertura

    poetry run pytest 04_laboratorios/lab_08_orm/tests/ --cov=04_laboratorios/lab_08_orm --cov-report=term-missing

### Solo un archivo

    poetry run pytest 04_laboratorios/lab_08_orm/tests/test_models.py -v
    poetry run pytest 04_laboratorios/lab_08_orm/tests/test_repository.py -v

### Archivos de tests

| Archivo | Qué cubre | Tests |
|---------|-----------|-------|
| test_models.py | User, Order, OrderItem, cascades | 5 |
| test_repository.py | CRUD de User y Order | 17 |

### SQLite en memoria

Los tests usan SQLite en memoria con `StaticPool`. Esto garantiza:

- Tests rápidos (sin disco)
- Aislamiento total (cada test tiene su propia BD)
- Sin limpieza manual (al cerrar el engine, la BD desaparece)

## Verificación de calidad

    poetry run ruff check 04_laboratorios/lab_08_orm/
    poetry run mypy 04_laboratorios/lab_08_orm/
    poetry run pre-commit run --all-files

## Notas de implementación

### SQLAlchemy 2.0 vs estilo antiguo

| Estilo antiguo | Estilo moderno (2.0) |
|----------------|----------------------|
| `session.query(User).all()` | `session.scalars(select(User)).all()` |
| `session.query(User).filter(...)` | `session.scalars(select(User).where(...))` |
| `session.query(User).get(1)` | `session.get(User, 1)` |

El estilo 2.0 es más explícito y compatible con mypy.

### Mapped[...] y mapped_column

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)

- `Mapped[T]` indica el tipo Python
- `mapped_column(...)` da configuración adicional (PK, unicidad, longitud)

### DetachedInstanceError (lección aprendida)

**Error común:** después de cerrar la `Session`, acceder a una relación lazy
(ej: `order.items`) lanza `DetachedInstanceError`.

**Solución:** usar `selectinload` para cargar la relación ANTES de cerrar la sesión:

    stmt = select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    order = session.scalar(stmt)

Esto carga los items en una sola query adicional (evita N+1).

### Cascade delete

    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

Al borrar un User, sus Orders se borran automáticamente. Y al borrar una Order, sus OrderItems también.

### Transacciones

Cada operación del repositorio abre su propia `Session` con `with Session(engine) as session`. Al salir del `with`, la sesión se cierra y los cambios se confirman.

Para transacciones más complejas:

    with Session(engine) as session:
        with session.begin():
            # múltiples operaciones atómicas
            ...

## Comandos rápidos (resumen)

    # Tests
    poetry run pytest 04_laboratorios/lab_08_orm/tests/ -v

    # Calidad
    poetry run ruff check 04_laboratorios/lab_08_orm/
    poetry run mypy 04_laboratorios/lab_08_orm/

    # Ejemplo interactivo
    poetry run python -c "
    import sys; sys.path.insert(0, '04_laboratorios/lab_08_orm')
    from sqlalchemy import create_engine
    from repository import init_db, UserRepository
    e = create_engine('sqlite:///:memory:'); init_db(e)
    u = UserRepository(e).create(email='a@b.com', name='A')
    print(f'Usuario creado: {u.id}')
    "

## Estado

- [x] Crear estructura del laboratorio
- [x] SQLAlchemy y Alembic instalados
- [x] Modelos User, Order, OrderItem
- [x] Relaciones 1-N con cascade
- [x] CRUD con eager loading
- [x] 22 tests con SQLite en memoria
- [x] ruff + mypy OK
- [x] Documentación completa

## Pendiente (más adelante)

- Migraciones con Alembic (se profundiza en Módulo 17)
- Uso de PostgreSQL real
- Consultas avanzadas (joins, agregaciones)

## Clonar este laboratorio

    git clone https://github.com/parisollie/python-training.git
    cd python-training
    poetry install

    # Tests
    poetry run pytest 04_laboratorios/lab_08_orm/tests/ -v

## Referencias

- SQLAlchemy docs: https://docs.sqlalchemy.org/
- SQLAlchemy 2.0 ORM tutorial: https://docs.sqlalchemy.org/en/20/tutorial/
- SQLAlchemy — Session: https://docs.sqlalchemy.org/en/20/orm/session.html
- SQLAlchemy — Relationships: https://docs.sqlalchemy.org/en/20/orm/relationships.html
- SQLAlchemy — selectinload: https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html
- Alembic docs: https://alembic.sqlalchemy.org/

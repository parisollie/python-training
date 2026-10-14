# Módulo 08 — Acceso a datos y ORM

## Objetivos
- Modelar entidades y relaciones en un ORM
- Gestionar migraciones y transacciones
- Escribir consultas eficientes sin SQL crudo

## Contenidos clave

### Bases de datos y drivers
- **SQLite**: embebida, ideal para desarrollo y tests
- **PostgreSQL**: la opcion open source mas usada en produccion
- **SQL Server**: comun en entornos empresariales Microsoft
- Drivers: sqlite3 (stdlib), psycopg (PostgreSQL), pyodbc (SQL Server)

### SQLAlchemy Core vs ORM
- **Core**: SQL expresivo con objetos Python (tablas, columnas, select)
- **ORM**: mapeo objeto-relacional (clases Python <-> tablas)
- Recomendacion actual: usar ORM con estilo 2.0 (select, no query)

### SQLAlchemy 2.0 (estilo moderno)
- DeclarativeBase y Mapped[...]
- mapped_column() con tipos y constraints
- relationship() para relaciones 1-N y N-M
- Session como unit of work
- select() con where, join, order_by, limit

### Relaciones
- 1-N: un User tiene muchas Orders
- N-M: una Order tiene muchos OrderItems (via tabla intermedia)
- back_populates para navegacion bidireccional
- lazy loading vs eager loading (joinedload, selectinload)

### Migraciones con Alembic
- Autogenerar migraciones desde los modelos
- Upgrades y downgrades
- Versionado del esquema (tabla alembic_version)
- Buenas practicas: revisar siempre el SQL generado

### Transacciones
- Session.begin() como context manager
- Commit y rollback automaticos
- Autocommit vs transacciones explicitas

### MongoDB (introduccion)
- NoSQL orientado a documentos
- Motor: driver async oficial
- Cuando usarlo (documentos flexibles) vs cuando NO (transacciones complejas)

## Laboratorio

Modelos User/Order/OrderItem con SQLAlchemy 2.0:

1. User: id, email (unico), name, created_at
2. Order: id, user_id (FK), status, created_at
3. OrderItem: id, order_id (FK), product, quantity, unit_price
4. Relaciones: User -> Orders (1-N), Order -> OrderItems (1-N)
5. CRUD basico con Session
6. Tests con SQLite en memoria

## Conceptos clave

### ¿Por que PEP 20 importa aqui?
- "Explícito es mejor que implícito" -> usar SQLAlchemy 2.0 con select(), no query()
- "Los errores nunca deben pasar silenciosamente" -> no silenciar IntegrityError
- "Simple es mejor que complejo" -> SQLite para tests, PostgreSQL para produccion

### Estilo 2.0: select() vs query()

| Estilo antiguo | Estilo moderno (2.0) |
|----------------|----------------------|
| session.query(User).all() | session.scalars(select(User)).all() |
| session.query(User).filter(...) | session.scalars(select(User).where(...)) |
| session.query(User).get(1) | session.get(User, 1) |

### Cuando usar ORM vs SQL crudo

| Caso | Recomendacion |
|------|---------------|
| CRUD simple | ORM |
| Relaciones complejas | ORM con eager loading |
| Reportes y agregaciones | SQL crudo o Core |
| Bulk insert (10k+ filas) | Core con bulk_insert_mappings |
| Query muy optimizada | SQL crudo con text() |

### Ejemplo: modelo basico (SQLAlchemy 2.0)

    from datetime import datetime
    from sqlalchemy import ForeignKey, String
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

    class Base(DeclarativeBase):
        pass

    class User(Base):
        __tablename__ = "users"
        id: Mapped[int] = mapped_column(primary_key=True)
        email: Mapped[str] = mapped_column(String(255), unique=True)
        name: Mapped[str] = mapped_column(String(100))
        created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

        orders: Mapped[list["Order"]] = relationship(back_populates="user")

### Ejemplo: crear engine y session

    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    engine = create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(email="a@b.com", name="Ana")
        session.add(user)
        session.commit()

### Ejemplo: query con select()

    from sqlalchemy import select

    with Session(engine) as session:
        # Todos los usuarios
        users = session.scalars(select(User)).all()

        # Filtrar
        user = session.scalar(select(User).where(User.email == "a@b.com"))

        # Con relacion cargada
        from sqlalchemy.orm import selectinload
        users_with_orders = session.scalars(
            select(User).options(selectinload(User.orders))
        ).all()

### Ejemplo: migracion con Alembic

    # Inicializar Alembic (una sola vez)
    alembic init migrations

    # Generar migracion automatica
    alembic revision --autogenerate -m "crear tablas iniciales"

    # Aplicar migracion
    alembic upgrade head

    # Retroceder una migracion
    alembic downgrade -1

### SQLite en memoria para tests

    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool

    # StaticPool mantiene la misma conexion en memoria durante el test
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

## Checklist
- [ ] Crear estructura del laboratorio
- [ ] Instalar SQLAlchemy y Alembic
- [ ] Definir modelos (User, Order, OrderItem)
- [ ] Configurar engine SQLite en memoria
- [ ] Implementar CRUD basico
- [ ] Escribir tests con pytest
- [ ] Correr ruff y mypy
- [ ] Documentar en README del laboratorio
- [ ] Commit del modulo

## Referencias
- SQLAlchemy docs: https://docs.sqlalchemy.org/
- SQLAlchemy 2.0 ORM tutorial: https://docs.sqlalchemy.org/en/20/tutorial/
- Alembic docs: https://alembic.sqlalchemy.org/
- Motor (MongoDB async): https://motor.readthedocs.io/
- PEP 249 — DB-API: https://peps.python.org/pep-0249/
- SQLite: https://www.sqlite.org/
- PostgreSQL: https://www.postgresql.org/

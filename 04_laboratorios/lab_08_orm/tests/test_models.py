"""Tests para los modelos SQLAlchemy."""

from models import Order, OrderItem, User
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


def test_crear_usuario(engine: Engine) -> None:
    """Un User se persiste y obtiene id."""
    with Session(engine) as session:
        user = User(email="paul@example.com", name="Paul")
        session.add(user)
        session.commit()

        assert user.id is not None
        assert user.email == "paul@example.com"
        assert user.created_at is not None


def test_email_unico(engine: Engine) -> None:
    """No se permiten emails duplicados."""
    from sqlalchemy.exc import IntegrityError

    with Session(engine) as session:
        session.add(User(email="a@b.com", name="A"))
        session.commit()

    with Session(engine) as session:
        session.add(User(email="a@b.com", name="B"))
        try:
            session.commit()
            raise AssertionError("Deberia haber fallado por email duplicado")
        except IntegrityError:
            pass  # comportamiento esperado


def test_orden_con_items(engine: Engine) -> None:
    """Una Order con OrderItems se persiste y calcula total."""
    with Session(engine) as session:
        user = User(email="ana@example.com", name="Ana")
        session.add(user)
        session.commit()

        order = Order(user_id=user.id)
        order.items.append(OrderItem(product="Teclado", quantity=2, unit_price=25.0))
        order.items.append(OrderItem(product="Mouse", quantity=1, unit_price=15.5))
        session.add(order)
        session.commit()

        assert order.id is not None
        assert len(order.items) == 2
        assert order.total == 65.5


def test_subtotal_item() -> None:
    """OrderItem.subtotal = quantity * unit_price."""
    item = OrderItem(product="X", quantity=3, unit_price=10.0)
    assert item.subtotal == 30.0


def test_cascade_delete_user(engine: Engine) -> None:
    """Al borrar un User se borran sus Orders (cascade)."""
    with Session(engine) as session:
        user = User(email="x@y.com", name="X")
        session.add(user)
        session.commit()

        order = Order(user_id=user.id)
        order.items.append(OrderItem(product="P", quantity=1, unit_price=1.0))
        session.add(order)
        session.commit()

        user_id = user.id
        session.delete(user)
        session.commit()

        # No debe quedar ninguna orden de este user
        ordenes = session.scalars(select(Order).where(Order.user_id == user_id)).all()
        assert len(ordenes) == 0

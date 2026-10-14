"""Tests para el repositorio CRUD."""

from repository import OrderRepository, UserRepository
from sqlalchemy.engine import Engine

# ============================================
# UserRepository
# ============================================


def test_user_create(engine: Engine) -> None:
    """create persiste y devuelve el usuario."""
    repo = UserRepository(engine)
    user = repo.create(email="a@b.com", name="Ana")
    assert user.id is not None
    assert user.email == "a@b.com"


def test_user_get(engine: Engine) -> None:
    """get devuelve el usuario por id."""
    repo = UserRepository(engine)
    user = repo.create(email="a@b.com", name="Ana")
    assert repo.get(user.id) is not None


def test_user_get_inexistente(engine: Engine) -> None:
    """get de id inexistente devuelve None."""
    repo = UserRepository(engine)
    assert repo.get(999) is None


def test_user_get_by_email(engine: Engine) -> None:
    """get_by_email busca por email."""
    repo = UserRepository(engine)
    repo.create(email="a@b.com", name="Ana")
    found = repo.get_by_email("a@b.com")
    assert found is not None
    assert found.name == "Ana"


def test_user_get_by_email_inexistente(engine: Engine) -> None:
    """get_by_email devuelve None si no existe."""
    repo = UserRepository(engine)
    assert repo.get_by_email("no@existe.com") is None


def test_user_list_all(engine: Engine) -> None:
    """list_all devuelve todos los usuarios."""
    repo = UserRepository(engine)
    repo.create(email="a@b.com", name="Ana")
    repo.create(email="c@d.com", name="Carlos")
    users = repo.list_all()
    assert len(users) == 2


def test_user_update_name(engine: Engine) -> None:
    """update_name actualiza el nombre."""
    repo = UserRepository(engine)
    user = repo.create(email="a@b.com", name="Ana")
    assert repo.update_name(user.id, "Ana Maria") is True
    updated = repo.get(user.id)
    assert updated is not None
    assert updated.name == "Ana Maria"


def test_user_update_name_inexistente(engine: Engine) -> None:
    """update_name devuelve False si no existe."""
    repo = UserRepository(engine)
    assert repo.update_name(999, "X") is False


def test_user_delete(engine: Engine) -> None:
    """delete elimina el usuario."""
    repo = UserRepository(engine)
    user = repo.create(email="a@b.com", name="Ana")
    assert repo.delete(user.id) is True
    assert repo.get(user.id) is None


def test_user_delete_inexistente(engine: Engine) -> None:
    """delete devuelve False si no existe."""
    repo = UserRepository(engine)
    assert repo.delete(999) is False


# ============================================
# OrderRepository
# ============================================


def test_order_create_con_items(engine: Engine) -> None:
    """create devuelve la orden con items cargados (sin DetachedInstanceError)."""
    users = UserRepository(engine)
    orders = OrderRepository(engine)

    user = users.create(email="a@b.com", name="Ana")
    order = orders.create(
        user_id=user.id,
        items=[
            {"product": "Monitor", "quantity": 1, "unit_price": 130.0},
            {"product": "Cable", "quantity": 2, "unit_price": 5.0},
        ],
    )

    # No debe lanzar DetachedInstanceError
    assert len(order.items) == 2
    assert order.total == 140.0


def test_order_get(engine: Engine) -> None:
    """get devuelve la orden con items."""
    users = UserRepository(engine)
    orders = OrderRepository(engine)

    user = users.create(email="a@b.com", name="Ana")
    order = orders.create(
        user_id=user.id,
        items=[{"product": "X", "quantity": 1, "unit_price": 10.0}],
    )

    loaded = orders.get(order.id)
    assert loaded is not None
    assert len(loaded.items) == 1
    assert loaded.total == 10.0


def test_order_get_inexistente(engine: Engine) -> None:
    """get devuelve None si no existe."""
    orders = OrderRepository(engine)
    assert orders.get(999) is None


def test_order_list_by_user(engine: Engine) -> None:
    """list_by_user devuelve las ordenes del usuario."""
    users = UserRepository(engine)
    orders = OrderRepository(engine)

    u1 = users.create(email="a@b.com", name="A")
    u2 = users.create(email="c@d.com", name="C")

    orders.create(user_id=u1.id, items=[{"product": "X", "quantity": 1, "unit_price": 1.0}])
    orders.create(user_id=u1.id, items=[{"product": "Y", "quantity": 1, "unit_price": 2.0}])
    orders.create(user_id=u2.id, items=[{"product": "Z", "quantity": 1, "unit_price": 3.0}])

    u1_orders = orders.list_by_user(u1.id)
    u2_orders = orders.list_by_user(u2.id)

    assert len(u1_orders) == 2
    assert len(u2_orders) == 1


def test_order_update_status(engine: Engine) -> None:
    """update_status cambia el estado."""
    users = UserRepository(engine)
    orders = OrderRepository(engine)

    user = users.create(email="a@b.com", name="Ana")
    order = orders.create(
        user_id=user.id,
        items=[{"product": "X", "quantity": 1, "unit_price": 1.0}],
    )

    assert orders.update_status(order.id, "confirmed") is True
    updated = orders.get(order.id)
    assert updated is not None
    assert updated.status == "confirmed"


def test_order_update_status_inexistente(engine: Engine) -> None:
    """update_status devuelve False si no existe."""
    orders = OrderRepository(engine)
    assert orders.update_status(999, "x") is False


def test_order_delete_cascade(engine: Engine) -> None:
    """delete elimina la orden y sus items (cascade)."""
    from models import OrderItem
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    users = UserRepository(engine)
    orders = OrderRepository(engine)

    user = users.create(email="a@b.com", name="Ana")
    order = orders.create(
        user_id=user.id,
        items=[{"product": "X", "quantity": 1, "unit_price": 1.0}],
    )
    order_id = order.id

    assert orders.delete(order_id) is True
    assert orders.get(order_id) is None

    # Items huerfanos no deben quedar
    with Session(engine) as session:
        items = session.scalars(select(OrderItem).where(OrderItem.order_id == order_id)).all()
        assert len(items) == 0

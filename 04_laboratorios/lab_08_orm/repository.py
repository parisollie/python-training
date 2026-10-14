"""Repositorio CRUD para User, Order y OrderItem usando SQLAlchemy 2.0.

Demuestra:
- Session como unit of work
- Estilo 2.0: select() en lugar de query()
- Eager loading con selectinload para evitar N+1
- Transacciones con Session.begin()
"""

from typing import Any

from models import Base, Order, OrderItem, User
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, selectinload


class UserRepository:
    """CRUD para User."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def create(self, email: str, name: str) -> User:
        """Crea un usuario.

        Args:
            email: Email unico.
            name: Nombre.

        Returns:
            El usuario creado con id asignado.
        """
        with Session(self.engine) as session:
            user = User(email=email, name=name)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def get(self, user_id: int) -> User | None:
        """Obtiene un usuario por id."""
        with Session(self.engine) as session:
            return session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        """Obtiene un usuario por email."""
        with Session(self.engine) as session:
            return session.scalar(select(User).where(User.email == email))

    def list_all(self) -> list[User]:
        """Lista todos los usuarios."""
        with Session(self.engine) as session:
            return list(session.scalars(select(User).order_by(User.id)))

    def update_name(self, user_id: int, new_name: str) -> bool:
        """Actualiza el nombre. Devuelve True si existia."""
        with Session(self.engine) as session:
            user = session.get(User, user_id)
            if user is None:
                return False
            user.name = new_name
            session.commit()
            return True

    def delete(self, user_id: int) -> bool:
        """Elimina un usuario. Devuelve True si existia."""
        with Session(self.engine) as session:
            user = session.get(User, user_id)
            if user is None:
                return False
            session.delete(user)
            session.commit()
            return True


class OrderRepository:
    """CRUD para Order con carga de items."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def create(self, user_id: int, items: list[dict[str, Any]]) -> Order:
        """Crea una orden con sus items.

        Args:
            user_id: FK al usuario.
            items: Lista de dicts con product, quantity, unit_price.

        Returns:
            La orden creada con id y items.
        """
        with Session(self.engine) as session:
            order = Order(user_id=user_id)
            for item_data in items:
                order.items.append(OrderItem(**item_data))
            session.add(order)
            session.commit()

            # Recargar con eager loading para que items este disponible
            # fuera de la sesion (evita DetachedInstanceError)
            stmt = select(Order).options(selectinload(Order.items)).where(Order.id == order.id)
            loaded = session.scalar(stmt)
            if loaded is None:
                raise RuntimeError("No se pudo recargar la orden recien creada")
            return loaded

    def get(self, order_id: int) -> Order | None:
        """Obtiene una orden con sus items cargados (eager)."""
        with Session(self.engine) as session:
            stmt = select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
            return session.scalar(stmt)

    def list_by_user(self, user_id: int) -> list[Order]:
        """Lista las ordenes de un usuario con items cargados."""
        with Session(self.engine) as session:
            stmt = (
                select(Order)
                .options(selectinload(Order.items))
                .where(Order.user_id == user_id)
                .order_by(Order.id)
            )
            return list(session.scalars(stmt))

    def update_status(self, order_id: int, new_status: str) -> bool:
        """Actualiza el status. Devuelve True si existia."""
        with Session(self.engine) as session:
            order = session.get(Order, order_id)
            if order is None:
                return False
            order.status = new_status
            session.commit()
            return True

    def delete(self, order_id: int) -> bool:
        """Elimina una orden (y sus items por cascade)."""
        with Session(self.engine) as session:
            order = session.get(Order, order_id)
            if order is None:
                return False
            session.delete(order)
            session.commit()
            return True


def init_db(engine: Engine) -> None:
    """Crea todas las tablas en el engine dado.

    Args:
        engine: Engine de SQLAlchemy.
    """
    Base.metadata.create_all(engine)

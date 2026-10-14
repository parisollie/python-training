"""Modelos SQLAlchemy 2.0 para la API.

Reutiliza el patron del Módulo 08 pero agrega:
- hashed_password en User (para JWT)
- status Literal-friendly en Order
"""

from datetime import UTC, datetime

from database import Base
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    """Usuario de la API.

    Attributes:
        id: Identificador unico.
        email: Email unico (usado para login).
        hashed_password: Password hasheado con bcrypt.
        name: Nombre del usuario.
        created_at: Timestamp de creacion (UTC).
        orders: Ordenes del usuario (relacion 1-N).
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r}, name={self.name!r})"


class Order(Base):
    """Orden de compra del usuario."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )

    @property
    def total(self) -> float:
        """Suma de subtotales de items."""
        return round(sum(item.subtotal for item in self.items), 2)

    def __repr__(self) -> str:
        return f"Order(id={self.id!r}, user_id={self.user_id!r}, status={self.status!r})"


class OrderItem(Base):
    """Item individual dentro de una orden."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product: Mapped[str] = mapped_column(String(100))
    quantity: Mapped[int] = mapped_column(default=1)
    unit_price: Mapped[float] = mapped_column(default=0.0)

    order: Mapped["Order"] = relationship(back_populates="items")

    @property
    def subtotal(self) -> float:
        """Subtotal del item (quantity * unit_price)."""
        return round(self.quantity * self.unit_price, 2)

    def __repr__(self) -> str:
        return (
            f"OrderItem(id={self.id!r}, product={self.product!r}, " f"quantity={self.quantity!r})"
        )

"""Modelos SQLAlchemy 2.0 para User, Order, OrderItem.

Demuestra:
- DeclarativeBase (estilo moderno)
- Mapped[...] y mapped_column()
- Relaciones 1-N con relationship() y back_populates
- ForeignKeys con ON DELETE CASCADE
- Timestamps automaticos
"""

from datetime import UTC, datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos."""


class User(Base):
    """Usuario del sistema.

    Attributes:
        id: Identificador unico.
        email: Email unico del usuario.
        name: Nombre del usuario.
        created_at: Timestamp de creacion (UTC).
        orders: Ordenes asociadas (relacion 1-N).
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r}, name={self.name!r})"


class Order(Base):
    """Orden de compra.

    Attributes:
        id: Identificador unico.
        user_id: FK al usuario dueno.
        status: Estado de la orden.
        created_at: Timestamp de creacion (UTC).
        user: Usuario dueno (relacion N-1).
        items: Items de la orden (relacion 1-N).
    """

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
    )

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )

    @property
    def total(self) -> float:
        """Suma de subtotales de los items."""
        return round(sum(item.subtotal for item in self.items), 2)

    def __repr__(self) -> str:
        return f"Order(id={self.id!r}, user_id={self.user_id!r}, status={self.status!r})"


class OrderItem(Base):
    """Item individual dentro de una orden.

    Attributes:
        id: Identificador unico.
        order_id: FK a la orden.
        product: Nombre del producto.
        quantity: Cantidad.
        unit_price: Precio unitario.
        order: Orden duena (relacion N-1).
    """

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


def create_all(engine: object) -> None:
    """Crea todas las tablas en el engine dado.

    Args:
        engine: Engine de SQLAlchemy.
    """
    Base.metadata.create_all(engine)  # type: ignore[arg-type]


# Helper de utilidad para tests
def utcnow() -> datetime:
    """Devuelve la fecha actual en UTC.

    Returns:
        datetime con timezone UTC.
    """
    return datetime.now(UTC)


__all__ = ["Base", "Order", "OrderItem", "User", "create_all", "func", "utcnow"]

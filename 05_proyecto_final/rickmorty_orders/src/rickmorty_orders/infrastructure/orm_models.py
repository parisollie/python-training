"""Modelos SQLAlchemy 2.0 para persistencia.

Mapean las entidades del dominio a tablas.

Nota: los modelos ORM son parte de infraestructura, no del dominio.
El dominio (Order, OrderItem) se mantiene puro.
"""

from datetime import UTC, datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rickmorty_orders.infrastructure.persistence import Base


class OrderModel(Base):
    """Modelo ORM para Order."""

    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    customer_email: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    items: Mapped[list["OrderItemModel"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"OrderModel(id={self.id!r}, customer_email={self.customer_email!r}, "
            f"status={self.status!r})"
        )


class OrderItemModel(Base):
    """Modelo ORM para OrderItem."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    character_id: Mapped[int] = mapped_column()
    character_name: Mapped[str] = mapped_column(String(100))
    quantity: Mapped[int] = mapped_column()
    unit_price_amount: Mapped[float] = mapped_column()
    unit_price_currency: Mapped[str] = mapped_column(String(3), default="USD")

    order: Mapped["OrderModel"] = relationship(back_populates="items")

    def __repr__(self) -> str:
        return (
            f"OrderItemModel(character_name={self.character_name!r}, "
            f"quantity={self.quantity!r})"
        )

"""Adaptadores SQLAlchemy de los puertos del dominio.

Traducen entre:
- Entidades del dominio (Order, OrderItem) -> Modelos ORM (OrderModel, ...)
- Y viceversa.

Cumplen los Protocols OrderRepository sin heredar de nada.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from rickmorty_orders.domain.order import Order, OrderItem, OrderStatus
from rickmorty_orders.domain.value_objects import (
    CharacterId,
    Email,
    Money,
    OrderId,
)
from rickmorty_orders.infrastructure.orm_models import (
    OrderItemModel,
    OrderModel,
)


def _order_to_model(order: Order) -> OrderModel:
    """Convierte una entidad Order a OrderModel (ORM)."""
    model = OrderModel(
        id=str(order.id),
        customer_email=str(order.customer_email),
        status=order.status.value,
        created_at=order.created_at,
    )
    for item in order.items:
        model.items.append(
            OrderItemModel(
                character_id=item.character_id.value,
                character_name=item.character_name,
                quantity=item.quantity,
                unit_price_amount=item.unit_price.amount,
                unit_price_currency=item.unit_price.currency,
            )
        )
    return model


def _model_to_order(model: OrderModel) -> Order:
    """Convierte un OrderModel (ORM) a entidad Order."""
    items = [
        OrderItem(
            character_id=CharacterId(item.character_id),
            character_name=item.character_name,
            quantity=item.quantity,
            unit_price=Money(
                amount=item.unit_price_amount,
                currency=item.unit_price_currency,
            ),
        )
        for item in model.items
    ]
    return Order(
        id=OrderId(model.id),
        customer_email=Email(model.customer_email),
        items=items,
        status=OrderStatus(model.status),
        created_at=model.created_at,
    )


class SQLOrderRepository:
    """Implementacion SQLAlchemy del puerto OrderRepository.

    Cada operacion abre una Session propia (unit of work por operacion).
    """

    def __init__(self, session_factory: object) -> None:
        """Inicializa el repositorio.

        Args:
            session_factory: callable que devuelve una Session.
                Normalmente es `sessionmaker(bind=engine)`.
        """
        self._session_factory = session_factory

    def save(self, order: Order) -> None:
        """Guarda o actualiza una orden."""
        session: Session = self._session_factory()  # type: ignore[operator]
        try:
            existing = session.get(OrderModel, str(order.id))
            if existing is not None:
                # Update: reemplazamos los datos
                existing.customer_email = str(order.customer_email)
                existing.status = order.status.value
                # Simplificacion: borrar items viejos y re-crear
                existing.items.clear()
                session.flush()
                for item in order.items:
                    existing.items.append(
                        OrderItemModel(
                            character_id=item.character_id.value,
                            character_name=item.character_name,
                            quantity=item.quantity,
                            unit_price_amount=item.unit_price.amount,
                            unit_price_currency=item.unit_price.currency,
                        )
                    )
            else:
                # Insert
                session.add(_order_to_model(order))
            session.commit()
        finally:
            session.close()

    def find_by_id(self, order_id: OrderId) -> Order | None:
        """Busca por id. Devuelve None si no existe."""
        session: Session = self._session_factory()  # type: ignore[operator]
        try:
            model = session.get(OrderModel, str(order_id))
            if model is None:
                return None
            return _model_to_order(model)
        finally:
            session.close()

    def find_by_customer(self, email: Email) -> list[Order]:
        """Lista las ordenes de un cliente."""
        session: Session = self._session_factory()  # type: ignore[operator]
        try:
            stmt = (
                select(OrderModel)
                .where(OrderModel.customer_email == str(email))
                .order_by(OrderModel.created_at)
            )
            models = session.scalars(stmt).all()
            return [_model_to_order(m) for m in models]
        finally:
            session.close()

    def list_all(self) -> list[Order]:
        """Lista todas las ordenes."""
        session: Session = self._session_factory()  # type: ignore[operator]
        try:
            stmt = select(OrderModel).order_by(OrderModel.created_at)
            models = session.scalars(stmt).all()
            return [_model_to_order(m) for m in models]
        finally:
            session.close()

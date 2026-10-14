"""Router de ordenes: CRUD protegido con JWT."""

from typing import Annotated

from database import get_db
from dependencies import CurrentUser
from fastapi import APIRouter, Depends, HTTPException, status
from models import Order, OrderItem
from schemas import OrderIn, OrderOut
from sqlalchemy.orm import Session, selectinload

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderIn,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> Order:
    """Crea una orden para el usuario autenticado.

    Args:
        order_in: Datos de la orden (items).
        current_user: Usuario autenticado.
        db: Sesion SQLAlchemy.

    Returns:
        Orden creada con items y total.
    """
    order = Order(user_id=current_user.id)
    for item_data in order_in.items:
        order.items.append(OrderItem(**item_data.model_dump()))

    db.add(order)
    db.commit()

    # Recargar con eager loading para evitar DetachedInstanceError
    loaded = db.query(Order).options(selectinload(Order.items)).filter(Order.id == order.id).first()
    if loaded is None:
        raise HTTPException(status_code=500, detail="Error al crear la orden")
    return loaded


@router.get("/", response_model=list[OrderOut])
def list_orders(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> list[Order]:
    """Lista las ordenes del usuario autenticado.

    Args:
        current_user: Usuario autenticado.
        db: Sesion SQLAlchemy.

    Returns:
        Lista de ordenes con items.
    """
    orders = (
        db.query(Order)
        .options(selectinload(Order.items))
        .filter(Order.user_id == current_user.id)
        .order_by(Order.id)
        .all()
    )
    return orders


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> Order:
    """Obtiene una orden del usuario autenticado.

    Args:
        order_id: ID de la orden.
        current_user: Usuario autenticado.
        db: Sesion SQLAlchemy.

    Returns:
        Orden con items.

    Raises:
        HTTPException 404: Si no existe o no pertenece al usuario.
    """
    order = (
        db.query(Order)
        .options(selectinload(Order.items))
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada",
        )
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Elimina una orden del usuario autenticado.

    Args:
        order_id: ID de la orden.
        current_user: Usuario autenticado.
        db: Sesion SQLAlchemy.

    Raises:
        HTTPException 404: Si no existe o no pertenece al usuario.
    """
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada",
        )
    db.delete(order)
    db.commit()

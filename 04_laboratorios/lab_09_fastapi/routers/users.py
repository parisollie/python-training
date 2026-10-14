"""Router de usuarios: crear usuario y ver el actual."""

from typing import Annotated

from database import get_db
from dependencies import CurrentUser
from fastapi import APIRouter, Depends, HTTPException, status
from models import User
from schemas import UserIn, UserOut
from security import hash_password
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserIn,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Crea un usuario nuevo.

    Args:
        user_in: Datos del usuario (email, password, name).
        db: Sesion SQLAlchemy.

    Returns:
        Usuario creado (sin password).

    Raises:
        HTTPException 400: Si el email ya existe.
    """
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya esta registrado",
        )

    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        name=user_in.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: CurrentUser) -> User:
    """Devuelve el usuario autenticado.

    Args:
        current_user: Usuario inyectado por get_current_user.

    Returns:
        Usuario actual.
    """
    return current_user

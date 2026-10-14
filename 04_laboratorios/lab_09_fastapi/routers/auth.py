"""Router de autenticacion: login con OAuth2 password flow."""

from typing import Annotated

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models import User
from schemas import Token
from security import create_access_token, verify_password
from sqlalchemy.orm import Session

router = APIRouter(tags=["auth"])


@router.post("/token", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """Login: valida credenciales y devuelve JWT.

    Args:
        form_data: Formulario OAuth2 (username + password).
        db: Sesion SQLAlchemy.

    Returns:
        Token con access_token y token_type.

    Raises:
        HTTPException 401: Si las credenciales son invalidas.
    """
    # En OAuth2PasswordRequestForm, "username" es el email
    user = db.query(User).filter(User.email == form_data.username).first()

    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)

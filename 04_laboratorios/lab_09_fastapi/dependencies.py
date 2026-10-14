"""Dependencias de FastAPI: autenticacion y DB.

get_db viene de database.py (re-exportado aqui por conveniencia).
get_current_user extrae y valida el JWT del header Authorization.
"""

from typing import Annotated

from database import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models import User
from security import decode_access_token
from sqlalchemy.orm import Session

# ============================================
# OAuth2 scheme (para el boton "Authorize" en /docs)
# ============================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ============================================
# Usuario actual (autenticacion)
# ============================================


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Obtiene el usuario actual a partir del JWT.

    Args:
        token: JWT extraido del header Authorization: Bearer <token>.
        db: Sesion SQLAlchemy.

    Returns:
        Usuario autenticado.

    Raises:
        HTTPException 401: Si el token es invalido o el usuario no existe.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales invalidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
    except ValueError as e:
        raise credentials_exception from e

    email = payload.get("sub")
    if email is None or not isinstance(email, str):
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


# Alias tipado para usar en routers (mas limpio)
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]

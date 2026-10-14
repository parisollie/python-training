"""Seguridad: hash de passwords (bcrypt directo) y JWT.

Usamos bcrypt directamente porque passlib 1.7.4 no es compatible
con bcrypt 4.1+ (bug conocido, sin fix upstream).
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

# ============================================
# Configuracion
# ============================================

SECRET_KEY = "cambiar-en-produccion-usar-os-environ"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ============================================
# Passwords (bcrypt directo)
# ============================================


def hash_password(password: str) -> str:
    """Hashea una password con bcrypt.

    Args:
        password: Password en texto plano.

    Returns:
        Hash bcrypt como string.
    """
    password_bytes = password.encode("utf-8")
    # bcrypt tiene limite de 72 bytes
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una password coincide con su hash.

    Args:
        plain_password: Password en texto plano.
        hashed_password: Hash bcrypt almacenado.

    Returns:
        True si coinciden, False en caso contrario.
    """
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    try:
        return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))
    except ValueError:
        return False


# ============================================
# JWT (sin cambios)
# ============================================


def create_access_token(data: dict[str, Any], expires_minutes: int | None = None) -> str:
    """Crea un JWT firmado."""
    if expires_minutes is None:
        expires_minutes = ACCESS_TOKEN_EXPIRE_MINUTES

    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decodifica y valida un JWT."""
    try:
        payload: object = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise ValueError(f"Token invalido: {e}") from e

    if not isinstance(payload, dict):
        raise ValueError("Payload del token invalido")

    return payload

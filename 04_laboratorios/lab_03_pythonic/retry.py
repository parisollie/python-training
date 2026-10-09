"""Decorador de reintentos con backoff exponencial.

Uso:
    from retry import retry

    @retry(max_attempts=3, base_delay=0.1)
    def funcion_inestable():
        ...
"""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def retry(
    max_attempts: int = 3,
    base_delay: float = 0.1,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """Decorador que reintenta una funcion si lanza excepcion.

    Args:
        max_attempts: Numero maximo de intentos (incluyendo el primero).
        base_delay: Segundos de espera inicial. Se multiplica por 2 en cada intento.
        exceptions: Tupla de excepciones a capturar. Por defecto captura todas.

    Returns:
        Decorador que envuelve la funcion original.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts debe ser >= 1")
    if base_delay < 0:
        raise ValueError("base_delay debe ser >= 0")

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        delay = base_delay * (2 ** (attempt - 1))
                        print(
                            f"⚠️  Intento {attempt}/{max_attempts} falló: {e!r}. "
                            f"Reintentando en {delay:.2f}s..."
                        )
                        time.sleep(delay)
                    else:
                        print(f"❌ Se agotaron los {max_attempts} intentos.")

            # Si llegamos aquí, se agotaron los intentos
            assert last_exception is not None
            raise last_exception

        return wrapper  # type: ignore[return-value]

    return decorator

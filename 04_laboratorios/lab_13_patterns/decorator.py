"""Patron Decorator: agregar comportamiento sin modificar la clase.

Demuestra 2 enfoques:
1. Decorator idiomatico con functools.wraps (para funciones)
2. Decorator clasico con clase (para objetos)

Casos:
- cache: memoiza resultados
- retry: reintenta si falla
- log_calls: registra las llamadas
"""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any

# ============================================
# Decorator idiomatico: cache
# ============================================


def cache[F: Callable[..., Any]](func: F) -> F:
    """Decorator simple de cache en memoria.

    Almacena los resultados por (args, kwargs).
    """
    memo: dict[tuple[Any, ...], Any] = {}

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = (args, tuple(sorted(kwargs.items())))
        if key not in memo:
            memo[key] = func(*args, **kwargs)
        return memo[key]

    wrapper.cache_info = lambda: {"size": len(memo)}  # type: ignore[attr-defined]
    wrapper.cache_clear = memo.clear  # type: ignore[attr-defined]
    return wrapper  # type: ignore[return-value]


# ============================================
# Decorator idiomatico: retry
# ============================================


def retry[F: Callable[..., Any]](
    max_attempts: int = 3,
    delay: float = 0.01,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """Decorator que reintenta una funcion si falla.

    Args:
        max_attempts: Numero maximo de intentos.
        delay: Segundos entre intentos.
        exceptions: Excepciones que activan el reintento.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last = e
                    if attempt < max_attempts:
                        time.sleep(delay)
            assert last is not None
            raise last

        return wrapper  # type: ignore[return-value]

    return decorator


# ============================================
# Decorator idiomatico: log_calls
# ============================================


def log_calls[F: Callable[..., Any]](func: F) -> F:
    """Decorator que registra las llamadas a la funcion."""
    calls: list[dict[str, Any]] = []

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        calls.append({"args": args, "kwargs": kwargs})
        return func(*args, **kwargs)

    wrapper.calls = calls  # type: ignore[attr-defined]
    return wrapper  # type: ignore[return-value]


# ============================================
# Decorator clasico (clase envolviendo clase)
# ============================================


class Notifier:
    """Notificador base."""

    def send(self, message: str) -> str:
        """Envia el mensaje."""
        return f"Enviado: {message}"


class LoggedNotifier:
    """Decorator clasico que agrega logging a un Notifier.

    Envuelve cualquier objeto con un metodo send(str) -> str.
    """

    def __init__(self, wrapped: Notifier) -> None:
        self._wrapped = wrapped
        self.log: list[str] = []

    def send(self, message: str) -> str:
        """Registra la llamada y delega al notifier envuelto."""
        self.log.append(message)
        return self._wrapped.send(message)


class RetriedNotifier:
    """Decorator clasico que reintenta send si falla."""

    def __init__(self, wrapped: Notifier, max_attempts: int = 3) -> None:
        self._wrapped = wrapped
        self.max_attempts = max_attempts
        self.attempts = 0

    def send(self, message: str) -> str:
        """Intenta enviar hasta max_attempts veces."""
        last: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                self.attempts = attempt
                return self._wrapped.send(message)
            except Exception as e:
                last = e
        assert last is not None
        raise last

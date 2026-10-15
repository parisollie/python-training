"""Tests de los decoradores."""

import pytest
from decorator import (
    LoggedNotifier,
    Notifier,
    RetriedNotifier,
    cache,
    log_calls,
    retry,
)

# ============================================
# cache
# ============================================


def test_cache_evita_recalculo() -> None:
    """El decorador cache solo ejecuta 1 vez por entrada."""
    llamadas = {"n": 0}

    @cache
    def doble(x: int) -> int:
        llamadas["n"] += 1
        return x * 2

    assert doble(5) == 10
    assert doble(5) == 10
    assert doble(5) == 10
    assert llamadas["n"] == 1


def test_cache_distintas_entradas() -> None:
    """Distintas entradas generan distintas ejecuciones."""
    llamadas = {"n": 0}

    @cache
    def doble(x: int) -> int:
        llamadas["n"] += 1
        return x * 2

    doble(1)
    doble(2)
    doble(3)
    assert llamadas["n"] == 3


def test_cache_con_kwargs() -> None:
    """El cache distingue por kwargs."""
    llamadas = {"n": 0}

    @cache
    def funcion(a: int, b: int = 0) -> int:
        llamadas["n"] += 1
        return a + b

    funcion(1, b=2)
    funcion(1, b=2)  # cacheada
    funcion(1, b=3)  # nueva
    assert llamadas["n"] == 2


def test_cache_info() -> None:
    """cache_info devuelve el tamano del cache."""

    @cache
    def identidad(x: int) -> int:
        return x

    identidad(1)
    identidad(2)
    info = identidad.cache_info()  # type: ignore[attr-defined]
    assert info["size"] == 2


# ============================================
# retry
# ============================================


def test_retry_exito_inmediato() -> None:
    """Si la funcion no falla, no hay reintentos."""
    intentos = {"n": 0}

    @retry(max_attempts=3, delay=0.001)
    def ok() -> str:
        intentos["n"] += 1
        return "ok"

    assert ok() == "ok"
    assert intentos["n"] == 1


def test_retry_exito_tras_fallos() -> None:
    """Reintenta hasta exito."""
    intentos = {"n": 0}

    @retry(max_attempts=5, delay=0.001)
    def inestable() -> str:
        intentos["n"] += 1
        if intentos["n"] < 3:
            raise ValueError("aun no")
        return "ok"

    assert inestable() == "ok"
    assert intentos["n"] == 3


def test_retry_falla_siempre() -> None:
    """Si nunca tiene exito, propaga la ultima excepcion."""
    intentos = {"n": 0}

    @retry(max_attempts=2, delay=0.001)
    def siempre_falla() -> None:
        intentos["n"] += 1
        raise RuntimeError(f"intento {intentos['n']}")

    with pytest.raises(RuntimeError, match="intento 2"):
        siempre_falla()
    assert intentos["n"] == 2


def test_retry_filtra_excepciones() -> None:
    """Solo reintenta las excepciones declaradas."""
    intentos = {"n": 0}

    @retry(max_attempts=3, delay=0.001, exceptions=(ValueError,))
    def solo_value_error() -> None:
        intentos["n"] += 1
        raise TypeError("no reintentar")

    with pytest.raises(TypeError):
        solo_value_error()
    assert intentos["n"] == 1


# ============================================
# log_calls
# ============================================


def test_log_calls() -> None:
    """Registra cada llamada."""

    @log_calls
    def suma(a: int, b: int) -> int:
        return a + b

    suma(1, 2)
    suma(3, 4)
    assert len(suma.calls) == 2  # type: ignore[attr-defined]
    assert suma.calls[0]["args"] == (1, 2)  # type: ignore[attr-defined]


# ============================================
# Decorator clasico
# ============================================


def test_logged_notifier() -> None:
    """LoggedNotifier registra y delega."""
    wrapped = Notifier()
    notifier = LoggedNotifier(wrapped)

    result = notifier.send("hola")
    assert result == "Enviado: hola"
    assert notifier.log == ["hola"]


def test_retried_notifier_exito() -> None:
    """RetriedNotifier funciona si no hay errores."""
    notifier = RetriedNotifier(Notifier())
    assert notifier.send("hola") == "Enviado: hola"
    assert notifier.attempts == 1


def test_retried_notifier_con_fallo() -> None:
    """RetriedNotifier reintenta si falla."""

    class FailingOnce(Notifier):
        def __init__(self) -> None:
            self.fails = 0

        def send(self, message: str) -> str:
            self.fails += 1
            if self.fails < 3:
                raise RuntimeError("fail")
            return f"OK: {message}"

    notifier = RetriedNotifier(FailingOnce(), max_attempts=5)
    assert notifier.send("hola") == "OK: hola"
    assert notifier.attempts == 3

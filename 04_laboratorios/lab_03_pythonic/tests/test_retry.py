"""Tests para el decorador retry."""

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from retry import retry  # noqa: E402


def test_retry_exito_inmediato() -> None:
    """Si la funcion no falla, no hay reintentos."""
    llamadas = []

    @retry(max_attempts=3, base_delay=0.01)
    def ok() -> str:
        llamadas.append(1)
        return "ok"

    assert ok() == "ok"
    assert len(llamadas) == 1


def test_retry_exito_tras_fallos() -> None:
    """Reintenta hasta exito."""
    intentos = {"n": 0}

    @retry(max_attempts=5, base_delay=0.01)
    def inestable() -> str:
        intentos["n"] += 1
        if intentos["n"] < 3:
            raise ValueError("aun no")
        return "exito"

    assert inestable() == "exito"
    assert intentos["n"] == 3


def test_retry_falla_siempre() -> None:
    """Si nunca tiene exito, propaga la ultima excepcion."""
    intentos = {"n": 0}

    @retry(max_attempts=2, base_delay=0.01)
    def siempre_falla() -> None:
        intentos["n"] += 1
        raise RuntimeError(f"intento {intentos['n']}")

    with pytest.raises(RuntimeError, match="intento 2"):
        siempre_falla()

    assert intentos["n"] == 2


def test_retry_solo_captura_excepciones_indicadas() -> None:
    """Solo reintenta las excepciones declaradas."""
    intentos = {"n": 0}

    @retry(max_attempts=3, base_delay=0.01, exceptions=(ValueError,))
    def falla_con_type_error() -> None:
        intentos["n"] += 1
        raise TypeError("no deberia reintentarse")

    with pytest.raises(TypeError):
        falla_con_type_error()

    assert intentos["n"] == 1


def test_retry_preserva_metadatos() -> None:
    """El decorador debe preservar __name__ y __doc__."""

    @retry(max_attempts=2, base_delay=0.01)
    def mi_funcion() -> None:
        """Docstring de prueba."""

    assert mi_funcion.__name__ == "mi_funcion"
    assert mi_funcion.__doc__ == "Docstring de prueba."


def test_retry_pasa_argumentos() -> None:
    """Los argumentos y kwargs se pasan correctamente."""

    @retry(max_attempts=2, base_delay=0.01)
    def suma(a: int, b: int, c: int = 0) -> int:
        return a + b + c

    assert suma(1, 2) == 3
    assert suma(1, 2, c=10) == 13


def test_retry_valida_max_attempts() -> None:
    """max_attempts debe ser >= 1."""
    with pytest.raises(ValueError, match="max_attempts"):

        @retry(max_attempts=0)
        def f() -> None:
            pass


def test_retry_valida_base_delay() -> None:
    """base_delay debe ser >= 0."""
    with pytest.raises(ValueError, match="base_delay"):

        @retry(base_delay=-1)
        def f() -> None:
            pass


def test_retry_backoff_creciente() -> None:
    """Los delays crecen exponencialmente (0.01, 0.02, 0.04...)."""
    tiempos = []

    @retry(max_attempts=4, base_delay=0.05)
    def siempre_falla() -> None:
        tiempos.append(time.perf_counter())
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        siempre_falla()

    # 4 intentos = 3 esperas
    assert len(tiempos) == 4
    # Verificar que el delay crece (con margen de tolerancia)
    d1 = tiempos[1] - tiempos[0]
    d2 = tiempos[2] - tiempos[1]
    d3 = tiempos[3] - tiempos[2]
    assert d2 > d1
    assert d3 > d2

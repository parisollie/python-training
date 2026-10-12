"""Tests para el context manager timer."""

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from timer import timer  # noqa: E402


def test_timer_mide_tiempo() -> None:
    """Elapsed debe ser > 0 despues del bloque."""
    with timer(verbose=False) as t:
        time.sleep(0.05)
    assert t.elapsed >= 0.05


def test_timer_verbose_imprime(capsys: pytest.CaptureFixture[str]) -> None:
    """Con verbose=True imprime la duracion."""
    with timer(verbose=True):
        pass
    captured = capsys.readouterr()
    assert "Duración" in captured.out


def test_timer_silencioso(capsys: pytest.CaptureFixture[str]) -> None:
    """Con verbose=False NO imprime nada."""
    with timer(verbose=False):
        pass
    captured = capsys.readouterr()
    assert captured.out == ""


def test_timer_elapsed_inicial_es_cero() -> None:
    """Elapsed es 0.0 hasta que termina el bloque."""
    with timer(verbose=False) as t:
        assert t.elapsed == 0.0


def test_timer_mide_incluso_con_excepcion() -> None:
    """El finally asegura que elapsed se actualiza aunque haya excepcion."""
    with pytest.raises(ValueError), timer(verbose=False) as t:
        raise ValueError("boom")
    assert t.elapsed >= 0.0


def test_timer_mide_tiempo_progresivo() -> None:
    """Bloques mas largos reportan mayor elapsed."""
    with timer(verbose=False) as t1:
        time.sleep(0.02)

    with timer(verbose=False) as t2:
        time.sleep(0.05)

    assert t2.elapsed > t1.elapsed


def test_timer_anidados() -> None:
    """Se pueden anidar dos timers y cada uno mide lo suyo."""
    with timer(verbose=False) as outer:
        with timer(verbose=False) as inner:
            time.sleep(0.02)
        time.sleep(0.02)

    assert outer.elapsed > inner.elapsed

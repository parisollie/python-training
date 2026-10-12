"""Tests para el generador batch."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from batching import batch  # noqa: E402


def test_batch_tamano_exacto() -> None:
    """6 elementos en lotes de 3 -> 2 lotes exactos."""
    result = list(batch([1, 2, 3, 4, 5, 6], size=3))
    assert result == [[1, 2, 3], [4, 5, 6]]


def test_batch_ultimo_lote_parcial() -> None:
    """7 elementos en lotes de 3 -> 2 completos + 1 parcial."""
    result = list(batch([1, 2, 3, 4, 5, 6, 7], size=3))
    assert result == [[1, 2, 3], [4, 5, 6], [7]]


def test_batch_vacio() -> None:
    """Iterable vacio -> sin lotes."""
    result = list(batch([], size=3))
    assert result == []


def test_batch_size_mayor_que_elementos() -> None:
    """size=10 con 2 elementos -> un solo lote con 2."""
    result = list(batch([1, 2], size=10))
    assert result == [[1, 2]]


def test_batch_size_uno() -> None:
    """size=1 -> un lote por elemento."""
    result = list(batch([1, 2, 3], size=1))
    assert result == [[1], [2], [3]]


def test_batch_con_generador() -> None:
    """Funciona con cualquier iterable, no solo listas."""

    def contar(n: int):
        yield from range(1, n + 1)

    result = list(batch(contar(7), size=3))
    assert result == [[1, 2, 3], [4, 5, 6], [7]]


def test_batch_con_string() -> None:
    """Funciona con strings (iterables de caracteres)."""
    result = list(batch("abcdefg", size=3))
    assert result == [["a", "b", "c"], ["d", "e", "f"], ["g"]]


def test_batch_es_lazy() -> None:
    """El generador no consume el iterable hasta que se itera."""
    consumidos = []

    def tracker():
        for i in range(1, 6):
            consumidos.append(i)
            yield i

    gen = batch(tracker(), size=2)
    # Aun no se ha consumido nada
    assert consumidos == []

    # Consumir solo el primer lote
    primer_lote = next(gen)
    assert primer_lote == [1, 2]
    assert consumidos == [1, 2]

    # Consumir el resto
    resto = list(gen)
    assert resto == [[3, 4], [5]]
    assert consumidos == [1, 2, 3, 4, 5]


def test_batch_size_invalido() -> None:
    """size < 1 lanza ValueError."""
    with pytest.raises(ValueError, match="size debe ser >= 1"):
        list(batch([1, 2, 3], size=0))


def test_batch_size_negativo() -> None:
    """size negativo tambien lanza ValueError."""
    with pytest.raises(ValueError, match="size debe ser >= 1"):
        list(batch([1, 2, 3], size=-5))


def test_batch_suma_total() -> None:
    """La suma de todos los lotes es igual al total de elementos."""
    datos = list(range(100))
    lotes = list(batch(datos, size=7))
    total = sum(len(lote) for lote in lotes)
    assert total == 100
    # 100 elementos / 7 = 14 lotes completos + 1 parcial (2 elementos)
    assert len(lotes) == 15
    assert len(lotes[-1]) == 2

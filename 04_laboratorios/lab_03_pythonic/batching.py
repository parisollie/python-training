"""Generador por lotes (batching).

Divide cualquier iterable en lotes de tamaño fijo.

Uso:
    from batching import batch

    for lote in batch([1, 2, 3, 4, 5], size=2):
        print(lote)
    # [1, 2]
    # [3, 4]
    # [5]
"""

from collections.abc import Iterable, Iterator


def batch[T](iterable: Iterable[T], size: int) -> Iterator[list[T]]:
    """Divide un iterable en lotes de tamaño fijo.

    Es un generador: no carga todo en memoria, va produciendo cada lote
    a medida que se consume.

    Args:
        iterable: Cualquier iterable (lista, tupla, generador, archivo, etc.).
        size: Tamaño de cada lote. Debe ser >= 1.

    Yields:
        Listas de hasta `size` elementos. El último lote puede ser más pequeño.

    Raises:
        ValueError: Si `size` es menor que 1.

    Examples:
        >>> list(batch([1, 2, 3, 4, 5], size=2))
        [[1, 2], [3, 4], [5]]
        >>> list(batch([], size=3))
        []
    """
    if size < 1:
        raise ValueError("size debe ser >= 1")

    lote: list[T] = []
    for item in iterable:
        lote.append(item)
        if len(lote) == size:
            yield lote
            lote = []

    # Último lote parcial (si quedó algo pendiente)
    if lote:
        yield lote

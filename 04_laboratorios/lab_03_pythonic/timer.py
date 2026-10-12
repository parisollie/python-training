"""Context manager de temporización.

Mide cuánto tarda un bloque de código y lo imprime al salir.

Uso:
    from timer import timer

    with timer() as t:
        sum(range(1_000_000))

    print(f"Elapsed: {t.elapsed:.4f}s")
"""

import time
from collections.abc import Iterator
from contextlib import contextmanager


class TimerResult:
    """Resultado de la medición de tiempo.

    Attributes:
        elapsed: Segundos transcurridos. 0.0 hasta que el bloque termina.
    """

    def __init__(self) -> None:
        self.elapsed: float = 0.0


@contextmanager
def timer(verbose: bool = True) -> Iterator[TimerResult]:
    """Context manager que mide el tiempo de ejecución de un bloque.

    Args:
        verbose: Si es True, imprime la duración al salir del bloque.

    Yields:
        TimerResult con el atributo `elapsed` (segundos).

    Examples:
        >>> with timer(verbose=False) as t:
        ...     sum(range(100))
        >>> t.elapsed > 0
        True
    """
    result = TimerResult()
    start = time.perf_counter()
    try:
        yield result
    finally:
        result.elapsed = time.perf_counter() - start
        if verbose:
            print(f"⏱️  Duración: {result.elapsed:.4f}s")

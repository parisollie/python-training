"""Tests para los fetchers concurrentes (sin red real con MockTransport)."""

import sys
from pathlib import Path
from typing import Any

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from fetchers import (  # noqa: E402
    compute_heavy,
    compute_parallel,
    compute_sync,
    fetch_sync,
    fetch_threaded,
    measure,
)

# ============================================
# Helper: handler de MockTransport
# ============================================


def make_handler(char_id: int) -> dict[str, Any]:
    """Devuelve el JSON simulado para un personaje."""
    return {"id": char_id, "name": f"Personaje {char_id}"}


def mock_handler(request: httpx.Request) -> httpx.Response:
    """Handler que extrae el ID de la URL y devuelve JSON."""
    path = request.url.path
    # path = /api/character/N
    char_id = int(path.rstrip("/").split("/")[-1])
    return httpx.Response(200, json=make_handler(char_id))


# ============================================
# fetch_sync
# ============================================


def test_fetch_sync() -> None:
    """fetch_sync devuelve los personajes en orden."""
    transport = httpx.MockTransport(mock_handler)
    with httpx.Client(transport=transport) as client:
        results = fetch_sync([1, 2, 3], client=client)
    assert len(results) == 3
    assert results[0]["name"] == "Personaje 1"
    assert results[2]["name"] == "Personaje 3"


def test_fetch_sync_lista_vacia() -> None:
    """fetch_sync con lista vacia devuelve lista vacia."""
    transport = httpx.MockTransport(mock_handler)
    with httpx.Client(transport=transport) as client:
        results = fetch_sync([], client=client)
    assert results == []


def test_fetch_sync_error_http() -> None:
    """fetch_sync propaga errores HTTP."""

    def error_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    transport = httpx.MockTransport(error_handler)
    with httpx.Client(transport=transport) as client, pytest.raises(httpx.HTTPStatusError):
        fetch_sync([1], client=client)


# ============================================
# fetch_threaded
# ============================================


def test_fetch_threaded() -> None:
    """fetch_threaded devuelve los personajes en orden."""
    transport = httpx.MockTransport(mock_handler)
    with httpx.Client(transport=transport) as client:
        results = fetch_threaded([1, 2, 3, 4, 5], max_workers=3, client=client)
    assert len(results) == 5
    assert [r["id"] for r in results] == [1, 2, 3, 4, 5]


def test_fetch_threaded_lista_vacia() -> None:
    """fetch_threaded con lista vacia devuelve lista vacia."""
    transport = httpx.MockTransport(mock_handler)
    with httpx.Client(transport=transport) as client:
        results = fetch_threaded([], max_workers=3, client=client)
    assert results == []


def test_fetch_threaded_con_error() -> None:
    """fetch_threaded propaga errores de cualquier hilo."""

    def error_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    transport = httpx.MockTransport(error_handler)
    with httpx.Client(transport=transport) as client, pytest.raises(httpx.HTTPStatusError):
        fetch_threaded([1, 2], max_workers=2, client=client)


# ============================================
# fetch_async
# ============================================


async def test_fetch_async() -> None:
    """fetch_async devuelve los personajes en orden."""
    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        from fetchers import fetch_async

        results = await fetch_async([1, 2, 3, 4, 5], max_concurrent=3, client=client)
    assert len(results) == 5
    assert [r["id"] for r in results] == [1, 2, 3, 4, 5]


async def test_fetch_async_lista_vacia() -> None:
    """fetch_async con lista vacia devuelve lista vacia."""
    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        from fetchers import fetch_async

        results = await fetch_async([], client=client)
    assert results == []


async def test_fetch_async_semaforo_limita() -> None:
    """El semaforo limita la concurrencia."""
    concurrentes = {"actual": 0, "max": 0}

    async def slow_handler(request: httpx.Request) -> httpx.Response:
        concurrentes["actual"] += 1
        concurrentes["max"] = max(concurrentes["max"], concurrentes["actual"])
        import asyncio

        await asyncio.sleep(0.02)
        concurrentes["actual"] -= 1
        return httpx.Response(200, json={"id": 1, "name": "X"})

    # Nota: MockTransport async no es estandar, usamos AsyncBaseTransport custom
    class AsyncMockTransport(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            return await slow_handler(request)

    async with httpx.AsyncClient(transport=AsyncMockTransport()) as client:
        from fetchers import fetch_async

        await fetch_async([1, 2, 3, 4, 5, 6, 7, 8], max_concurrent=2, client=client)

    # Con semaforo de 2, el maximo de concurrentes debe ser <= 2
    assert concurrentes["max"] <= 2


# ============================================
# CPU-bound
# ============================================


def test_compute_heavy() -> None:
    """compute_heavy devuelve la suma correcta."""
    assert compute_heavy(5) == 0 + 1 + 4 + 9 + 16  # 30
    assert compute_heavy(0) == 0
    assert compute_heavy(1) == 0


def test_compute_sync() -> None:
    """compute_sync procesa la lista."""
    results = compute_sync([100, 200, 300])
    assert len(results) == 3
    assert results[0] == compute_heavy(100)


def test_compute_parallel() -> None:
    """compute_parallel da el mismo resultado que sync."""
    values = [100, 200, 300]
    assert compute_parallel(values) == compute_sync(values)


def test_compute_parallel_lista_vacia() -> None:
    """compute_parallel con lista vacia devuelve lista vacia."""
    assert compute_parallel([]) == []


# ============================================
# measure
# ============================================


def test_measure() -> None:
    """measure devuelve resultado y duracion."""

    def suma(a: int, b: int) -> int:
        return a + b

    result, duracion = measure(suma, 2, 3)
    assert result == 5
    assert duracion >= 0.0


def test_measure_duracion_real() -> None:
    """measure captura una duracion real."""
    import time

    def dormir() -> None:
        time.sleep(0.05)

    _, duracion = measure(dormir)
    assert duracion >= 0.05


# ============================================
# Integracion: async vs sync dan lo mismo
# ============================================


def test_async_y_sync_dan_lo_mismo() -> None:
    """Los fetchers producen resultados identicos (con MockTransport)."""
    transport = httpx.MockTransport(mock_handler)
    ids = [1, 2, 3, 4, 5]

    with httpx.Client(transport=transport) as client:
        sync_result = fetch_sync(ids, client=client)
        threaded_result = fetch_threaded(ids, max_workers=3, client=client)

    # Async con su propio transport
    async def run() -> list[dict[str, Any]]:
        async_transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=async_transport) as aclient:
            from fetchers import fetch_async

            return await fetch_async(ids, client=aclient)

    import asyncio

    async_result = asyncio.run(run())

    assert sync_result == threaded_result == async_result

"""Fetchers concurrentes contra la API de Rick and Morty.

Demuestra 4 modelos de concurrencia:
1. Sincrono (baseline): uno por uno
2. Threaded: ThreadPoolExecutor
3. Async: httpx.AsyncClient + asyncio.Semaphore
4. CPU-bound: ProcessPoolExecutor

Para cada uno se puede medir el tiempo con time.perf_counter().
"""

import asyncio
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any

import httpx

BASE_URL = "https://rickandmortyapi.com/api"


# ============================================
# 1. Sincrono (baseline)
# ============================================


def fetch_sync(ids: list[int], client: httpx.Client | None = None) -> list[dict[str, Any]]:
    """Fetch secuencial: uno por uno.

    Args:
        ids: Lista de IDs de personajes.
        client: Cliente httpx opcional (para tests).

    Returns:
        Lista de personajes en el mismo orden.
    """
    close = client is None
    if client is None:
        client = httpx.Client(timeout=10.0)
    try:
        results: list[dict[str, Any]] = []
        for char_id in ids:
            response = client.get(f"{BASE_URL}/character/{char_id}")
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError("Respuesta inesperada")
            results.append(data)
        return results
    finally:
        if close:
            client.close()


# ============================================
# 2. Threaded (I/O-bound con threads)
# ============================================


def fetch_threaded(
    ids: list[int],
    max_workers: int = 10,
    client: httpx.Client | None = None,
) -> list[dict[str, Any]]:
    """Fetch concurrente con ThreadPoolExecutor.

    Args:
        ids: Lista de IDs.
        max_workers: Numero de hilos.
        client: Cliente httpx opcional (para tests).

    Returns:
        Lista de personajes (en el orden original si se usa map).
    """
    close = client is None
    if client is None:
        client = httpx.Client(timeout=10.0)

    def fetch_one(char_id: int) -> dict[str, Any]:
        response = client.get(f"{BASE_URL}/character/{char_id}")
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Respuesta inesperada")
        return data

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            return list(executor.map(fetch_one, ids))
    finally:
        if close:
            client.close()


# ============================================
# 3. Async (I/O-bound con asyncio)
# ============================================


async def fetch_async(
    ids: list[int],
    max_concurrent: int = 10,
    client: httpx.AsyncClient | None = None,
) -> list[dict[str, Any]]:
    """Fetch concurrente con httpx.AsyncClient + semaforo.

    Args:
        ids: Lista de IDs.
        max_concurrent: Numero maximo de requests concurrentes.
        client: Cliente httpx.AsyncClient opcional (para tests).

    Returns:
        Lista de personajes (en el orden original).
    """
    sem = asyncio.Semaphore(max_concurrent)

    close = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=10.0)

    async def fetch_one(char_id: int) -> dict[str, Any]:
        async with sem:
            response = await client.get(f"{BASE_URL}/character/{char_id}")
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError("Respuesta inesperada")
            return data

    try:
        return list(await asyncio.gather(*[fetch_one(i) for i in ids]))
    finally:
        if close:
            await client.aclose()


def run_fetch_async(ids: list[int], max_concurrent: int = 10) -> list[dict[str, Any]]:
    """Wrapper sincrono de fetch_async (para facilitar su uso)."""
    return asyncio.run(fetch_async(ids, max_concurrent=max_concurrent))


# ============================================
# 4. CPU-bound (ProcessPoolExecutor)
# ============================================


def compute_heavy(n: int) -> int:
    """Calculo CPU-bound: suma de cuadrados hasta n.

    Args:
        n: Limite superior.

    Returns:
        Suma de i*i para i en [0, n).
    """
    total = 0
    for i in range(n):
        total += i * i
    return total


def compute_sync(values: list[int]) -> list[int]:
    """Version secuencial del calculo CPU-bound."""
    return [compute_heavy(v) for v in values]


def compute_parallel(values: list[int], max_workers: int = 4) -> list[int]:
    """Version paralela con ProcessPoolExecutor.

    Ideal para CPU-bound (evita el GIL).
    """
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(compute_heavy, values))


# ============================================
# Medicion
# ============================================


def measure(func: Any, *args: Any, **kwargs: Any) -> tuple[Any, float]:
    """Mide el tiempo de ejecucion de una funcion.

    Args:
        func: Funcion a ejecutar.
        *args: Argumentos posicionales.
        **kwargs: Argumentos nombrados.

    Returns:
        Tupla (resultado, duracion_en_segundos).
    """
    inicio = time.perf_counter()
    result = func(*args, **kwargs)
    duracion = time.perf_counter() - inicio
    return result, duracion

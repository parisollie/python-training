# Laboratorio 11 — Concurrencia y rendimiento

Comparativa práctica de 4 modelos de concurrencia en Python contra la API de Rick and Morty:

1. Síncrono (baseline)
2. Threaded (ThreadPoolExecutor)
3. Async (httpx.AsyncClient + asyncio.Semaphore)
4. CPU-bound (ProcessPoolExecutor)

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1
- httpx 0.28.1, pytest-asyncio 1.4.0

## Estructura

lab_11_concurrencia/
├── README.md              ← este archivo
├── fetchers.py            ← 4 fetchers + compute + measure
└── tests/
    └── test_fetchers.py   ← 16 tests con MockTransport

## Modelos de concurrencia

### 1. Síncrono (baseline)

Uno por uno. Simple pero lento con muchas I/O.

    from fetchers import fetch_sync
    results = fetch_sync([1, 2, 3, 4, 5])

### 2. Threaded

`ThreadPoolExecutor` con N workers. Ideal para I/O-bound (la red libera el GIL durante la espera).

    from fetchers import fetch_threaded
    results = fetch_threaded([1, 2, 3, 4, 5], max_workers=10)

### 3. Async

`httpx.AsyncClient` + `asyncio.Semaphore` para limitar concurrencia. Más escalable que threads con miles de conexiones.

    from fetchers import fetch_async
    import asyncio
    results = asyncio.run(fetch_async([1, 2, 3, 4, 5], max_concurrent=10))

    # O con wrapper sincrono:
    from fetchers import run_fetch_async
    results = run_fetch_async([1, 2, 3, 4, 5])

### 4. CPU-bound

`ProcessPoolExecutor` para cálculos pesados. Evita el GIL usando procesos separados.

    from fetchers import compute_parallel
    results = compute_parallel([10_000, 20_000, 30_000], max_workers=4)

## Comparativa de rendimiento

Ejecuta la comparativa contra la API real (requiere internet):

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_11_concurrencia')
    from fetchers import fetch_sync, fetch_threaded, run_fetch_async, measure

    ids = list(range(1, 11))

    _, t_sync = measure(fetch_sync, ids)
    print(f'Sync:      {t_sync:.2f}s')

    _, t_threads = measure(fetch_threaded, ids, max_workers=10)
    print(f'Threaded:  {t_threads:.2f}s  (speedup {t_sync/t_threads:.1f}x)')

    _, t_async = measure(run_fetch_async, ids, max_concurrent=10)
    print(f'Async:     {t_async:.2f}s  (speedup {t_sync/t_async:.1f}x)')
    "

Salida esperada (tiempos aproximados, varían según red):

    Sync:      1.06s
    Threaded:  0.24s  (speedup 4.5x)
    Async:     0.31s  (speedup 3.4x)

## Cómo ejecutar los tests

### Todos los tests

    poetry run pytest 04_laboratorios/lab_11_concurrencia/tests/ -v

Salida esperada:

    16 passed in 0.34s

### Con cobertura

    poetry run pytest 04_laboratorios/lab_11_concurrencia/tests/ --cov=04_laboratorios/lab_11_concurrencia --cov-report=term-missing

### Archivos de tests

| Archivo | Qué cubre | Tests |
|---------|-----------|-------|
| test_fetchers.py | sync, threaded, async, CPU-bound, measure | 16 |

### Tests sin red real

Todos los tests usan `httpx.MockTransport` (o `AsyncBaseTransport` para async), por lo que:

- No dependen de internet
- Son rápidos y deterministas
- Verifican el comportamiento del semáforo (max concurrentes <= N)

## Cuándo usar cada modelo

| Escenario | Modelo recomendado | Por qué |
|-----------|-------------------|---------|
| Pocas operaciones | Síncrono | Simple, sin overhead |
| Muchas I/O (10-100s) | Threading | Fácil, buena aceleración |
| Muchísimas I/O (1000s) | Asyncio | Escala mejor, menos overhead |
| CPU-bound | Multiprocessing | Evita el GIL |
| Mixto (I/O + CPU) | Asyncio + ProcessPoolExecutor | Combinación |

## Notas de implementación

### GIL (Global Interpreter Lock)

El GIL permite que solo un hilo ejecute bytecode Python a la vez. Pero:

- **I/O libera el GIL**: mientras un hilo espera la red, otro puede ejecutar
- **CPU no lo libera**: threads no aceleran cálculos puros

Por eso:
- **I/O-bound** → threads o asyncio
- **CPU-bound** → multiprocessing

### Asyncio vs Threads

| Aspecto | Asyncio | Threads |
|---------|---------|---------|
| Memoria por tarea | Muy baja | ~8 MB por hilo |
| Cambio de contexto | Cooperativo (rápido) | Preemptivo (OS) |
| Complejidad | Requiere async/await | Código sync normal |
| Librerías | Deben ser async | Cualquiera |
| Ideal para | Miles de conexiones | Decenas de conexiones |

### Semaforo en asyncio

El `asyncio.Semaphore(N)` limita la concurrencia:

    sem = asyncio.Semaphore(10)  # max 10 concurrentes

    async def fetch(url):
        async with sem:
            return await client.get(url)

Sin el semáforo, `asyncio.gather()` lanzaría **todas** las requests a la vez. Con muchas URLs, esto puede saturar la red o la API (rate limit).

### ProcessPoolExecutor

Cada proceso es un intérprete Python separado → sin GIL compartido.

Requisitos:
- Los argumentos y retornos deben ser **picklables**
- El código de la función debe estar en un módulo **importable** (no en `__main__`)

Overhead: crear procesos es caro. Útil solo cuando el cálculo justifica el costo.

### Medición con time.perf_counter()

    from time import perf_counter

    inicio = perf_counter()
    resultado = funcion()
    duracion = perf_counter() - inicio

- `perf_counter()`: reloj de mayor resolución (wall-clock)
- `process_time()`: tiempo de CPU (útil para CPU-bound)
- `timeit`: para microbenchmarks
- `cProfile`: profiling completo

**Regla:** no optimizar sin medir.

## Comandos rápidos (resumen)

    # Comparativa contra API real (necesita internet)
    poetry run python -c "
    import sys; sys.path.insert(0, '04_laboratorios/lab_11_concurrencia')
    from fetchers import fetch_sync, fetch_threaded, run_fetch_async, measure
    ids = list(range(1, 11))
    _, t = measure(fetch_sync, ids); print(f'Sync:     {t:.2f}s')
    _, t = measure(fetch_threaded, ids); print(f'Threaded: {t:.2f}s')
    _, t = measure(run_fetch_async, ids); print(f'Async:    {t:.2f}s')
    "

    # Tests
    poetry run pytest 04_laboratorios/lab_11_concurrencia/tests/ -v

    # Calidad
    poetry run ruff check 04_laboratorios/lab_11_concurrencia/
    poetry run mypy 04_laboratorios/lab_11_concurrencia/

## Estado

- [x] Estructura del laboratorio
- [x] pytest-asyncio instalado y configurado (mode=auto)
- [x] Fetcher síncrono (baseline)
- [x] Fetcher con ThreadPoolExecutor
- [x] Fetcher con httpx.AsyncClient + semáforo
- [x] Cálculo CPU-bound con ProcessPoolExecutor
- [x] Función measure con time.perf_counter
- [x] 16 tests con MockTransport (sin red real)
- [x] ruff + mypy OK
- [x] Documentación completa

## Clonar este laboratorio

    git clone https://github.com/parisollie/python-training.git
    cd python-training
    poetry install

    # Tests
    poetry run pytest 04_laboratorios/lab_11_concurrencia/tests/ -v

    # Comparativa contra API real (necesita internet)
    poetry run python -c "
    import sys; sys.path.insert(0, '04_laboratorios/lab_11_concurrencia')
    from fetchers import fetch_sync, fetch_threaded, run_fetch_async, measure
    ids = list(range(1, 11))
    _, t = measure(fetch_sync, ids); print(f'Sync:     {t:.2f}s')
    _, t = measure(fetch_threaded, ids); print(f'Threaded: {t:.2f}s')
    _, t = measure(run_fetch_async, ids); print(f'Async:    {t:.2f}s')
    "

## Referencias

- Python docs — threading: https://docs.python.org/3/library/threading.html
- Python docs — concurrent.futures: https://docs.python.org/3/library/concurrent.futures.html
- Python docs — asyncio: https://docs.python.org/3/library/asyncio.html
- Python docs — multiprocessing: https://docs.python.org/3/library/multiprocessing.html
- Python docs — timeit: https://docs.python.org/3/library/timeit.html
- Python docs — cProfile: https://docs.python.org/3/library/profile.html
- Real Python — Concurrency: https://realpython.com/python-concurrency/
- httpx — Async: https://www.python-httpx.org/async/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/

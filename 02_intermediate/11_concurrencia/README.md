# Módulo 11 — Concurrencia y rendimiento

## Objetivos
- Elegir el modelo de concurrencia apropiado (sync, threads, async, procesos)
- Implementar E/S concurrente y medir mejoras
- Entender las limitaciones del GIL

## Contenidos clave

### GIL (Global Interpreter Lock)
- Python tiene un lock global que permite solo un hilo ejecutando bytecode a la vez
- Implica: threads NO aceleran CPU-bound
- Pero SÍ aceleran I/O-bound (I/O libera el GIL)

### Cuándo usar cada modelo

| Modelo | Ideal para | Limitacion |
|--------|-----------|------------|
| Sincrono | Pocas operaciones, secuencial | Lento con muchas I/O |
| Threading | Muchas I/O concurrentes | GIL limita CPU |
| Asyncio | Muchas I/O concurrentes (mas escalable) | Requiere librerias async |
| Multiprocessing | CPU-bound | Overhead de procesos, sin memoria compartida |

### threading y concurrent.futures
- ThreadPoolExecutor como API de alto nivel
- submit() / map() / as_completed()
- Cuándo NO usar threads (CPU-bound)

### asyncio
- Event loop (single thread, cooperativo)
- async def / await
- asyncio.gather() para concurrencia
- asyncio.Semaphore para limitar concurrencia
- asyncio.run() como entry point
- asyncio.TaskGroup (Python 3.11+)

### multiprocessing
- ProcessPoolExecutor
- Ideal para CPU-bound
- Serializacion (pickle) obligatoria
- Overhead de crear procesos

### Medicion
- time.perf_counter() para wall-clock
- time.process_time() para CPU
- timeit para microbenchmarks
- cProfile para profiling completo
- No optimizar sin medir

## Laboratorio

Fetcher concurrente contra la API de Rick and Morty:

1. **Baseline**: fetcher sincrono (uno por uno)
2. **Threaded**: ThreadPoolExecutor con N workers
3. **Async**: httpx.AsyncClient + asyncio.Semaphore
4. **CPU-bound**: ProcessPoolExecutor con calculo pesado

Comparativa de tiempos:
- Medir con time.perf_counter()
- Mostrar speedup de cada version

## Conceptos clave

### ¿Por que PEP 20 importa aqui?
- "Simple es mejor que complejo" -> empezar con sync, luego optimizar
- "Explícito es mejor que implícito" -> declarar cuando es async
- "Los errores nunca deben pasar silenciosamente" -> asyncio.gather con return_exceptions

### Modelo mental: I/O vs CPU

    I/O-bound (red, disco, DB):
    - Threads o asyncio
    - El GIL se libera durante la espera

    CPU-bound (numeros, parsing):
    - Multiprocessing
    - El GIL bloquea threads

### Ejemplo: sync vs threads

    import time
    from concurrent.futures import ThreadPoolExecutor

    def tarea(x: int) -> int:
        time.sleep(0.1)  # simula I/O
        return x * 2

    # Sync: 1 segundo (10 * 0.1s)
    inicio = time.perf_counter()
    [tarea(i) for i in range(10)]
    print(f"Sync: {time.perf_counter() - inicio:.2f}s")

    # Threaded: ~0.1s
    inicio = time.perf_counter()
    with ThreadPoolExecutor(max_workers=10) as ex:
        list(ex.map(tarea, range(10)))
    print(f"Threaded: {time.perf_counter() - inicio:.2f}s")

### Ejemplo: asyncio

    import asyncio
    import httpx

    async def fetch(client, url):
        r = await client.get(url)
        return r.json()

    async def main():
        async with httpx.AsyncClient() as client:
            urls = [f"https://api.ejemplo.com/{i}" for i in range(10)]
            results = await asyncio.gather(*[fetch(client, u) for u in urls])
            return results

    asyncio.run(main())

### Ejemplo: semaforo para limitar concurrencia

    async def fetch_con_limite(client, sem, url):
        async with sem:
            return await fetch(client, url)

    async def main():
        sem = asyncio.Semaphore(5)  # max 5 concurrentes
        async with httpx.AsyncClient() as client:
            urls = [f"https://api.ejemplo.com/{i}" for i in range(50)]
            await asyncio.gather(*[fetch_con_limite(client, sem, u) for u in urls])

### Ejemplo: ProcessPoolExecutor

    from concurrent.futures import ProcessPoolExecutor

    def calcular_pesado(n: int) -> int:
        return sum(i * i for i in range(n))

    with ProcessPoolExecutor() as ex:
        results = list(ex.map(calcular_pesado, [10_000] * 8))

### Cuando NO usar asyncio

- Codigo CPU-bound (usa multiprocessing)
- Librerias sin soporte async (usa threads)
- Scripts simples de 1-2 requests (usa sync)

## Checklist
- [ ] Crear estructura del laboratorio
- [ ] Implementar fetcher sincrono (baseline)
- [ ] Implementar fetcher con threads
- [ ] Implementar fetcher con asyncio + semaforo
- [ ] Implementar calculo CPU-bound con procesos
- [ ] Medir y comparar
- [ ] Tests con pytest + httpx.MockTransport
- [ ] Correr ruff y mypy
- [ ] Documentar en README del laboratorio
- [ ] Commit del modulo

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

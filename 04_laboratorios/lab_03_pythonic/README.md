# Laboratorio 03 — Programación pythonic

Tres ejercicios prácticos que cubren los temas del Módulo 03:
1. Decorador de reintentos con backoff exponencial
2. Generador por lotes (batching)
3. Context manager de temporización

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1

## Estructura

lab_03_pythonic/
├── README.md              ← este archivo
├── retry.py               ← decorador de reintentos
├── batching.py            ← generador por lotes
├── timer.py               ← context manager de temporización (pendiente)
└── tests/
    ├── test_retry.py      ← 9 tests
    ├── test_batching.py   ← 11 tests
    └── test_timer.py      ← pendiente

## Instalación

Desde la raíz del proyecto:

    poetry install

## Ejercicio 1 — Decorador de reintentos

### Uso

    import sys
    sys.path.insert(0, '04_laboratorios/lab_03_pythonic')
    from retry import retry

    @retry(max_attempts=3, base_delay=0.1)
    def funcion_inestable():
        # Si esto falla, se reintenta automáticamente
        return "ok"

### Parámetros

| Parámetro | Tipo | Descripción | Default |
|-----------|------|-------------|---------|
| max_attempts | int | Número máximo de intentos | 3 |
| base_delay | float | Segundos de espera inicial (se duplica cada vez) | 0.1 |
| exceptions | tuple[type[Exception], ...] | Excepciones a capturar | (Exception,) |

### Ejemplo: éxito tras 2 fallos

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_03_pythonic')
    from retry import retry

    contador = {'n': 0}

    @retry(max_attempts=3, base_delay=0.1)
    def funcion_inestable():
        contador['n'] += 1
        if contador['n'] < 3:
            raise ValueError(f'Fallo simulado #{contador[\"n\"]}')
        return f'Éxito en intento {contador[\"n\"]}'

    print(funcion_inestable())
    "

Salida esperada:

    ⚠️  Intento 1/3 falló: ValueError('Fallo simulado #1'). Reintentando en 0.10s...
    ⚠️  Intento 2/3 falló: ValueError('Fallo simulado #2'). Reintentando en 0.20s...
    Éxito en intento 3

### Ejemplo: fallo total

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_03_pythonic')
    from retry import retry

    @retry(max_attempts=2, base_delay=0.05)
    def siempre_falla():
        raise RuntimeError('boom')

    try:
        siempre_falla()
    except RuntimeError as e:
        print(f'Excepción final: {e}')
    "

Salida esperada:

    ⚠️  Intento 1/2 falló: RuntimeError('boom'). Reintentando en 0.05s...
    ❌ Se agotaron los 2 intentos.
    Excepción final: boom

## Ejercicio 2 — Generador por lotes (batching)

### Uso

    import sys
    sys.path.insert(0, '04_laboratorios/lab_03_pythonic')
    from batching import batch

    for lote in batch([1, 2, 3, 4, 5], size=2):
        print(lote)
    # [1, 2]
    # [3, 4]
    # [5]

### Parámetros

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| iterable | Iterable[T] | Cualquier iterable (lista, generador, string, etc.) |
| size | int | Tamaño de cada lote. Debe ser >= 1 |

### Ejemplo: varios casos

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_03_pythonic')
    from batching import batch

    # Lote exacto
    print(list(batch([1, 2, 3, 4, 5, 6], size=3)))

    # Último lote parcial
    print(list(batch([1, 2, 3, 4, 5, 6, 7], size=3)))

    # Iterable vacío
    print(list(batch([], size=3)))

    # Con generador (lazy)
    def contar(n):
        yield from range(1, n + 1)

    print(list(batch(contar(7), size=3)))
    "

Salida esperada:

    [[1, 2, 3], [4, 5, 6]]
    [[1, 2, 3], [4, 5, 6], [7]]
    []
    [[1, 2, 3], [4, 5, 6], [7]]

### Notas de implementación

- Es un **generador** (usa `yield`), por lo que no carga todo en memoria.
- Usa la **sintaxis moderna de genéricos** de Python 3.12 (PEP 695): `def batch[T](...)`.
- El último lote puede ser más pequeño que `size`.
- Si `size < 1`, lanza `ValueError`.
- Funciona con cualquier iterable: listas, tuplas, generadores, strings, archivos.

## Cómo ejecutar los tests

### Todos los tests

    poetry run pytest 04_laboratorios/lab_03_pythonic/tests/ -v

Salida esperada:

    20 passed in 0.43s

### Con cobertura

    poetry run pytest 04_laboratorios/lab_03_pythonic/tests/ --cov=04_laboratorios/lab_03_pythonic --cov-report=term-missing

### Solo un archivo

    poetry run pytest 04_laboratorios/lab_03_pythonic/tests/test_retry.py -v
    poetry run pytest 04_laboratorios/lab_03_pythonic/tests/test_batching.py -v

### Archivos de tests

| Archivo | Qué cubre | Tests |
|---------|-----------|-------|
| test_retry.py | retry (éxito, fallos, validaciones, backoff) | 9 |
| test_batching.py | batch (lotes, lazy, edge cases) | 11 |
| test_timer.py | timer (pendiente) | — |

## Verificación de calidad

    poetry run ruff check 04_laboratorios/lab_03_pythonic/
    poetry run mypy 04_laboratorios/lab_03_pythonic/
    poetry run pre-commit run --all-files

## Comandos rápidos (resumen)

    # Tests
    poetry run pytest 04_laboratorios/lab_03_pythonic/tests/ -v

    # Cobertura
    poetry run pytest 04_laboratorios/lab_03_pythonic/tests/ --cov=04_laboratorios/lab_03_pythonic --cov-report=term-missing

    # Calidad
    poetry run ruff check 04_laboratorios/lab_03_pythonic/
    poetry run mypy 04_laboratorios/lab_03_pythonic/

## Estado

- [x] Ejercicio 1: Decorador de reintentos
- [x] Ejercicio 2: Generador por lotes
- [ ] Ejercicio 3: Context manager de temporización
- [ ] README completo al final

## Clonar este laboratorio

    git clone https://github.com/parisollie/python-training.git
    cd python-training
    poetry install

    # Ejecutar tests
    poetry run pytest 04_laboratorios/lab_03_pythonic/tests/ -v

## Referencias

- Python docs — Decoradores: https://docs.python.org/3/glossary.html#term-decorator
- functools.wraps: https://docs.python.org/3/library/functools.html#functools.wraps
- PEP 318 — Decorators: https://peps.python.org/pep-0318/
- PEP 695 — Type Parameter Syntax: https://peps.python.org/pep-0695/
- Python docs — Generadores: https://docs.python.org/3/tutorial/classes.html#generators

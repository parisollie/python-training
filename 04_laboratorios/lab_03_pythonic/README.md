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
├── batching.py            ← generador por lotes (pendiente)
├── timer.py               ← context manager de temporización (pendiente)
└── tests/
    ├── test_retry.py      ← 9 tests
    ├── test_batching.py   ← pendiente
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

## Cómo ejecutar los tests

### Todos los tests

    poetry run pytest 04_laboratorios/lab_03_pythonic/tests/ -v

Salida esperada:

    9 passed in 0.42s

### Con cobertura

    poetry run pytest 04_laboratorios/lab_03_pythonic/tests/ --cov=04_laboratorios/lab_03_pythonic --cov-report=term-missing

### Solo un archivo

    poetry run pytest 04_laboratorios/lab_03_pythonic/tests/test_retry.py -v

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
- [ ] Ejercicio 2: Generador por lotes
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

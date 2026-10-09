# Módulo 03 — Funciones y programación pythonic

## Objetivos
- Diseñar APIs de funciones claras y expresivas
- Implementar decoradores y generadores utiles
- Crear context managers para recursos

## Contenidos clave

### Funciones
- Definicion con def y return
- Argumentos posicionales y nombrados
- Valores por defecto (y el peligro de los mutables)
- *args y **kwargs
- Keyword-only arguments (despues de *)

### Lambdas y closures
- Funciones anonimas con lambda
- Funciones de orden superior: map, filter, sorted
- Closures: funciones que recuerdan su entorno

### Decoradores
- Funcion que envuelve a otra funcion
- functools.wraps para preservar metadatos
- Decoradores con argumentos
- Casos de uso: reintentos, logging, cache, temporizacion

### Iteradores y generadores
- Iteradores: __iter__ y __next__
- Generadores con yield
- Expresiones generadoras
- yield from
- Lazy evaluation y uso eficiente de memoria

### Comprensiones
- List comprehension
- Dict comprehension
- Set comprehension
- Generator expression
- Cuando NO usarlas (legibilidad)

### Context managers
- Protocolo with
- __enter__ y __exit__
- contextlib.contextmanager
- Casos de uso: archivos, conexiones, locks, temporizacion

## Laboratorio

Tres ejercicios practicos que cubren los tres temas principales:

1. Decorador de reintentos con backoff exponencial
2. Generador por lotes (batching)
3. Context manager de temporizacion

## Conceptos clave

### ¿Por que PEP 20 importa aqui?
- "Simple es mejor que complejo" -> usar la herramienta minima necesaria
- "Plano es mejor que anidado" -> evitar decoradores dentro de decoradores sin razon
- "La legibilidad cuenta" -> no usar comprensiones anidadas si confunden

### Regla practica: cuando usar cada herramienta

| Herramienta | Cuando usar |
|-------------|-------------|
| Funcion normal | Logica con nombre claro y reutilizable |
| Lambda | Funciones cortas que se usan una sola vez |
| Decorador | Agregar comportamiento a funciones existentes sin modificarlas |
| Generador | Iterar grandes volumenes de datos sin cargar todo en memoria |
| Comprension | Transformar/filtrar colecciones en una linea legible |
| Context manager | Gestionar recursos que requieren setup/teardown |

### Ejemplo de decorador con functools.wraps

    from functools import wraps

    def mi_decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"Antes de {func.__name__}")
            result = func(*args, **kwargs)
            print(f"Despues de {func.__name__}")
            return result
        return wrapper

### Ejemplo de generador

    def contar_hasta(n):
        for i in range(1, n + 1):
            yield i

    for num in contar_hasta(3):
        print(num)  # 1, 2, 3

### Ejemplo de context manager con contextlib

    from contextlib import contextmanager
    import time

    @contextmanager
    def timer():
        inicio = time.perf_counter()
        yield
        print(f"Duracion: {time.perf_counter() - inicio:.4f}s")

    with timer():
        sum(range(1_000_000))

## Checklist
- [ ] Crear estructura del laboratorio
- [ ] Escribir decorador de reintentos con backoff
- [ ] Escribir generador por lotes
- [ ] Escribir context manager de temporizacion
- [ ] Escribir tests con pytest
- [ ] Correr ruff y mypy
- [ ] Documentar en README del laboratorio
- [ ] Commit del modulo

## Referencias
- Python docs — Funciones: https://docs.python.org/3/tutorial/controlflow.html#defining-functions
- Python docs — Decoradores: https://docs.python.org/3/glossary.html#term-decorator
- Python docs — Generadores: https://docs.python.org/3/tutorial/classes.html#generators
- Python docs — contextlib: https://docs.python.org/3/library/contextlib.html
- PEP 318 — Decorators: https://peps.python.org/pep-0318/
- PEP 255 — Simple Generators: https://peps.python.org/pep-0255/

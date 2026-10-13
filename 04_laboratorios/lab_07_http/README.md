# Laboratorio 07 — Cliente HTTP con httpx (Rick and Morty)

Cliente HTTP robusto que consume la API de Rick and Morty con:
- Timeouts configurables
- Reintentos con backoff exponencial
- Manejo de errores por código HTTP
- Paginación automática
- Streaming a disco

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1
- httpx (instalado en el proyecto)
- Conexión a internet (solo para pruebas manuales)

## Estructura

lab_07_http/
├── README.md              ← este archivo
├── client.py              ← cliente httpx con reintentos
├── downloads/             ← archivos descargados (ignorados por git)
└── tests/
    └── test_client.py     ← 11 tests con MockTransport (sin red)

## Cliente HTTP (client.py)

### RickMortyClient

Clase con context manager (`with`) que encapsula el cliente `httpx.Client`.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| base_url | str | Rick and Morty API | URL base |
| timeout | float | 10.0 | Timeout por operación (segundos) |
| max_attempts | int | 3 | Intentos máximos por request |
| base_delay | float | 0.5 | Segundos iniciales del backoff |

### Métodos

| Método | Descripción |
|--------|-------------|
| `get_character(id)` | Obtiene un personaje por ID |
| `get_all_characters(max_pages=None)` | Recorre todas las páginas |
| `stream_to_file(path, output)` | Descarga por streaming a disco |
| `close()` | Cierra el cliente |

### Política de reintentos

| Código | Reintenta |
|--------|:---:|
| 2xx | — (éxito) |
| 4xx (excepto 429) | ❌ No (error del cliente) |
| 429 | ✅ Sí (rate limit) |
| 5xx | ✅ Sí (error del servidor) |
| Timeout / Error de conexión | ✅ Sí |

### Backoff exponencial

- Intento 1 falla → espera `base_delay * 1` = 0.5s
- Intento 2 falla → espera `base_delay * 2` = 1.0s
- Intento 3 falla → no más intentos, propaga excepción

## Ejemplos de uso

### Obtener un personaje

    poetry run python -c "
    import sys, logging
    sys.path.insert(0, '04_laboratorios/lab_07_http')
    logging.basicConfig(level=logging.WARNING)
    from client import RickMortyClient

    with RickMortyClient() as client:
        rick = client.get_character(1)
        print(f'{rick[\"name\"]} - {rick[\"species\"]}')
    "

Salida esperada:

    Rick Sanchez - Human

### Recorrer todas las páginas (limitado a 2)

    poetry run python -c "
    import sys, logging
    sys.path.insert(0, '04_laboratorios/lab_07_http')
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    from client import RickMortyClient

    with RickMortyClient() as client:
        chars = client.get_all_characters(max_pages=2)
        print(f'Total: {len(chars)}')
    "

Salida esperada:

    INFO: Pagina 1: 20 personajes
    INFO: Pagina 2: 20 personajes
    INFO: Limite de 2 paginas alcanzado
    INFO: Total: 40 personajes en 3 paginas
    Total: 40

### Streaming a disco

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_07_http')
    from pathlib import Path
    from client import RickMortyClient

    with RickMortyClient() as client:
        size = client.stream_to_file('/character/1', Path('04_laboratorios/lab_07_http/downloads/rick.json'))
        print(f'Descargados {size} bytes')
    "

Salida esperada:

    Descargados XXX bytes

## Cómo ejecutar los tests

### Todos los tests

    poetry run pytest 04_laboratorios/lab_07_http/tests/ -v

Salida esperada:

    11 passed in 0.17s

### Con cobertura

    poetry run pytest 04_laboratorios/lab_07_http/tests/ --cov=04_laboratorios/lab_07_http --cov-report=term-missing

### Archivos de tests

| Archivo | Qué cubre | Tests |
|---------|-----------|-------|
| test_client.py | get_character, get_all_characters, stream, context manager, reintentos | 11 |

### Tests sin red real

Los tests usan `httpx.MockTransport`, que intercepta las requests y devuelve respuestas simuladas. Esto permite:

- Probar sin conexión a internet
- Simular errores (500, 404, 429) sin depender de la API real
- Tests rápidos y deterministas
- No consumir la cuota de la API pública

## Verificación de calidad

    poetry run ruff check 04_laboratorios/lab_07_http/
    poetry run mypy 04_laboratorios/lab_07_http/
    poetry run pre-commit run --all-files

## Notas de implementación

### Por qué httpx y no requests

- API moderna y consistente
- Soporte nativo de async/await (útil en Módulo 11)
- Type hints completos (bueno para mypy strict)
- `MockTransport` para testing sin red
- Soporte HTTP/2

### Timeouts explícitos

    httpx.Timeout(timeout, connect=5.0)

- `timeout` global (read/write/pool)
- `connect=5.0` específico para la conexión TCP

Nunca dejar sin timeout: si el servidor no responde, la app se cuelga.

### No reintentar 4xx

Los errores 4xx (excepto 429) indican que **el cliente** está mal (URL incorrecta, sin auth, recurso no existe). Reintentar no ayuda.

### Lazy logging

    logger.warning("Intento %d/%d fallo (%s)", attempt, max_attempts, e)

Se usan `%s` en lugar de f-strings para evitar formatear el mensaje si el nivel no está activo.

### Cast de `response.json()`

mypy strict no acepta devolver `Any`. Por eso validamos:

    data = response.json()
    if not isinstance(data, dict):
        raise ValueError(...)
    return data

Esto satisface a mypy y agrega una capa de robustez en runtime.

## Comandos rápidos (resumen)

    # Un personaje
    poetry run python -c "
    import sys; sys.path.insert(0, '04_laboratorios/lab_07_http')
    from client import RickMortyClient
    with RickMortyClient() as c: print(c.get_character(1)['name'])
    "

    # Tests
    poetry run pytest 04_laboratorios/lab_07_http/tests/ -v

    # Calidad
    poetry run ruff check 04_laboratorios/lab_07_http/
    poetry run mypy 04_laboratorios/lab_07_http/

## Estado

- [x] Crear estructura del laboratorio
- [x] httpx instalado
- [x] Cliente con timeouts
- [x] Reintentos con backoff exponencial
- [x] Paginación
- [x] Streaming a disco
- [x] 11 tests con MockTransport
- [x] ruff + mypy OK
- [x] Documentación completa

## Clonar este laboratorio

    git clone https://github.com/parisollie/python-training.git
    cd python-training
    poetry install

    # Tests (sin red real)
    poetry run pytest 04_laboratorios/lab_07_http/tests/ -v

    # Prueba manual (necesita red)
    poetry run python -c "
    import sys; sys.path.insert(0, '04_laboratorios/lab_07_http')
    from client import RickMortyClient
    with RickMortyClient() as c: print(c.get_character(1)['name'])
    "

## Referencias

- httpx docs: https://www.python-httpx.org/
- httpx — Timeouts: https://www.python-httpx.org/advanced/timeouts/
- httpx — MockTransport: https://www.python-httpx.org/advanced/transports/#mock-transport
- httpx — Streaming: https://www.python-httpx.org/advanced/#streaming-responses
- Rick and Morty API: https://rickandmortyapi.com/documentation
- MDN — HTTP Status: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

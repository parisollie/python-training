# Laboratorio 06 — Librería estándar y E/S

Script de ingesta que lee un CSV de Rick and Morty, calcula métricas, exporta a JSON y registra todo con logging.

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1

## Estructura

```text
lab_06_stdlib/
├── README.md              ← este archivo
├── ingest.py              ← script principal
├── data/
│   └── characters.csv     ← 20 personajes de Rick and Morty
├── output/
│   └── metrics.json       ← generado al ejecutar (no versionado)
└── tests/
    └── test_ingest.py     ← 12 tests
```

## Conceptos demostrados

| Módulo | Uso |
|--------|-----|
| `pathlib` | Rutas relativas al script con `Path(__file__).parent` |
| `csv.DictReader` | Leer CSV como diccionarios |
| `datetime` con `UTC` | Timestamps en UTC (Python 3.11+) |
| `logging` | Logging estructurado con niveles |
| `json.dump` | Serialización con `indent`, `sort_keys`, `ensure_ascii` |
| `collections.Counter` | Contar valores sin diccionarios manuales |

## Ejecutar el script

    poetry run python 04_laboratorios/lab_06_stdlib/ingest.py

Salida esperada:

    2026-XX-XX XX:XX:XX [INFO] __main__: 🚀 Iniciando ingesta
    2026-XX-XX XX:XX:XX [INFO] __main__: Leidos 20 personajes desde characters.csv
    2026-XX-XX XX:XX:XX [INFO] __main__: Metricas exportadas a .../output/metrics.json
    2026-XX-XX XX:XX:XX [INFO] __main__: 📊 Resumen: 20 personajes | Vivos: 8 | Muertos: 6
    2026-XX-XX XX:XX:XX [INFO] __main__: ✅ Ingesta completada

## Ver el JSON generado

    cat 04_laboratorios/lab_06_stdlib/output/metrics.json

Salida esperada:

    {
      "by_species": {
        "Alien": 5,
        "Human": 15
      },
      "by_status": {
        "Alive": 8,
        "Dead": 6,
        "unknown": 6
      },
      "timestamp": "2026-10-13T18:09:17.754673+00:00",
      "total": 20
    }

## Cambiar el nivel de logging

Para ver logs de DEBUG (más detalle):

    poetry run python -c "
    import logging, sys
    sys.path.insert(0, '04_laboratorios/lab_06_stdlib')
    from ingest import configure_logging, load_characters, compute_metrics, CSV_FILE
    configure_logging(logging.DEBUG)
    chars = load_characters(CSV_FILE)
    compute_metrics(chars)
    "

Salida esperada (incluye DEBUG):

    ... [DEBUG] __main__: Metricas calculadas: {'total': 20, ...}
    ... [INFO] __main__: Leidos 20 personajes desde characters.csv

## Cómo ejecutar los tests

### Todos los tests

    poetry run pytest 04_laboratorios/lab_06_stdlib/tests/ -v

Salida esperada:

    12 passed in 0.02s

### Con cobertura

    poetry run pytest 04_laboratorios/lab_06_stdlib/tests/ --cov=04_laboratorios/lab_06_stdlib --cov-report=term-missing

### Archivos de tests

| Archivo | Qué cubre | Tests |
|---------|-----------|-------|
| test_ingest.py | load_characters, compute_metrics, export_json, logging | 12 |

### Fixtures usadas

- `tmp_path` (built-in): directorio temporal único por test (evita ensuciar el repo)
- `caplog` (built-in): capturar mensajes de logging para verificar

## Verificación de calidad

    poetry run ruff check 04_laboratorios/lab_06_stdlib/
    poetry run mypy 04_laboratorios/lab_06_stdlib/
    poetry run pre-commit run --all-files

## Notas de implementación

### pathlib en lugar de os.path

    BASE_DIR = Path(__file__).parent
    CSV_FILE = BASE_DIR / "data" / "characters.csv"

Funciona igual en macOS, Linux y Windows. No hace falta `os.path.join`.

### mkdir con parents=True

    output_path.parent.mkdir(parents=True, exist_ok=True)

`parents=True` crea toda la cadena de directorios intermedios si no existen.
Sin esto, `mkdir` solo crea el último nivel y falla si el padre no existe.

### UTC en lugar de timezone.utc

    from datetime import UTC, datetime
    datetime.now(UTC).isoformat()

Desde Python 3.11, `datetime.UTC` es un alias más limpio que `timezone.utc`.
Ruff lo detecta con la regla UP017.

### logging con lazy formatting

    logger.info("Leidos %d personajes desde %s", len(characters), csv_path.name)

Usar `%s` en lugar de f-strings evita formatear el mensaje si el nivel no
está habilitado. Es una micro-optimización recomendada.

### No usar print para debugging

- `print` va a stdout siempre
- `logging` respeta niveles, se puede redirigir, tiene timestamps
- En producción, `logger.info` se puede silenciar, `print` no

## Comandos rápidos (resumen)

    # Ejecutar
    poetry run python 04_laboratorios/lab_06_stdlib/ingest.py

    # Ver JSON
    cat 04_laboratorios/lab_06_stdlib/output/metrics.json

    # Tests
    poetry run pytest 04_laboratorios/lab_06_stdlib/tests/ -v

    # Calidad
    poetry run ruff check 04_laboratorios/lab_06_stdlib/
    poetry run mypy 04_laboratorios/lab_06_stdlib/

## Estado

- [x] Crear estructura del laboratorio
- [x] Lectura de CSV con DictReader
- [x] pathlib para rutas
- [x] datetime con UTC
- [x] logging estructurado
- [x] Exportación a JSON
- [x] 12 tests con pytest
- [x] ruff + mypy OK
- [x] Documentación completa

## Clonar este laboratorio

    git clone https://github.com/parisollie/python-training.git
    cd python-training
    poetry install

    # Ejecutar
    poetry run python 04_laboratorios/lab_06_stdlib/ingest.py

    # Tests
    poetry run pytest 04_laboratorios/lab_06_stdlib/tests/ -v

## Referencias

- Python docs — pathlib: https://docs.python.org/3/library/pathlib.html
- Python docs — csv: https://docs.python.org/3/library/csv.html
- Python docs — json: https://docs.python.org/3/library/json.html
- Python docs — datetime: https://docs.python.org/3/library/datetime.html
- Python docs — logging: https://docs.python.org/3/library/logging.html
- Python docs — collections.Counter: https://docs.python.org/3/library/collections.html#collections.Counter

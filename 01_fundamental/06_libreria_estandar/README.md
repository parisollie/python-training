# Módulo 06 — Librería estándar y E/S

## Objetivos
- Manipular archivos y rutas de forma segura con pathlib
- Parsear y serializar CSV, JSON, YAML
- Manejar fechas y zonas horarias
- Configurar logging estructurado
- Automatizar con subprocess

## Contenidos clave

### pathlib
- Path vs str para rutas
- Operadores: / para unir rutas
- Metodos: exists, is_file, is_dir, mkdir, glob, read_text, write_text
- Rutas relativas y absolutas
- Path(__file__).parent para rutas relativas al script

### CSV
- csv.reader y csv.writer
- csv.DictReader y csv.DictWriter (mas comodo)
- Dialectos y delimitadores
- Manejo de encoding (utf-8)

### JSON
- json.load / json.loads
- json.dump / json.dumps
- Parametros: indent, ensure_ascii, sort_keys
- Manejo de errores (JSONDecodeError)

### YAML (requiere PyYAML)
- yaml.safe_load / yaml.safe_dump
- Diferencias con JSON (comentarios, mas legible)
- Riesgos de yaml.load sin safe_load

### datetime
- datetime.now() vs datetime.utcnow() (deprecated)
- datetime.now(timezone.utc) para UTC consciente
- ZoneInfo para zonas horarias (Python 3.9+)
- timedelta para diferencias
- strftime / strptime para formateo
- ISO 8601: isoformat() y fromisoformat()

### logging
- logging.basicConfig para configuracion rapida
- Niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Loggers nombrados (logging.getLogger(__name__))
- Handlers: StreamHandler, FileHandler
- Formatters personalizados
- No usar print para debugging en produccion

### subprocess
- subprocess.run (recomendado)
- Captura de salida: capture_output=True
- Manejo de errores: check=True
- Alternativas mas seguras que os.system

## Laboratorio

Script de ingesta y procesamiento:

1. Leer un CSV de personajes de Rick and Morty
2. Calcular metricas (total, vivos, muertos, por especie)
3. Exportar resultados a JSON
4. Registrar todo con logging (distintos niveles)
5. Usar pathlib para todas las rutas
6. Usar datetime para timestamps

## Conceptos clave

### ¿Por que PEP 20 importa aqui?
- "Simple es mejor que complejo" -> usar csv.DictReader en lugar de split(',')
- "Explícito es mejor que implícito" -> encoding='utf-8' siempre
- "Los errores nunca deben pasar silenciosamente" -> logging.exception para capturar

### Cuando usar cada formato

| Formato | Cuando usar |
|---------|-------------|
| JSON | APIs, configuracion estructurada, intercambio de datos |
| CSV | Datos tabulares simples, export desde Excel/Sheets |
| YAML | Configuracion legible por humanos (Kubernetes, CI/CD) |
| TOML | Configuracion de proyectos Python (pyproject.toml) |

### Niveles de logging

| Nivel | Uso |
|-------|-----|
| DEBUG | Detalles finos, solo en desarrollo |
| INFO | Eventos normales (inicio, fin, hitos) |
| WARNING | Algo inesperado pero no rompe (fallback, dato faltante) |
| ERROR | Algo fallo pero la app sigue (endpoint falla, archivo no se pudo leer) |
| CRITICAL | La app no puede continuar (DB caida, config corrupta) |

### Ejemplo: pathlib

    from pathlib import Path

    # Construir rutas (independiente del SO)
    data_dir = Path(__file__).parent / "data"
    archivo = data_dir / "characters.csv"

    # Verificar y crear
    data_dir.mkdir(exist_ok=True)

    # Leer/escribir
    contenido = archivo.read_text(encoding="utf-8")
    archivo.write_text("nuevo contenido", encoding="utf-8")

    # Listar archivos
    for csv_file in data_dir.glob("*.csv"):
        print(csv_file.name)

### Ejemplo: CSV con DictReader

    import csv
    from pathlib import Path

    with Path("data.csv").open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(row["name"], row["status"])

### Ejemplo: datetime con timezone

    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo

    # UTC consciente (recomendado)
    ahora_utc = datetime.now(timezone.utc)

    # Zona horaria especifica
    madrid = ZoneInfo("Europe/Madrid")
    ahora_madrid = datetime.now(madrid)

    # Formateo ISO 8601
    print(ahora_utc.isoformat())

### Ejemplo: logging estructurado

    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logger = logging.getLogger(__name__)
    logger.info("Iniciando proceso")
    logger.warning("Dato faltante, usando default")
    logger.error("No se pudo conectar")

## Checklist
- [ ] Crear estructura del laboratorio
- [ ] Implementar lectura de CSV con DictReader
- [ ] Usar pathlib para rutas
- [ ] Usar datetime para timestamps
- [ ] Configurar logging con niveles
- [ ] Exportar resultados a JSON
- [ ] Escribir tests con pytest (tmp_path)
- [ ] Correr ruff y mypy
- [ ] Documentar en README del laboratorio
- [ ] Commit del modulo

## Referencias
- Python docs — pathlib: https://docs.python.org/3/library/pathlib.html
- Python docs — csv: https://docs.python.org/3/library/csv.html
- Python docs — json: https://docs.python.org/3/library/json.html
- Python docs — datetime: https://docs.python.org/3/library/datetime.html
- Python docs — zoneinfo: https://docs.python.org/3/library/zoneinfo.html
- Python docs — logging: https://docs.python.org/3/library/logging.html
- Python docs — subprocess: https://docs.python.org/3/library/subprocess.html
- PyYAML docs: https://pyyaml.org/wiki/PyYAMLDocumentation

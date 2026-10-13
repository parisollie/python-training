"""Ingesta de CSV de Rick and Morty con metricas y logging.

Demuestra:
- pathlib para manejo de rutas
- csv.DictReader para leer CSV
- datetime con UTC para timestamps
- logging con distintos niveles
- json para exportar resultados
"""

import csv
import json
import logging
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# ============================================
# Rutas (relativas al script)
# ============================================

BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "data" / "characters.csv"
OUTPUT_DIR = BASE_DIR / "output"


# ============================================
# Logging
# ============================================

logger = logging.getLogger(__name__)


def configure_logging(level: int = logging.INFO) -> None:
    """Configura logging basico para la consola.

    Args:
        level: Nivel minimo (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,  # Reemplaza configuracion previa (util en tests)
    )


# ============================================
# Lectura del CSV
# ============================================


def load_characters(csv_path: Path) -> list[dict[str, str]]:
    """Lee el CSV y devuelve una lista de diccionarios.

    Args:
        csv_path: Ruta al archivo CSV.

    Returns:
        Lista de filas como diccionarios (una por personaje).
        Lista vacia si hay error.
    """
    if not csv_path.exists():
        logger.error("Archivo no encontrado: %s", csv_path)
        return []

    try:
        with csv_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            characters = list(reader)
    except OSError as e:
        logger.exception("Error leyendo CSV: %s", e)
        return []

    logger.info("Leidos %d personajes desde %s", len(characters), csv_path.name)
    return characters


# ============================================
# Metricas
# ============================================


def compute_metrics(characters: list[dict[str, str]]) -> dict[str, Any]:
    """Calcula metricas de los personajes.

    Args:
        characters: Lista de personajes.

    Returns:
        Diccionario con metricas agregadas.
    """
    total = len(characters)
    by_status: Counter[str] = Counter(c["status"] for c in characters)
    by_species: Counter[str] = Counter(c["species"] for c in characters)

    metrics: dict[str, Any] = {
        "total": total,
        "by_status": dict(by_status),
        "by_species": dict(by_species),
        "timestamp": datetime.now(UTC).isoformat(),
    }

    logger.debug("Metricas calculadas: %s", metrics)
    return metrics


# ============================================
# Exportacion
# ============================================


def export_json(data: dict[str, Any], output_path: Path) -> None:
    """Exporta las metricas a JSON.

    Args:
        data: Diccionario con las metricas.
        output_path: Ruta de salida.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
    except OSError as e:
        logger.exception("Error escribiendo JSON: %s", e)
        return

    logger.info("Metricas exportadas a %s", output_path)


# ============================================
# Main
# ============================================


def main() -> None:
    """Punto de entrada del script."""
    configure_logging(logging.INFO)

    logger.info("🚀 Iniciando ingesta")

    # 1. Leer CSV
    characters = load_characters(CSV_FILE)
    if not characters:
        logger.warning("No hay personajes para procesar")
        return

    # 2. Calcular metricas
    metrics = compute_metrics(characters)

    # 3. Exportar JSON
    output_file = OUTPUT_DIR / "metrics.json"
    export_json(metrics, output_file)

    # 4. Resumen final
    logger.info(
        "📊 Resumen: %d personajes | Vivos: %d | Muertos: %d",
        metrics["total"],
        metrics["by_status"].get("Alive", 0),
        metrics["by_status"].get("Dead", 0),
    )
    logger.info("✅ Ingesta completada")


if __name__ == "__main__":
    main()

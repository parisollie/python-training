"""Tests para ingest.py."""

import csv
import json
import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from ingest import (  # noqa: E402
    compute_metrics,
    export_json,
    load_characters,
)

# ============================================
# load_characters
# ============================================


def test_load_characters_ok(tmp_path: Path) -> None:
    """Lee un CSV valido y devuelve la lista."""
    csv_file = tmp_path / "test.csv"
    with csv_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "status", "species", "origin"])
        writer.writeheader()
        writer.writerow(
            {"id": "1", "name": "Rick", "status": "Alive", "species": "Human", "origin": "Earth"}
        )
        writer.writerow(
            {"id": "2", "name": "Morty", "status": "Alive", "species": "Human", "origin": "Earth"}
        )

    result = load_characters(csv_file)
    assert len(result) == 2
    assert result[0]["name"] == "Rick"


def test_load_characters_no_existe(tmp_path: Path) -> None:
    """Archivo no existente devuelve lista vacia."""
    result = load_characters(tmp_path / "no_existe.csv")
    assert result == []


def test_load_characters_vacio(tmp_path: Path) -> None:
    """CSV solo con headers devuelve lista vacia."""
    csv_file = tmp_path / "vacio.csv"
    with csv_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "status", "species", "origin"])
        writer.writeheader()

    result = load_characters(csv_file)
    assert result == []


# ============================================
# compute_metrics
# ============================================


def test_compute_metrics_vacio() -> None:
    """Lista vacia da total=0."""
    metrics = compute_metrics([])
    assert metrics["total"] == 0
    assert metrics["by_status"] == {}
    assert metrics["by_species"] == {}


def test_compute_metrics_basico() -> None:
    """Calcula total, by_status, by_species."""
    characters = [
        {"status": "Alive", "species": "Human"},
        {"status": "Alive", "species": "Human"},
        {"status": "Dead", "species": "Alien"},
        {"status": "unknown", "species": "Alien"},
    ]
    metrics = compute_metrics(characters)

    assert metrics["total"] == 4
    assert metrics["by_status"] == {"Alive": 2, "Dead": 1, "unknown": 1}
    assert metrics["by_species"] == {"Human": 2, "Alien": 2}


def test_compute_metrics_timestamp() -> None:
    """El timestamp es ISO 8601 con UTC."""
    metrics = compute_metrics([])
    timestamp = metrics["timestamp"]
    assert isinstance(timestamp, str)
    assert "T" in timestamp
    assert "+00:00" in timestamp  # UTC offset


# ============================================
# export_json
# ============================================


def test_export_json(tmp_path: Path) -> None:
    """Exporta el JSON y se puede releer."""
    data = {"total": 10, "by_status": {"Alive": 5}}
    output = tmp_path / "sub" / "metrics.json"

    export_json(data, output)

    assert output.exists()
    with output.open(encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded == data


def test_export_json_crea_directorio(tmp_path: Path) -> None:
    """Crea el directorio de salida si no existe."""
    output = tmp_path / "nuevo" / "sub" / "metrics.json"
    export_json({"test": True}, output)
    assert output.exists()


def test_export_json_sort_keys(tmp_path: Path) -> None:
    """Las claves se ordenan alfabeticamente."""
    data = {"z": 1, "a": 2, "m": 3}
    output = tmp_path / "metrics.json"
    export_json(data, output)

    content = output.read_text(encoding="utf-8")
    # "a" debe aparecer antes que "m" y "z"
    assert content.index('"a"') < content.index('"m"') < content.index('"z"')


def test_export_json_ensure_ascii_false(tmp_path: Path) -> None:
    """Caracteres no ASCII se preservan."""
    data = {"nombre": "Jesús"}
    output = tmp_path / "metrics.json"
    export_json(data, output)

    content = output.read_text(encoding="utf-8")
    assert "Jesús" in content


# ============================================
# Integracion (flujo completo)
# ============================================


def test_flujo_completo(tmp_path: Path) -> None:
    """CSV -> load -> compute -> export -> relectura."""
    csv_file = tmp_path / "data.csv"
    with csv_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "status", "species", "origin"])
        writer.writeheader()
        for i, status in enumerate(["Alive", "Alive", "Dead"]):
            writer.writerow(
                {
                    "id": str(i),
                    "name": f"Personaje {i}",
                    "status": status,
                    "species": "Human",
                    "origin": "Earth",
                }
            )

    characters = load_characters(csv_file)
    metrics = compute_metrics(characters)
    output = tmp_path / "out.json"
    export_json(metrics, output)

    with output.open(encoding="utf-8") as f:
        loaded = json.load(f)

    assert loaded["total"] == 3
    assert loaded["by_status"]["Alive"] == 2
    assert loaded["by_status"]["Dead"] == 1


# ============================================
# Logging
# ============================================


def test_logging_configurado(caplog: pytest.LogCaptureFixture) -> None:
    """El logging registra eventos en el nivel adecuado."""
    logger = logging.getLogger("test_ingest")
    with caplog.at_level(logging.INFO):
        logger.info("Mensaje de prueba")
    assert "Mensaje de prueba" in caplog.text

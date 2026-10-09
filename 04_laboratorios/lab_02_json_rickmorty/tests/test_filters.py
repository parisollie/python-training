"""Tests para filter_by_status y count_by_species."""

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import count_by_species, filter_by_status  # noqa: E402

# Fixtures con datos de prueba
SAMPLE: list[dict[str, Any]] = [
    {"name": "Rick", "status": "Alive", "species": "Human"},
    {"name": "Morty", "status": "Alive", "species": "Human"},
    {"name": "Birdperson", "status": "Dead", "species": "Alien"},
    {"name": "Squanchy", "status": "unknown", "species": "Alien"},
]


def test_filter_by_status_alive() -> None:
    result = filter_by_status(SAMPLE, "Alive")
    assert len(result) == 2
    assert all(c["status"] == "Alive" for c in result)


def test_filter_by_status_dead() -> None:
    result = filter_by_status(SAMPLE, "Dead")
    assert len(result) == 1
    assert result[0]["name"] == "Birdperson"


def test_filter_by_status_unknown() -> None:
    result = filter_by_status(SAMPLE, "unknown")
    assert len(result) == 1
    assert result[0]["name"] == "Squanchy"


def test_filter_by_status_case_insensitive() -> None:
    """'alive' y 'ALIVE' deben devolver lo mismo que 'Alive'."""
    assert filter_by_status(SAMPLE, "alive") == filter_by_status(SAMPLE, "ALIVE")
    assert len(filter_by_status(SAMPLE, "alive")) == 2


def test_filter_by_status_no_match() -> None:
    result = filter_by_status(SAMPLE, "Zombie")
    assert result == []


def test_count_by_species() -> None:
    counts = count_by_species(SAMPLE)
    assert counts["Human"] == 2
    assert counts["Alien"] == 2


def test_count_by_species_order() -> None:
    """El diccionario debe venir ordenado de mayor a menor."""
    counts = count_by_species(SAMPLE)
    values = list(counts.values())
    assert values == sorted(values, reverse=True)


def test_count_by_species_empty() -> None:
    assert count_by_species([]) == {}

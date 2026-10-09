"""Tests para la funcion classify_character (pattern matching)."""

import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import classify_character  # noqa: E402


@pytest.mark.parametrize(
    "character,expected_contains",
    [
        ({"status": "Alive", "species": "Human"}, "Vivo humano"),
        ({"status": "Alive", "species": "Alien"}, "Vivo alien"),
        ({"status": "Dead", "species": "Human"}, "Muerto humano"),
        ({"status": "Dead", "species": "Alien"}, "Muerto alien"),
        ({"status": "Alive", "species": "Robot"}, "Vivo (otra especie)"),
        ({"status": "Dead", "species": "Robot"}, "Muerto (otra especie)"),
        ({"status": "unknown", "species": "Human"}, "Sin clasificar"),
        ({"status": "unknown", "species": "Alien"}, "Sin clasificar"),
        ({}, "Sin clasificar"),
    ],
)
def test_classify_character_cases(character: dict[str, Any], expected_contains: str) -> None:
    """Cada combinacion estado+especie devuelve la clasificacion correcta."""
    result = classify_character(character)
    assert expected_contains in result


def test_classify_character_case_insensitive() -> None:
    """Mayusculas/minusculas no importan."""
    upper = classify_character({"status": "ALIVE", "species": "HUMAN"})
    lower = classify_character({"status": "alive", "species": "human"})
    assert upper == lower

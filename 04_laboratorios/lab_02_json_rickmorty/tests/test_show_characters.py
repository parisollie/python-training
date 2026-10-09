"""Tests para la funcion show_characters."""

import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import show_characters  # noqa: E402


def test_show_characters_empty(capsys: pytest.CaptureFixture[str]) -> None:
    """Con lista vacia, muestra advertencia y no falla."""
    show_characters([])
    captured = capsys.readouterr()
    assert "No hay personajes" in captured.out


def test_show_characters_prints_table(capsys: pytest.CaptureFixture[str]) -> None:
    """Con personajes, imprime el total y una tabla."""
    characters: list[dict[str, Any]] = [
        {"id": 1, "name": "Rick", "status": "Alive", "species": "Human"},
        {"id": 2, "name": "Morty", "status": "Alive", "species": "Human"},
    ]
    show_characters(characters)
    captured = capsys.readouterr()
    assert "Total de personajes: 2" in captured.out
    assert "Rick" in captured.out
    assert "Morty" in captured.out


def test_show_characters_missing_fields(capsys: pytest.CaptureFixture[str]) -> None:
    """Personajes sin campos completos usan valores por defecto."""
    characters: list[dict[str, Any]] = [{"id": 99}]
    show_characters(characters)
    captured = capsys.readouterr()
    assert "Desconocido" in captured.out

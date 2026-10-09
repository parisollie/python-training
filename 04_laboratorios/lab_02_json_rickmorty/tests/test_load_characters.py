"""Tests para la funcion load_characters."""

import json

# Importamos las funciones desde main.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import load_characters  # noqa: E402

DATA_FILE = Path(__file__).parent.parent / "data" / "characters.json"


def test_load_characters_ok() -> None:
    """Carga el archivo real y devuelve 20 personajes."""
    characters = load_characters(DATA_FILE)
    assert len(characters) == 20
    assert characters[0]["name"] == "Rick Sanchez"


def test_load_characters_file_not_found() -> None:
    """Archivo no existente devuelve lista vacia."""
    characters = load_characters(Path("no_existe.json"))
    assert characters == []


def test_load_characters_invalid_json(tmp_path: Path) -> None:
    """JSON invalido devuelve lista vacia."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("esto no es json", encoding="utf-8")
    characters = load_characters(bad_file)
    assert characters == []


def test_load_characters_wrong_structure(tmp_path: Path) -> None:
    """JSON sin 'results' devuelve lista vacia."""
    wrong = tmp_path / "wrong.json"
    wrong.write_text(json.dumps({"otra_cosa": []}), encoding="utf-8")
    characters = load_characters(wrong)
    assert characters == []


def test_load_characters_results_not_list(tmp_path: Path) -> None:
    """Si 'results' no es lista, devuelve lista vacia."""
    weird = tmp_path / "weird.json"
    weird.write_text(json.dumps({"results": "no soy lista"}), encoding="utf-8")
    characters = load_characters(weird)
    assert characters == []

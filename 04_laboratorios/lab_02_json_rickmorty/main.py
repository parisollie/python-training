"""Laboratorio 02: Leer y procesar JSON de Rick and Morty.

Este script demuestra:
- Lectura de archivos JSON con manejo de errores
- Uso de estructuras de datos (list, dict)
- Control de flujo (for, if)
- Type hints para claridad
"""

import json
from pathlib import Path
from typing import Any

# Ruta del archivo de datos (relativa al script)
DATA_FILE = Path(__file__).parent / "data" / "characters.json"


def load_characters(path: Path) -> list[dict[str, Any]]:
    """Carga los personajes desde un archivo JSON.

    Args:
        path: Ruta al archivo JSON.

    Returns:
        Lista de diccionarios, uno por personaje. Lista vacía si hay error.

    Raises:
        No lanza excepciones; las maneja internamente y retorna lista vacía.
    """
    try:
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"❌ Error: no se encontró el archivo {path}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error: el archivo no es un JSON válido: {e}")
        return []
    except PermissionError:
        print(f"❌ Error: no hay permisos para leer {path}")
        return []

    # La API de Rick and Morty devuelve {"info": {...}, "results": [...]}
    if not isinstance(data, dict) or "results" not in data:
        print("❌ Error: el JSON no tiene la estructura esperada")
        return []

    results = data["results"]
    if not isinstance(results, list):
        print("❌ Error: 'results' no es una lista")
        return []

    return results


def show_characters(characters: list[dict[str, Any]]) -> None:
    """Muestra los personajes en la terminal.

    Args:
        characters: Lista de diccionarios de personajes.
    """
    if not characters:
        print("⚠️  No hay personajes para mostrar.")
        return

    print(f"\n📋 Total de personajes: {len(characters)}\n")
    print(f"{'ID':<5} {'Nombre':<25} {'Estado':<10} {'Especie':<15}")
    print("-" * 60)

    for char in characters:
        char_id = char.get("id", "?")
        name = char.get("name", "Desconocido")
        status = char.get("status", "?")
        species = char.get("species", "?")
        print(f"{char_id:<5} {name:<25} {status:<10} {species:<15}")


def main() -> None:
    """Punto de entrada del script."""
    print("🚀 Laboratorio 02 — Rick and Morty JSON\n")
    print(f"📁 Leyendo: {DATA_FILE}\n")

    characters = load_characters(DATA_FILE)
    show_characters(characters)


if __name__ == "__main__":
    main()

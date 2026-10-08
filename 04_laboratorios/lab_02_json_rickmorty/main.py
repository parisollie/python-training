"""Laboratorio 02: Leer y procesar JSON de Rick and Morty.

Este script demuestra:
- Lectura de archivos JSON con manejo de errores
- Uso de estructuras de datos (list, dict)
- Control de flujo (for, if)
- Filtros y agregaciones
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


def filter_by_status(characters: list[dict[str, Any]], status: str) -> list[dict[str, Any]]:
    """Filtra los personajes por estado (Alive, Dead, unknown).

    Args:
        characters: Lista completa de personajes.
        status: Estado a filtrar (case-insensitive).

    Returns:
        Lista de personajes cuyo estado coincide.
    """
    target = status.lower()
    return [c for c in characters if c.get("status", "").lower() == target]


def count_by_species(characters: list[dict[str, Any]]) -> dict[str, int]:
    """Cuenta cuántos personajes hay por especie.

    Args:
        characters: Lista de personajes.

    Returns:
        Diccionario {especie: cantidad}, ordenado de mayor a menor.
    """
    counts: dict[str, int] = {}
    for c in characters:
        species = c.get("species", "Desconocida")
        counts[species] = counts.get(species, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def main() -> None:
    """Punto de entrada del script."""
    print("🚀 Laboratorio 02 — Rick and Morty JSON\n")
    print(f"📁 Leyendo: {DATA_FILE}\n")

    characters = load_characters(DATA_FILE)
    show_characters(characters)

    if not characters:
        return

    # Filtros por estado
    print("\n" + "=" * 60)
    print("🔍 Filtros por estado\n")

    alive = filter_by_status(characters, "Alive")
    dead = filter_by_status(characters, "Dead")
    unknown = filter_by_status(characters, "unknown")

    print(f"👥 Vivos:        {len(alive)}")
    print(f"💀 Muertos:      {len(dead)}")
    print(f"❓ Desconocidos: {len(unknown)}")

    # Conteo por especie
    print("\n" + "=" * 60)
    print("📊 Conteo por especie\n")

    species_count = count_by_species(characters)
    for species, count in species_count.items():
        print(f"  {species:<20} {count}")


if __name__ == "__main__":
    main()

"""Tests de la entidad Character."""

from dataclasses import FrozenInstanceError

import pytest
from rickmorty_orders.domain.character import Character, CharacterStatus
from rickmorty_orders.domain.value_objects import CharacterId


@pytest.fixture
def rick() -> Character:
    return Character(
        id=CharacterId(1),
        name="Rick Sanchez",
        species="Human",
        status=CharacterStatus.ALIVE,
        image_url="https://example.com/rick.png",
    )


# ============================================
# Creacion y validaciones
# ============================================


def test_character_creacion(rick: Character) -> None:
    """Character con todos sus campos."""
    assert rick.id.value == 1
    assert rick.name == "Rick Sanchez"
    assert rick.species == "Human"
    assert rick.status == CharacterStatus.ALIVE
    assert rick.image_url == "https://example.com/rick.png"


def test_character_nombre_vacio_falla() -> None:
    """Nombre vacio lanza."""
    with pytest.raises(ValueError, match="nombre"):
        Character(
            id=CharacterId(1),
            name="",
            species="Human",
            status=CharacterStatus.ALIVE,
        )


def test_character_especie_vacia_falla() -> None:
    """Especie vacia lanza."""
    with pytest.raises(ValueError, match="especie"):
        Character(
            id=CharacterId(1),
            name="Rick",
            species="",
            status=CharacterStatus.ALIVE,
        )


# ============================================
# is_alive
# ============================================


def test_character_alive_es_alive(rick: Character) -> None:
    """Character ALIVE -> is_alive True."""
    assert rick.is_alive is True


def test_character_dead_no_es_alive() -> None:
    """Character DEAD -> is_alive False."""
    char = Character(
        id=CharacterId(2),
        name="Birdperson",
        species="Alien",
        status=CharacterStatus.DEAD,
    )
    assert char.is_alive is False


def test_character_unknown_no_es_alive() -> None:
    """Character UNKNOWN -> is_alive False."""
    char = Character(
        id=CharacterId(3),
        name="Misterio",
        species="?",
        status=CharacterStatus.UNKNOWN,
    )
    assert char.is_alive is False


# ============================================
# Igualdad por valor
# ============================================


def test_character_igualdad_por_valor() -> None:
    """Dos Character iguales (mismos campos)."""
    c1 = Character(
        id=CharacterId(1),
        name="Rick",
        species="Human",
        status=CharacterStatus.ALIVE,
    )
    c2 = Character(
        id=CharacterId(1),
        name="Rick",
        species="Human",
        status=CharacterStatus.ALIVE,
    )
    assert c1 == c2


def test_character_distinto_por_status() -> None:
    """Mismo id, distinto status -> distintos."""
    c1 = Character(
        id=CharacterId(1),
        name="Rick",
        species="Human",
        status=CharacterStatus.ALIVE,
    )
    c2 = Character(
        id=CharacterId(1),
        name="Rick",
        species="Human",
        status=CharacterStatus.DEAD,
    )
    assert c1 != c2


# ============================================
# Inmutabilidad
# ============================================


def test_character_inmutable(rick: Character) -> None:
    """Character es inmutable."""
    with pytest.raises(FrozenInstanceError):
        rick.name = "Otro"  # type: ignore[misc]


# ============================================
# CharacterStatus (StrEnum)
# ============================================


def test_character_status_valores() -> None:
    """CharacterStatus tiene los valores esperados."""
    assert CharacterStatus.ALIVE.value == "Alive"
    assert CharacterStatus.DEAD.value == "Dead"
    assert CharacterStatus.UNKNOWN.value == "unknown"

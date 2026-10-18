"""Tests de contrato para CharacterRepository.

Adaptadores probados:
- InMemoryCharacterRepository
- RickMortyApiClient (con httpx.MockTransport)

Verifica que ambos se comportan igual.
"""

import httpx
import pytest
from rickmorty_orders.domain.character import CharacterStatus
from rickmorty_orders.domain.ports import CharacterRepository
from rickmorty_orders.domain.value_objects import CharacterId
from rickmorty_orders.infrastructure.in_memory import InMemoryCharacterRepository
from rickmorty_orders.infrastructure.rickmorty_client import RickMortyApiClient

# ============================================
# Fixtures
# ============================================


@pytest.fixture
def memory_chars_contract() -> CharacterRepository:
    """Adaptador en memoria con 2 personajes."""
    from rickmorty_orders.domain.character import Character

    repo = InMemoryCharacterRepository()
    repo.add(
        Character(
            id=CharacterId(1),
            name="Rick Sanchez",
            species="Human",
            status=CharacterStatus.ALIVE,
        )
    )
    repo.add(
        Character(
            id=CharacterId(2),
            name="Morty Smith",
            species="Human",
            status=CharacterStatus.ALIVE,
        )
    )
    return repo


@pytest.fixture
def http_chars_contract() -> CharacterRepository:
    """Adaptador HTTP con MockTransport."""

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        # /api/character/1 -> dict
        # /api/character/1,2 -> list
        parts = path.rstrip("/").split("/")
        ids_part = parts[-1]

        if "," in ids_part:
            # Batch: ids validos son <= 100. El 999 NO existe.
            ids = [int(i) for i in ids_part.split(",")]
            valid_ids = [i for i in ids if i <= 100]
            if not valid_ids:
                return httpx.Response(404)
            return httpx.Response(
                200,
                json=[
                    {"id": i, "name": f"Char {i}", "species": "Human", "status": "Alive"}
                    for i in valid_ids
                ],
            )

        char_id = int(ids_part)
        if char_id > 100:
            return httpx.Response(404)
        return httpx.Response(
            200,
            json={
                "id": char_id,
                "name": f"Char {char_id}",
                "species": "Human",
                "status": "Alive",
            },
        )

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    api = RickMortyApiClient(client=client)
    return api


@pytest.fixture(params=["memory", "http"])
def chars_repo(request: pytest.FixtureRequest) -> CharacterRepository:
    """Devuelve cada implementacion de CharacterRepository."""
    if request.param == "memory":
        return request.getfixturevalue("memory_chars_contract")  # type: ignore[no-any-return]
    return request.getfixturevalue("http_chars_contract")  # type: ignore[no-any-return]


# ============================================
# Tests de contrato (LSP)
# ============================================


def test_find_by_id_existente(chars_repo: CharacterRepository) -> None:
    """find_by_id devuelve el personaje."""
    char = chars_repo.find_by_id(CharacterId(1))
    assert char is not None
    assert char.id.value == 1


def test_find_by_id_inexistente(chars_repo: CharacterRepository) -> None:
    """find_by_id de id inexistente devuelve None."""
    # En HTTP, id > 100 da 404. En memory, no existe.
    char = chars_repo.find_by_id(CharacterId(999))
    assert char is None


def test_list_by_ids_vacio(chars_repo: CharacterRepository) -> None:
    """list_by_ids([]) devuelve []."""
    assert chars_repo.list_by_ids([]) == []


def test_list_by_ids(chars_repo: CharacterRepository) -> None:
    """list_by_ids devuelve los personajes existentes."""
    chars = chars_repo.list_by_ids([CharacterId(1), CharacterId(2)])
    assert len(chars) == 2
    assert {c.id.value for c in chars} == {1, 2}


def test_list_by_ids_parcial(chars_repo: CharacterRepository) -> None:
    """list_by_ids ignora los ids que no existen."""
    chars = chars_repo.list_by_ids([CharacterId(1), CharacterId(999)])
    # Solo devuelve el que existe (id 1)
    assert len(chars) >= 1
    assert any(c.id.value == 1 for c in chars)
    # No debe incluir el 999
    assert all(c.id.value != 999 for c in chars)

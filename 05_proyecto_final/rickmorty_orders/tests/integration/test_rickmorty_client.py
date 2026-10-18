"""Tests de integracion del cliente HTTP de Rick and Morty.

Usa httpx.MockTransport para simular la API sin red real.

Verifica:
- Timeouts y reintentos
- Manejo de 4xx vs 5xx
- Fallback a requests individuales
- Parsing del JSON
"""

import httpx
import pytest
from rickmorty_orders.domain.character import CharacterStatus
from rickmorty_orders.domain.errors import CharacterServiceError
from rickmorty_orders.domain.value_objects import CharacterId
from rickmorty_orders.infrastructure.rickmorty_client import RickMortyApiClient

# ============================================
# Helpers
# ============================================


def make_client(handler: object, max_attempts: int = 3) -> RickMortyApiClient:
    """Crea un RickMortyApiClient con MockTransport."""
    transport = httpx.MockTransport(handler)  # type: ignore[arg-type]
    client = httpx.Client(transport=transport)
    return RickMortyApiClient(client=client, max_attempts=max_attempts)


# ============================================
# find_by_id
# ============================================


def test_find_by_id_ok() -> None:
    """find_by_id parsea el JSON correctamente."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": 1,
                "name": "Rick Sanchez",
                "species": "Human",
                "status": "Alive",
                "image": "https://example.com/rick.png",
            },
        )

    client = make_client(handler)
    char = client.find_by_id(CharacterId(1))
    assert char is not None
    assert char.name == "Rick Sanchez"
    assert char.species == "Human"
    assert char.status == CharacterStatus.ALIVE
    assert char.is_alive is True


def test_find_by_id_404_devuelve_none() -> None:
    """Un 404 devuelve None (no lanza)."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    client = make_client(handler)
    char = client.find_by_id(CharacterId(999))
    assert char is None


def test_find_by_id_500_reintenta_y_falla() -> None:
    """Un 500 reintenta hasta max_attempts y luego lanza."""
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(500)

    client = make_client(handler, max_attempts=3)
    with pytest.raises(CharacterServiceError):
        client.find_by_id(CharacterId(1))
    assert calls["n"] == 3


def test_find_by_id_500_y_luego_200() -> None:
    """Falla 2 veces y a la tercera devuelve."""
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(500)
        return httpx.Response(
            200,
            json={
                "id": 1,
                "name": "Rick",
                "species": "Human",
                "status": "Alive",
            },
        )

    client = make_client(handler, max_attempts=3)
    char = client.find_by_id(CharacterId(1))
    assert char is not None
    assert char.name == "Rick"
    assert calls["n"] == 3


# ============================================
# list_by_ids
# ============================================


def test_list_by_ids_batch() -> None:
    """list_by_ids con batch devuelve lista."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[
                {"id": 1, "name": "Rick", "species": "Human", "status": "Alive"},
                {"id": 2, "name": "Morty", "species": "Human", "status": "Alive"},
            ],
        )

    client = make_client(handler)
    chars = client.list_by_ids([CharacterId(1), CharacterId(2)])
    assert len(chars) == 2


def test_list_by_ids_un_solo_elemento_dict() -> None:
    """list_by_ids con 1 elemento devuelve dict (no list)."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"id": 1, "name": "Rick", "species": "Human", "status": "Alive"},
        )

    client = make_client(handler)
    chars = client.list_by_ids([CharacterId(1)])
    assert len(chars) == 1


def test_list_by_ids_fallback_individual() -> None:
    """Si el batch falla, hace fallback a individuales."""
    calls = {"batch": 0, "individual": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if "," in path:
            calls["batch"] += 1
            return httpx.Response(500)  # batch falla
        calls["individual"] += 1
        # Individuales funcionan
        parts = path.rstrip("/").split("/")
        char_id = int(parts[-1])
        return httpx.Response(
            200,
            json={
                "id": char_id,
                "name": f"Char {char_id}",
                "species": "Human",
                "status": "Alive",
            },
        )

    client = make_client(handler, max_attempts=1)
    chars = client.list_by_ids([CharacterId(1), CharacterId(2)])
    assert len(chars) == 2
    assert calls["individual"] == 2


def test_list_by_ids_vacio() -> None:
    """list_by_ids([]) devuelve [] sin llamar a la API."""
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200, json=[])

    client = make_client(handler)
    chars = client.list_by_ids([])
    assert chars == []
    assert calls["n"] == 0


# ============================================
# Context manager y close
# ============================================


def test_context_manager() -> None:
    """Se puede usar con with."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"id": 1, "name": "Rick", "species": "Human", "status": "Alive"},
        )

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    api = RickMortyApiClient(client=client)

    with api:
        char = api.find_by_id(CharacterId(1))
        assert char is not None

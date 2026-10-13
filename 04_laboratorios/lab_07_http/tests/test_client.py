"""Tests para client.py usando httpx.MockTransport (sin red real)."""

import json
import sys
from pathlib import Path
from typing import Any

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from client import RickMortyClient  # noqa: E402

# ============================================
# Helpers
# ============================================


def make_client_with_handler(
    handler: Any,
    max_attempts: int = 3,
    base_delay: float = 0.01,
) -> RickMortyClient:
    """Crea un RickMortyClient con un MockTransport."""
    client = RickMortyClient(max_attempts=max_attempts, base_delay=base_delay)
    client._client.close()
    client._client = httpx.Client(transport=httpx.MockTransport(handler))
    return client


# ============================================
# get_character
# ============================================


def test_get_character_ok() -> None:
    """Un GET exitoso devuelve el dict del personaje."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/character/1"
        return httpx.Response(200, json={"id": 1, "name": "Rick"})

    client = make_client_with_handler(handler)
    data = client.get_character(1)
    client.close()

    assert data["name"] == "Rick"


def test_get_character_404_no_reintenta() -> None:
    """Un 404 no se reintenta (falla inmediato)."""
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(404, json={"error": "Not found"})

    client = make_client_with_handler(handler, max_attempts=5)
    with pytest.raises(httpx.HTTPStatusError):
        client.get_character(999)
    client.close()

    # Solo un intento: los 4xx no se reintentan
    assert calls["n"] == 1


def test_get_character_500_reintenta() -> None:
    """Un 500 se reintenta hasta max_attempts."""
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(500, json={"error": "Server error"})

    client = make_client_with_handler(handler, max_attempts=3)
    with pytest.raises(httpx.HTTPStatusError):
        client.get_character(1)
    client.close()

    assert calls["n"] == 3


def test_get_character_500_y_luego_200() -> None:
    """Falla 2 veces y a la tercera funciona."""
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(500)
        return httpx.Response(200, json={"id": 1, "name": "Rick"})

    client = make_client_with_handler(handler, max_attempts=3)
    data = client.get_character(1)
    client.close()

    assert data["name"] == "Rick"
    assert calls["n"] == 3


def test_get_character_429_reintenta() -> None:
    """429 (rate limit) SI se reintenta."""
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] < 2:
            return httpx.Response(429)
        return httpx.Response(200, json={"id": 1, "name": "Rick"})

    client = make_client_with_handler(handler, max_attempts=3)
    data = client.get_character(1)
    client.close()

    assert data["name"] == "Rick"
    assert calls["n"] == 2


# ============================================
# get_all_characters (paginacion)
# ============================================


def test_get_all_characters_una_pagina() -> None:
    """Una sola pagina devuelve 20 personajes."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "info": {"next": None, "count": 20},
                "results": [{"id": i, "name": f"P{i}"} for i in range(1, 21)],
            },
        )

    client = make_client_with_handler(handler)
    chars = client.get_all_characters()
    client.close()

    assert len(chars) == 20
    assert chars[0]["name"] == "P1"


def test_get_all_characters_varias_paginas() -> None:
    """Recorre multiples paginas usando el campo 'next'."""
    base = "https://rickandmortyapi.com/api/character"

    def handler(request: httpx.Request) -> httpx.Response:
        page = request.url.params.get("page")
        if page is None or page == "1":
            return httpx.Response(
                200,
                json={
                    "info": {"next": f"{base}?page=2", "count": 30},
                    "results": [{"id": i} for i in range(1, 21)],
                },
            )
        if page == "2":
            return httpx.Response(
                200,
                json={
                    "info": {"next": None, "count": 30},
                    "results": [{"id": i} for i in range(21, 31)],
                },
            )
        return httpx.Response(404)

    client = make_client_with_handler(handler)
    chars = client.get_all_characters()
    client.close()

    assert len(chars) == 30


def test_get_all_characters_max_pages() -> None:
    """max_pages limita el recorrido."""
    base = "https://rickandmortyapi.com/api/character"

    def handler(request: httpx.Request) -> httpx.Response:
        # Siempre devuelve "next" para simular muchas paginas
        return httpx.Response(
            200,
            json={
                "info": {"next": f"{base}?page=999", "count": 1000},
                "results": [{"id": 1}],
            },
        )

    client = make_client_with_handler(handler)
    chars = client.get_all_characters(max_pages=2)
    client.close()

    assert len(chars) == 2  # solo 2 paginas


# ============================================
# stream_to_file
# ============================================


def test_stream_to_file(tmp_path: Path) -> None:
    """Descarga un payload a disco."""
    payload = {"message": "hola mundo" * 1000}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    client = make_client_with_handler(handler)
    output = tmp_path / "download.json"
    size = client.stream_to_file("/character/1", output)
    client.close()

    assert output.exists()
    assert size > 0
    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded == payload


def test_stream_to_file_crea_directorio(tmp_path: Path) -> None:
    """Crea el directorio de salida si no existe."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"data")

    client = make_client_with_handler(handler)
    output = tmp_path / "sub" / "nested" / "file.bin"
    client.stream_to_file("/x", output)
    client.close()

    assert output.exists()


# ============================================
# Context manager
# ============================================


def test_context_manager() -> None:
    """Se puede usar con with."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"id": 1})

    original = RickMortyClient.__init__

    def patched_init(self: RickMortyClient, *args: Any, **kwargs: Any) -> None:
        original(self, *args, **kwargs)
        self._client.close()
        self._client = httpx.Client(transport=httpx.MockTransport(handler))

    RickMortyClient.__init__ = patched_init  # type: ignore[method-assign]
    try:
        with RickMortyClient() as client:
            assert client.get_character(1) == {"id": 1}
    finally:
        RickMortyClient.__init__ = original  # type: ignore[method-assign]

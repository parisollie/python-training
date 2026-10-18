"""Adaptador HTTP del puerto CharacterRepository.

Consume la API publica de Rick and Morty (https://rickandmortyapi.com/api).

Demuestra:
- httpx.Client con timeouts
- Reintentos con backoff exponencial
- Traduccion de JSON a entidad Character
- Manejo de errores (404, 5xx, timeout)
"""

import logging
import time
from typing import Any, cast

import httpx

from rickmorty_orders.domain.character import Character, CharacterStatus
from rickmorty_orders.domain.errors import CharacterServiceError
from rickmorty_orders.domain.value_objects import CharacterId

logger = logging.getLogger(__name__)


class RickMortyApiClient:
    """Cliente HTTP para la API de Rick and Morty.

    Cumple el puerto CharacterRepository del dominio.
    """

    def __init__(
        self,
        base_url: str = "https://rickandmortyapi.com/api",
        timeout: float = 10.0,
        max_attempts: int = 3,
        base_delay: float = 0.5,
        client: httpx.Client | None = None,
    ) -> None:
        """Inicializa el cliente.

        Args:
            base_url: URL base de la API.
            timeout: timeout por request (segundos).
            max_attempts: intentos maximos por request.
            base_delay: delay inicial del backoff (segundos).
            client: httpx.Client opcional (para tests).
        """
        self.base_url = base_url.rstrip("/")
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self._owns_client = client is None
        self._client = client or httpx.Client(
            timeout=httpx.Timeout(timeout, connect=5.0),
            headers={"User-Agent": "rickmorty-orders/0.1.0"},
        )

    def close(self) -> None:
        """Cierra el cliente si fue creado por esta clase."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "RickMortyApiClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _request(self, path: str) -> dict[str, Any] | list[dict[str, Any]]:
        """Hace un GET con reintentos.

        Args:
            path: ruta relativa (ej: /character/1 o /character/1,2).

        Returns:
            JSON parseado como dict (1 resultado) o list (varios).

        Raises:
            CharacterServiceError: si el personaje no existe o hay error.
        """
        url = f"{self.base_url}{path}"
        last_exc: Exception | None = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self._client.get(url)
                if response.status_code == 404:
                    raise CharacterServiceError(f"Personaje no encontrado: {path}")
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, dict | list):
                    raise CharacterServiceError(
                        f"Respuesta inesperada de la API: {type(data).__name__}"
                    )
                return data
            except httpx.HTTPStatusError as e:
                # 4xx (excepto 429): no reintentar
                if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                    raise CharacterServiceError(
                        f"Error HTTP {e.response.status_code}: {url}"
                    ) from e
                last_exc = e
            except httpx.RequestError as e:
                last_exc = e
            except CharacterServiceError:
                raise

            if attempt < self.max_attempts:
                delay = self.base_delay * (2 ** (attempt - 1))
                logger.warning(
                    "Intento %d/%d fallo (%s). Reintentando en %.2fs",
                    attempt,
                    self.max_attempts,
                    last_exc,
                    delay,
                )
                time.sleep(delay)

        raise CharacterServiceError(
            f"Fallaron los {self.max_attempts} intentos para {url}: {last_exc}"
        )

    def _json_to_character(self, data: dict[str, Any]) -> Character:
        """Convierte el JSON de la API a la entidad Character."""
        return Character(
            id=CharacterId(int(data["id"])),
            name=str(data["name"]),
            species=str(data["species"]),
            status=CharacterStatus(str(data["status"])),
            image_url=str(data.get("image", "")),
        )

    # ============================================
    # Implementacion del puerto CharacterRepository
    # ============================================

    def find_by_id(self, character_id: CharacterId) -> Character | None:
        """Busca un personaje por id.

        Returns:
            Character si existe, None si no.
        """
        try:
            data = self._request(f"/character/{character_id.value}")
        except CharacterServiceError as e:
            if "no encontrado" in str(e).lower():
                return None
            raise
        # find_by_id siempre pide 1 personaje -> _request devuelve dict.
        # Cast porque mypy no narrow bien dict|list[dict] tras try/except.
        return self._json_to_character(cast(dict[str, Any], data))

    def list_by_ids(self, character_ids: list[CharacterId]) -> list[Character]:
        """Busca multiples personajes por id.

        La API soporta /character/1,2,3 para batch. Si falla, cae a uno por uno.
        """
        if not character_ids:
            return []
        ids_str = ",".join(str(c.value) for c in character_ids)
        try:
            data = self._request(f"/character/{ids_str}")
            # Respuesta multiple: {"id": ..., ...} si es 1, o lista si son varios
            # Narrow: si es dict -> 1 elemento; si es list -> varios.
            if isinstance(data, dict):
                return [self._json_to_character(data)]
            return [self._json_to_character(item) for item in data]
        except CharacterServiceError:
            # Fallback: uno por uno (ignorando los que no existen)
            logger.warning("Fallback a requests individuales")
            results: list[Character] = []
            for cid in character_ids:
                try:
                    char = self.find_by_id(cid)
                except CharacterServiceError:
                    continue
                if char is not None:
                    results.append(char)
            return results

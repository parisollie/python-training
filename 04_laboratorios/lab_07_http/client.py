"""Cliente HTTP para la API de Rick and Morty.

Demuestra:
- httpx.Client con timeouts configurables
- Reintentos con backoff exponencial
- Manejo robusto de errores HTTP
- Paginacion para recorrer todos los resultados
- Streaming de respuestas grandes a disco
"""

import logging
import time
from pathlib import Path
from typing import Any

import httpx

BASE_URL = "https://rickandmortyapi.com/api"

logger = logging.getLogger(__name__)


class RickMortyClient:
    """Cliente HTTP con reintentos y timeouts para la API de Rick and Morty."""

    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: float = 10.0,
        max_attempts: int = 3,
        base_delay: float = 0.5,
    ) -> None:
        """Inicializa el cliente.

        Args:
            base_url: URL base de la API.
            timeout: Timeout en segundos (aplica a toda la operacion).
            max_attempts: Numero maximo de intentos por request.
            base_delay: Segundos de espera inicial (se duplica cada intento).
        """
        self.base_url = base_url.rstrip("/")
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self._client = httpx.Client(
            timeout=httpx.Timeout(timeout, connect=5.0),
            headers={"User-Agent": "python-training/0.1.0"},
        )

    def __enter__(self) -> "RickMortyClient":
        """Soporta el protocolo de context manager."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Cierra el cliente al salir del with."""
        self._client.close()

    def close(self) -> None:
        """Cierra el cliente manualmente."""
        self._client.close()

    def _request_with_retry(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Hace una request con reintentos y backoff exponencial.

        Args:
            method: Metodo HTTP (GET, POST, etc.).
            url: URL completa.
            **kwargs: Argumentos extra para httpx.

        Returns:
            Response exitosa.

        Raises:
            httpx.HTTPError: Si se agotan los reintentos.
        """
        last_exception: Exception | None = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self._client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                last_exception = e
                # No reintentar errores 4xx (excepto 429)
                if isinstance(e, httpx.HTTPStatusError):
                    status = e.response.status_code
                    if 400 <= status < 500 and status != 429:
                        logger.warning("Error %d no reintentable: %s", status, url)
                        raise

                if attempt < self.max_attempts:
                    delay = self.base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        "Intento %d/%d fallo (%s). Reintentando en %.2fs",
                        attempt,
                        self.max_attempts,
                        e,
                        delay,
                    )
                    time.sleep(delay)
                else:
                    logger.error("Se agotaron los %d intentos", self.max_attempts)

        if last_exception is None:
            raise RuntimeError("unreachable")
        raise last_exception

    def get_character(self, character_id: int) -> dict[str, Any]:
        """Obtiene un personaje por ID.

        Args:
            character_id: ID del personaje.

        Returns:
            Diccionario con los datos del personaje.

        Raises:
            httpx.HTTPError: Si falla tras los reintentos.
        """
        url = f"{self.base_url}/character/{character_id}"
        response = self._request_with_retry("GET", url)
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError(f"Se esperaba dict, se recibio {type(data).__name__}")
        return data

    def get_all_characters(self, max_pages: int | None = None) -> list[dict[str, Any]]:
        """Recorre todas las paginas y devuelve todos los personajes.

        Args:
            max_pages: Limite de paginas a recorrer (None = todas).

        Returns:
            Lista con todos los personajes.
        """
        all_characters: list[dict[str, Any]] = []
        url: str | None = f"{self.base_url}/character"
        page = 0

        while url is not None:
            page += 1
            if max_pages is not None and page > max_pages:
                logger.info("Limite de %d paginas alcanzado", max_pages)
                break

            response = self._request_with_retry("GET", url)
            data = response.json()

            all_characters.extend(data.get("results", []))
            logger.debug("Pagina %d: %d personajes", page, len(data.get("results", [])))

            info = data.get("info", {})
            url = info.get("next")

        logger.info("Total: %d personajes en %d paginas", len(all_characters), page)
        return all_characters

    def stream_to_file(self, path: str, output: Path) -> int:
        """Descarga una respuesta por streaming a disco.

        Args:
            path: Ruta relativa de la API (ej: "/character/1").
            output: Ruta donde guardar el archivo.

        Returns:
            Tamano del archivo descargado en bytes.
        """
        url = f"{self.base_url}{path}"
        output.parent.mkdir(parents=True, exist_ok=True)

        total = 0
        with self._client.stream("GET", url) as response:
            response.raise_for_status()
            with output.open("wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)
                    total += len(chunk)

        logger.info("Descargado %s (%d bytes) a %s", url, total, output)
        return total

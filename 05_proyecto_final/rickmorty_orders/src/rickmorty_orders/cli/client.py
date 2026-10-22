"""Cliente HTTP del CLI.

Habla con la API del proyecto final (FastAPI) usando httpx.
"""

from typing import Any

import httpx


class ApiClient:
    """Cliente HTTP hacia la API de rickmorty_orders."""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        response = self._client.request(method, f"{self.base_url}{path}", **kwargs)
        return response

    def list_orders(self, customer_email: str | None = None) -> list[dict[str, Any]]:
        params = {}
        if customer_email:
            params["customer_email"] = customer_email
        response = self._request("GET", "/orders/", params=params)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            return []
        return data

    def get_order(self, order_id: str) -> dict[str, Any] | None:
        response = self._request("GET", f"/orders/{order_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            return None
        return data

    def create_order(self, customer_email: str, items: list[dict[str, Any]]) -> dict[str, Any]:
        response = self._request(
            "POST",
            "/orders/",
            json={"customer_email": customer_email, "items": items},
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError("Respuesta inesperada al crear orden")
        return data

    def confirm_order(self, order_id: str) -> dict[str, Any]:
        response = self._request("PATCH", f"/orders/{order_id}/confirm")
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError("Respuesta inesperada al confirmar orden")
        return data

    def cancel_order(self, order_id: str, reason: str = "") -> dict[str, Any]:
        params = {"reason": reason} if reason else {}
        response = self._request("PATCH", f"/orders/{order_id}/cancel", params=params)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError("Respuesta inesperada al cancelar orden")
        return data

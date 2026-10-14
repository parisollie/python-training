"""Fixtures compartidas para tests del carrito."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from cart import Cart, InMemoryUserService  # noqa: E402


@pytest.fixture
def cart() -> Cart:
    """Carrito vacio sin usuario."""
    return Cart()


@pytest.fixture
def premium_service() -> InMemoryUserService:
    """Servicio con user-1 marcado como premium."""
    return InMemoryUserService(premium_users={"user-1"})


@pytest.fixture
def premium_cart(premium_service: InMemoryUserService) -> Cart:
    """Carrito de user-1 (premium)."""
    return Cart(user_id="user-1", user_service=premium_service)

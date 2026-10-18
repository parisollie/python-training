"""Tests E2E de la API de orders.

Usa TestClient de FastAPI con dependency_overrides para:
- DB SQLite en memoria (no la real)
- Cliente HTTP mockeado (no la API real)

Flujo completo: HTTP -> router -> caso de uso -> dominio -> repo (sqlite) -> response.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from rickmorty_orders.domain.character import CharacterStatus
from rickmorty_orders.infrastructure.api_app import app
from rickmorty_orders.infrastructure.dependencies import (
    get_character_client,
    get_order_repository,
)
from rickmorty_orders.infrastructure.in_memory import (
    InMemoryCharacterRepository,
)
from rickmorty_orders.infrastructure.orm_models import (  # noqa: F401
    OrderItemModel,
    OrderModel,
)
from rickmorty_orders.infrastructure.persistence import Base
from rickmorty_orders.infrastructure.sql_repositories import SQLOrderRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ============================================
# Fixtures
# ============================================


@pytest.fixture
def e2e_client() -> Iterator[TestClient]:
    """TestClient con DB en memoria y repositorio SQL."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    # Override del repo: usar SQLite en memoria
    def override_get_order_repository() -> SQLOrderRepository:
        return SQLOrderRepository(session_factory)

    # Override del CharacterRepository: en memoria con personajes fake
    from rickmorty_orders.domain.character import Character
    from rickmorty_orders.domain.value_objects import CharacterId

    fake_chars = InMemoryCharacterRepository()
    for cid, name, status in [
        (1, "Rick Sanchez", CharacterStatus.ALIVE),
        (2, "Morty Smith", CharacterStatus.ALIVE),
        (3, "Birdperson", CharacterStatus.DEAD),
    ]:
        fake_chars.add(
            Character(
                id=CharacterId(cid),
                name=name,
                species="Human" if cid != 3 else "Alien",
                status=status,
            )
        )

    def override_get_character_client() -> InMemoryCharacterRepository:
        return fake_chars

    app.dependency_overrides[get_order_repository] = override_get_order_repository
    app.dependency_overrides[get_character_client] = override_get_character_client

    # Nota: NO usamos TestClient(app) como context manager, porque eso
    # dispara el lifespan (que crea tablas en la DB global rickmorty_orders.db).
    # Como ya creamos las tablas en el engine en memoria, no lo necesitamos.
    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()
        app.dependency_overrides.clear()
        engine.dispose()


# ============================================
# Tests basicos
# ============================================


def test_health(e2e_client: TestClient) -> None:
    """GET /health responde healthy."""
    response = e2e_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root(e2e_client: TestClient) -> None:
    """GET / responde con info del servicio."""
    response = e2e_client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()


# ============================================
# POST /orders/ (crear)
# ============================================


def test_create_order_ok(e2e_client: TestClient) -> None:
    """POST /orders/ crea una orden."""
    response = e2e_client.post(
        "/orders/",
        json={
            "customer_email": "paul@example.com",
            "items": [
                {"character_id": 1, "quantity": 1},
                {"character_id": 2, "quantity": 2},
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["customer_email"] == "paul@example.com"
    assert data["status"] == "pending"
    assert len(data["items"]) == 2
    # Rick: 1x50 = 50, Morty: 2x50 = 100
    assert data["subtotal"] == 150.0
    assert data["tax"] == 24.0
    assert data["total"] == 174.0
    assert data["total_items"] == 3


def test_create_order_character_no_existe(e2e_client: TestClient) -> None:
    """POST /orders/ con personaje inexistente -> 404."""
    response = e2e_client.post(
        "/orders/",
        json={
            "customer_email": "paul@example.com",
            "items": [{"character_id": 999, "quantity": 1}],
        },
    )
    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"].lower()


def test_create_order_email_invalido(e2e_client: TestClient) -> None:
    """Email invalido -> 422 (Pydantic)."""
    response = e2e_client.post(
        "/orders/",
        json={
            "customer_email": "no-es-email",
            "items": [{"character_id": 1, "quantity": 1}],
        },
    )
    assert response.status_code == 422


def test_create_order_sin_items(e2e_client: TestClient) -> None:
    """Sin items -> 422 (Pydantic)."""
    response = e2e_client.post(
        "/orders/",
        json={"customer_email": "a@b.com", "items": []},
    )
    assert response.status_code == 422


def test_create_order_quantity_invalida(e2e_client: TestClient) -> None:
    """quantity 0 -> 422."""
    response = e2e_client.post(
        "/orders/",
        json={
            "customer_email": "a@b.com",
            "items": [{"character_id": 1, "quantity": 0}],
        },
    )
    assert response.status_code == 422


# ============================================
# GET /orders/ (listar)
# ============================================


def test_list_orders_vacio(e2e_client: TestClient) -> None:
    """GET /orders/ sin ordenes -> []."""
    response = e2e_client.get("/orders/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_orders(e2e_client: TestClient) -> None:
    """GET /orders/ lista las ordenes creadas."""
    e2e_client.post(
        "/orders/",
        json={
            "customer_email": "a@b.com",
            "items": [{"character_id": 1, "quantity": 1}],
        },
    )
    e2e_client.post(
        "/orders/",
        json={
            "customer_email": "c@d.com",
            "items": [{"character_id": 2, "quantity": 1}],
        },
    )
    response = e2e_client.get("/orders/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_orders_filtrado_por_email(e2e_client: TestClient) -> None:
    """GET /orders/?customer_email=... filtra."""
    e2e_client.post(
        "/orders/",
        json={"customer_email": "paul@example.com", "items": [{"character_id": 1, "quantity": 1}]},
    )
    e2e_client.post(
        "/orders/",
        json={"customer_email": "ana@example.com", "items": [{"character_id": 2, "quantity": 1}]},
    )
    response = e2e_client.get("/orders/?customer_email=paul@example.com")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["customer_email"] == "paul@example.com"


# ============================================
# GET /orders/{id}
# ============================================


def test_get_order_ok(e2e_client: TestClient) -> None:
    """GET /orders/{id} devuelve la orden."""
    created = e2e_client.post(
        "/orders/",
        json={"customer_email": "a@b.com", "items": [{"character_id": 1, "quantity": 1}]},
    ).json()
    order_id = created["id"]

    response = e2e_client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_get_order_inexistente(e2e_client: TestClient) -> None:
    """GET /orders/inexistente -> 404."""
    response = e2e_client.get("/orders/no-existe")
    assert response.status_code == 404


# ============================================
# PATCH /orders/{id}/confirm
# ============================================


def test_confirm_order(e2e_client: TestClient) -> None:
    """PATCH confirm cambia status."""
    created = e2e_client.post(
        "/orders/",
        json={"customer_email": "a@b.com", "items": [{"character_id": 1, "quantity": 1}]},
    ).json()
    order_id = created["id"]

    response = e2e_client.patch(f"/orders/{order_id}/confirm")
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


def test_confirm_order_inexistente(e2e_client: TestClient) -> None:
    """PATCH confirm inexistente -> 404."""
    response = e2e_client.patch("/orders/no-existe/confirm")
    assert response.status_code == 404


def test_confirm_order_dos_veces_falla(e2e_client: TestClient) -> None:
    """Confirmar dos veces -> 409."""
    created = e2e_client.post(
        "/orders/",
        json={"customer_email": "a@b.com", "items": [{"character_id": 1, "quantity": 1}]},
    ).json()
    order_id = created["id"]

    e2e_client.patch(f"/orders/{order_id}/confirm")
    response = e2e_client.patch(f"/orders/{order_id}/confirm")
    assert response.status_code == 409


# ============================================
# PATCH /orders/{id}/cancel
# ============================================


def test_cancel_order(e2e_client: TestClient) -> None:
    """PATCH cancel cambia status."""
    created = e2e_client.post(
        "/orders/",
        json={"customer_email": "a@b.com", "items": [{"character_id": 1, "quantity": 1}]},
    ).json()
    order_id = created["id"]

    response = e2e_client.patch(f"/orders/{order_id}/cancel?reason=test")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_cancel_order_inexistente(e2e_client: TestClient) -> None:
    """PATCH cancel inexistente -> 404."""
    response = e2e_client.patch("/orders/no-existe/cancel")
    assert response.status_code == 404


# ============================================
# Flujo completo
# ============================================


def test_flujo_completo(e2e_client: TestClient) -> None:
    """Crear -> obtener -> confirmar -> listar."""
    # 1. Crear
    created = e2e_client.post(
        "/orders/",
        json={"customer_email": "a@b.com", "items": [{"character_id": 1, "quantity": 2}]},
    ).json()
    order_id = created["id"]
    assert created["status"] == "pending"

    # 2. Obtener
    get_response = e2e_client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200

    # 3. Confirmar
    confirm_response = e2e_client.patch(f"/orders/{order_id}/confirm")
    assert confirm_response.status_code == 200
    assert confirm_response.json()["status"] == "confirmed"

    # 4. Listar
    list_response = e2e_client.get("/orders/")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["status"] == "confirmed"

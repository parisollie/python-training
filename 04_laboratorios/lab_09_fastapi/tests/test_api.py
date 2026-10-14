"""Tests de integracion de la API."""

from fastapi.testclient import TestClient

# ============================================
# Health checks
# ============================================


def test_root(client: TestClient) -> None:
    """GET / responde con status ok."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health(client: TestClient) -> None:
    """GET /health responde healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ============================================
# Users
# ============================================


def test_create_user(client: TestClient) -> None:
    """POST /users/ crea un usuario."""
    response = client.post(
        "/users/",
        json={"email": "paul@example.com", "password": "password123", "name": "Paul"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "paul@example.com"
    assert data["name"] == "Paul"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_create_user_email_duplicado(client: TestClient) -> None:
    """POST /users/ con email duplicado devuelve 400."""
    payload = {"email": "a@b.com", "password": "password123", "name": "A"}
    client.post("/users/", json=payload)
    response = client.post("/users/", json=payload)
    assert response.status_code == 400
    assert "ya esta registrado" in response.json()["detail"]


def test_create_user_password_corta(client: TestClient) -> None:
    """Password menor a 8 chars devuelve 422 (Pydantic)."""
    response = client.post(
        "/users/",
        json={"email": "a@b.com", "password": "123", "name": "A"},
    )
    assert response.status_code == 422


def test_create_user_email_invalido(client: TestClient) -> None:
    """Email invalido devuelve 422."""
    response = client.post(
        "/users/",
        json={"email": "no-es-email", "password": "password123", "name": "A"},
    )
    assert response.status_code == 422


# ============================================
# Auth
# ============================================


def test_login_ok(client: TestClient) -> None:
    """POST /token devuelve JWT."""
    client.post(
        "/users/",
        json={"email": "a@b.com", "password": "password123", "name": "A"},
    )
    response = client.post(
        "/token",
        data={"username": "a@b.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_password_incorrecta(client: TestClient) -> None:
    """Password incorrecta devuelve 401."""
    client.post(
        "/users/",
        json={"email": "a@b.com", "password": "password123", "name": "A"},
    )
    response = client.post(
        "/token",
        data={"username": "a@b.com", "password": "wrong"},
    )
    assert response.status_code == 401


def test_login_email_inexistente(client: TestClient) -> None:
    """Email inexistente devuelve 401."""
    response = client.post(
        "/token",
        data={"username": "no@existe.com", "password": "password123"},
    )
    assert response.status_code == 401


def test_me_sin_token(client: TestClient) -> None:
    """GET /users/me sin token devuelve 401."""
    response = client.get("/users/me")
    assert response.status_code == 401


def test_me_con_token(auth_client: TestClient) -> None:
    """GET /users/me con token devuelve el usuario."""
    response = auth_client.get("/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"


# ============================================
# Orders
# ============================================


def test_create_order(auth_client: TestClient) -> None:
    """POST /orders/ crea una orden."""
    response = auth_client.post(
        "/orders/",
        json={
            "items": [
                {"product": "Teclado", "quantity": 2, "unit_price": 25.0},
                {"product": "Mouse", "quantity": 1, "unit_price": 15.5},
            ]
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 65.5
    assert data["status"] == "pending"


def test_create_order_sin_token(client: TestClient) -> None:
    """POST /orders/ sin token devuelve 401."""
    response = client.post(
        "/orders/",
        json={"items": [{"product": "X", "quantity": 1, "unit_price": 1.0}]},
    )
    assert response.status_code == 401


def test_create_order_items_vacio(auth_client: TestClient) -> None:
    """POST /orders/ con items vacios devuelve 422."""
    response = auth_client.post("/orders/", json={"items": []})
    assert response.status_code == 422


def test_list_orders_vacio(auth_client: TestClient) -> None:
    """GET /orders/ sin ordenes devuelve lista vacia."""
    response = auth_client.get("/orders/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_orders(auth_client: TestClient) -> None:
    """GET /orders/ lista las ordenes del usuario."""
    auth_client.post(
        "/orders/",
        json={"items": [{"product": "A", "quantity": 1, "unit_price": 10.0}]},
    )
    auth_client.post(
        "/orders/",
        json={"items": [{"product": "B", "quantity": 1, "unit_price": 20.0}]},
    )

    response = auth_client.get("/orders/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_order(auth_client: TestClient) -> None:
    """GET /orders/{id} devuelve la orden."""
    created = auth_client.post(
        "/orders/",
        json={"items": [{"product": "X", "quantity": 1, "unit_price": 100.0}]},
    )
    order_id = created.json()["id"]

    response = auth_client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_get_order_inexistente(auth_client: TestClient) -> None:
    """GET /orders/999 devuelve 404."""
    response = auth_client.get("/orders/999")
    assert response.status_code == 404


def test_delete_order(auth_client: TestClient) -> None:
    """DELETE /orders/{id} elimina la orden."""
    created = auth_client.post(
        "/orders/",
        json={"items": [{"product": "X", "quantity": 1, "unit_price": 10.0}]},
    )
    order_id = created.json()["id"]

    response = auth_client.delete(f"/orders/{order_id}")
    assert response.status_code == 204

    response = auth_client.get(f"/orders/{order_id}")
    assert response.status_code == 404


def test_delete_order_inexistente(auth_client: TestClient) -> None:
    """DELETE /orders/999 devuelve 404."""
    response = auth_client.delete("/orders/999")
    assert response.status_code == 404


def test_usuario_no_ve_ordenes_de_otros(client: TestClient) -> None:
    """Un usuario no puede ver las ordenes de otro usuario."""
    # Crear usuario A y su orden
    client.post(
        "/users/",
        json={"email": "a@b.com", "password": "password123", "name": "A"},
    )
    token_a = client.post("/token", data={"username": "a@b.com", "password": "password123"}).json()[
        "access_token"
    ]
    client.headers.update({"Authorization": f"Bearer {token_a}"})
    order_a = client.post(
        "/orders/",
        json={"items": [{"product": "A", "quantity": 1, "unit_price": 1.0}]},
    ).json()

    # Crear usuario B
    client.headers.pop("Authorization", None)
    client.post(
        "/users/",
        json={"email": "b@b.com", "password": "password123", "name": "B"},
    )
    token_b = client.post("/token", data={"username": "b@b.com", "password": "password123"}).json()[
        "access_token"
    ]
    client.headers.update({"Authorization": f"Bearer {token_b}"})

    # B intenta ver la orden de A
    response = client.get(f"/orders/{order_a['id']}")
    assert response.status_code == 404  # no 403, para no filtrar existencia

    # B no ve las ordenes de A en su lista
    response = client.get("/orders/")
    assert response.json() == []

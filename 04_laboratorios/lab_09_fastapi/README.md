# Laboratorio 09 — API REST con FastAPI

API completa con CRUD de ordenes, autenticacion JWT y documentacion OpenAPI automatica.

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1
- FastAPI 0.143.1, uvicorn 0.54.0, python-jose 3.5.0
- SQLAlchemy 2.1.4

## Estructura

lab_09_fastapi/
├── README.md              ← este archivo
├── main.py                ← FastAPI app + include_router
├── database.py            ← engine, SessionLocal, Base, get_db
├── models.py              ← User, Order, OrderItem (SQLAlchemy)
├── schemas.py             ← Pydantic: UserIn/Out, OrderIn/Out, Token
├── security.py            ← hash (bcrypt) + JWT (python-jose)
├── dependencies.py        ← get_current_user, CurrentUser, DbSession
├── routers/
│   ├── auth.py            ← POST /token
│   ├── users.py           ← POST /users/, GET /users/me
│   └── orders.py          ← CRUD /orders/
└── tests/
    ├── conftest.py        ← TestClient + SQLite en memoria
    └── test_api.py        ← 21 tests de integracion

## Ejecutar la API

Desde la carpeta del laboratorio:

    cd 04_laboratorios/lab_09_fastapi
    poetry run uvicorn main:app --reload --port 8000

Abrir en el navegador:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Detener con `Ctrl+C`.

## Endpoints

| Metodo | Ruta | Auth | Descripcion |
|--------|------|:----:|-------------|
| GET | `/` | No | Health check |
| GET | `/health` | No | Health detallado |
| POST | `/users/` | No | Crear usuario |
| GET | `/users/me` | Si | Usuario actual |
| POST | `/token` | No | Login (devuelve JWT) |
| POST | `/orders/` | Si | Crear orden |
| GET | `/orders/` | Si | Listar ordenes del usuario |
| GET | `/orders/{id}` | Si | Obtener orden |
| DELETE | `/orders/{id}` | Si | Eliminar orden |

## Flujo completo con curl

### 1. Crear usuario

    curl -X POST http://localhost:8000/users/ \
      -H "Content-Type: application/json" \
      -d '{"email": "paul@example.com", "password": "password123", "name": "Paul"}'

Respuesta (201):

    {"id":1,"email":"paul@example.com","name":"Paul","created_at":"..."}

### 2. Login

    curl -X POST http://localhost:8000/token \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "username=paul@example.com&password=password123"

Respuesta (200):

    {"access_token":"eyJ...","token_type":"bearer"}

### 3. Crear orden (con token)

    TOKEN="eyJ..."  # pegar el access_token del paso 2

    curl -X POST http://localhost:8000/orders/ \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"items": [{"product": "Teclado", "quantity": 2, "unit_price": 25.0}]}'

Respuesta (201):

    {"id":1,"user_id":1,"status":"pending","items":[...],"total":58.0}

### 4. Listar ordenes

    curl http://localhost:8000/orders/ -H "Authorization: Bearer $TOKEN"

### 5. Obtener orden

    curl http://localhost:8000/orders/1 -H "Authorization: Bearer $TOKEN"

### 6. Eliminar orden

    curl -X DELETE http://localhost:8000/orders/1 -H "Authorization: Bearer $TOKEN"

Respuesta: 204 No Content

## Cómo ejecutar los tests

### Todos los tests

    poetry run pytest 04_laboratorios/lab_09_fastapi/tests/ -v

Salida esperada:

    21 passed in 4.68s

### Con cobertura

    poetry run pytest 04_laboratorios/lab_09_fastapi/tests/ --cov=04_laboratorios/lab_09_fastapi --cov-report=term-missing

### Archivos de tests

| Archivo | Que cubre | Tests |
|---------|-----------|-------|
| test_api.py | health, users, auth, orders, aislamiento | 21 |

### Fixtures

- `client`: TestClient con SQLite en memoria (override de `get_db`)
- `auth_client`: TestClient con usuario creado y token inyectado en headers

## Verificacion de calidad

    poetry run ruff check 04_laboratorios/lab_09_fastapi/
    poetry run mypy 04_laboratorios/lab_09_fastapi/
    poetry run pre-commit run --all-files

## Notas de implementacion

### Bug resuelto: passlib + bcrypt 4.1+

El lab originalmente usaba `passlib[bcrypt]`, pero `passlib 1.7.4` no es
compatible con `bcrypt 4.1+` (bug conocido, sin fix upstream desde 2020).
Solucion: usar `bcrypt` directamente sin `passlib`.

- `bcrypt.hashpw(password, bcrypt.gensalt())` -> hash
- `bcrypt.checkpw(password, hash)` -> verificacion
- Limite de 72 bytes por password (truncar si es necesario)

### FastAPI 0.143+: routers anidados

En FastAPI 0.143+ los `include_router` crean objetos `_IncludedRouter` en
`app.routes`. Para inspeccionar todas las rutas aplanadas usar:

    app.openapi()["paths"]

No es un bug, es un cambio de diseno interno.

### SQLAlchemy en FastAPI

- `get_db` es una dependencia con `yield` que se cierra al terminar el request
- Los tests sobreescriben `get_db` con `app.dependency_overrides`
- Eager loading con `selectinload` para evitar `DetachedInstanceError`

### JWT con python-jose

- HS256 con `SECRET_KEY` (en produccion: variable de entorno)
- `exp` en el payload limita validez
- `OAuth2PasswordBearer` extrae el token del header `Authorization: Bearer ...`

### Seguridad

- Los errores de autenticacion devuelven **401** (no 403) para no filtrar
  si el recurso existe
- El usuario solo ve sus propias ordenes (filtro por `user_id`)
- Los schemas `UserOut` no exponen `hashed_password`

### Warning de Starlette

    StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated

Es un aviso de que Starlette migrara de `httpx` a `httpx2` en el futuro.
No afecta funcionalidad actual.

## Comandos rapidos (resumen)

    # Arrancar API
    cd 04_laboratorios/lab_09_fastapi
    poetry run uvicorn main:app --reload --port 8000

    # Tests
    poetry run pytest 04_laboratorios/lab_09_fastapi/tests/ -v

    # Calidad
    poetry run ruff check 04_laboratorios/lab_09_fastapi/
    poetry run mypy 04_laboratorios/lab_09_fastapi/

## Estado

- [x] Estructura del laboratorio
- [x] FastAPI + uvicorn + python-jose + bcrypt
- [x] Modelos SQLAlchemy
- [x] Schemas Pydantic
- [x] Seguridad (bcrypt + JWT)
- [x] Routers (auth, users, orders)
- [x] App principal con CORS
- [x] 21 tests con TestClient + SQLite
- [x] ruff + mypy OK
- [x] Documentacion completa

## Clonar este laboratorio

    git clone https://github.com/parisollie/python-training.git
    cd python-training
    poetry install

    # Arrancar API
    cd 04_laboratorios/lab_09_fastapi
    poetry run uvicorn main:app --reload

    # O solo correr tests
    poetry run pytest tests/ -v

## Referencias

- FastAPI docs: https://fastapi.tiangolo.com/
- FastAPI — Security: https://fastapi.tiangolo.com/tutorial/security/
- FastAPI — SQL Databases: https://fastapi.tiangolo.com/tutorial/sql-databases/
- Pydantic v2: https://docs.pydantic.dev/
- python-jose: https://python-jose.readthedocs.io/
- bcrypt: https://github.com/pyca/bcrypt
- JWT: https://jwt.io/introduction
- OAuth2 password flow: https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/

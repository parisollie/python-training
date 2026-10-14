# Módulo 09 — APIs web con FastAPI

## Objetivos
- Exponer una API coherente, validada y documentada
- Asegurar endpoints con autenticacion JWT
- Testear endpoints con pytest

## Contenidos clave

### Estructura de proyecto FastAPI
- `main.py` con la app principal
- Routers en `routers/` o `api/`
- Schemas en `schemas/` (Pydantic)
- Modelos en `models/` (SQLAlchemy)
- Dependencias en `dependencies.py`
- Configuracion en `config.py`

### Routers y dependencias
- APIRouter con prefix y tags
- include_router en la app principal
- Depends() para inyeccion de dependencias
- Dependencias con yield (ej: sesion de DB)

### Schemas Pydantic
- BaseModel para validacion
- Field con constraints (min_length, ge, le, pattern)
- model_config para configuracion (from_attributes, etc.)
- Separacion: XxxIn (entrada), XxxOut (salida)

### OpenAPI y Swagger
- FastAPI genera OpenAPI automaticamente
- /docs -> Swagger UI
- /redoc -> ReDoc
- response_model para tipar la salida
- summary, description, response_description

### Autenticacion JWT
- Flujo: POST /token con credenciales -> JWT
- JWT firmado con SECRET_KEY y algoritmo HS256
- Header: Authorization: Bearer <token>
- Dependencia get_current_user que valida el token
- Hash de passwords con bcrypt (passlib)

### Middlewares y CORS
- CORS para permitir frontends en otros dominios
- Middleware para logging, timing, etc.
- Exception handlers personalizados

### Codigos de estado HTTP
- 200 OK, 201 Created, 204 No Content
- 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found
- 422 Unprocessable Entity (validacion Pydantic)
- 500 Internal Server Error

### Testing
- TestClient (sincrono) o httpx.AsyncClient
- Fixture de app con DB en memoria
- Dependency override para usar DB de test
- Tests de integracion por endpoint

## Laboratorio

API de Orders con:

1. Modelos SQLAlchemy: User, Order, OrderItem
2. Schemas Pydantic: OrderIn, OrderOut, UserIn, UserOut, Token
3. Endpoints:
   - POST /users -> crear usuario
   - POST /token -> login (devuelve JWT)
   - GET /users/me -> usuario actual (protegido)
   - POST /orders -> crear orden (protegido)
   - GET /orders -> listar ordenes del usuario (protegido)
   - GET /orders/{id} -> obtener orden (protegido)
   - DELETE /orders/{id} -> eliminar (protegido)
4. Autenticacion JWT con bcrypt para passwords
5. Tests con TestClient + DB en memoria

## Conceptos clave

### ¿Por que PEP 20 importa aqui?
- "Explícito es mejor que implícito" -> response_model en cada endpoint
- "Los errores nunca deben pasar silenciosamente" -> HTTPException con mensajes claros
- "Simple es mejor que complejo" -> routers pequenos, no un main.py de 500 lineas

### Estructura recomendada

    app/
    ├── main.py              <- FastAPI() + include_router
    ├── config.py            <- Settings (pydantic-settings)
    ├── database.py          <- engine, SessionLocal, Base
    ├── dependencies.py      <- get_db, get_current_user
    ├── models/              <- SQLAlchemy
    │   ├── __init__.py
    │   ├── user.py
    │   └── order.py
    ├── schemas/             <- Pydantic
    │   ├── __init__.py
    │   ├── user.py
    │   ├── order.py
    │   └── token.py
    ├── routers/             <- APIRouter
    │   ├── __init__.py
    │   ├── auth.py
    │   ├── users.py
    │   └── orders.py
    └── security.py          <- hash, JWT

### Ejemplo: endpoint basico

    from fastapi import FastAPI

    app = FastAPI(title="Mi API", version="1.0.0")

    @app.get("/")
    def read_root() -> dict[str, str]:
        return {"message": "Hola"}

### Ejemplo: router con dependencias

    from fastapi import APIRouter, Depends, HTTPException, status
    from sqlalchemy.orm import Session

    router = APIRouter(prefix="/orders", tags=["orders"])

    @router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
    def create_order(
        order_in: OrderIn,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> Order:
        order = Order(user_id=current_user.id)
        # ... agregar items
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

### Ejemplo: JWT

    from datetime import UTC, datetime, timedelta
    from jose import jwt

    SECRET_KEY = "cambiar-en-produccion"
    ALGORITHM = "HS256"

    def create_access_token(data: dict, expires_minutes: int = 30) -> str:
        to_encode = data.copy()
        to_encode["exp"] = datetime.now(UTC) + timedelta(minutes=expires_minutes)
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(token: str) -> dict:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.JWTError as e:
            raise HTTPException(status_code=401, detail="Token invalido") from e

### Ejemplo: hash de password con bcrypt

    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

### Ejemplo: dependencia de DB con yield

    from sqlalchemy.orm import Session

    def get_db() -> Generator[Session, None, None]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

### Override de dependencias en tests

    from app.main import app
    from app.dependencies import get_db

    def override_get_db() -> Generator[Session, None, None]:
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

## Checklist
- [ ] Crear estructura del laboratorio
- [ ] Instalar fastapi, uvicorn, python-jose, passlib[bcrypt]
- [ ] Modelos SQLAlchemy
- [ ] Schemas Pydantic
- [ ] Seguridad (hash + JWT)
- [ ] Routers (auth, users, orders)
- [ ] App principal con include_router
- [ ] Tests con TestClient + SQLite en memoria
- [ ] Documentar en README del laboratorio
- [ ] Commit del modulo

## Referencias
- FastAPI docs: https://fastapi.tiangolo.com/
- FastAPI tutorial (user guide): https://fastapi.tiangolo.com/tutorial/
- Pydantic v2 docs: https://docs.pydantic.dev/
- python-jose: https://python-jose.readthedocs.io/
- passlib: https://passlib.readthedocs.io/
- JWT: https://jwt.io/introduction
- HTTP status codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

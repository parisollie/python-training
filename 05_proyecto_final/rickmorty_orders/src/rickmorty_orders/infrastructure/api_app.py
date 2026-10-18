"""Aplicacion FastAPI principal.

Ejecutar con:
    uvicorn rickmorty_orders.infrastructure.api_app:app --reload

Docs:
    http://localhost:8000/docs
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rickmorty_orders.infrastructure.api_health import router as health_router
from rickmorty_orders.infrastructure.api_orders import router as orders_router
from rickmorty_orders.infrastructure.config import get_settings
from rickmorty_orders.infrastructure.persistence import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifecycle: crea tablas al iniciar."""
    init_db()
    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Servicio de Orders con arquitectura hexagonal",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(orders_router)

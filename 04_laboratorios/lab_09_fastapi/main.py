"""Aplicacion FastAPI principal.

Ensambla los routers y configura la app.
Ejecutar con: uvicorn main:app --reload
Docs en: http://localhost:8000/docs
"""

from database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, orders, users

# Crear tablas al iniciar (en produccion: usar Alembic)
Base.metadata.create_all(bind=engine)

# ============================================
# App
# ============================================

app = FastAPI(
    title="Python Training API",
    description="API de ejemplo para la capacitacion (Rick and Morty + Orders)",
    version="0.1.0",
)

# ============================================
# CORS
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En produccion: especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Routers
# ============================================

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(orders.router)


# ============================================
# Health check
# ============================================


@app.get("/", tags=["health"])
def read_root() -> dict[str, str]:
    """Health check."""
    return {"status": "ok", "service": "python-training-api"}


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Health check detallado."""
    return {"status": "healthy"}

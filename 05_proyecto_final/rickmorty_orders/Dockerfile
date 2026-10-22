# =============================================================
# Stage 1: Builder (instala dependencias con Poetry)
# =============================================================
FROM python:3.12-slim AS builder

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=2.5.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Instalar Poetry + dependencias de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar SOLO los archivos de dependencias primero (mejor cache)
COPY pyproject.toml poetry.lock ./

# Instalar dependencias (sin dev, sin proyecto)
RUN poetry install --only main --no-root

# Copiar README.md de la raiz (pyproject.toml lo referencia)
COPY README.md ./

# Copiar el codigo fuente (necesario para instalar el paquete)
COPY src/ ./src/
COPY 05_proyecto_final/rickmorty_orders/src/ ./05_proyecto_final/rickmorty_orders/src/
COPY 04_laboratorios/lab_16_clean_arch/src/ ./04_laboratorios/lab_16_clean_arch/src/

# Instalar el proyecto
RUN poetry install --only main


# =============================================================
# Stage 2: Runtime (imagen final, sin build tools)
# =============================================================
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    RMO_DATABASE_URL="sqlite:////app/data/rickmorty_orders.db"

# Usuario no-root
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --create-home app

WORKDIR /app

# Crear carpeta data con permisos del usuario app
RUN mkdir -p /app/data && chown -R app:app /app/data

# Copiar el venv del builder
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Copiar el codigo fuente (necesario para el paquete rickmorty_orders)
COPY --from=builder --chown=app:app /app/src /app/src
COPY --from=builder --chown=app:app /app/05_proyecto_final/rickmorty_orders/src /app/05_proyecto_final/rickmorty_orders/src
COPY --from=builder --chown=app:app /app/04_laboratorios/lab_16_clean_arch/src /app/04_laboratorios/lab_16_clean_arch/src

# Copiar alembic (para migraciones en runtime)
COPY --chown=app:app 05_proyecto_final/rickmorty_orders/alembic.ini ./
COPY --chown=app:app 05_proyecto_final/rickmorty_orders/alembic/ ./alembic/

# Cambiar a usuario no-root
USER app

# Exponer puerto
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

# Entrypoint: arrancar uvicorn
CMD ["sh", "-c", "alembic upgrade head && uvicorn rickmorty_orders.infrastructure.api_app:app --host 0.0.0.0 --port 8000"]

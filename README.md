# Python Training

Capacitación completa de Python (Fundamental → Intermediate → Advanced) con
proyecto integrador usando la API de Rick and Morty y arquitectura hexagonal.

## Stack

- Python 3.12.15
- Poetry 2.5.1
- Git 2.54.0
- Docker Desktop
- VS Code
- FastAPI, httpx, SQLAlchemy, Alembic, Typer, rich, gRPC, redis
- pytest, ruff, black, isort, mypy, pre-commit, pip-audit

## Estructura

- `00_setup/` - Instalación y configuración
- `01_fundamental/` - Nivel Fundamental (módulos 01-07)
- `02_intermediate/` - Nivel Intermediate (módulos 08-15)
- `03_advanced/` - Nivel Advanced (módulos 16-20)
- `04_laboratorios/` - Laboratorios prácticos
- `05_proyecto_final/` - Proyecto integrador (rickmorty_orders)

## Progreso

### Fundamental (7/7) ✅
- [x] Módulo 01 — Introducción
- [x] Módulo 02 — Tipos y variables
- [x] Módulo 03 — Control de flujo
- [x] Módulo 04 — Funciones
- [x] Módulo 05 — Estructuras de datos
- [x] Módulo 06 — Módulos y paquetes
- [x] Módulo 07 — Archivos y excepciones

### Intermediate (8/8) ✅
- [x] Módulo 08 — POO
- [x] Módulo 09 — Errores y logging
- [x] Módulo 10 — Testing (pytest)
- [x] Módulo 11 — Concurrencia
- [x] Módulo 12 — SOLID
- [x] Módulo 13 — Patrones de diseño
- [x] Módulo 14 — Data Science
- [x] Módulo 15 — Arquitectura hexagonal

### Advanced (5/5) ✅
- [x] Módulo 16 — Arquitectura limpia
- [x] Módulo 17 — Empaquetado + CI/CD
- [x] Módulo 18 — CLI con Typer
- [x] Módulo 19 — Seguridad y mantenimiento
- [x] Módulo 20 — Interoperabilidad (gRPC + Redis)

### Proyecto final (7/7) ✅
- [x] Fase 1 — Setup
- [x] Fase 2 — Dominio
- [x] Fase 3 — Aplicación
- [x] Fase 4 — Infraestructura
- [x] Fase 5 — Testing (162 tests, 93% cobertura)
- [x] Fase 6 — Alembic + Docker + CI/CD
- [x] Fase 7 — Auditoría + presentación

## Cómo correr los tests

### Proyecto final (recomendado — todo junto)

    poetry run pytest 05_proyecto_final/rickmorty_orders/tests/ -q

Salida esperada: `162 passed`.

### Laboratorios (uno por uno)

⚠️ **Importante:** los laboratorios **deben correrse individualmente**.
Si se corren todos juntos con `pytest 04_laboratorios/`, fallan por
colisión de nombres de módulos (`tests/__init__.py`, `conftest.py` con el
mismo nombre en varios labs). Es un problema preexistente del repo y
**no afecta** al proyecto final ni a los tests individuales.

    # Bien: un lab a la vez
    poetry run pytest 04_laboratorios/lab_05_typing/tests/ -q
    poetry run pytest 04_laboratorios/lab_16_clean_arch/tests/ -q

    # Mal: todos juntos
    # poetry run pytest 04_laboratorios/   ← errores de collection

## Calidad de código

    poetry run ruff check .
    poetry run mypy 05_proyecto_final/rickmorty_orders/src/rickmorty_orders/grpc/server.py \
                   05_proyecto_final/rickmorty_orders/src/rickmorty_orders/grpc/converters.py \
                   05_proyecto_final/rickmorty_orders/src/rickmorty_orders/grpc/client.py
    poetry run pre-commit run --all-files

## Convenciones de commits

- `feat:` nueva funcionalidad
- `fix:` corrección de bug
- `docs:` documentación
- `test:` tests
- `refactor:` refactorización
- `chore:` mantenimiento

## Autor

parisollie - pjff18@gmail.com

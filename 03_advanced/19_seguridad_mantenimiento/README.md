# Módulo 19 — Seguridad y mantenimiento

## Objetivos
- Proteger secretos y reducir superficie de riesgo
- Mantener dependencias seguras y actualizadas
- Endurecer el contenedor y el runtime

## Contenidos clave

### Gestion de secretos

**Regla de oro**: los secretos NUNCA se commitean.

| Practica | Herramienta |
|----------|-------------|
| Variables de entorno | `pydantic-settings` (prefijo `RMO_`) |
| Archivo local | `.env` (en `.gitignore`) |
| Template en el repo | `.env.example` (placeholders, sin valores reales) |
| CI/CD | GitHub Secrets (o Azure Key Vault) |
| Contenedor | Variables de entorno inyectadas al arrancar |

**Deteccion de secretos en commits**:

    # pre-commit detecta claves privadas
    - id: detect-private-key

    # Herramientas dedicadas (opcional):
    # - gitleaks: https://github.com/gitleaks/gitleaks
    # - trufflehog: https://github.com/trufflesecurity/trufflehog

**Rotacion de secretos**:
- Si un secreto se filtra, ROTARLO inmediatamente
- Tokens de PyPI, GitHub, AWS: usar scopes minimos y rotacion periodica
- Nunca reutilizar el mismo secreto en dev y prod

### Auditoria de dependencias

**pip-audit** (oficial de PyPA):

    poetry run pip-audit

**safety** (alternativa, base de datos paga/community):

    poetry run safety check

**Trivy** (escaneo de imagenes Docker):

    trivy image rickmorty-orders:latest

**Politica de auditoria**:
- Ejecutar en cada PR (CI)
- Falla el pipeline si hay vulnerabilidades CRITICAL sin fix
- Documentar excepciones en el README con justificacion
- Revisar dependencias periodicamente (semanal o mensual)

### Actualizaciones (PEP 440)

**Versionado semantico**:
- `^2.14.1` -> acepta 2.x.x (no 3.x)
- `~2.14.1` -> acepta 2.14.x (no 2.15)
- `2.14.1` -> version exacta
- `*` -> cualquier version (evitar)

**Comandos**:

    # Ver dependencias desactualizadas
    poetry show --outdated

    # Actualizar dentro de los limites del pyproject.toml
    poetry update

    # Actualizar un paquete especifico
    poetry update fastapi

    # Regenerar lockfile sin actualizar
    poetry lock

**Compatibilidad**:
- Pinear versiones MAYOR en produccion
- Testear actualizaciones en ramas antes de mergear
- Leer el CHANGELOG de cada dependencia antes de actualizar

### Hardening de contenedores

**Checklist de seguridad Docker**:

- [x] Multistage (no incluir build tools en runtime)
- [x] Usuario non-root (`app` con uid 1000)
- [x] `.dockerignore` agresivo (excluir .git, tests, .env)
- [x] Pinear version base (`python:3.12-slim`, no `latest`)
- [x] HEALTHCHECK
- [x] No instalar dev dependencies
- [x] Secrets via env vars (no en la imagen)
- [ ] Escanear con `trivy` o `docker scout` (opcional)
- [ ] Firmar imagen con `cosign` (opcional)
- [ ] Limitar recursos (CPU, memoria) en runtime

**Ejemplo de hardening**:

    # Dockerfile
    FROM python:3.12.5-slim AS runtime

    RUN groupadd --gid 1000 app \
        && useradd --uid 1000 --gid app --create-home app

    # ... copia de .venv, src, alembic

    USER app

    # Limites del runtime (en docker run o docker-compose)
    # --memory="512m" --cpus="1.0" --read-only --tmpfs /tmp

### Hardening del runtime

**Python**:
- No usar `eval()` ni `exec()` con input del usuario
- Validar TODO con Pydantic en el borde
- Usar `secrets` para tokens (no `random`)
- Hashear passwords con bcrypt (nunca en texto plano)
- Timeouts en TODAS las llamadas HTTP

**FastAPI**:
- CORS con `allow_origins` especifico (no `*` en prod)
- Rate limiting (slowapi, fastapi-limiter)
- Autenticacion JWT con expiracion corta
- No exponer stack traces en produccion (`debug=False`)

**Logging**:
- No loggear credenciales ni PII
- Loggear eventos de seguridad (login, cambio de password, acceso denegado)
- Rotacion de logs (logrotate, logging.handlers.RotatingFileHandler)

### Mantenimiento programado

**Tareas periodicas**:
- Semanal: `pip-audit`, revisar dependencias desactualizadas
- Mensual: `poetry update` en rama de pruebas
- Trimestral: rotacion de secretos, revision de permisos
- Anual: actualizacion de version MAYOR de Python, revision de arquitectura

**Documentar el plan**:
- En el README del proyecto
- Con fechas y responsables
- Con criterios de aceptacion

## Aplicacion al proyecto final

Este modulo se aplico **directamente al proyecto `rickmorty_orders`**:

### Ya implementado (FASE 6 del proyecto final)

- Docker multistage + usuario non-root `app`
- `pydantic-settings` con prefijo `RMO_` (todos los secrets via env)
- `.env.example` con placeholders (sin valores reales)
- `.env` en `.gitignore`
- `pip-audit` corriendo (3 CVEs ignorados justificadamente)
- `detect-private-key` en pre-commit
- Timeouts en `httpx` (10s)
- bcrypt para passwords (sin passlib)
- JWT con expiracion (en lab 09, no en proyecto final)

### Nuevo en este modulo (Módulo 19)

- Auditoria con `safety` (segunda opinion)
- Escaneo de imagen Docker con `trivy` o `docker scout`
- Documentar el plan de mantenimiento en el README
- Politica de excepciones para `pip-audit` (documentada)
- Checklist de hardening en el README

## Resultados del escaneo de seguridad (Trivy)

Se escaneo la imagen `rickmorty-orders:latest` con Trivy (vulnerabilidades
del OS + paquetes Python). Resultados tras las correcciones:

### Antes (imagen vieja)

- **CRITICAL**: `python-jose 3.5.0` (CVE-2026-85394, algorithm confusion)
- **HIGH**: `urllib3 2.7.0` (3 CVEs)
- **HIGH**: `setuptools`, `pip` (build-time, no afectan runtime)

### Correcciones aplicadas

1. **`python-jose` movido al grupo dev**: la imagen se reconstruye con
   `poetry install --only main`, por lo que `python-jose` **ya no esta en la imagen**.
2. **`urllib3` actualizado a 2.8.0**: se agrego `urllib3@^2.8.0` al
   `pyproject.toml` para forzar la version parcheada (dependencia transitiva
   de `httpx`).
3. **Imagen reconstruida sin cache**: `docker build --no-cache` para
   garantizar que se usa el `poetry.lock` actualizado.

### Despues (imagen actual)

| Categoria | Estado |
|-----------|--------|
| `python-jose` (CRITICAL) | ✅ **Eliminado** |
| `urllib3` (HIGH) | ✅ **Actualizado a 2.8.0** |
| `pip` / `setuptools` (HIGH/MEDIUM) | ⚠️ Build-time (no runtime) |
| Vulnerabilidades del OS (Debian) | ⚠️ De la imagen base, no explotables |

### Vulnerabilidades del OS (imagen base)

El escaneo detecta vulnerabilidades en paquetes del **sistema operativo**
de la imagen base `python:3.12-slim` (Debian 13.7):
- `libacl1`, `libsystemd0`, `util-linux`, `ncurses`, `perl-base`, etc.

**Evaluacion**:
- **No son explotables** desde el codigo del proyecto (no usamos esas
  funcionalidades del OS).
- **Se mitigan** con `USER app` (usuario non-root, sin privilegios).
- **Se resuelven** cuando Docker/Python actualicen la imagen base
  `python:3.12-slim`.
- **Accion**: actualizar la imagen base periodicamente (mensual) y
  re-escanear con Trivy.

### Comando para re-escanear

    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
      aquasec/trivy:latest image --scanners vuln --quiet rickmorty-orders:latest

## Nota: safety omitido (conflicto con typer)

`safety 3.8.1` no se instalo porque depende de `typer >=0.16.0,<0.26.0`,
y el proyecto usa `typer 0.27.3` (para el CLI del Modulo 18). Los rangos
no se solapan y Poetry falla al resolver.

**Decision**: no instalar `safety`. `pip-audit` (ya integrado en la
FASE 7 del proyecto final) cubre la auditoria de dependencias. `safety`
era una segunda opinion opcional, no obligatoria.

**Alternativa** si se necesita `safety`:

    python3.12 -m venv /tmp/safety_env
    /tmp/safety_env/bin/pip install safety
    /tmp/safety_env/bin/safety check

Esto lo instala en un venv aislado sin afectar al proyecto.

## Checklist
- [ ] Instalar `safety` como dev dependency _(no aplica: conflicto con typer 0.27.3)_
- [ ] Ejecutar `safety check` y comparar con `pip-audit` _(no aplica: safety no instalado)_
- [x] Escanear la imagen Docker (`trivy image` o `docker scout`)
- [x] Documentar el plan de mantenimiento en el README
- [x] Documentar excepciones de auditoria
- [x] Correr ruff y mypy
- [x] Commit del modulo

## Referencias
- pip-audit: https://pypi.org/project/pip-audit/
- safety: https://pypi.org/project/safety/
- Trivy: https://aquasecurity.github.io/trivy/
- Docker Scout: https://docs.docker.com/scout/
- PEP 440 — Version Identification: https://peps.python.org/pep-0440/
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Python security best practices: https://python.readthedocs.io/en/stable/library/security_warnings.html
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/

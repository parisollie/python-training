# Módulo 17 — Empaquetado, distribucion y CI/CD

## Objetivos
- Empaquetar el proyecto como wheel y sdist reproducibles
- Publicar artefactos en PyPI o un repositorio interno
- Contenerizar con Docker multistage y buenas practicas
- Automatizar pipelines en GitHub Actions
- Desplegar en Azure (App Service, Container Apps, Functions)

## Contenidos clave

### Empaquetado con Poetry

**Wheel (.whl)** — distribucion binaria (lo que se instala con pip).
**sdist (.tar.gz)** — codigo fuente empaquetado.
**pyproject.toml** — declara metadata y entry points.

    poetry build
    # Genera: dist/mi_paquete-0.1.0-py3-none-any.whl
    #         dist/mi_paquete-0.1.0.tar.gz

**Versionado semantico (PEP 440)**:
- MAJOR.MINOR.PATCH
- 1.2.3 = release estable
- 1.2.3a1 = alpha
- 1.2.3rc1 = release candidate
- 1.2.3.post1 = post-release
- 1.2.3.dev1 = development

**Como bumpear la version**:
    poetry version patch   # 0.1.0 -> 0.1.1
    poetry version minor   # 0.1.1 -> 0.2.0
    poetry version major   # 0.2.0 -> 1.0.0

### Publicacion en PyPI

    # Configurar token (una sola vez)
    poetry config pypi-token.pypi pypi-XXXX

    # Publicar (usa la version actual de pyproject.toml)
    poetry publish --build

    # Publicar en un repositorio interno (Artifactory, Nexus)
    poetry config repositories.internal https://artifacts.example.com/pypi
    poetry publish --repository internal --build

**TestPyPI** (para probar sin tocar el PyPI real):
    poetry config repositories.testpypi https://test.pypi.org/legacy/
    poetry publish --repository testpypi --build

### Docker multistage (repaso y profundizacion)

    # Stage 1: builder (instala deps, compila wheels)
    FROM python:3.12-slim AS builder
    WORKDIR /app
    COPY pyproject.toml poetry.lock ./
    RUN pip install poetry && poetry install --only main --no-root
    COPY src/ ./src/
    RUN poetry install --only main

    # Stage 2: runtime (solo lo necesario)
    FROM python:3.12-slim AS runtime
    RUN useradd --create-home --uid 1000 app
    WORKDIR /app
    COPY --from=builder /app/.venv /app/.venv
    COPY --from=builder /app/src /app/src
    USER app
    CMD ["python", "-m", "mi_paquete"]

**Buenas practicas Docker**:
- Multistage (reducir tamano y superficie de ataque)
- Usuario non-root
- .dockerignore agresivo
- HEALTHCHECK
- No instalar dev dependencies
- Pinear la version base (python:3.12.5-slim, no python:latest)
- Escanear con `trivy` o `docker scout`

### GitHub Actions (CI/CD)

**Workflow tipico** (.github/workflows/ci.yml):

    name: CI
    on:
      push:
        branches: [main]
      pull_request:

    jobs:
      lint:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-python@v5
            with:
              python-version: "3.12"
          - run: pip install ruff && ruff check .

      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - run: pip install poetry && poetry install
          - run: poetry run pytest

      build:
        needs: [lint, test]
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - run: docker build -t app:${{ github.sha }} .

**Artefactos y cache**:

    - uses: actions/cache@v4
      with:
        path: ~/.cache/pypoetry
        key: poetry-${{ hashFiles('poetry.lock') }}

    - uses: actions/upload-artifact@v4
      with:
        name: wheel
        path: dist/*.whl

**Publicacion automatica al hacer tag**:

    on:
      push:
        tags: ["v*"]

    jobs:
      publish:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - run: pip install poetry && poetry build
          - uses: pypa/gh-action-pypi-publish@release/v1
            with:
              password: ${{ secrets.PYPI_TOKEN }}

### Despliegue en Azure

**App Service (PaaS)**:
- Deploy de un wheel + `requirements.txt` o de una imagen Docker
- Configuracion en el portal o via `az webapp`
- Escalado automatico

**Container Apps (serverless containers)**:
- Deploy de imagen Docker
- Escala a cero si no hay trafico
- Ideal para APIs con poco trafico

**Functions (serverless)**:
- Codigo sin servidor
- Pago por ejecucion
- Ideal para tareas puntuales

**Comando tipico**:

    az webapp create --name mi-app --resource-group mi-rg \\
      --plan mi-plan --runtime "PYTHON:3.12"

    az webapp deployment source config-zip \\
      --name mi-app --resource-group mi-rg \\
      --src dist/mi_paquete-0.1.0-py3-none-any.whl

### Seguridad en CI/CD

- **Secrets**: GitHub Secrets, Azure Key Vault, no .env en CI
- **Tokens de PyPI**: alcance minimo, rotacion periodica
- **Pinear actions**: `actions/checkout@v4` (no `@main`)
- **Firmar artefactos**: `sigstore/cosign` (opcional)
- **Auditoria**: `pip-audit` en el pipeline

## Laboratorio

Aplicar todo lo anterior al proyecto final `rickmorty_orders`:

1. **Empaquetar** el proyecto como wheel
2. **Publicar** en TestPyPI (o simular)
3. **Extender CI**: agregar job `publish` cuando se cree un tag `v*`
4. **Tag de release** `v0.1.0` y push de tags
5. **Verificar** que el workflow corre en GitHub Actions
6. **Documentar** el proceso en el README del proyecto

## Laboratorio realizado (aplicado al proyecto final)

Aplicamos el Modulo 17 al proyecto final `rickmorty_orders` **sin modificar su codigo**.
Todo es aditivo: wheel + CI publish + tag.

### Que se hizo

1. **Empaquetado**: `poetry build` genero wheel + sdist del paquete raiz
   (`python_training-0.1.0-py3-none-any.whl` y `.tar.gz`).
2. **Verificacion**: `unzip -l dist/*.whl` confirmo que el wheel incluye
   `clean_arch/` (lab 16) y `rickmorty_orders/` (proyecto final).
3. **Prueba en venv limpio**: se instalo el wheel con `pip install` en un
   venv temporal y se verifico que ambos paquetes se importan.
4. **CI publish**: se creo `.github/workflows/publish.yml` que se dispara
   con tags `v*` y **simula** la publicacion (guarda el wheel como
   artefacto de GitHub Actions, sin subir a PyPI real).
5. **Tag de release**: se creara `v0.1.0` para disparar el workflow.

### Comandos ejecutados (reproducibles)

#### 1. Construir el wheel y sdist

    poetry build

Salida esperada:

    Building python-training (0.1.0)
      - Built python_training-0.1.0.tar.gz
      - Built python_training-0.1.0-py3-none-any.whl

Los archivos quedan en `dist/` (ignorado por `.gitignore`).

#### 2. Verificar el contenido del wheel

    unzip -l dist/python_training-0.1.0-py3-none-any.whl

Debe listar `clean_arch/...` y `rickmorty_orders/...`.

#### 3. Probar el wheel en un venv limpio

    python3.12 -m venv /tmp/test_wheel
    /tmp/test_wheel/bin/pip install dist/python_training-0.1.0-py3-none-any.whl
    /tmp/test_wheel/bin/python -c "import clean_arch, rickmorty_orders; print('OK')"
    rm -rf /tmp/test_wheel

Salida esperada: `OK`.

#### 4. Ver el workflow de publish

    cat .github/workflows/publish.yml

#### 5. Crear el tag de release (paso final)

    git tag -a v0.1.0 -m "Primera version del proyecto final"
    git push origin v0.1.0

Al hacer push del tag, GitHub Actions ejecuta `publish.yml`:
- Corre tests
- Construye el wheel
- Lo guarda como artefacto descargable

Ver el resultado en:
https://github.com/parisollie/python-training/actions

### Archivos creados/modificados

| Archivo | Cambio |
|---------|--------|
| `03_advanced/17_empaquetado_cicd/README.md` | este archivo |
| `.github/workflows/publish.yml` | workflow de publish (tag v*) |

### Notas de implementacion

- **`dist/` no se commitea**: ya esta en `.gitignore`. Los wheels son
  artefactos generados, no codigo.
- **Publicacion simulada**: el workflow guarda el wheel como artefacto de
  GitHub Actions en lugar de subirlo a PyPI. Esto evita depender de
  cuentas/tokens externos y no afecta al proyecto.
- **Para publicar de verdad**: en `publish.yml`, reemplazar el paso
  `actions/upload-artifact@v4` por `pypa/gh-action-pypi-publish@release/v1`
  y configurar `PYPI_TOKEN` en GitHub Secrets. El flujo es identico.
- **No se modifico el codigo del proyecto**: ni `rickmorty_orders` ni
  `clean_arch` cambiaron. El Modulo 17 es solo delivery.

## Conceptos clave

### ¿Por que PEP 20 importa aqui?
- "Simple es mejor que complejo" -> un wheel hace una cosa bien
- "Explícito es mejor que implícito" -> la version esta en pyproject.toml
- "Los errores nunca deben pasar silenciosamente" -> el CI falla si algo falla

### Cuando publicar en PyPI vs repositorio interno

| Caso | Donde publicar |
|------|----------------|
| Libreria open source | PyPI publico |
| Paquete interno de la empresa | Artifactory / Nexus / AWS CodeArtifact |
| Prototipo | TestPyPI |
| Codigo propietario | Repositorio interno (nunca PyPI) |

### Flujo completo de release

    1. Bump version: poetry version patch
    2. Commit: git commit -am "chore: bump version to 0.1.1"
    3. Tag: git tag v0.1.1
    4. Push tags: git push origin v0.1.1
    5. CI: corre tests + build + publish (trigger: tag v*)
    6. Verificar en PyPI / repositorio interno

### Docker: checklist de buenas practicas

- [ ] Multistage (builder + runtime)
- [ ] Usuario non-root
- [ ] .dockerignore agresivo
- [ ] HEALTHCHECK
- [ ] No instalar dev dependencies
- [ ] Pinear version base
- [ ] Escanear con trivy/docker scout
- [ ] Imagen final < 500 MB (idealmente)

## Checklist
- [x] Crear estructura del laboratorio
- [x] `poetry build` genera wheel + sdist
- [x] Verificar el contenido del wheel (`unzip -l dist/*.whl`)
- [x] Instalar el wheel en un venv limpio y probarlo
- [x] Extender CI con job `publish` (trigger tag v*)
- [x] Crear tag v0.1.0 y push
- [x] Verificar que el workflow corre en GitHub Actions
- [x] Documentar el proceso de release en el README
- [x] Commit del modulo

## Referencias
- PEP 440 — Version Identification: https://peps.python.org/pep-0440/
- PEP 517 — Build system interface: https://peps.python.org/pep-0517/
- Poetry — Publishing: https://python-poetry.org/docs/libraries/#publishing-to-pypi
- GitHub Actions docs: https://docs.github.com/en/actions
- pypa/gh-action-pypi-publish: https://github.com/pypa/gh-action-pypi-publish
- Docker best practices: https://docs.docker.com/develop/dev-best-practices/
- Trivy: https://aquasecurity.github.io/trivy/
- Azure Container Apps: https://learn.microsoft.com/en-us/azure/container-apps/

# Módulo 01 — Entorno y herramientas

## Objetivos
- Instalar y gestionar versiones de Python y entornos virtuales
- Configurar VS Code y herramientas de calidad
- Aplicar PEP 8 / PEP 20
- Automatizar calidad con black, isort, ruff y pre-commit

## Stack instalado
| Herramienta | Versión |
|-------------|---------|
| Python | 3.12.15 |
| Poetry | 2.5.1 |
| Git | 2.54.0 |
| ruff | 0.16.10 |
| black | 26.10.0 |
| isort | 9.0.2 |
| mypy | 2.4.0 |
| pytest | 9.1.1 |
| pre-commit | 4.6.2 |

## Laboratorio
Crear proyecto con Poetry, activar venv, instalar herramientas de calidad, configurar pre-commit y corregir infracciones PEP 8.

Estado: Completado

## Conceptos clave

### Por que Poetry
Reemplaza venv + pip + requirements.txt con un solo flujo basado en pyproject.toml.
- Un solo archivo de configuracion
- Resolucion automatica de conflictos
- poetry.lock garantiza versiones exactas
- Separa dependencias de produccion y desarrollo

### PEP 8 (estilo)
- Indentacion: 4 espacios
- Lineas: maximo 100 caracteres
- snake_case para funciones/variables
- PascalCase para clases
- UPPER_CASE para constantes

### PEP 20 (Zen of Python)
Ejecuta: python3.12 -c "import this"

## Checklist
- [x] Instalar Homebrew
- [x] Instalar Python 3.12
- [x] Instalar Poetry
- [x] Configurar Poetry
- [x] Crear estructura de carpetas
- [x] Configurar .gitignore
- [x] Inicializar Git
- [x] Crear pyproject.toml
- [x] Instalar herramientas de calidad
- [x] Configurar pre-commit
- [x] Primeros commits

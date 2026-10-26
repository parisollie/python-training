# Módulo 18 — CLI y automatización

## Objetivos
- Construir CLIs productivas y mantenibles con Typer
- Configurar por variables de entorno (pydantic-settings)
- Crear scripts de mantenimiento y automatización
- Exponer el CLI como entry point del paquete

## Contenidos clave

### Librerias para CLI en Python

| Libreria | Cuando usar |
|----------|-------------|
| **argparse** | stdlib, sin dependencias, CLIs simples |
| **click** | CLIs medianas, decoradores, muy usada |
| **Typer** | CLIs modernas con type hints, docs automaticas |

En este modulo usamos **Typer** porque:
- Basado en type hints (Python 3.6+)
- Genera `--help` automaticamente
- Documentacion con `--docs` (interfaz web)
- Menos boilerplate que click
- Escrito por el autor de FastAPI (misma filosofia)

### Typer basico

    import typer

    app = typer.Typer()

    @app.command()
    def hello(name: str) -> None:
        """Saluda a alguien."""
        typer.echo(f"Hola {name}")

    if __name__ == "__main__":
        app()

Ejecucion:

    python cli.py hello "Paul"
    # Hola Paul

    python cli.py hello --help
    # Muestra la ayuda automaticamente

### Comandos y subcomandos

    app = typer.Typer()

    users_app = typer.Typer()
    orders_app = typer.Typer()

    app.add_typer(users_app, name="users")
    app.add_typer(orders_app, name="orders")

    @users_app.command("list")
    def users_list() -> None:
        ...

    # Uso:
    # cli users list
    # cli orders create

### Options vs Arguments

    @app.command()
    def create(
        name: str,                                        # argumento (posicional)
        quantity: int = typer.Option(1, "--quantity", "-q"),  # opcion
        verbose: bool = typer.Option(False, "--verbose", "-v"),
    ) -> None:
        ...

    # Uso:
    # cli create "Rick" --quantity 2 --verbose
    # cli create "Rick" -q 2 -v

### Output formateado

    # Texto simple
    typer.echo("Hola")

    # Colores con rich (Typer lo soporta via rich)
    typer.secho("OK", fg=typer.colors.GREEN)
    typer.secho("Error", fg=typer.colors.RED, err=True)

    # JSON
    import json
    typer.echo(json.dumps(data, indent=2))

### Variables de entorno con pydantic-settings

    from pydantic_settings import BaseSettings

    class Settings(BaseSettings):
        api_url: str = "http://localhost:8000"
        timeout: float = 10.0

        model_config = SettingsConfigDict(env_prefix="CLI_")

    settings = Settings()
    # Lee CLI_API_URL, CLI_TIMEOUT del entorno

### Entry points (instalar el CLI con pip)

En `pyproject.toml`:

    [tool.poetry.scripts]
    rickmorty-orders = "rickmorty_orders.cli:app"

Despues de `poetry install`, el comando `rickmorty-orders` esta disponible
globalmente en el venv:

    rickmorty-orders --help
    rickmorty-orders orders list

### Patrones utiles

**Comando con confirmacion**:

    @app.command()
    def delete(order_id: str) -> None:
        if typer.confirm(f"Borrar orden {order_id}?"):
            ...

**Progreso** (con rich):

    from rich.progress import track

    for item in track(items, description="Procesando..."):
        ...

**Tablas** (con rich):

    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title="Orders")
    table.add_column("ID")
    table.add_column("Total")
    table.add_row("...", "...")
    console.print(table)

### Scripts de mantenimiento

Los scripts de mantenimiento son CLIs que automatizan tareas repetitivas:

- Backup de la DB
- Limpieza de logs viejos
- Migracion de datos
- Verificacion de salud
- Reportes periodicos

Ejemplo:

    @app.command()
    def backup(output: str = "backup.db") -> None:
        """Copia la DB a un archivo."""
        import shutil
        shutil.copy("rickmorty_orders.db", output)
        typer.secho(f"Backup guardado en {output}", fg="green")

## Laboratorio

CLI con Typer para gestionar ordenes consumiendo la API del proyecto final:

1. **Estructura**: paquete `rickmorty_orders.cli/` dentro del proyecto final
2. **Comandos**:
   - `orders list` -> lista ordenes
   - `orders create --email X --item Y` -> crear orden
   - `orders get <id>` -> obtener por id
   - `orders confirm <id>` -> confirmar
   - `orders cancel <id> --reason X` -> cancelar
3. **Config**: usa pydantic-settings (prefijo `CLI_`) para la API URL
4. **Entry point**: `rickmorty-orders` en `pyproject.toml`
5. **Tests**: con `typer.testing.CliRunner`
6. **Documentacion**: README del laboratorio + comandos de uso

## Conceptos clave

### ¿Por que PEP 20 importa aqui?
- "Simple es mejor que complejo" -> Typer: un decorador por comando, sin boilerplate
- "Explícito es mejor que implícito" -> los tipos estan en las firmas
- "La legibilidad cuenta" -> los comandos se leen como funciones

### Cuando usar argparse vs click vs Typer

| Situacion | Herramienta |
|-----------|-------------|
| Script de 10 lineas | argparse |
| CLI mediana (10-50 comandos) | click |
| CLI nueva con type hints | Typer |
| Legacy con click | click |

### Estructura recomendada de un CLI

    rickmorty_orders/
    └── cli/
        ├── __init__.py
        ├── main.py           # app Typer + subcomandos
        ├── config.py         # Settings (pydantic-settings)
        ├── client.py         # HTTP client hacia la API
        └── formatters.py     # helpers para tablas/colores

### Testing de CLIs

    from typer.testing import CliRunner

    runner = CliRunner()

    def test_hello() -> None:
        result = runner.invoke(app, ["hello", "Paul"])
        assert result.exit_code == 0
        assert "Hola Paul" in result.stdout

## Checklist
- [x] Crear estructura del CLI (paquete `cli/`)
- [x] Implementar subcomandos (list, create, get, confirm, cancel)
- [x] Config con pydantic-settings (prefijo `CLI_`)
- [x] Cliente HTTP hacia la API (httpx)
- [x] Output formateado (rich: tablas, colores)
- [x] Entry point `rickmorty-orders` en pyproject.toml
- [x] Tests con `CliRunner`
- [x] Correr ruff y mypy
- [x] Documentar en README del laboratorio
- [x] Commit del modulo

## Referencias
- Typer docs: https://typer.tiangolo.com/
- Click docs: https://click.palletsprojects.com/
- argparse docs: https://docs.python.org/3/library/argparse.html
- Rich docs: https://rich.readthedocs.io/
- pydantic-settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- Entry points: https://python-poetry.org/docs/pyproject/#scripts

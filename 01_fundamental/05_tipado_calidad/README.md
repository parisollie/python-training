# Módulo 05 — Tipado estático opcional y calidad

## Objetivos
- Anotar tipos y verificar estáticamente con mypy/pyright
- Hacer cumplir PEP 8 y documentar excepciones
- Integrar linters/formatters en CI (se profundiza en Módulo 17)

## Contenidos clave

### Type hints básicos (repaso)
- Tipos primitivos: int, str, float, bool, None
- Colecciones: list[int], dict[str, int], set[str], tuple[int, str]
- Opcionales: int | None (Python 3.10+)
- Funciones: def f(x: int) -> str

### Typing avanzado
- Union y el operador | (PEP 604)
- Optional (equivalente a X | None)
- Literal: valores específicos permitidos
- TypedDict: diccionarios con estructura fija
- Protocol: interfaces estructurales (duck typing con tipos)
- Final: constantes no reasignables
- Annotated: metadatos adicionales

### Sintaxis moderna de genéricos (PEP 695, Python 3.12)
- def funcion[T](x: T) -> T
- class Caja[T]: ...
- type ListaEnteros = list[int]

### mypy y pyright
- Verificación estática sin ejecutar el código
- Modo strict: la configuración más estricta
- Directivas: # type: ignore, # noqa
- Límites: código dinámico, metaprogramación, librerías sin stubs

### PEP 8 y PEP 20
- PEP 8: guía de estilo (indentación, longitud, nombres)
- PEP 20: Zen of Python (filosofía de diseño)
- Documentar excepciones locales con # noqa: CODE (comentario justificado)

### Herramientas de calidad
- ruff: linter + formatter ultrarrápido
- black: formatter estándar
- isort: orden de imports
- mypy: verificación de tipos
- pre-commit: hooks automáticos antes del commit

## Laboratorio

Anotar tipos avanzados en el código del laboratorio 04 (orders):

1. Usar Literal para estados
2. Usar TypedDict para JSON crudo
3. Usar Protocol para un repositorio abstracto
4. Verificar que todo sigue pasando mypy strict

## Conceptos clave

### ¿Por qué tipado estático si Python es dinámico?

- Detección temprana de errores (antes de ejecutar)
- Documentación viva (los tipos son la mejor doc)
- Autocompletado en el IDE más preciso
- Refactorización más segura
- Los tipos NO se ejecutan: son opcionales y no afectan performance

### Regla práctica: cuándo usar cada tipo

| Tipo | Cuándo usar |
|------|-------------|
| int, str, bool | Siempre, en cualquier firma |
| int \| None | Cuando un valor puede faltar |
| Literal["a", "b"] | Cuando solo hay opciones específicas |
| TypedDict | Cuando procesas JSON con estructura conocida |
| Protocol | Cuando quieres definir una interfaz sin herencia |
| Final | Constantes que no deben reasignarse |
| Annotated | Validación, metadatos (Pydantic, FastAPI) |

### Ejemplo: Literal

    from typing import Literal

    Status = Literal["Alive", "Dead", "unknown"]

    def clasificar(status: Status) -> str:
        ...

    clasificar("Alive")     # OK
    clasificar("Muerto")    # Error en mypy

### Ejemplo: TypedDict

    from typing import TypedDict

    class PersonajeJSON(TypedDict):
        id: int
        name: str
        status: str

    data: PersonajeJSON = {"id": 1, "name": "Rick", "status": "Alive"}
    print(data["name"])  # mypy sabe que es str

### Ejemplo: Protocol

    from typing import Protocol

    class Repositorio(Protocol):
        def guardar(self, item: str) -> None: ...
        def obtener(self, id: str) -> str | None: ...

    class EnMemoria:
        def __init__(self) -> None:
            self._data: dict[str, str] = {}
        def guardar(self, item: str) -> None:
            self._data[item] = item
        def obtener(self, id: str) -> str | None:
            return self._data.get(id)

    def usar_repo(repo: Repositorio) -> None:
        repo.guardar("hola")

    usar_repo(EnMemoria())  # OK, cumple el Protocol

### Documentar excepciones locales con noqa

    x = algo_raro()  # noqa: ANN001  # Justificación: viene de librería sin stubs

## Checklist
- [ ] Crear estructura del laboratorio
- [ ] Anotar con Literal
- [ ] Anotar con TypedDict
- [ ] Anotar con Protocol
- [ ] Correr mypy strict
- [ ] Correr ruff
- [ ] Documentar en README del laboratorio
- [ ] Commit del modulo

## Referencias
- Python docs — typing: https://docs.python.org/3/library/typing.html
- PEP 484 — Type Hints: https://peps.python.org/pep-0484/
- PEP 604 — Union operator |: https://peps.python.org/pep-0604/
- PEP 695 — Type Parameter Syntax: https://peps.python.org/pep-0695/
- mypy docs: https://mypy.readthedocs.io/
- ruff docs: https://docs.astral.sh/ruff/
- PEP 8: https://peps.python.org/pep-0008/
- PEP 20: https://peps.python.org/pep-0020/

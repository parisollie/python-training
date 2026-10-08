# Laboratorio 02 — JSON de Rick and Morty

Script que lee, filtra y agrega datos de la API de Rick and Morty, con manejo robusto de errores.

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1
- Datos descargados en `data/characters.json`

## Estructura

lab_02_json_rickmorty/
├── README.md              ← este archivo
├── main.py                ← script principal
├── data/
│   └── characters.json    ← datos de la API (20 personajes)
└── tests/                 ← tests con pytest (pendiente)

## Instalación

Desde la raíz del proyecto:

    poetry install

## Descargar los datos

Si el archivo `data/characters.json` no existe:

    curl -s "https://rickandmortyapi.com/api/character" -o 04_laboratorios/lab_02_json_rickmorty/data/characters.json

Fuente: https://rickandmortyapi.com/api/character

## Cómo ejecutar

### 1. Ejecutar el script principal

Desde la raíz del proyecto:

    poetry run python 04_laboratorios/lab_02_json_rickmorty/main.py

Salida esperada:

    🚀 Laboratorio 02 — Rick and Morty JSON

    📁 Leyendo: .../data/characters.json

    📋 Total de personajes: 20

    ID    Nombre                    Estado     Especie
    ------------------------------------------------------------
    1     Rick Sanchez              Alive      Human
    2     Morty Smith               Alive      Human
    ...

### 2. Probar el manejo de errores

#### Archivo no encontrado

    poetry run python -c "
    from pathlib import Path
    import sys
    sys.path.insert(0, '04_laboratorios/lab_02_json_rickmorty')
    from main import load_characters
    result = load_characters(Path('no_existe.json'))
    print(f'Resultado: {result}')
    "

Salida esperada:

    ❌ Error: no se encontró el archivo no_existe.json
    Resultado: []

#### JSON inválido

    echo "esto no es json" > /tmp/invalid.json

    poetry run python -c "
    from pathlib import Path
    import sys
    sys.path.insert(0, '04_laboratorios/lab_02_json_rickmorty')
    from main import load_characters
    result = load_characters(Path('/tmp/invalid.json'))
    print(f'Resultado: {result}')
    "

    rm /tmp/invalid.json

Salida esperada:

    ❌ Error: el archivo no es un JSON válido: Expecting value: line 1 column 1 (char 0)
    Resultado: []

## Verificación de calidad

### 3. Linter (ruff)

    poetry run ruff check 04_laboratorios/lab_02_json_rickmorty/main.py

Salida esperada:

    All checks passed!

Si hay errores corregibles automáticamente:

    poetry run ruff check --fix 04_laboratorios/lab_02_json_rickmorty/main.py

### 4. Tipos (mypy)

    poetry run mypy 04_laboratorios/lab_02_json_rickmorty/main.py

Salida esperada:

    Success: no issues found in 1 source file

### 5. Formato (pre-commit, todos los hooks)

    poetry run pre-commit run --all-files

Salida esperada:

    trim trailing whitespace.................................................Passed
    fix end of files.........................................................Passed
    check yaml...............................................................Passed
    check toml...............................................................Passed
    check for added large files..............................................Passed
    check for merge conflicts................................................Passed
    check for case conflicts.................................................Passed
    detect private key.......................................................Passed
    ruff.....................................................................Passed
    ruff-format..............................................................Passed
    mypy.....................................................................Passed

## Comandos rápidos (resumen)

    # Ejecutar
    poetry run python 04_laboratorios/lab_02_json_rickmorty/main.py

    # Calidad
    poetry run ruff check 04_laboratorios/lab_02_json_rickmorty/main.py
    poetry run mypy 04_laboratorios/lab_02_json_rickmorty/main.py
    poetry run pre-commit run --all-files

## Notas de implementación

- DATA_FILE: ruta construida con Path(__file__).parent / "data" / "characters.json", por lo que funciona desde cualquier directorio.
- load_characters(path): lee el JSON y devuelve la lista de personajes. Maneja:
  - FileNotFoundError: el archivo no existe
  - json.JSONDecodeError: el archivo no es JSON válido
  - PermissionError: no hay permisos de lectura
  - Estructura inesperada: el JSON no tiene results o no es lista
- show_characters(characters): imprime los personajes en formato tabla alineada.
- Type hints: todas las funciones están anotadas con list[dict[str, Any]], Path, None.

## Estado

- [x] Lectura de JSON con manejo de errores
- [x] Mostrar personajes en tabla
- [x] Pasar ruff, mypy, pre-commit
- [ ] Filtros (por estado, especie)
- [ ] Agregaciones (contar por especie, top episodios)
- [ ] Pattern matching
- [ ] Tests con pytest

## Referencias

- Rick and Morty API — Documentación: https://rickandmortyapi.com/documentation
- Python docs — json: https://docs.python.org/3/library/json.html
- Python docs — pathlib: https://docs.python.org/3/library/pathlib.html

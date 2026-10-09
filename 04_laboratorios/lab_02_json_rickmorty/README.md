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
- [x] Filtros (por estado, especie)
- [ ] Agregaciones (contar por especie, top episodios)
- [x] Pattern matching
- [x] Tests con pytest

## Referencias

- Rick and Morty API — Documentación: https://rickandmortyapi.com/documentation
- Python docs — json: https://docs.python.org/3/library/json.html
- Python docs — pathlib: https://docs.python.org/3/library/pathlib.html

## Funciones implementadas

### filter_by_status(characters, status)

Filtra los personajes por estado (case-insensitive).

Ejemplo:

    alive = filter_by_status(characters, "Alive")

### count_by_species(characters)

Cuenta cuantos personajes hay por especie. Devuelve un diccionario ordenado de mayor a menor.

Ejemplo:

    species_count = count_by_species(characters)

## Resultados con los 20 personajes

| Filtro | Cantidad |
|--------|----------|
| Vivos | 8 |
| Muertos | 6 |
| Desconocidos | 6 |
| Total | 20 |

| Especie | Cantidad |
|---------|----------|
| Human | 15 |
| Alien | 5 |
| Total | 20 |

## Pattern matching con match/case

Funcion `classify_character(character)` que usa `match / case` (Python 3.10+) para clasificar personajes segun su estado y especie.

Reglas:

| Estado | Especie | Clasificacion |
|--------|---------|---------------|
| alive | human | Vivo humano |
| alive | alien | Vivo alien |
| dead | human | Muerto humano |
| dead | alien | Muerto alien |
| alive | otra | Vivo (otra especie) |
| dead | otra | Muerto (otra especie) |
| otro | cualquiera | Sin clasificar |

Ejemplo de uso:

    classification = classify_character(character)
    print(classification)

Ejemplo de salida (primeros 5):

      Rick Sanchez                   Vivo humano
      Morty Smith                    Vivo humano
      Summer Smith                   Vivo humano
      Beth Smith                     Vivo humano
      Jerry Smith                    Vivo humano

## Probar las funciones individualmente

Para probar cada funcion sin ejecutar el script completo, usa `python -c`.

### Probar filter_by_status

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_02_json_rickmorty')
    from pathlib import Path
    from main import load_characters, filter_by_status
    chars = load_characters(Path('04_laboratorios/lab_02_json_rickmorty/data/characters.json'))
    alive = filter_by_status(chars, 'Alive')
    print(f'Vivos: {len(alive)}')
    for c in alive:
        print(f'  - {c[\"name\"]}')
    "

Salida esperada:

    Vivos: 8
      - Rick Sanchez
      - Morty Smith
      ...

### Probar count_by_species

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_02_json_rickmorty')
    from pathlib import Path
    from main import load_characters, count_by_species
    chars = load_characters(Path('04_laboratorios/lab_02_json_rickmorty/data/characters.json'))
    counts = count_by_species(chars)
    for species, n in counts.items():
        print(f'{species}: {n}')
    "

Salida esperada:

    Human: 15
    Alien: 5

### Probar classify_character

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_02_json_rickmorty')
    from pathlib import Path
    from main import load_characters, classify_character
    chars = load_characters(Path('04_laboratorios/lab_02_json_rickmorty/data/characters.json'))
    for c in chars[:5]:
        print(f'{c[\"name\"]}: {classify_character(c)}')
    "

Salida esperada:

    Rick Sanchez: 👨 Vivo humano
    Morty Smith: 👨 Vivo humano
    Summer Smith: 👨 Vivo humano
    Beth Smith: 👨 Vivo humano
    Jerry Smith: 👨 Vivo humano

## Clonar este laboratorio

    git clone https://github.com/parisollie/python-training.git
    cd python-training
    poetry install

    # Descargar datos si no existen
    curl -s "https://rickandmortyapi.com/api/character" -o 04_laboratorios/lab_02_json_rickmorty/data/characters.json

    # Ejecutar
    poetry run python 04_laboratorios/lab_02_json_rickmorty/main.py

## Tests con pytest

Se han escrito 26 tests que cubren las 5 funciones del laboratorio.

### Ejecutar todos los tests

    poetry run pytest 04_laboratorios/lab_02_json_rickmorty/tests/ -v

Salida esperada:

    26 passed in 0.01s

### Ejecutar con cobertura

    poetry run pytest 04_laboratorios/lab_02_json_rickmorty/tests/ --cov=04_laboratorios/lab_02_json_rickmorty --cov-report=term-missing

Salida esperada:

    main.py                               93     29    69%
    tests/test_classify_character.py      14      0   100%
    tests/test_filters.py                 34      0   100%
    tests/test_load_characters.py         30      0   100%
    tests/test_show_characters.py         22      0   100%
    TOTAL                                193     29    85%

### Ejecutar un archivo de tests especifico

    poetry run pytest 04_laboratorios/lab_02_json_rickmorty/tests/test_filters.py -v

### Archivos de tests

| Archivo | Que cubre | Tests |
|---------|-----------|-------|
| test_load_characters.py | load_characters (exito + 4 errores) | 5 |
| test_show_characters.py | show_characters (vacio, tabla, campos faltantes) | 3 |
| test_filters.py | filter_by_status y count_by_species | 8 |
| test_classify_character.py | classify_character (parametrizado) | 10 |

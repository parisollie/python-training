# Módulo 02 — Fundamentos del lenguaje

## Objetivos
- Manejar estructuras de datos y control de flujo
- Implementar manejo de errores robusto
- Usar pattern matching en casos adecuados
- Aplicar expresiones regulares cuando sea necesario

## Contenidos clave

### Sintaxis y variables
- Indentación con 4 espacios (PEP 8)
- Variables y alcance (local, global, nonlocal)
- Asignación múltiple y desempaquetado

### Tipos básicos
- int, float, str, bool, None
- Conversión entre tipos: int(), str(), float()

### Colecciones
- list: ordenada, mutable
- tuple: ordenada, inmutable
- dict: pares clave-valor
- set: sin duplicados, sin orden

### Control de flujo
- if / elif / else
- for / while
- break / continue / else en bucles
- Pattern matching (match / case) — Python 3.10+

### Excepciones
- try / except / else / finally
- raise y excepciones personalizadas
- Manejo de errores de archivo y formato

### Expresiones regulares
- Módulo re
- Patrones básicos: \d, \w, \s, ., *, +, ?
- Funciones: re.search, re.findall, re.sub

## Laboratorio

Script que lee el JSON de la API de Rick and Morty, filtra y agrega datos, y maneja errores de archivo/formato.

**Fuente de datos:** https://rickandmortyapi.com/api/character

## Conceptos clave

### ¿Por qué PEP 20 importa aquí?
- "Simple es mejor que complejo" → usar listas y dicts sin sobre-ingeniería
- "Plano es mejor que anidado" → evitar if dentro de if dentro de if
- "Los errores nunca deben pasar silenciosamente" → siempre manejar excepciones

### Estructuras de datos: cuándo usar cada una
| Estructura | Uso |
|------------|-----|
| list | Colección ordenada que puede cambiar |
| tuple | Colección ordenada que NO cambia |
| dict | Acceso rápido por clave |
| set | Verificar pertenencia, eliminar duplicados |

### Manejo de errores típico (ejemplo de código, NO se ejecuta)
try:
    datos = json.load(archivo)
except FileNotFoundError:
    print("Archivo no encontrado")
except json.JSONDecodeError as e:
    print(f"JSON inválido: {e}")

### Pattern matching (Python 3.10+) — ejemplo de código, NO se ejecuta
match status:
    case "Alive":
        print("Vivo")
    case "Dead":
        print("Muerto")
    case _:
        print("Desconocido")

## Checklist
- [ ] Crear estructura del laboratorio
- [ ] Descargar JSON de la API de Rick and Morty
- [ ] Escribir script main.py
- [ ] Aplicar tipos y estructuras de datos
- [ ] Manejar excepciones correctamente
- [ ] Correr ruff y mypy
- [ ] Escribir tests con pytest
- [ ] Commit del módulo

## Referencias
- [Python docs — Estructuras de datos](https://docs.python.org/3/tutorial/datastructures.html)
- [Python docs — Errores y excepciones](https://docs.python.org/3/tutorial/errors.html)
- [PEP 636 — Pattern Matching](https://peps.python.org/pep-0636/)
- [Rick and Morty API](https://rickandmortyapi.com/documentation)

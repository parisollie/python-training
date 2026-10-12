# Módulo 04 — Objetos y modelos de datos

## Objetivos
- Modelar entidades con comportamientos y validaciones
- Serializar y validar entradas/salidas

## Contenidos clave

### Clases y objetos
- Definicion con class
- Constructor __init__ y self
- Atributos de instancia vs atributos de clase
- Metodos de instancia, clase y estaticos

### Herencia y composicion
- Herencia simple y multiple
- super()
- Composicion: "tiene un" vs herencia: "es un"
- Cuando preferir composicion sobre herencia

### Dunder methods (magic methods)
- __init__: constructor
- __repr__: representacion para debugging
- __str__: representacion para el usuario
- __eq__: igualdad
- __lt__, __le__, __gt__, __ge__: ordenamiento
- __hash__: para usar en sets y dicts
- __len__, __getitem__, __iter__: protocolos de contenedor

### dataclasses
- Decorador @dataclass
- Generacion automatica de __init__, __repr__, __eq__
- field(default_factory=...) para mutables
- frozen=True para inmutabilidad
- order=True para comparaciones
- Cálculos derivados con @property

### attrs (alternativa)
- Libreria externa mas antigua que dataclasses
- Validadores y converters
- Diferencias con dataclasses

### Pydantic
- Validacion automatica de tipos
- Modelos con BaseModel
- Field con constraints
- Serializacion con model_dump y model_dump_json
- Validacion con model_validate
- Modelos inmutables (frozen)
- Conversion desde/hacia dict y JSON
- Uso tipico: schemas de API (input/output)

## Laboratorio

Modelar ordenes de compra con dos enfoques:

1. dataclass Order con cálculos derivados y comparaciones
2. Modelos Pydantic (OrderIn/OrderOut) y conversion a entidad

## Conceptos clave

### ¿Por que PEP 20 importa aqui?
- "Simple es mejor que complejo" -> dataclass si no necesitas validacion, Pydantic si la necesitas
- "Explícito es mejor que implícito" -> declarar tipos claramente
- "Los errores nunca deben pasar silenciosamente" -> Pydantic valida al construir

### Cuando usar cada herramienta

| Herramienta | Cuando usar |
|-------------|-------------|
| class clasica | Comportamiento complejo, herencia multiple, metaprogramacion |
| dataclass | Datos + poca logica, entidades de dominio, DTOs internos |
| attrs | Necesitas validadores sin Pydantic, o compatibilidad con codigo viejo |
| Pydantic | Validacion de entrada/salida, APIs, configuracion, JSON serialization |

### Ejemplo: dataclass basica

    from dataclasses import dataclass, field

    @dataclass
    class Order:
        id: str
        customer: str
        items: list[str] = field(default_factory=list)

        @property
        def total_items(self) -> int:
            return len(self.items)

### Ejemplo: modelo Pydantic

    from pydantic import BaseModel, Field

    class OrderIn(BaseModel):
        customer: str = Field(min_length=1, max_length=100)
        items: list[str] = Field(min_length=1)

    class OrderOut(BaseModel):
        id: str
        customer: str
        items: list[str]
        total_items: int

### Dunder methods mas usados

    @dataclass(order=True)
    class Precio:
        monto: float

    p1 = Precio(10.0)
    p2 = Precio(20.0)

    print(p1 == p2)     # False (compara por __eq__)
    print(p1 < p2)      # True (compara por __lt__)
    print(repr(p1))     # Precio(monto=10.0)

## Checklist
- [ ] Instalar Pydantic
- [ ] Crear estructura del laboratorio
- [ ] Implementar dataclass Order
- [ ] Implementar modelos Pydantic OrderIn/OrderOut
- [ ] Escribir tests con pytest
- [ ] Correr ruff y mypy
- [ ] Documentar en README del laboratorio
- [ ] Commit del modulo

## Referencias
- Python docs — Clases: https://docs.python.org/3/tutorial/classes.html
- Python docs — dataclasses: https://docs.python.org/3/library/dataclasses.html
- Python docs — Modelo de datos (dunder methods): https://docs.python.org/3/reference/datamodel.html
- Pydantic docs: https://docs.pydantic.dev/
- attrs docs: https://www.attrs.org/
- PEP 557 — Data Classes: https://peps.python.org/pep-0557/

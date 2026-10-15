# Módulo 13 — Patrones de diseno

## Objetivos
- Implementar patrones relevantes con ejemplos reales
- Identificar antipatrones y senales de refactor
- Aplicar patrones idiomaticos de Python

## Contenidos clave

### Que es un patron de diseno
Solucion reutilizable a un problema comun de diseno.
No es codigo copiable, es un **concepto** que se adapta al contexto.

### Categorias (GoF — Gang of Four)

**Creacionales** (como se crean objetos):
- Factory Method: crear objetos sin especificar la clase exacta
- Abstract Factory: familias de objetos relacionados
- Builder: construir objetos complejos paso a paso
- Singleton: una sola instancia (cuidado, suele ser antipatron)

**Estructurales** (como se componen):
- Adapter: adaptar una interfaz a otra
- Facade: simplificar un subsistema complejo
- Composite: tratar objetos individuales y compuestos igual
- Decorator: agregar comportamiento sin modificar la clase
- Proxy: controlar acceso a un objeto

**De comportamiento** (como interactuan):
- Strategy: intercambiar algoritmos
- Observer: notificar cambios a multiples interesados
- Command: encapsular una accion
- Mediator: centralizar comunicacion
- Template Method: esqueleto con pasos variables
- State: comportamiento que cambia con el estado

### Patrones idiomaticos en Python
- Decoradores (@decorador) -> reemplazan Decorator clasico
- Context managers (with) -> reemplazan Template Method
- dataclasses -> reemplazan Builder simple
- functools.lru_cache -> reemplaza Proxy de cache
- Generadores -> reemplazan Iterator

**Regla:** antes de implementar el patron "clasico", verificar si Python ya tiene una forma idiomatica.

## Laboratorio

Implementar 4 patrones con ejemplos reales:

1. **Strategy**: calculadoras de precio (normal, premium, vip)
2. **Decorator**: cache de llamadas costosas
3. **Adapter**: adaptar un proveedor externo (API vieja) a la interfaz nueva
4. **Factory**: crear notificadores segun configuracion

## Conceptos clave

### ¿Por que PEP 20 importa aqui?
- "Simple es mejor que complejo" -> no usar patron si no hace falta
- "Explícito es mejor que implícito" -> Protocol + nombre claro
- "La legibilidad cuenta" -> el patron debe comunicar intencion

### Cuando usar cada patron

| Patron | Cuando usar |
|--------|-------------|
| Strategy | Multiples algoritmos intercambiables |
| Decorator | Agregar comportamiento sin tocar la clase |
| Adapter | Integrar API externa con interfaz distinta |
| Factory | Crear objetos segun configuracion |
| Observer | Notificar cambios a varios interesados |
| Singleton | Estado global unico (rara vez justificado) |

### Antipatrones comunes
- **God Object**: una clase hace todo
- **Singleton global**: dificil de testear
- **Anemic Domain Model**: entidades sin comportamiento
- **Primitive Obsession**: usar str/int para conceptos del dominio
- **Copy-paste inheritance**: heredar solo para reutilizar codigo

### Ejemplo: Strategy

    from typing import Protocol

    class PricingStrategy(Protocol):
        def calculate(self, subtotal: float) -> float: ...

    class NormalPricing:
        def calculate(self, subtotal: float) -> float:
            return subtotal

    class PremiumPricing:
        def calculate(self, subtotal: float) -> float:
            return subtotal * 0.9  # 10% off

    class VipPricing:
        def calculate(self, subtotal: float) -> float:
            return subtotal * 0.8  # 20% off

    # Uso:
    pricing: PricingStrategy = PremiumPricing()
    total = pricing.calculate(100.0)  # 90.0

### Ejemplo: Decorator (idiomatico con functools)

    from functools import wraps

    def cache(func):
        """Decorator simple de cache."""
        memo = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            if key not in memo:
                memo[key] = func(*args, **kwargs)
            return memo[key]

        return wrapper

    @cache
    def fibonacci(n: int) -> int:
        if n < 2:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)

### Ejemplo: Adapter

    class PaymentGateway(Protocol):
        def pay(self, amount: float) -> bool: ...

    class OldPaymentAPI:
        def make_payment(self, cents: int) -> dict:  # API vieja
            return {"status": "ok", "cents": cents}

    class OldPaymentAdapter:
        """Adapta OldPaymentAPI a PaymentGateway."""
        def __init__(self, old_api: OldPaymentAPI) -> None:
            self._api = old_api

        def pay(self, amount: float) -> bool:
            cents = int(amount * 100)
            result = self._api.make_payment(cents)
            return result["status"] == "ok"

### Ejemplo: Factory

    def create_notifier(kind: str) -> Notifier:
        if kind == "email":
            return EmailNotifier()
        if kind == "sms":
            return SmsNotifier()
        if kind == "console":
            return ConsoleNotifier()
        raise ValueError(f"Tipo desconocido: {kind}")

## Checklist
- [ ] Crear estructura del laboratorio
- [ ] Implementar Strategy (precios)
- [ ] Implementar Decorator (cache)
- [ ] Implementar Adapter (API externa)
- [ ] Implementar Factory (notificadores)
- [ ] Tests con pytest
- [ ] Correr ruff y mypy
- [ ] Documentar en README del laboratorio
- [ ] Commit del modulo

## Referencias
- Refactoring Guru: https://refactoring.guru/design-patterns
- GoF — Design Patterns (libro)
- Python docs — functools: https://docs.python.org/3/library/functools.html
- Python docs — abc: https://docs.python.org/3/library/abc.html
- Python docs — typing.Protocol: https://docs.python.org/3/library/typing.html#typing.Protocol
- Real Python — Design Patterns: https://realpython.com/tutorials/design-patterns/

# Laboratorio 13 — Patrones de diseño

4 patrones de diseño implementados con ejemplos reales y tests:

1. **Strategy**: calculadoras de precio intercambiables
2. **Decorator**: cache, retry y logging (idiomáticos) + decoradores clásicos
3. **Adapter**: adaptar APIs externas a una interfaz interna
4. **Factory**: crear notificadores según configuración (con registro extensible)

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1

## Estructura

```text
lab_13_patterns/
├── README.md              ← este archivo
├── strategy.py            ← Strategy: 4 calculadoras de precio
├── decorator.py           ← Decorator: cache, retry, log_calls + envuelven clases
├── adapter.py             ← Adapter: Old y Modern Payment
├── factory.py             ← Factory: registro de notifiers
└── tests/
    ├── __init__.py
    ├── conftest.py        ← resetea el registro de factory entre tests
    ├── test_strategy.py   ← 15 tests
    ├── test_decorator.py  ← 13 tests
    ├── test_adapter.py    ← 9 tests
    └── test_factory.py    ← 14 tests
```

## 1. Strategy — calculadoras de precio

### El problema
Diferentes clientes necesitan diferentes descuentos. Un `if/elif` dentro del `Cart` sería frágil.

### La solución
Cada Strategy encapsula un algoritmo de descuento.

    from strategy import Cart, PremiumPricing, VipPricing

    cart = Cart()
    cart.add_item(100.0)
    cart.change_pricing(PremiumPricing())   # 10% off
    print(cart.total())  # 90.0

    cart.change_pricing(VipPricing())       # 20% off
    print(cart.total())  # 80.0

### Strategies disponibles

| Strategy | Descuento |
|----------|-----------|
| `NormalPricing` | 0% |
| `PremiumPricing` | 10% |
| `VipPricing` | 20% |
| `SeasonalPricing` | 5% / 15% / 25% escalonado |

### Ejemplo completo

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_13_patterns')
    from strategy import Cart, PremiumPricing, VipPricing, SeasonalPricing

    cart = Cart()
    cart.add_item(100.0)
    cart.add_item(50.0)

    print(f'Subtotal: {cart.subtotal()}')
    print(f'Normal:   {cart.total()}')
    cart.change_pricing(PremiumPricing())
    print(f'Premium:  {cart.total()}')
    cart.change_pricing(VipPricing())
    print(f'VIP:      {cart.total()}')
    cart.change_pricing(SeasonalPricing())
    print(f'Seasonal: {cart.total()}')
    "

Salida esperada:

    Subtotal: 150.0
    Normal:   150.0
    Premium:  135.0
    VIP:      120.0
    Seasonal: 127.5

## 2. Decorator — agregar comportamiento sin tocar la clase

### Enfoque idiomatico (funciones)

    from decorator import cache, retry, log_calls

    @cache
    def lento(x: int) -> int:
        print("Calculando...")
        return x * 2

    lento(5)  # imprime "Calculando..."
    lento(5)  # NO imprime (cacheado)

    @retry(max_attempts=3, delay=0.01)
    def inestable() -> str:
        ...

    @log_calls
    def suma(a: int, b: int) -> int:
        return a + b

### Enfoque clásico (envolver objetos)

    from decorator import Notifier, LoggedNotifier

    notifier = LoggedNotifier(Notifier())
    notifier.send("hola")
    notifier.send("mundo")
    print(notifier.log)  # ['hola', 'mundo']

### Ejemplo completo

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_13_patterns')
    from decorator import cache, retry, log_calls, Notifier, LoggedNotifier

    # Cache
    llamadas = {'n': 0}

    @cache
    def doble(x):
        llamadas['n'] += 1
        return x * 2

    doble(5); doble(5); doble(5)
    print(f'Cache: {llamadas[\"n\"]} llamadas reales')

    # Retry
    intentos = {'n': 0}

    @retry(max_attempts=3, delay=0.001)
    def inestable():
        intentos['n'] += 1
        if intentos['n'] < 3:
            raise ValueError('fallo')
        return 'ok'

    print(f'Retry: {inestable()} en {intentos[\"n\"]} intentos')

    # Log
    @log_calls
    def suma(a, b):
        return a + b

    suma(1, 2); suma(3, 4)
    print(f'Log: {len(suma.calls)} llamadas')

    # Decorator clasico
    n = LoggedNotifier(Notifier())
    n.send('hola'); n.send('mundo')
    print(f'Log clase: {n.log}')
    "

Salida esperada:

    Cache: 1 llamadas reales
    Retry: ok en 3 intentos
    Log: 2 llamadas
    Log clase: ['hola', 'mundo']

## 3. Adapter — adaptar APIs externas

### El problema
Dos APIs externas con interfaces distintas:
- `OldPaymentAPI.make_payment(cents, customer) -> dict` (centavos, dict)
- `ModernPaymentAPI.process(amount, user) -> None` (float, excepciones)

Pero nuestro dominio espera: `PaymentGateway.pay(amount, user_id) -> bool`.

### La solución
Un Adapter por cada API externa.

    from adapter import CheckoutService, OldPaymentAdapter, OldPaymentAPI

    api = OldPaymentAPI()
    service = CheckoutService(OldPaymentAdapter(api))
    print(service.checkout(10.50, "user-1"))

### Ejemplo completo

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_13_patterns')
    from adapter import (
        OldPaymentAPI, OldPaymentAdapter,
        ModernPaymentAPI, ModernPaymentAdapter,
        FailingPaymentAPI, CheckoutService,
    )

    # Via API vieja
    old = OldPaymentAPI()
    service = CheckoutService(OldPaymentAdapter(old))
    print(service.checkout(10.50, 'user-1'))
    print(f'  API calls: {old.calls}')

    # Via API moderna
    modern = ModernPaymentAPI()
    service = CheckoutService(ModernPaymentAdapter(modern))
    print(service.checkout(20.0, 'user-2'))

    # Via API que falla
    service = CheckoutService(OldPaymentAdapter(FailingPaymentAPI()))
    print(service.checkout(5.0, 'user-3'))
    "

Salida esperada:

    Pago exitoso de $10.5 para user-1
      API calls: [{'cents': 1050, 'customer': 'user-1'}]
    Pago exitoso de $20.0 para user-2
    Pago fallido de $5.0 para user-3

## 4. Factory — crear objetos segun configuracion

### Dos variantes

**Simple (if/elif):**

    from factory import create_notifier_simple
    notifier = create_notifier_simple("email")

**Con registro (extensible, OCP):**

    from factory import create_notifier, register

    class WebhookNotifier:
        def send(self, message: str) -> str:
            return f"webhook:{message}"

    register("webhook", WebhookNotifier)
    n = create_notifier("webhook")

### Ejemplo completo

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_13_patterns')
    from factory import create_notifier, create_notifier_simple, register

    # Simple
    n = create_notifier_simple('console')
    print(n.send('hola'))

    # Registro
    n = create_notifier('email')
    print(n.send('hola'))

    # Extender sin tocar la funcion
    class CustomNotifier:
        def send(self, message):
            return f'custom:{message}'

    register('custom', CustomNotifier)
    n = create_notifier('custom')
    print(n.send('hola'))

    # Error
    try:
        create_notifier('desconocido')
    except ValueError as e:
        print(f'Error: {e}')
    "

Salida esperada:

    [CONSOLE] hola
    console:hola
    email:hola
    custom:hola
    Error: Tipo desconocido: desconocido. Registrados: [...]

## Cómo ejecutar los tests

    poetry run pytest 04_laboratorios/lab_13_patterns/tests/ -v

Salida esperada:

    51 passed in 0.08s

### Con cobertura

    poetry run pytest 04_laboratorios/lab_13_patterns/tests/ --cov=04_laboratorios/lab_13_patterns --cov-report=term-missing

### Archivos de tests

| Archivo | Qué cubre | Tests |
|---------|-----------|-------|
| test_strategy.py | Cart, 4 PricingStrategy, cambio runtime | 15 |
| test_decorator.py | cache, retry, log_calls, decoradores clásicos | 13 |
| test_adapter.py | OldPaymentAdapter, ModernPaymentAdapter, CheckoutService | 9 |
| test_factory.py | create_notifier_simple, create_notifier, registro | 14 |

## Verificación de calidad

    poetry run ruff check 04_laboratorios/lab_13_patterns/
    poetry run mypy 04_laboratorios/lab_13_patterns/
    poetry run pre-commit run --all-files

## Notas de implementación

### Patrones idiomáticos en Python

Antes de implementar el patrón "clásico", verificar si Python ya tiene una forma idiomatica:

| Patrón clásico | Alternativa Python |
|----------------|---------------------|
| Decorator (GoF) | `@decorador` con `functools.wraps` |
| Template Method | Context managers (`with`) |
| Builder simple | `@dataclass` con defaults |
| Proxy de cache | `functools.lru_cache` |
| Iterator (GoF) | Generadores (`yield`) |
| Singleton | Módulo con constantes o `@functools.cache` |

### Protocol en lugar de ABC

Usamos `Protocol` (PEP 544) para las interfaces:
- `PricingStrategy`
- `PaymentGateway`
- `Notifier`

Ventajas:
- Duck typing tipado
- Sin herencia forzada
- Compatible con clases existentes

### Factory con registro (OCP)

La versión con `_REGISTRY` cumple **Open/Closed**:
- Se **extiende** con `register()` (agregar entradas)
- **No se modifica** `create_notifier()` al agregar tipos

### Ruff UP047 — PEP 695

Los decoradores `cache`, `retry` y `log_calls` usan la sintaxis moderna:

    def cache[F: Callable[..., Any]](func: F) -> F:
        ...

En lugar del clásico:

    F = TypeVar("F", bound=Callable[..., Any])
    def cache(func: F) -> F:
        ...

La primera es PEP 695 (Python 3.12+) y ruff la prefiere.

### LSP en adapter

`FailingPaymentAPI` hereda de `OldPaymentAPI` para cumplir el tipo (LSP):
- La firma del método es idéntica
- Cambia el **comportamiento** (siempre falla), no la **interfaz**
- Puede sustituir a `OldPaymentAPI` en `OldPaymentAdapter` sin problemas

## Comandos rápidos (resumen)

    # Tests
    poetry run pytest 04_laboratorios/lab_13_patterns/tests/ -v

    # Calidad
    poetry run ruff check 04_laboratorios/lab_13_patterns/
    poetry run mypy 04_laboratorios/lab_13_patterns/

    # Ejemplos (ver README más arriba)

## Estado

- [x] Estructura del laboratorio
- [x] Strategy (4 calculadoras de precio)
- [x] Decorator (cache, retry, log_calls + clases)
- [x] Adapter (old + modern + failing)
- [x] Factory (simple + registro extensible)
- [x] 51 tests
- [x] ruff + mypy OK
- [x] Documentación completa

## Clonar este laboratorio

    git clone https://github.com/parisollie/python-training.git
    cd python-training
    poetry install

    # Tests
    poetry run pytest 04_laboratorios/lab_13_patterns/tests/ -v

## Referencias

- Refactoring Guru: https://refactoring.guru/design-patterns
- GoF — Design Patterns (libro)
- Python docs — functools: https://docs.python.org/3/library/functools.html
- Python docs — abc: https://docs.python.org/3/library/abc.html
- Python docs — typing.Protocol: https://docs.python.org/3/library/typing.html#typing.Protocol
- PEP 544 — Protocols: https://peps.python.org/pep-0544/
- PEP 695 — Type Parameter Syntax: https://peps.python.org/pep-0695/
- Real Python — Design Patterns: https://realpython.com/tutorials/design-patterns/

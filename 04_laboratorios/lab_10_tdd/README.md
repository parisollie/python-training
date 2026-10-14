# Laboratorio 10 — Pruebas y TDD

Carrito de compras con descuentos, implementado con TDD y probado con 3 técnicas complementarias: tests clásicos, mocking y property-based testing.

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1
- pytest 9.1.1, pytest-cov 7.1.0, hypothesis 6.169.1

## Estructura

lab_10_tdd/
├── README.md              ← este archivo
├── cart.py                ← Cart + UserService (Protocol) + InMemoryUserService
└── tests/
    ├── conftest.py        ← fixtures (cart, premium_cart, premium_service)
    ├── test_cart.py       ← 18 tests clásicos
    ├── test_mocking.py    ← 7 tests con unittest.mock
    └── test_properties.py ← 8 tests con Hypothesis

## Reglas de negocio

### Subtotal
Suma de los precios de todos los items.

### Descuento por monto
| Subtotal | Descuento |
|----------|-----------|
| <= 100 | 0% |
| > 100 y <= 500 | 10% |
| > 500 | 20% |

### Descuento premium
Si el usuario es premium: +5% adicional.

### Total
`total = subtotal - descuento`

## Clases

### `UserService` (Protocol)

Interfaz para consultar si un usuario es premium.

    class UserService(Protocol):
        def is_premium(self, user_id: str) -> bool: ...

### `InMemoryUserService`

Implementación en memoria para tests.

    service = InMemoryUserService(premium_users={"user-1"})
    service.is_premium("user-1")  # True

### `Cart`

    cart = Cart()
    cart.add_item(50.0)
    cart.add_item(100.0)
    cart.subtotal()   # 150.0
    cart.discount()   # 15.0
    cart.total()      # 135.0

Con usuario premium:

    cart = Cart(user_id="user-1", user_service=service)
    cart.add_item(200.0)
    cart.discount()   # 30.0 (15% total)
    cart.total()      # 170.0

## Ejemplo: uso básico

    poetry run python -c "
    import sys
    sys.path.insert(0, '04_laboratorios/lab_10_tdd')
    from cart import Cart, InMemoryUserService

    # Carrito normal
    cart = Cart()
    cart.add_item(50.0)
    cart.add_item(100.0)
    print(f'Subtotal: {cart.subtotal()}')
    print(f'Descuento: {cart.discount()}')
    print(f'Total: {cart.total()}')

    # Carrito premium
    service = InMemoryUserService(premium_users={'user-1'})
    premium = Cart(user_id='user-1', user_service=service)
    premium.add_item(200.0)
    print(f'Premium total: {premium.total()}')
    "

Salida esperada:

    Subtotal: 150.0
    Descuento: 15.0
    Total: 135.0
    Premium total: 170.0

## Cómo ejecutar los tests

### Todos los tests

    poetry run pytest 04_laboratorios/lab_10_tdd/tests/ -v

Salida esperada:

    33 passed in 0.26s

### Con cobertura

    poetry run pytest 04_laboratorios/lab_10_tdd/tests/ --cov=04_laboratorios/lab_10_tdd --cov-report=term-missing

Salida esperada:

    Name                                                  Stmts   Miss  Cover
    --------------------------------------------------------------------------
    cart.py                                                  37      0   100%
    ...
    TOTAL                                                   220      0   100%

### Solo un archivo

    poetry run pytest 04_laboratorios/lab_10_tdd/tests/test_cart.py -v
    poetry run pytest 04_laboratorios/lab_10_tdd/tests/test_mocking.py -v
    poetry run pytest 04_laboratorios/lab_10_tdd/tests/test_properties.py -v

### Archivos de tests

| Archivo | Técnica | Tests |
|---------|---------|-------|
| test_cart.py | Tests clásicos + parametrize | 18 |
| test_mocking.py | unittest.mock (Mock, patch, side_effect) | 7 |
| test_properties.py | Hypothesis (property-based) | 8 |

## Las 3 técnicas de testing

### 1. Tests clásicos (`test_cart.py`)

- Tests unitarios con `assert`
- `@pytest.mark.parametrize` para múltiples casos
- Fixtures en `conftest.py`

Ejemplo:

    @pytest.mark.parametrize("items,expected_discount", [
        ([50.0], 0.0),
        ([150.0], 15.0),
        ([501.0], 100.2),
    ])
    def test_descuento_por_monto(cart, items, expected_discount):
        for price in items:
            cart.add_item(price)
        assert cart.discount() == expected_discount

### 2. Mocking (`test_mocking.py`)

- `Mock()`: objeto falso que registra llamadas
- `assert_called_once_with()`: verifica interacciones
- `side_effect`: simula comportamiento dinámico o excepciones
- `patch.object()`: reemplaza métodos temporalmente

Ejemplo:

    mock_service = Mock()
    mock_service.is_premium.return_value = True
    cart = Cart(user_id="user-1", user_service=mock_service)
    cart.add_item(200.0)

    assert cart.discount() == 30.0
    mock_service.is_premium.assert_called_once_with("user-1")

### 3. Property-based testing (`test_properties.py`)

- `@given(estrategia)`: Hypothesis genera casos aleatorios
- Describe **invariantes**, no casos específicos
- Encuentra edge cases que no se te ocurrieron
- Encoge (shrink) al mínimo contraejemplo

Ejemplo:

    @given(prices)
    @settings(max_examples=100)
    def test_total_nunca_negativo(items):
        cart = Cart()
        for price in items:
            cart.add_item(price)
        assert cart.total() >= 0

## TDD (Test-Driven Development)

El flujo aplicado en este laboratorio:

    RED   -> Escribe un test que falla
    GREEN -> Implementa lo mínimo para que pase
    REFACTOR -> Mejora sin romper tests

**Beneficios demostrados aquí:**

- El código está diseñado para ser testeable (inyección de `UserService`)
- Cada test documenta un comportamiento
- La suite completa corre en <1s

## Verificación de calidad

    poetry run ruff check 04_laboratorios/lab_10_tdd/
    poetry run mypy 04_laboratorios/lab_10_tdd/
    poetry run pre-commit run --all-files

## Notas de implementación

### Protocol vs ABC

`UserService` es un `Protocol`, no una `ABC`. Esto permite:

- Duck typing tipado (cualquier clase con `is_premium` lo cumple)
- Mocks que satisfacen el Protocol sin heredar
- Tests sin acoplamiento a una jerarquía

### Inyección de dependencias

`Cart` recibe `user_service` en el constructor:

    Cart(user_id="user-1", user_service=InMemoryUserService(...))
    Cart(user_id="user-1", user_service=Mock())
    Cart(user_id="user-1", user_service=RealDBService())

El mismo código sirve para producción y para tests.

### Por qué Hypothesis

Testear `descuento <= subtotal` con casos manuales es frágil. Con
Hypothesis, se generan 100 combinaciones aleatorias de precios y se
verifica la invariante. Si falla, se encoge al mínimo contraejemplo.

### Cobertura al 100%

- Todo el código de `cart.py` está cubierto
- Las branches (if/elif/else) están todas ejercitadas
- Los errores (`ValueError`) también

## Comandos rápidos (resumen)

    # Tests
    poetry run pytest 04_laboratorios/lab_10_tdd/tests/ -v

    # Cobertura
    poetry run pytest 04_laboratorios/lab_10_tdd/tests/ --cov=04_laboratorios/lab_10_tdd --cov-report=term-missing

    # Calidad
    poetry run ruff check 04_laboratorios/lab_10_tdd/
    poetry run mypy 04_laboratorios/lab_10_tdd/

## Estado

- [x] Estructura del laboratorio
- [x] Hypothesis instalado
- [x] Cart + UserService (Protocol)
- [x] 18 tests clásicos con parametrize
- [x] 7 tests de mocking
- [x] 8 tests de property-based
- [x] Cobertura 100%
- [x] ruff + mypy OK
- [x] Documentación completa

## Clonar este laboratorio

    git clone https://github.com/parisollie/python-training.git
    cd python-training
    poetry install

    # Tests
    poetry run pytest 04_laboratorios/lab_10_tdd/tests/ -v

## Referencias

- pytest docs: https://docs.pytest.org/
- pytest fixtures: https://docs.pytest.org/en/stable/fixture.html
- pytest parametrize: https://docs.pytest.org/en/stable/how-to/parametrize.html
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html
- Hypothesis docs: https://hypothesis.readthedocs.io/
- pytest-cov: https://pytest-cov.readthedocs.io/
- TDD (Wikipedia): https://en.wikipedia.org/wiki/Test-driven_development

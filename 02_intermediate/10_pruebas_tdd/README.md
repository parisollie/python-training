# Módulo 10 — Pruebas y TDD

## Objetivos
- Practicar TDD (Test-Driven Development)
- Disenar pruebas confiables y mantenibles
- Asegurar cobertura suficiente con una suite estable

## Contenidos clave

### pytest basico
- Estructura: test_*.py, test_*(), Test*
- assert como unica asercion
- Fixtures con @pytest.fixture
- Scope: function, class, module, session

### Fixtures avanzadas
- conftest.py para fixtures compartidas
- tmp_path (archivos temporales)
- caplog (captura de logs)
- monkeypatch (parchear atributos)
- parametrize para multiples casos

### Markers
- @pytest.mark.skip / skipif
- @pytest.mark.xfail (test que se espera falle)
- @pytest.mark.slow (para excluir en CI rapido)
- @pytest.mark.parametrize
- Configuracion de markers en pyproject.toml

### Mocking con unittest.mock
- Mock: objeto falso
- MagicMock: con dunder methods
- patch: reemplaza un atributo temporalmente
- patch.object / patch.dict
- return_value / side_effect
- assert_called_once_with
- Cuando mockear (I/O, red, DB, tiempo)

### Property-based testing con Hypothesis
- @given con estrategias
- st.integers, st.text, st.lists, st.dictionaries
- Encogimiento (shrink) automatico
- Encontrar casos edge que no se te ocurrieron
- Cuando usarlo (logica pura, parsers, validaciones)

### Cobertura
- pytest-cov
- Reporte term-missing
- Umbral minimo (fail-under)
- Que NO perseguir 100%

### TDD (Test-Driven Development)
- Ciclo: Red -> Green -> Refactor
- Escribir el test primero (falla)
- Implementar lo minimo para que pase
- Refactorizar manteniendo tests verdes
- Beneficios: diseno emergente, confianza, documentacion viva

## Laboratorio

Implementar una historia con TDD:

**Historia:** Un carrito de compras con descuentos.

1. `Cart`: agregar items, calcular subtotal
2. `Discount`:
   - 10% si subtotal > 100
   - 20% si subtotal > 500
   - 5% extra si el usuario es premium
3. `Cart.total()`: subtotal - descuento

Se implementa con TDD:
- Primero el test (falla)
- Luego el codigo minimo
- Refactor

Ademas:
- Tests de property-based con Hypothesis (ej: total <= subtotal siempre)
- Mocking del "servicio de usuario premium" (no llamar a la DB real)

## Conceptos clave

### ¿Por que PEP 20 importa aqui?
- "Simple es mejor que complejo" -> tests pequenos y enfocados
- "La legibilidad cuenta" -> nombre del test describe el comportamiento
- "Los errores nunca deben pasar silenciosamente" -> tests con assert claros

### Cuando usar cada herramienta

| Herramienta | Cuando usar |
|-------------|-------------|
| Test normal | Logica pura sin dependencias externas |
| Mock | I/O (red, DB, archivos, tiempo) |
| Property-based | Logica con invariantes (siempre se cumple X) |
| Snapshot | Salidas complejas que cambian poco |
| Parametrize | Mismo test con multiples inputs |

### Ciclo TDD (Red-Green-Refactor)

    RED   -> Escribe un test que falla
    GREEN -> Escribe el codigo minimo para que pase
    REFACTOR -> Mejora el codigo sin romper tests

### Ejemplo: test basico

    def test_suma() -> None:
        assert suma(2, 3) == 5

### Ejemplo: fixture

    import pytest

    @pytest.fixture
    def cart():
        return Cart()

    def test_cart_vacio(cart):
        assert cart.subtotal() == 0.0

### Ejemplo: parametrize

    @pytest.mark.parametrize("a,b,expected", [
        (2, 3, 5),
        (0, 0, 0),
        (-1, 1, 0),
    ])
    def test_suma(a, b, expected):
        assert suma(a, b) == expected

### Ejemplo: mock

    from unittest.mock import Mock

    def test_notifica_al_pagar():
        notifier = Mock()
        cart = Cart(notifier=notifier)
        cart.checkout()
        notifier.send.assert_called_once_with("Gracias por tu compra")

### Ejemplo: patch

    from unittest.mock import patch

    @patch("mymodule.httpx.get")
    def test_llamada_api(mock_get):
        mock_get.return_value.json.return_value = {"ok": True}
        result = mi_funcion()
        assert result == {"ok": True}

### Ejemplo: Hypothesis

    from hypothesis import given
    from hypothesis import strategies as st

    @given(st.lists(st.integers(min_value=1, max_value=1000)))
    def test_total_nunca_negativo(items):
        cart = Cart()
        for price in items:
            cart.add_item(price)
        assert cart.total() >= 0

## Checklist
- [ ] Crear estructura del laboratorio
- [ ] Instalar hypothesis
- [ ] Escribir tests con TDD (Red-Green-Refactor)
- [ ] Tests con mocking
- [ ] Tests con property-based (Hypothesis)
- [ ] Correr cobertura
- [ ] Documentar en README del laboratorio
- [ ] Commit del modulo

## Referencias
- pytest docs: https://docs.pytest.org/
- pytest fixtures: https://docs.pytest.org/en/stable/fixture.html
- pytest markers: https://docs.pytest.org/en/stable/how-to/mark.html
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html
- Hypothesis docs: https://hypothesis.readthedocs.io/
- pytest-cov: https://pytest-cov.readthedocs.io/
- TDD (Kent Beck): https://en.wikipedia.org/wiki/Test-driven_development

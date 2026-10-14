"""Tests con mocking (unittest.mock).

Demuestra:
- Mock: objeto falso que registra llamadas
- patch.object para reemplazar metodos temporalmente
- assert_called_once_with para verificar interacciones
"""

from unittest.mock import Mock, patch

from cart import Cart


def test_mock_user_service_premium() -> None:
    """Un Mock que devuelve True para is_premium da descuento extra."""
    mock_service = Mock()
    mock_service.is_premium.return_value = True

    cart = Cart(user_id="user-1", user_service=mock_service)
    cart.add_item(200.0)

    # 10% (monto) + 5% (premium) = 15% de 200 = 30
    # (discount() llama internamente a is_premium)
    assert cart.discount() == 30.0

    # Verificar que se llamo a is_premium con el user_id correcto
    mock_service.is_premium.assert_called_once_with("user-1")


def test_mock_user_service_no_premium() -> None:
    """Mock que devuelve False: solo descuento por monto."""
    mock_service = Mock()
    mock_service.is_premium.return_value = False

    cart = Cart(user_id="user-1", user_service=mock_service)
    cart.add_item(200.0)

    assert cart.discount() == 20.0  # solo 10%
    mock_service.is_premium.assert_called_once_with("user-1")


def test_mock_no_se_llama_sin_user_id() -> None:
    """Sin user_id, no se llama al servicio."""
    mock_service = Mock()

    cart = Cart(user_service=mock_service)  # sin user_id
    cart.add_item(200.0)
    _ = cart.discount()

    mock_service.is_premium.assert_not_called()


def test_mock_side_effect() -> None:
    """side_effect permite simular comportamiento dinamico."""
    mock_service = Mock()
    # El primer user_id es premium, el segundo no
    mock_service.is_premium.side_effect = lambda uid: uid == "premium-1"

    cart1 = Cart(user_id="premium-1", user_service=mock_service)
    cart1.add_item(200.0)
    assert cart1.discount() == 30.0  # 15%

    cart2 = Cart(user_id="normal-1", user_service=mock_service)
    cart2.add_item(200.0)
    assert cart2.discount() == 20.0  # 10%


def test_mock_side_effect_excepcion() -> None:
    """side_effect puede lanzar excepciones."""
    mock_service = Mock()
    mock_service.is_premium.side_effect = ConnectionError("DB caida")

    cart = Cart(user_id="user-1", user_service=mock_service)
    cart.add_item(200.0)

    import pytest

    with pytest.raises(ConnectionError, match="DB caida"):
        cart.discount()


def test_patch_object() -> None:
    """patch.object reemplaza un metodo temporalmente."""
    cart = Cart()
    cart.add_item(100.0)

    with patch.object(cart, "subtotal", return_value=999.0) as mock_subtotal:
        assert cart.subtotal() == 999.0
        mock_subtotal.assert_called_once()

    # Al salir del with, se restaura el metodo real
    assert cart.subtotal() == 100.0


def test_patch_clase_completa() -> None:
    """patch reemplaza una clase entera durante un bloque."""
    with patch("cart.Cart") as mock_cart:
        instance = mock_cart.return_value
        instance.total.return_value = 42.0

        from cart import Cart as CartClass

        cart = CartClass()
        assert cart.total() == 42.0

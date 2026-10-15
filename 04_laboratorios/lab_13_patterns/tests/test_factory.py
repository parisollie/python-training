"""Tests del patron Factory."""

import pytest
from factory import (
    ConsoleNotifier,
    EmailNotifier,
    SlackNotifier,
    SmsNotifier,
    create_notifier,
    create_notifier_simple,
    register,
)

# ============================================
# create_notifier_simple
# ============================================


@pytest.mark.parametrize(
    "kind,expected_class",
    [
        ("console", ConsoleNotifier),
        ("email", EmailNotifier),
        ("sms", SmsNotifier),
        ("slack", SlackNotifier),
    ],
)
def test_simple_crea_correcta(kind: str, expected_class: type) -> None:
    """create_notifier_simple devuelve la clase correcta."""
    notifier = create_notifier_simple(kind)
    assert isinstance(notifier, expected_class)


def test_simple_tipo_desconocido() -> None:
    """Tipo desconocido lanza ValueError."""
    with pytest.raises(ValueError, match="desconocido"):
        create_notifier_simple("telegram")


# ============================================
# create_notifier (registro)
# ============================================


@pytest.mark.parametrize(
    "kind,expected_class",
    [
        ("console", ConsoleNotifier),
        ("email", EmailNotifier),
        ("sms", SmsNotifier),
        ("slack", SlackNotifier),
    ],
)
def test_registry_crea_correcta(kind: str, expected_class: type) -> None:
    """create_notifier devuelve la clase correcta segun el registro."""
    notifier = create_notifier(kind)
    assert isinstance(notifier, expected_class)


def test_registry_tipo_desconocido() -> None:
    """Tipo no registrado lanza ValueError con lista de registrados."""
    with pytest.raises(ValueError, match="Registrados"):
        create_notifier("no_existe")


def test_extender_registro() -> None:
    """Se puede registrar un nuevo tipo sin tocar create_notifier."""

    class CustomNotifier:
        def send(self, message: str) -> str:
            return f"custom:{message}"

    register("custom_test", CustomNotifier)
    notifier = create_notifier("custom_test")
    assert isinstance(notifier, CustomNotifier)


# ============================================
# Comportamiento de los notifiers
# ============================================


def test_console_notifier(capsys: pytest.CaptureFixture[str]) -> None:
    """ConsoleNotifier imprime."""
    n = create_notifier("console")
    result = n.send("hola")
    captured = capsys.readouterr()
    assert "[CONSOLE] hola" in captured.out
    assert result == "console:hola"


def test_email_notifier_acumula() -> None:
    """EmailNotifier acumula los envios."""
    n = create_notifier("email")
    n.send("m1")
    n.send("m2")
    assert len(n.sent) == 2  # type: ignore[attr-defined]


def test_sms_notifier_acumula() -> None:
    """SmsNotifier acumula los envios."""
    n = create_notifier("sms")
    n.send("m1")
    assert len(n.sent) == 1  # type: ignore[attr-defined]


def test_slack_notifier_acumula() -> None:
    """SlackNotifier acumula los envios."""
    n = create_notifier("slack")
    n.send("m1")
    assert len(n.sent) == 1  # type: ignore[attr-defined]

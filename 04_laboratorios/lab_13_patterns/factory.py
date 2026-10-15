"""Patron Factory: crear objetos segun configuracion.

Demuestra:
- Factory Method: funcion que decide que clase instanciar
- Registro con dict: alternativa extensible (sin if/elif)
- Sin acoplamiento: el cliente no conoce las clases concretas
"""

from typing import Protocol

# ============================================
# Interfaz
# ============================================


class Notifier(Protocol):
    """Interfaz comun de todos los notificadores."""

    def send(self, message: str) -> str:
        """Envia el mensaje. Devuelve un acuse."""
        ...


# ============================================
# Implementaciones concretas
# ============================================


class ConsoleNotifier:
    """Imprime en consola."""

    def send(self, message: str) -> str:
        """Imprime y devuelve el mensaje."""
        print(f"[CONSOLE] {message}")
        return f"console:{message}"


class EmailNotifier:
    """Simula envio de email."""

    def __init__(self, smtp: str = "smtp.example.com") -> None:
        self.smtp = smtp
        self.sent: list[str] = []

    def send(self, message: str) -> str:
        """Registra el envio."""
        self.sent.append(message)
        return f"email:{message}"


class SmsNotifier:
    """Simula envio de SMS."""

    def __init__(self, phone: str = "+123456789") -> None:
        self.phone = phone
        self.sent: list[str] = []

    def send(self, message: str) -> str:
        """Registra el envio."""
        self.sent.append(message)
        return f"sms:{message}"


class SlackNotifier:
    """Simula envio a Slack."""

    def __init__(self, channel: str = "#general") -> None:
        self.channel = channel
        self.sent: list[str] = []

    def send(self, message: str) -> str:
        """Registra el envio."""
        self.sent.append(message)
        return f"slack:{message}"


# ============================================
# Factory 1: con if/elif (simple)
# ============================================


def create_notifier_simple(kind: str) -> Notifier:
    """Factory con if/elif. Simple pero hay que tocar la funcion al agregar tipos."""
    if kind == "console":
        return ConsoleNotifier()
    if kind == "email":
        return EmailNotifier()
    if kind == "sms":
        return SmsNotifier()
    if kind == "slack":
        return SlackNotifier()
    raise ValueError(f"Tipo desconocido: {kind}")


# ============================================
# Factory 2: con registro (extensible)
# ============================================

# El registro se puede modificar sin tocar la funcion
_REGISTRY: dict[str, type[Notifier]] = {}


def register(kind: str, cls: type[Notifier]) -> None:
    """Registra una nueva implementacion.

    Args:
        kind: Identificador del tipo.
        cls: Clase que implementa Notifier.
    """
    _REGISTRY[kind] = cls


def create_notifier(kind: str) -> Notifier:
    """Factory basada en registro (Open/Closed Principle).

    Agregar tipos nuevos es solo `register("nuevo", NuevaClase)`.

    Raises:
        ValueError: Si el tipo no esta registrado.
    """
    if kind not in _REGISTRY:
        raise ValueError(f"Tipo desconocido: {kind}. Registrados: {list(_REGISTRY)}")
    return _REGISTRY[kind]()


# ============================================
# Registro inicial
# ============================================


register("console", ConsoleNotifier)
register("email", EmailNotifier)
register("sms", SmsNotifier)
register("slack", SlackNotifier)

"""Fixtures compartidas para tests de patrones."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(autouse=True)
def _reset_factory_registry() -> None:
    """Limpia el registro de factory antes de cada test.

    Evita contaminacion entre tests que registran tipos.
    """
    from factory import _REGISTRY

    # Copia de la configuracion inicial (los 4 registrados por defecto)
    initial = {"console", "email", "sms", "slack"}
    current = set(_REGISTRY.keys())
    # Elimina los que se agregaron en tests
    for extra in current - initial:
        _REGISTRY.pop(extra, None)

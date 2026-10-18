"""Entidad Character (referencia externa a la API de Rick and Morty).

Este es un modelo de lectura del dominio: representa un personaje
que vive en la API externa, no en nuestra DB.

El dominio lo usa para validar y enriquecer items de orden.

Nota: es `frozen=True` porque los datos vienen de una fuente externa
y no se modifican (los personajes no cambian en nuestra app).
"""

from dataclasses import dataclass
from enum import StrEnum

from rickmorty_orders.domain.value_objects import CharacterId


class CharacterStatus(StrEnum):
    """Estado de un personaje en la API R&M."""

    ALIVE = "Alive"
    DEAD = "Dead"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Character:
    """Personaje de Rick and Morty (fuente externa)."""

    id: CharacterId
    name: str
    species: str
    status: CharacterStatus
    image_url: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("El nombre del personaje no puede estar vacio")
        if not self.species.strip():
            raise ValueError("La especie del personaje no puede estar vacia")

    @property
    def is_alive(self) -> bool:
        """True si el personaje esta vivo."""
        return self.status == CharacterStatus.ALIVE

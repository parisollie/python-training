"""Caso de uso: CreateOrderService.

Orquesta el flujo de creacion de una orden:

1. Consulta los personajes a la API externa (CharacterRepository)
2. Valida que existan
3. Crea los OrderItem con datos enriquecidos
4. Crea la entidad Order (aplica invariantes)
5. Persiste (OrderRepository)
6. Notifica (Notifier)
7. Publica evento (EventBus)
8. Devuelve DTO de salida

El caso de uso NO conoce adaptadores concretos, solo Protocols.
"""

import logging

from rickmorty_orders.application.dtos import CreateOrderInput, OrderOutput
from rickmorty_orders.domain.character import Character, CharacterStatus
from rickmorty_orders.domain.errors import CharacterNotFoundError
from rickmorty_orders.domain.events import OrderCreated
from rickmorty_orders.domain.order import Order, OrderItem
from rickmorty_orders.domain.ports import (
    CharacterRepository,
    EventBus,
    Notifier,
    OrderRepository,
)
from rickmorty_orders.domain.value_objects import (
    CharacterId,
    Email,
    Money,
)

logger = logging.getLogger(__name__)


class CreateOrderService:
    """Caso de uso: crear una orden.

    Depende de 4 puertos:
    - OrderRepository: persistir ordenes
    - CharacterRepository: consultar personajes
    - Notifier: notificar al cliente
    - EventBus: publicar eventos

    No conoce FastAPI, SQLAlchemy, httpx ni nada concreto.
    """

    def __init__(
        self,
        order_repository: OrderRepository,
        character_repository: CharacterRepository,
        notifier: Notifier,
        event_bus: EventBus,
    ) -> None:
        """Inyecta las dependencias."""
        self._orders = order_repository
        self._characters = character_repository
        self._notifier = notifier
        self._event_bus = event_bus

    def execute(self, input_dto: CreateOrderInput) -> OrderOutput:
        """Ejecuta el caso de uso.

        Args:
            input_dto: DTO validado de entrada.

        Returns:
            DTO con la orden creada.

        Raises:
            CharacterNotFoundError: si algun personaje no existe.
        """
        logger.info(
            "Creando orden para %s con %d items",
            input_dto.customer_email,
            len(input_dto.items),
        )

        # 1. Consultar personajes a la API externa
        character_ids = [CharacterId(item.character_id) for item in input_dto.items]
        characters = self._characters.list_by_ids(character_ids)

        # 2. Validar que todos existan
        found_ids = {c.id.value for c in characters}
        missing = [cid.value for cid in character_ids if cid.value not in found_ids]
        if missing:
            raise CharacterNotFoundError(f"Personajes no encontrados: {missing}")

        # 3. Crear OrderItems con datos enriquecidos
        # Precio: usamos un precio simulado segun el status del personaje
        # (los personajes vivos cuestan mas, como "mas valiosos")
        characters_by_id = {c.id.value: c for c in characters}
        order_items = []
        for item_input in input_dto.items:
            char = characters_by_id[item_input.character_id]
            unit_price = self._calculate_price(char)
            order_items.append(
                OrderItem(
                    character_id=char.id,
                    character_name=char.name,
                    quantity=item_input.quantity,
                    unit_price=unit_price,
                )
            )

        # 4. Crear entidad Order (aplica invariantes)
        order = Order.create(
            customer_email=Email(input_dto.customer_email),
            items=order_items,
        )

        # 5. Persistir
        self._orders.save(order)

        # 6. Notificar
        self._notifier.notify_order_created(order)

        # 7. Publicar evento
        self._event_bus.publish(
            OrderCreated(
                order_id=order.id,
                customer_email=str(order.customer_email),
                total=order.total.amount,
            )
        )

        logger.info("Orden creada: %s (total: %s)", order.id, order.total)

        # 8. Devolver DTO
        return OrderOutput.from_entity(order)

    @staticmethod
    def _calculate_price(character: Character) -> Money:
        """Calcula el precio de un personaje.

        Regla de negocio: los personajes vivos son mas caros.
        - Vivos: $50
        - Muertos: $25
        - Desconocidos: $10
        """
        prices = {
            CharacterStatus.ALIVE: Money(50.0),
            CharacterStatus.DEAD: Money(25.0),
            CharacterStatus.UNKNOWN: Money(10.0),
        }
        return prices[character.status]

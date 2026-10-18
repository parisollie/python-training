"""Wiring de dependencias para FastAPI."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from rickmorty_orders.application.create_order import CreateOrderService
from rickmorty_orders.application.order_actions import (
    CancelOrderService,
    ConfirmOrderService,
)
from rickmorty_orders.application.order_queries import (
    GetOrderService,
    ListOrdersService,
)
from rickmorty_orders.domain.ports import (
    CharacterRepository,
    EventBus,
    Notifier,
    OrderRepository,
)
from rickmorty_orders.infrastructure.console_notifier import ConsoleNotifier
from rickmorty_orders.infrastructure.event_bus import InMemoryEventBus
from rickmorty_orders.infrastructure.persistence import (
    get_db,
    get_session_factory,
)
from rickmorty_orders.infrastructure.rickmorty_client import RickMortyApiClient
from rickmorty_orders.infrastructure.sql_repositories import SQLOrderRepository


@lru_cache
def _get_character_client() -> RickMortyApiClient:
    return RickMortyApiClient()


@lru_cache
def _get_notifier() -> ConsoleNotifier:
    return ConsoleNotifier()


@lru_cache
def _get_event_bus() -> InMemoryEventBus:
    return InMemoryEventBus()


def get_character_client() -> CharacterRepository:
    return _get_character_client()


def get_notifier() -> Notifier:
    return _get_notifier()


def get_event_bus() -> EventBus:
    return _get_event_bus()


def get_order_repository(
    db: Annotated[Session, Depends(get_db)],
) -> OrderRepository:
    _ = db
    return SQLOrderRepository(get_session_factory())


def get_create_order_service(
    repo: Annotated[OrderRepository, Depends(get_order_repository)],
    chars: Annotated[CharacterRepository, Depends(get_character_client)],
    notifier: Annotated[Notifier, Depends(get_notifier)],
    event_bus: Annotated[EventBus, Depends(get_event_bus)],
) -> CreateOrderService:
    return CreateOrderService(repo, chars, notifier, event_bus)


def get_get_order_service(
    repo: Annotated[OrderRepository, Depends(get_order_repository)],
) -> GetOrderService:
    return GetOrderService(repo)


def get_list_orders_service(
    repo: Annotated[OrderRepository, Depends(get_order_repository)],
) -> ListOrdersService:
    return ListOrdersService(repo)


def get_confirm_order_service(
    repo: Annotated[OrderRepository, Depends(get_order_repository)],
    notifier: Annotated[Notifier, Depends(get_notifier)],
    event_bus: Annotated[EventBus, Depends(get_event_bus)],
) -> ConfirmOrderService:
    return ConfirmOrderService(repo, notifier, event_bus)


def get_cancel_order_service(
    repo: Annotated[OrderRepository, Depends(get_order_repository)],
    notifier: Annotated[Notifier, Depends(get_notifier)],
    event_bus: Annotated[EventBus, Depends(get_event_bus)],
) -> CancelOrderService:
    return CancelOrderService(repo, notifier, event_bus)


CreateOrderDep = Annotated[CreateOrderService, Depends(get_create_order_service)]
GetOrderDep = Annotated[GetOrderService, Depends(get_get_order_service)]
ListOrdersDep = Annotated[ListOrdersService, Depends(get_list_orders_service)]
ConfirmOrderDep = Annotated[ConfirmOrderService, Depends(get_confirm_order_service)]
CancelOrderDep = Annotated[CancelOrderService, Depends(get_cancel_order_service)]
DbDep = Annotated[Session, Depends(get_db)]

"""Router de orders para FastAPI."""

from fastapi import APIRouter, HTTPException, status

from rickmorty_orders.application.dtos import CreateOrderInput, OrderOutput
from rickmorty_orders.domain.errors import (
    CharacterNotFoundError,
    CharacterServiceError,
    InvalidOrderError,
    InvalidStatusTransitionError,
    OrderNotFoundError,
)
from rickmorty_orders.infrastructure.dependencies import (
    CancelOrderDep,
    ConfirmOrderDep,
    CreateOrderDep,
    GetOrderDep,
    ListOrdersDep,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderOutput, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: CreateOrderInput,
    service: CreateOrderDep,
) -> OrderOutput:
    """Crea una nueva orden.

    Consulta los personajes a la API de Rick and Morty,
    calcula precios y persiste la orden.
    """
    try:
        return service.execute(order_in)
    except CharacterNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except CharacterServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error consultando API externa: {e}",
        ) from e
    except InvalidOrderError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/", response_model=list[OrderOutput])
def list_orders(
    service: ListOrdersDep,
    customer_email: str | None = None,
) -> list[OrderOutput]:
    """Lista ordenes, opcionalmente filtradas por cliente."""
    return service.execute(customer_email)


@router.get("/{order_id}", response_model=OrderOutput)
def get_order(
    order_id: str,
    service: GetOrderDep,
) -> OrderOutput:
    """Obtiene una orden por id."""
    try:
        return service.execute(order_id)
    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.patch("/{order_id}/confirm", response_model=OrderOutput)
def confirm_order(
    order_id: str,
    service: ConfirmOrderDep,
) -> OrderOutput:
    """Confirma una orden (pending -> confirmed)."""
    try:
        return service.execute(order_id)
    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except InvalidStatusTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e


@router.patch("/{order_id}/cancel", response_model=OrderOutput)
def cancel_order(
    order_id: str,
    service: CancelOrderDep,
    reason: str = "",
) -> OrderOutput:
    """Cancela una orden."""
    try:
        return service.execute(order_id, reason=reason)
    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except InvalidStatusTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e

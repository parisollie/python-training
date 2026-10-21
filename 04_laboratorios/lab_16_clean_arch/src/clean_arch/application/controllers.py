"""Controllers del lab 16 (puros, sin FastAPI).

Un Controller:
- Recibe un DTO de entrada
- Invoca el caso de uso
- Convierte la entidad resultante con el Presenter
- Devuelve el DTO de salida

No conoce FastAPI, ni HTTP, ni Pydantic. Es testeable de forma aislada.
"""

from clean_arch.application.create_order import CreateOrderService
from clean_arch.application.dtos import CreateOrderInput, OrderOutput
from clean_arch.application.presenters import OrderPresenter


class CreateOrderController:
    """Controller para crear ordenes."""

    def __init__(
        self,
        service: CreateOrderService,
        presenter: OrderPresenter,
    ) -> None:
        self._service = service
        self._presenter = presenter

    def handle(self, input_dto: CreateOrderInput) -> OrderOutput:
        """Flujo: input -> caso de uso -> presenter -> output."""
        order = self._service.execute(input_dto)
        return self._presenter.present(order)

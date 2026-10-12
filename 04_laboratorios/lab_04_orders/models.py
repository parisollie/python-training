"""Modelos de dominio para ordenes de compra.

Usa dataclasses para representar entidades con logica derivada.
"""

from dataclasses import dataclass, field


@dataclass(order=True)
class OrderItem:
    """Item individual dentro de una orden.

    Attributes:
        name: Nombre del producto.
        quantity: Cantidad pedida. Debe ser >= 1.
        unit_price: Precio unitario. Debe ser >= 0.
    """

    name: str
    quantity: int
    unit_price: float

    def __post_init__(self) -> None:
        """Valida que quantity y unit_price sean coherentes."""
        if self.quantity < 1:
            raise ValueError(f"quantity debe ser >= 1 (recibido: {self.quantity})")
        if self.unit_price < 0:
            raise ValueError(f"unit_price debe ser >= 0 (recibido: {self.unit_price})")

    @property
    def subtotal(self) -> float:
        """Subtotal del item (quantity * unit_price)."""
        return self.quantity * self.unit_price


@dataclass(eq=True)
class Order:
    """Orden de compra con calculos derivados.

    Attributes:
        id: Identificador unico de la orden.
        customer: Nombre del cliente.
        items: Lista de items. Puede estar vacia al crear.

    Properties:
        subtotal: Suma de subtotales de items.
        tax: IVA (16%) sobre el subtotal.
        total: subtotal + tax.
        total_items: Cantidad total de unidades.

    Notas:
        - La comparacion con == usa todos los campos (default de dataclass).
        - La comparacion con < > se hace por `total` (implementacion custom).
    """

    id: str
    customer: str
    items: list[OrderItem] = field(default_factory=list)

    TAX_RATE: float = 0.16

    def __post_init__(self) -> None:
        """Valida que id y customer no esten vacios."""
        if not self.id:
            raise ValueError("id no puede estar vacio")
        if not self.customer:
            raise ValueError("customer no puede estar vacio")

    @property
    def subtotal(self) -> float:
        """Suma de subtotales de todos los items."""
        return sum(item.subtotal for item in self.items)

    @property
    def tax(self) -> float:
        """IVA sobre el subtotal (16% por defecto)."""
        return round(self.subtotal * self.TAX_RATE, 2)

    @property
    def total(self) -> float:
        """Total a pagar (subtotal + IVA)."""
        return round(self.subtotal + self.tax, 2)

    @property
    def total_items(self) -> int:
        """Cantidad total de unidades (suma de quantities)."""
        return sum(item.quantity for item in self.items)

    def add_item(self, item: OrderItem) -> None:
        """Agrega un item a la orden.

        Args:
            item: Item a agregar.
        """
        self.items.append(item)

    def __lt__(self, other: "Order") -> bool:
        """Compara ordenes por total (para sorted y min/max).

        Args:
            other: Otra orden con la que comparar.

        Returns:
            True si el total de esta orden es menor que el de la otra.
        """
        if not isinstance(other, Order):
            return NotImplemented
        return self.total < other.total

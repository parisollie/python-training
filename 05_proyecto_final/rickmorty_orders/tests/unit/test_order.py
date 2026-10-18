"""Tests de la entidad Order y OrderItem (dominio puro)."""

from dataclasses import FrozenInstanceError

import pytest
from rickmorty_orders.domain.errors import (
    InvalidOrderError,
    InvalidStatusTransitionError,
)
from rickmorty_orders.domain.order import (
    TAX_RATE,
    Order,
    OrderItem,
    OrderStatus,
)
from rickmorty_orders.domain.value_objects import CharacterId, Email, Money

# ============================================
# OrderItem (Value Object)
# ============================================


def test_order_item_subtotal() -> None:
    """subtotal = unit_price * quantity."""
    item = OrderItem(
        character_id=CharacterId(1),
        character_name="Rick Sanchez",
        quantity=3,
        unit_price=Money(10.0),
    )
    assert item.subtotal.amount == 30.0


def test_order_item_producto_vacio_falla() -> None:
    """character_name vacio lanza InvalidOrderError."""
    with pytest.raises(InvalidOrderError, match="nombre"):
        OrderItem(
            character_id=CharacterId(1),
            character_name="",
            quantity=1,
            unit_price=Money(10.0),
        )


def test_order_item_quantity_cero_falla() -> None:
    """quantity < 1 lanza."""
    with pytest.raises(InvalidOrderError, match="quantity"):
        OrderItem(
            character_id=CharacterId(1),
            character_name="X",
            quantity=0,
            unit_price=Money(10.0),
        )


def test_order_item_inmutable() -> None:
    """OrderItem es inmutable."""
    item = OrderItem(
        character_id=CharacterId(1),
        character_name="X",
        quantity=1,
        unit_price=Money(10.0),
    )
    with pytest.raises(FrozenInstanceError):
        item.quantity = 5  # type: ignore[misc]


# ============================================
# Order (creacion)
# ============================================


def test_order_create_asigna_id(sample_items: list[OrderItem]) -> None:
    """Order.create asigna OrderId."""
    order = Order.create(
        customer_email=Email("a@b.com"),
        items=sample_items,
    )
    assert order.id is not None
    assert len(order.id.value) == 36


def test_order_create_status_pending(sample_items: list[OrderItem]) -> None:
    """Status inicial es PENDING."""
    order = Order.create(
        customer_email=Email("a@b.com"),
        items=sample_items,
    )
    assert order.status == OrderStatus.PENDING


def test_order_sin_items_falla() -> None:
    """Sin items lanza InvalidOrderError."""
    with pytest.raises(InvalidOrderError, match="al menos un item"):
        Order.create(customer_email=Email("a@b.com"), items=[])


def test_order_created_at_utc(sample_order: Order) -> None:
    """created_at tiene timezone UTC."""
    assert sample_order.created_at is not None
    assert sample_order.created_at.tzinfo is not None


# ============================================
# Order (calculos)
# ============================================


def test_order_subtotal(sample_order: Order) -> None:
    """subtotal = suma de items."""
    # 1 * 50 + 2 * 50 = 150
    assert sample_order.subtotal.amount == 150.0


def test_order_tax(sample_order: Order) -> None:
    """tax = subtotal * TAX_RATE."""
    assert sample_order.tax.amount == pytest.approx(150.0 * TAX_RATE, abs=0.01)


def test_order_total(sample_order: Order) -> None:
    """total = subtotal + tax."""
    expected = sample_order.subtotal.amount + sample_order.tax.amount
    assert sample_order.total.amount == pytest.approx(expected, abs=0.01)


def test_order_total_items(sample_order: Order) -> None:
    """total_items suma quantities."""
    # 1 + 2 = 3
    assert sample_order.total_items == 3


def test_order_subtotal_vacio_es_cero() -> None:
    """Una orden vacia (via constructor directo) subtotal 0."""
    # Nota: no se puede crear Order sin items, pero podemos testear
    # que el subtotal sumaria 0 si no hubiera items
    from rickmorty_orders.domain.value_objects import OrderId

    order = Order.__new__(Order)
    order.id = OrderId.generate()
    order.customer_email = Email("a@b.com")
    order.items = []
    order.status = OrderStatus.PENDING
    from datetime import UTC, datetime

    order.created_at = datetime.now(UTC)

    assert order.subtotal.amount == 0.0


# ============================================
# Order (transiciones de estado)
# ============================================


def test_order_confirm_desde_pending(sample_order: Order) -> None:
    """confirm() cambia PENDING -> CONFIRMED."""
    sample_order.confirm()
    assert sample_order.status == OrderStatus.CONFIRMED


def test_order_confirm_desde_confirmed_falla(sample_order: Order) -> None:
    """No se puede confirmar dos veces."""
    sample_order.confirm()
    with pytest.raises(InvalidStatusTransitionError, match="PENDING"):
        sample_order.confirm()


def test_order_confirm_desde_cancelled_falla(sample_order: Order) -> None:
    """No se puede confirmar una cancelada."""
    sample_order.cancel()
    with pytest.raises(InvalidStatusTransitionError):
        sample_order.confirm()


def test_order_ship_desde_confirmed(sample_order: Order) -> None:
    """ship() cambia CONFIRMED -> SHIPPED."""
    sample_order.confirm()
    sample_order.ship()
    assert sample_order.status == OrderStatus.SHIPPED


def test_order_ship_desde_pending_falla(sample_order: Order) -> None:
    """No se puede enviar sin confirmar."""
    with pytest.raises(InvalidStatusTransitionError, match="CONFIRMED"):
        sample_order.ship()


def test_order_cancel_desde_pending(sample_order: Order) -> None:
    """cancel() cambia PENDING -> CANCELLED."""
    sample_order.cancel()
    assert sample_order.status == OrderStatus.CANCELLED


def test_order_cancel_desde_confirmed(sample_order: Order) -> None:
    """Se puede cancelar una confirmada."""
    sample_order.confirm()
    sample_order.cancel()
    assert sample_order.status == OrderStatus.CANCELLED


def test_order_cancel_desde_shipped_falla(sample_order: Order) -> None:
    """No se puede cancelar una enviada."""
    sample_order.confirm()
    sample_order.ship()
    with pytest.raises(InvalidStatusTransitionError, match="enviada"):
        sample_order.cancel()


def test_order_cancel_dos_veces_falla(sample_order: Order) -> None:
    """No se puede cancelar dos veces."""
    sample_order.cancel()
    with pytest.raises(InvalidStatusTransitionError, match="ya esta cancelada"):
        sample_order.cancel()


# ============================================
# Order (add_item / remove_item)
# ============================================


def test_order_add_item_pending(sample_order: Order) -> None:
    """Se puede agregar item en PENDING."""
    new_item = OrderItem(
        character_id=CharacterId(99),
        character_name="Nuevo",
        quantity=1,
        unit_price=Money(10.0),
    )
    original_count = len(sample_order.items)
    sample_order.add_item(new_item)
    assert len(sample_order.items) == original_count + 1


def test_order_add_item_confirmada_falla(sample_order: Order) -> None:
    """No se puede agregar en CONFIRMED."""
    sample_order.confirm()
    new_item = OrderItem(
        character_id=CharacterId(99),
        character_name="Nuevo",
        quantity=1,
        unit_price=Money(10.0),
    )
    with pytest.raises(InvalidStatusTransitionError, match="No se pueden agregar"):
        sample_order.add_item(new_item)


def test_order_remove_item_pending(sample_order: Order) -> None:
    """Se puede remover item en PENDING."""
    original_count = len(sample_order.items)
    sample_order.remove_item(CharacterId(1))
    assert len(sample_order.items) == original_count - 1


def test_order_remove_item_inexistente_falla(sample_order: Order) -> None:
    """Remover id inexistente lanza."""
    with pytest.raises(InvalidOrderError, match="No existe"):
        sample_order.remove_item(CharacterId(999))


def test_order_remove_item_confirmada_falla(sample_order: Order) -> None:
    """No se puede remover en CONFIRMED."""
    sample_order.confirm()
    with pytest.raises(InvalidStatusTransitionError):
        sample_order.remove_item(CharacterId(1))


def test_order_remove_ultimo_item_falla() -> None:
    """Si solo queda 1 item, remove falla."""
    item = OrderItem(
        character_id=CharacterId(1),
        character_name="X",
        quantity=1,
        unit_price=Money(10.0),
    )
    order = Order.create(customer_email=Email("a@b.com"), items=[item])
    with pytest.raises(InvalidOrderError, match="no puede quedar vacia"):
        order.remove_item(CharacterId(1))

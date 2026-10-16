"""Tests de la entidad Order (dominio puro)."""

import pytest
from domain.order import Order, OrderItem, OrderStatus
from domain.value_objects import Email, Money, OrderId


@pytest.fixture
def order() -> Order:
    return Order.create(
        customer_email=Email("paul@example.com"),
        items=[
            OrderItem(product="Teclado", quantity=2, unit_price=Money(25.0)),
            OrderItem(product="Mouse", quantity=1, unit_price=Money(15.5)),
        ],
    )


# ============================================
# OrderItem
# ============================================


def test_order_item_subtotal() -> None:
    """subtotal = unit_price * quantity."""
    item = OrderItem(product="X", quantity=3, unit_price=Money(10.0))
    assert item.subtotal.amount == 30.0


def test_order_item_producto_vacio() -> None:
    """Producto vacio lanza."""
    with pytest.raises(ValueError, match="producto"):
        OrderItem(product="", quantity=1, unit_price=Money(10.0))


def test_order_item_quantity_invalida() -> None:
    """quantity < 1 lanza."""
    with pytest.raises(ValueError, match="quantity"):
        OrderItem(product="X", quantity=0, unit_price=Money(10.0))


# ============================================
# Order (creacion)
# ============================================


def test_order_create(order: Order) -> None:
    """Order.create asigna id y status PENDING."""
    assert order.id is not None
    assert order.status == OrderStatus.PENDING
    assert order.created_at is not None


def test_order_sin_items_falla() -> None:
    """Sin items lanza."""
    with pytest.raises(ValueError, match="al menos un item"):
        Order.create(customer_email=Email("a@b.com"), items=[])


# ============================================
# Order (calculos)
# ============================================


def test_order_subtotal(order: Order) -> None:
    """Suma de subtotales de items."""
    assert order.subtotal.amount == 65.5


def test_order_tax(order: Order) -> None:
    """IVA 16% del subtotal."""
    assert order.tax.amount == pytest.approx(10.48, abs=0.01)


def test_order_total(order: Order) -> None:
    """total = subtotal + tax."""
    assert order.total.amount == 75.98


def test_order_total_items(order: Order) -> None:
    """Suma de quantities."""
    assert order.total_items == 3


# ============================================
# Order (estados)
# ============================================


def test_order_confirm(order: Order) -> None:
    """confirm cambia status a CONFIRMED."""
    order.confirm()
    assert order.status == OrderStatus.CONFIRMED


def test_order_confirm_desde_confirmada_falla(order: Order) -> None:
    """No se puede confirmar dos veces."""
    order.confirm()
    with pytest.raises(ValueError, match="PENDING"):
        order.confirm()


def test_order_cancel(order: Order) -> None:
    """cancel cambia status a CANCELLED."""
    order.cancel()
    assert order.status == OrderStatus.CANCELLED


def test_order_cancel_desde_shipped_falla(order: Order) -> None:
    """No se puede cancelar una orden enviada."""
    order.confirm()
    order.status = OrderStatus.SHIPPED  # forzar para test
    with pytest.raises(ValueError, match="ya enviada"):
        order.cancel()


# ============================================
# Order (add_item)
# ============================================


def test_order_add_item_pending(order: Order) -> None:
    """Se puede agregar item en PENDING."""
    item = OrderItem(product="Nuevo", quantity=1, unit_price=Money(5.0))
    order.add_item(item)
    assert len(order.items) == 3


def test_order_add_item_confirmada_falla(order: Order) -> None:
    """No se puede agregar item en CONFIRMED."""
    order.confirm()
    item = OrderItem(product="Nuevo", quantity=1, unit_price=Money(5.0))
    with pytest.raises(ValueError, match="No se pueden agregar"):
        order.add_item(item)


# ============================================
# LSP / invariantes
# ============================================


def test_order_id_es_unico() -> None:
    """Dos ordenes creadas tienen ids distintos."""
    o1 = Order.create(
        customer_email=Email("a@b.com"),
        items=[OrderItem(product="X", quantity=1, unit_price=Money(1.0))],
    )
    o2 = Order.create(
        customer_email=Email("a@b.com"),
        items=[OrderItem(product="X", quantity=1, unit_price=Money(1.0))],
    )
    assert o1.id != o2.id


def test_order_con_order_id_custom() -> None:
    """Se puede crear con OrderId explicito."""
    oid = OrderId("custom-id-123")
    o = Order(
        id=oid,
        customer_email=Email("a@b.com"),
        items=[OrderItem(product="X", quantity=1, unit_price=Money(1.0))],
    )
    assert o.id == oid

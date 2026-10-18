"""Tests de eventos de dominio."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest
from rickmorty_orders.domain.events import (
    DomainEvent,
    OrderCancelled,
    OrderConfirmed,
    OrderCreated,
)
from rickmorty_orders.domain.value_objects import OrderId

# ============================================
# DomainEvent (base)
# ============================================


def test_domain_event_tiene_timestamp() -> None:
    """DomainEvent tiene occurred_at en UTC."""
    event = DomainEvent()
    assert event.occurred_at is not None
    assert event.occurred_at.tzinfo is not None


def test_domain_event_inmutable() -> None:
    """DomainEvent es inmutable."""
    event = DomainEvent()
    with pytest.raises(FrozenInstanceError):
        event.occurred_at = datetime.now(UTC)  # type: ignore[misc]


# ============================================
# OrderCreated
# ============================================


def test_order_created_campos() -> None:
    """OrderCreated tiene order_id, customer_email, total."""
    oid = OrderId.generate()
    event = OrderCreated(
        order_id=oid,
        customer_email="paul@example.com",
        total=150.0,
    )
    assert event.order_id == oid
    assert event.customer_email == "paul@example.com"
    assert event.total == 150.0


def test_order_created_timestamp() -> None:
    """OrderCreated tiene occurred_at."""
    event = OrderCreated(
        order_id=OrderId.generate(),
        customer_email="a@b.com",
        total=100.0,
    )
    assert event.occurred_at is not None


def test_order_created_heredado_de_domain_event() -> None:
    """OrderCreated hereda de DomainEvent."""
    assert issubclass(OrderCreated, DomainEvent)


# ============================================
# OrderConfirmed
# ============================================


def test_order_confirmed_campos() -> None:
    """OrderConfirmed tiene order_id."""
    oid = OrderId.generate()
    event = OrderConfirmed(order_id=oid)
    assert event.order_id == oid


def test_order_confirmed_heredado_de_domain_event() -> None:
    """OrderConfirmed hereda de DomainEvent."""
    assert issubclass(OrderConfirmed, DomainEvent)


# ============================================
# OrderCancelled
# ============================================


def test_order_cancelled_campos() -> None:
    """OrderCancelled tiene order_id y reason."""
    oid = OrderId.generate()
    event = OrderCancelled(order_id=oid, reason="cliente cambio de opinion")
    assert event.order_id == oid
    assert event.reason == "cliente cambio de opinion"


def test_order_cancelled_sin_reason() -> None:
    """OrderCancelled sin reason (default vacio)."""
    oid = OrderId.generate()
    event = OrderCancelled(order_id=oid)
    assert event.reason == ""


def test_order_cancelled_heredado_de_domain_event() -> None:
    """OrderCancelled hereda de DomainEvent."""
    assert issubclass(OrderCancelled, DomainEvent)


# ============================================
# Timestamp UTC
# ============================================


def test_eventos_occurred_at_es_utc() -> None:
    """occurred_at tiene timezone."""
    event = OrderCreated(
        order_id=OrderId.generate(),
        customer_email="a@b.com",
        total=100.0,
    )
    assert event.occurred_at.tzinfo is not None

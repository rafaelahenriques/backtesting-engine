import pytest

from backtester.broker import SimulatedBroker
from backtester.models import Order, Side
from tests.factories import make_bar


def test_fill_uses_open_price_and_charges_commission() -> None:
    broker = SimulatedBroker(commission_rate=0.01)
    bar = make_bar(0, open=50, close=55)

    fill = broker.fill(Order(Side.BUY, quantity=10), bar)

    assert fill.timestamp == bar.timestamp
    assert fill.side is Side.BUY
    assert fill.quantity == 10
    assert fill.price == 50
    assert fill.commission == pytest.approx(5)


def test_affordable_quantity_includes_commission() -> None:
    broker = SimulatedBroker(commission_rate=0.01)

    # 100 shares at 10 would cost 1010 with commission, so only 99 fit in 1000.
    assert broker.affordable_quantity(1000, make_bar(0, open=10)) == 99


def test_rejects_negative_commission() -> None:
    with pytest.raises(ValueError):
        SimulatedBroker(commission_rate=-0.01)

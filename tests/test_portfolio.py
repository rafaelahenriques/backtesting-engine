import pytest

from backtester.models import Fill, Side
from backtester.portfolio import Portfolio
from tests.factories import START


def make_fill(side: Side, quantity: int, price: float, commission: float = 0.0) -> Fill:
    return Fill(START, side, quantity, price, commission)


def test_buy_then_sell_updates_cash_and_records_trade() -> None:
    portfolio = Portfolio(cash=1000)

    portfolio.apply(make_fill(Side.BUY, quantity=10, price=50, commission=1))

    assert portfolio.cash == 499
    assert portfolio.quantity == 10
    assert portfolio.value(price=60) == 1099

    portfolio.apply(make_fill(Side.SELL, quantity=10, price=60, commission=1))

    assert portfolio.cash == 1098
    assert portfolio.quantity == 0
    assert [trade.pnl for trade in portfolio.trades] == [98]


def test_buy_while_holding_raises() -> None:
    portfolio = Portfolio(cash=1000)
    portfolio.apply(make_fill(Side.BUY, quantity=1, price=10))

    with pytest.raises(ValueError):
        portfolio.apply(make_fill(Side.BUY, quantity=1, price=10))


def test_sell_without_position_raises() -> None:
    with pytest.raises(ValueError):
        Portfolio(cash=1000).apply(make_fill(Side.SELL, quantity=1, price=10))


def test_partial_sell_raises() -> None:
    portfolio = Portfolio(cash=1000)
    portfolio.apply(make_fill(Side.BUY, quantity=10, price=10))

    with pytest.raises(ValueError):
        portfolio.apply(make_fill(Side.SELL, quantity=5, price=10))

import pytest

from backtester.broker import SimulatedBroker
from backtester.engine import run_backtest
from backtester.models import Bar, Side
from tests.factories import make_bar

BARS = [
    make_bar(0, open=10, close=10),
    make_bar(1, open=11, close=12),
    make_bar(2, open=12, close=13),
    make_bar(3, open=15, close=14),
]


class ScriptedStrategy:
    """Returns a fixed signal per bar index."""

    def __init__(self, signals: dict[int, Side]) -> None:
        self.signals = signals
        self.index = 0

    def on_bar(self, bar: Bar) -> Side | None:
        signal = self.signals.get(self.index)
        self.index += 1
        return signal


def test_signals_execute_at_the_next_bars_open() -> None:
    strategy = ScriptedStrategy({0: Side.BUY, 2: Side.SELL})

    result = run_backtest(BARS, strategy, broker=SimulatedBroker(), initial_cash=100)

    # Buy 9 at 11 on bar 1 (cash left: 1), sell 9 at 15 on bar 3.
    assert [value for _, value in result.equity_curve] == [100, 109, 118, 136]
    assert [trade.pnl for trade in result.trades] == [36]
    assert result.performance.total_return == pytest.approx(0.36)
    assert result.performance.trades == 1


def test_signals_that_do_not_change_the_position_are_ignored() -> None:
    # SELL while flat and BUY while already holding do nothing.
    strategy = ScriptedStrategy({0: Side.SELL, 1: Side.BUY, 2: Side.BUY})

    result = run_backtest(BARS, strategy, broker=SimulatedBroker(), initial_cash=100)

    # Buy 8 at 12 on bar 2 (cash left: 4), still holding at the end.
    assert [value for _, value in result.equity_curve] == [100, 100, 108, 116]
    assert result.trades == []


def test_rejects_empty_bars() -> None:
    with pytest.raises(ValueError):
        run_backtest([], ScriptedStrategy({}), broker=SimulatedBroker(), initial_cash=100)

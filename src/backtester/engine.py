"""Runs a strategy over historical bars."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from backtester.broker import SimulatedBroker
from backtester.metrics import Performance, evaluate
from backtester.models import Bar, Order, Side, Trade
from backtester.portfolio import Portfolio
from backtester.strategy import Strategy


@dataclass(frozen=True, slots=True)
class BacktestResult:
    equity_curve: list[tuple[datetime, float]]
    trades: list[Trade]
    performance: Performance


def run_backtest(
    bars: Sequence[Bar],
    strategy: Strategy,
    *,
    broker: SimulatedBroker,
    initial_cash: float,
    periods_per_year: int = 252,
) -> BacktestResult:
    """Replay bars through the strategy and simulate the trades it signals.

    For each bar, in order:
      1. Execute the previous bar's signal at this bar's open.
      2. Record the portfolio value at this bar's close.
      3. Show the bar to the strategy and keep its signal for the next bar.

    Acting on the next bar means the strategy never trades on prices it could not have known.
    Long only: a BUY invests all cash, a SELL closes the whole position.
    A position still open after the last bar stays open and is valued at the last close.
    """
    if not bars:
        raise ValueError("No bars to backtest")

    portfolio = Portfolio(initial_cash)
    equity_curve: list[tuple[datetime, float]] = []
    signal: Side | None = None

    for bar in bars:
        if signal is not None:
            order = _order_for(signal, portfolio, broker, bar)
            if order is not None:
                portfolio.apply(broker.fill(order, bar))

        equity_curve.append((bar.timestamp, portfolio.value(bar.close)))
        signal = strategy.on_bar(bar)

    equity = [value for _, value in equity_curve]
    performance = evaluate(equity, portfolio.trades, periods_per_year)
    return BacktestResult(equity_curve, portfolio.trades, performance)


def _order_for(
    signal: Side, portfolio: Portfolio, broker: SimulatedBroker, bar: Bar
) -> Order | None:
    """Turn a signal into an order, or None when it does not apply to the current position."""
    if signal is Side.BUY and portfolio.quantity == 0:
        quantity = broker.affordable_quantity(portfolio.cash, bar)
        return Order(Side.BUY, quantity) if quantity > 0 else None
    if signal is Side.SELL and portfolio.quantity > 0:
        return Order(Side.SELL, portfolio.quantity)
    return None

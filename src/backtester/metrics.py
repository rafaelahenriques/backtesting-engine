"""Performance metrics for a finished backtest.

Ratios are fractions: 0.12 means 12%.
"""

import math
import statistics
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise

from backtester.models import Trade


@dataclass(frozen=True, slots=True)
class Performance:
    total_return: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    volatility: float
    trades: int


def evaluate(
    equity: Sequence[float], trades: Sequence[Trade], periods_per_year: int
) -> Performance:
    """Score a backtest from its equity curve (portfolio value per bar) and closed trades."""
    returns = period_returns(equity)
    return Performance(
        total_return=total_return(equity),
        win_rate=win_rate(trades),
        max_drawdown=max_drawdown(equity),
        sharpe_ratio=sharpe_ratio(returns, periods_per_year),
        volatility=volatility(returns, periods_per_year),
        trades=len(trades),
    )


def period_returns(equity: Sequence[float]) -> list[float]:
    """Return from each bar to the next."""
    return [current / previous - 1 for previous, current in pairwise(equity)]


def total_return(equity: Sequence[float]) -> float:
    """Total change in portfolio value over the test period."""
    return equity[-1] / equity[0] - 1


def win_rate(trades: Sequence[Trade]) -> float:
    """Share of closed trades that made a profit. 0 when there are no trades."""
    if not trades:
        return 0.0
    return sum(trade.pnl > 0 for trade in trades) / len(trades)


def max_drawdown(equity: Sequence[float]) -> float:
    """Largest fall from a peak before a new high. 0.25 means a 25% fall."""
    peak = equity[0]
    largest_fall = 0.0
    for value in equity:
        peak = max(peak, value)
        largest_fall = max(largest_fall, (peak - value) / peak)
    return largest_fall


def volatility(returns: Sequence[float], periods_per_year: int) -> float:
    """Annualised standard deviation of period returns."""
    if len(returns) < 2:
        return 0.0
    return statistics.stdev(returns) * math.sqrt(periods_per_year)


def sharpe_ratio(returns: Sequence[float], periods_per_year: int) -> float:
    """Annualised mean return per unit of volatility, with a risk-free rate of 0."""
    if len(returns) < 2:
        return 0.0
    deviation = statistics.stdev(returns)
    if deviation == 0:
        return 0.0
    return statistics.mean(returns) / deviation * math.sqrt(periods_per_year)

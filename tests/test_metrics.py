import math

import pytest

from backtester.metrics import (
    max_drawdown,
    period_returns,
    sharpe_ratio,
    total_return,
    volatility,
    win_rate,
)
from backtester.models import Fill, Side, Trade
from tests.factories import START


def make_trade(entry_price: float, exit_price: float) -> Trade:
    return Trade(
        entry=Fill(START, Side.BUY, 1, entry_price, commission=0),
        exit=Fill(START, Side.SELL, 1, exit_price, commission=0),
    )


def test_period_returns() -> None:
    assert period_returns([100, 110, 99]) == pytest.approx([0.1, -0.1])


def test_total_return() -> None:
    assert total_return([100, 110, 121]) == pytest.approx(0.21)


def test_win_rate() -> None:
    trades = [make_trade(10, 12), make_trade(10, 8), make_trade(10, 11)]

    assert win_rate(trades) == pytest.approx(2 / 3)


def test_win_rate_without_trades_is_zero() -> None:
    assert win_rate([]) == 0


def test_max_drawdown_is_largest_fall_from_a_peak() -> None:
    # 120 -> 90 is a 25% fall; 130 -> 117 is only 10%.
    assert max_drawdown([100, 120, 90, 130, 117]) == pytest.approx(0.25)


def test_max_drawdown_without_falls_is_zero() -> None:
    assert max_drawdown([100, 110, 120]) == 0


def test_volatility_is_annualised_standard_deviation() -> None:
    returns = [0.01, 0.03]
    standard_deviation = math.sqrt(2) / 100

    assert volatility(returns, periods_per_year=1) == pytest.approx(standard_deviation)
    assert volatility(returns, periods_per_year=4) == pytest.approx(2 * standard_deviation)


def test_sharpe_ratio_is_annualised_mean_over_standard_deviation() -> None:
    returns = [0.01, 0.03]
    mean_over_deviation = 0.02 / (math.sqrt(2) / 100)

    assert sharpe_ratio(returns, periods_per_year=1) == pytest.approx(mean_over_deviation)
    assert sharpe_ratio(returns, periods_per_year=4) == pytest.approx(2 * mean_over_deviation)


def test_sharpe_ratio_without_variation_is_zero() -> None:
    assert sharpe_ratio([0.01, 0.01, 0.01], periods_per_year=252) == 0

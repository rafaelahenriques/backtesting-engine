import pytest

from backtester.models import Side
from backtester.strategy import MovingAverageCrossover
from tests.factories import make_bar


def run(strategy: MovingAverageCrossover, closes: list[float]) -> list[Side | None]:
    return [strategy.on_bar(make_bar(day, close=close)) for day, close in enumerate(closes)]


def test_moving_average_crossover_signals_on_crossovers() -> None:
    strategy = MovingAverageCrossover(fast=2, slow=3)

    signals = run(strategy, [3, 2, 1, 1, 5, 1, 0.5])

    assert signals == [None, None, None, None, Side.BUY, None, Side.SELL]


def test_moving_average_crossover_needs_a_full_slow_window_and_a_cross() -> None:
    strategy = MovingAverageCrossover(fast=2, slow=3)

    signals = run(strategy, [1, 2, 3, 4])

    assert signals == [None, None, None, None]


@pytest.mark.parametrize(("fast", "slow"), [(0, 3), (3, 3), (4, 3)])
def test_moving_average_crossover_rejects_invalid_windows(fast: int, slow: int) -> None:
    with pytest.raises(ValueError):
        MovingAverageCrossover(fast=fast, slow=slow)

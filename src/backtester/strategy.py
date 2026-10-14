"""Strategies turn each new bar into buy and sell signals."""

from collections import deque
from typing import Protocol

from backtester.models import Bar, Side


class Strategy(Protocol):
    def on_bar(self, bar: Bar) -> Side | None:
        """Return BUY or SELL to signal a trade, or None to do nothing."""
        ...


class MovingAverageCrossover:
    """Buys when the fast moving average crosses above the slow one, sells when it crosses below."""

    def __init__(self, fast: int, slow: int) -> None:
        if not 0 < fast < slow:
            raise ValueError("Expected 0 < fast < slow")
        self.fast = fast
        self.slow = slow
        self._closes: deque[float] = deque(maxlen=slow)
        self._fast_was_above: bool | None = None

    def on_bar(self, bar: Bar) -> Side | None:
        self._closes.append(bar.close)
        if len(self._closes) < self.slow:
            return None

        fast_average = sum(list(self._closes)[-self.fast :]) / self.fast
        slow_average = sum(self._closes) / self.slow
        fast_is_above = fast_average > slow_average

        crossed = self._fast_was_above is not None and fast_is_above != self._fast_was_above
        self._fast_was_above = fast_is_above

        if not crossed:
            return None
        return Side.BUY if fast_is_above else Side.SELL

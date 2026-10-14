"""Tracks cash, the open position and closed trades."""

from backtester.models import Fill, Side, Trade


class Portfolio:
    """Cash plus at most one long position.

    A buy opens the position and a sell closes all of it.
    """

    def __init__(self, cash: float) -> None:
        self.cash = cash
        self.entry: Fill | None = None
        self.trades: list[Trade] = []

    @property
    def quantity(self) -> int:
        return self.entry.quantity if self.entry else 0

    def apply(self, fill: Fill) -> None:
        """Update cash and position for an executed order."""
        traded_value = fill.price * fill.quantity

        match fill.side:
            case Side.BUY:
                if self.entry is not None:
                    raise ValueError("A position is already open")
                self.cash -= traded_value + fill.commission
                self.entry = fill
            case Side.SELL:
                if self.entry is None or fill.quantity != self.entry.quantity:
                    raise ValueError("A sell must close the whole open position")
                self.cash += traded_value - fill.commission
                self.trades.append(Trade(entry=self.entry, exit=fill))
                self.entry = None

    def value(self, price: float) -> float:
        """Cash plus the open position valued at price."""
        return self.cash + self.quantity * price

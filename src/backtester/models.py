"""Data types shared across the engine."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass(frozen=True, slots=True)
class Bar:
    """Prices for one period, e.g. one trading day."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class Side(Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass(frozen=True, slots=True)
class Order:
    """A request to buy or sell a quantity at the market price."""

    side: Side
    quantity: int


@dataclass(frozen=True, slots=True)
class Fill:
    """An order that has been executed."""

    timestamp: datetime
    side: Side
    quantity: int
    price: float
    commission: float


@dataclass(frozen=True, slots=True)
class Trade:
    """A closed position: the buy that opened it and the sell that closed it."""

    entry: Fill
    exit: Fill

    @property
    def pnl(self) -> float:
        """Profit or loss after commissions."""
        gross = (self.exit.price - self.entry.price) * self.exit.quantity
        return gross - self.entry.commission - self.exit.commission

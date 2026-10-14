"""Simulated order execution."""

import math

from backtester.models import Bar, Fill, Order


class SimulatedBroker:
    """Fills orders at the bar's open price and charges a commission.

    commission_rate is a fraction of the traded value: 0.001 means 0.1%.
    """

    def __init__(self, commission_rate: float = 0.0) -> None:
        if commission_rate < 0:
            raise ValueError("commission_rate cannot be negative")
        self.commission_rate = commission_rate

    def fill(self, order: Order, bar: Bar) -> Fill:
        price = bar.open
        commission = price * order.quantity * self.commission_rate
        return Fill(bar.timestamp, order.side, order.quantity, price, commission)

    def affordable_quantity(self, cash: float, bar: Bar) -> int:
        """Largest whole quantity that cash can buy at this bar, commission included."""
        return math.floor(cash / (bar.open * (1 + self.commission_rate)))

from datetime import datetime, timedelta

from backtester.models import Bar

START = datetime(2026, 1, 1)


def make_bar(day: int, open: float = 100.0, close: float = 100.0) -> Bar:
    """A daily bar `day` days after START. High and low span open and close."""
    return Bar(
        timestamp=START + timedelta(days=day),
        open=open,
        high=max(open, close),
        low=min(open, close),
        close=close,
        volume=1_000,
    )

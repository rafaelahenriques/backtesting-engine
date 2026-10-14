"""Loading historical price data."""

import csv
from datetime import datetime
from itertools import pairwise
from pathlib import Path

from backtester.models import Bar


def load_bars_csv(path: Path) -> list[Bar]:
    """Load bars from a CSV file with columns: timestamp, open, high, low, close, volume.

    Timestamps must be ISO 8601. Bars are returned oldest first.
    Raises ValueError if two bars share a timestamp.
    """
    with path.open(newline="") as file:
        bars = [_parse_row(row) for row in csv.DictReader(file)]

    bars.sort(key=lambda bar: bar.timestamp)
    for previous, current in pairwise(bars):
        if current.timestamp == previous.timestamp:
            raise ValueError(f"Duplicate timestamp: {current.timestamp.isoformat()}")

    return bars


def _parse_row(row: dict[str, str]) -> Bar:
    return Bar(
        timestamp=datetime.fromisoformat(row["timestamp"]),
        open=float(row["open"]),
        high=float(row["high"]),
        low=float(row["low"]),
        close=float(row["close"]),
        volume=float(row["volume"]),
    )

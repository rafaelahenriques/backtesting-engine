from datetime import datetime
from pathlib import Path

import pytest

from backtester.data import load_bars_csv
from backtester.models import Bar

HEADER = "timestamp,open,high,low,close,volume\n"


def test_load_bars_csv_returns_bars_oldest_first(tmp_path: Path) -> None:
    path = tmp_path / "bars.csv"
    path.write_text(
        HEADER + "2026-01-02,11,12,10,11.5,2000\n2026-01-01,10,11,9,10.5,1000\n",
    )

    bars = load_bars_csv(path)

    assert bars == [
        Bar(datetime(2026, 1, 1), open=10, high=11, low=9, close=10.5, volume=1000),
        Bar(datetime(2026, 1, 2), open=11, high=12, low=10, close=11.5, volume=2000),
    ]


def test_load_bars_csv_rejects_duplicate_timestamps(tmp_path: Path) -> None:
    path = tmp_path / "bars.csv"
    path.write_text(HEADER + "2026-01-01,10,11,9,10.5,1000\n2026-01-01,10,11,9,10.5,1000\n")

    with pytest.raises(ValueError, match="Duplicate timestamp"):
        load_bars_csv(path)

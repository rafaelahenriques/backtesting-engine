# Trading Backtesting Engine

Replays historical market data through a trading strategy, simulates the orders it would place
and measures how that strategy would have performed.

## Architecture

| Stage | Module | Status |
| --- | --- | --- |
| 1. Historical data | `data.py` | CSV files. Market-data APIs not built yet. |
| 2. Data processing | `data.py` | Sorts bars and rejects duplicate timestamps. |
| 3. Strategy engine | `strategy.py` | `Strategy` interface and a moving average crossover. |
| 4. Order simulation | `broker.py` | Fills at the next bar's open with a percentage commission. |
| 5. Portfolio engine | `portfolio.py` | Cash and one long position. |
| 6. Performance analysis | `metrics.py` | Return, win rate, max drawdown, Sharpe ratio, volatility, trades. |

`engine.py` connects the stages. Not built yet: market-data API client, PostgreSQL storage, Docker setup.

## Usage

```python
from pathlib import Path

from backtester.broker import SimulatedBroker
from backtester.data import load_bars_csv
from backtester.engine import run_backtest
from backtester.strategy import MovingAverageCrossover

bars = load_bars_csv(Path("data/prices.csv"))
result = run_backtest(
    bars,
    MovingAverageCrossover(fast=20, slow=50),
    broker=SimulatedBroker(commission_rate=0.001),
    initial_cash=10_000,
)
print(result.performance)
```

The CSV needs the columns `timestamp,open,high,low,close,volume`, with ISO 8601 timestamps.

## Development

Requires [uv](https://docs.astral.sh/uv/). It installs the Python version from `.python-version`.

```bash
uv sync                # install dependencies
uv run pytest          # run tests
uv run ruff check      # lint
uv run ruff format     # format
uv run mypy            # type-check
```

CI runs the same checks on every pull request.

## Workflow

GitHub flow: `main` is always working. Branch from `main`, commit, open a pull request,
merge once CI passes.

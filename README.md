# Crypto Quant

Crypto Quant is a long-term scaffold for a modular cryptocurrency quantitative trading platform, initially focused on Binance Spot.

The project is currently in the foundation stage. It contains the package layout, configuration skeleton, dashboard skeleton, test layout, and architecture documentation. Trading logic, market data downloaders, backtest engines, brokers, and live trading components are not implemented yet.

## Design Principles

- Keep domain models simple.
- Hide external dependencies behind ports/interfaces.
- Compose runtime flows instead of hard-wiring modes.
- Make strategies, exchanges, storage, and execution replaceable.
- Keep the dashboard as an observation and controlled-operations layer, not a trading logic layer.

## Current Scope

Planned build order:

```text
historical data
-> vectorized backtest
-> event-driven backtest
-> paper trading
-> live safety layer
-> small live trading
-> dashboard
-> multi-symbol / multi-strategy
-> production hardening
```

The first real milestone is a reproducible Binance Spot `BTCUSDT` historical backtest using local candle storage and a baseline EMA crossover strategy.

## Repository Layout

```text
config/                 Runtime configuration files
dashboard/              Frontend dashboard skeleton
data/                   Local data directories; real data is git-ignored
docs/                   Architecture, interface, safety, and development docs
research/               Experiments and notebooks, isolated from production code
scripts/                CLI entry points for data, trading, and ops workflows
src/cq/                 Main Python package
tests/                  Unit, integration, e2e, and fixture layout
```

Important backend packages:

```text
src/cq/domain/          Core domain models
src/cq/ports/           Interfaces for replaceable dependencies
src/cq/data/            Historical and live market data logic
src/cq/exchanges/       Exchange adapters, starting with Binance
src/cq/storage/         SQLite, PostgreSQL, Parquet, and repositories
src/cq/features/        Indicators and feature transforms
src/cq/strategies/      Strategy implementations and registry
src/cq/portfolio/       Portfolio accounting and valuation
src/cq/risk/            Pre-trade checks, limits, kill switch
src/cq/execution/       Order lifecycle, brokers, fills, reconciliation
src/cq/backtest/        Vectorized and event-driven backtest engines
src/cq/runtime/         Backtest, paper, and live runtime orchestration
src/cq/api/             Backend API for the dashboard
src/cq/monitoring/      Logging, metrics, alerts, and health checks
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Interfaces](docs/INTERFACES.md)
- [Trading Safety](docs/TRADING_SAFETY.md)
- [Development Guide](docs/DEVELOPMENT_GUIDE.md)
- [Dashboard Guide](docs/DASHBOARD_GUIDE.md)
- [Architecture Notes Index](docs/ARCHITECTURE_NOTES.md)

## Development Status

Implemented:

- Project directory scaffold.
- Python package skeleton under `src/cq`.
- Configuration skeleton under `config`.
- Dashboard directory skeleton under `dashboard`.
- Test directory skeleton under `tests`.
- Architecture and safety documentation.
- Basic `pyproject.toml`, `.env.example`, `Makefile`, and `docker-compose.yml`.

Not implemented yet:

- Domain models.
- Ports/interfaces.
- Config loader and validation.
- Market data storage.
- Binance clients and mappers.
- Backtest engines.
- Risk, execution, reconciliation, and paper/live trading.
- API server and dashboard UI.

## Setup

The project currently requires Python 3.11 or newer. Dependency management is not finalized yet; `uv` is the preferred direction.

Basic editable install:

```bash
python -m pip install -e .
```

Verify the package import:

```bash
python -c "import cq; print(cq.__name__)"
```

The current `Makefile` is minimal:

```bash
make test
make lint
make format
```

These commands are placeholders until `pytest`, `ruff`, and development dependencies are fully configured.

## Configuration

Configuration files live in `config/`:

```text
base.yaml
backtest.yaml
paper.yaml
live.yaml
logging.yaml
```

Live trading must remain disabled by default. Future live configuration should require explicit enablement, symbol allowlists, max notional limits, mandatory reconciliation, and a kill switch.

## Secrets

Use `.env.example` as a template. Do not commit real secrets.

Expected environment variables include:

```text
BINANCE_API_KEY
BINANCE_API_SECRET
BINANCE_TESTNET
CQ_ENV
CQ_CONFIG
DATABASE_URL
CQ_API_HOST
CQ_API_PORT
```

## Safety Rules

Live trading code must follow these constraints:

- Strategies must not call Binance clients directly.
- Dashboard code must not call Binance APIs directly.
- All live orders must pass pre-trade risk checks.
- All live orders must pass Binance filter validation.
- Startup must run account/order reconciliation before trading.
- Client order IDs must be idempotent.
- Core order, fill, balance, price, and quantity logic must not rely on raw `float`.

See [Trading Safety](docs/TRADING_SAFETY.md) for the detailed rules.

## Roadmap

Near-term tasks:

1. Finalize Python toolchain and dependencies.
2. Configure `pytest`, `ruff`, and type checking.
3. Implement domain models.
4. Implement ports/interfaces.
5. Implement config loading and validation.
6. Implement local candle storage.
7. Implement Binance historical data download.
8. Implement the first EMA crossover vectorized backtest.

## License

No license has been selected yet.

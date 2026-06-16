"""Download historical candles from Binance into the configured candle store."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from cq.config import AppConfig, ConfigError, load_config  # noqa: E402
from cq.domain import RuntimeMode  # noqa: E402
from cq.exchanges.binance import (  # noqa: E402
    BinanceKlineClient,
    BinancePublicRestClient,
    download_historical_candles,
)
from cq.storage import JsonlCandleStore  # noqa: E402


def run_download_history(
    config: AppConfig,
    client: BinanceKlineClient | None = None,
) -> tuple[int, int]:
    if config.mode is RuntimeMode.LIVE:
        raise ConfigError("download history must not run in live mode")

    start = config.data.start
    end = config.data.end
    if start is None or end is None:
        raise ConfigError("data start and end are required to download history")

    symbol = config.exchange.symbols[0]
    store = JsonlCandleStore(config.storage.root)
    kline_client = BinancePublicRestClient() if client is None else client
    return download_historical_candles(
        kline_client,
        store,
        symbol,
        config.data.interval,
        start,
        end,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default=RuntimeMode.BACKTEST.value)
    parser.add_argument("--config-dir", default="config")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(args.mode, args.config_dir)
    fetched_count, saved_count = run_download_history(config)
    print(f"fetched={fetched_count} saved={saved_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

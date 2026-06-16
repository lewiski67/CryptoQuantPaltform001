from datetime import UTC, datetime, timedelta
from pathlib import Path

from scripts.data.download_history import run_download_history
from tests.unit.domain.helpers import assert_value_error

from cq.config import AppConfig, LiveConfig, load_config
from cq.domain import Symbol
from cq.domain.enums import RuntimeMode
from cq.exchanges.binance import BinanceKline
from cq.storage import JsonlCandleStore


def test_run_download_history_uses_config_and_saves_candles(tmp_path: Path) -> None:
    config_dir = write_config(tmp_path, include_range=True)
    config = load_config("backtest", config_dir)
    client = FakeBinanceClient((sample_kline(0, 1),))

    fetched_count, saved_count = run_download_history(config, client)

    loaded = JsonlCandleStore(config.storage.root).load_candles(
        config.exchange.symbols[0],
        config.data.interval,
        timestamp(0),
        timestamp(1),
    )
    assert fetched_count == 1
    assert saved_count == 1
    assert client.requests == ((config.exchange.symbols[0], "1h", timestamp(0), timestamp(1)),)
    assert len(loaded) == 1


def test_run_download_history_requires_configured_time_range(tmp_path: Path) -> None:
    config_dir = write_config(tmp_path, include_range=False)
    config = load_config("backtest", config_dir)

    def download_without_range() -> object:
        return run_download_history(config, FakeBinanceClient(()))

    assert_value_error(
        "data start and end are required to download history",
        download_without_range,
    )


def test_run_download_history_rejects_live_mode(tmp_path: Path) -> None:
    config_dir = write_config(tmp_path, include_range=True)
    backtest_config = load_config("backtest", config_dir)
    live_config = AppConfig(
        mode=RuntimeMode.LIVE,
        exchange=backtest_config.exchange,
        data=backtest_config.data,
        storage=backtest_config.storage,
        risk=backtest_config.risk,
        live=LiveConfig(enabled=True, require_confirmation=True, reconciliation_required=True),
    )
    client = FakeBinanceClient(())

    def download_live_history() -> object:
        return run_download_history(live_config, client)

    assert_value_error("download history must not run in live mode", download_live_history)
    assert client.requests == ()


class FakeBinanceClient:
    def __init__(self, klines: tuple[BinanceKline, ...]) -> None:
        self.klines = klines
        self.requests: tuple[tuple[Symbol, str, datetime, datetime], ...] = ()

    def fetch_klines(
        self,
        symbol: Symbol,
        interval: str,
        start: datetime,
        end: datetime,
        limit: int = 1000,
    ) -> tuple[BinanceKline, ...]:
        self.requests = (*self.requests, (symbol, interval, start, end))
        return self.klines[:limit]


def write_config(tmp_path: Path, include_range: bool) -> Path:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    storage_root = tmp_path / "storage"
    (config_dir / "base.yaml").write_text(
        "\n".join(
            [
                "exchange:",
                "  name: binance",
                "  symbols:",
                "    - value: BTCUSDT",
                "      base_asset: BTC",
                "      quote_asset: USDT",
                "data:",
                "  interval: 1h",
                "  start: null",
                "  end: null",
                "storage:",
                f"  root: {storage_root}",
                "risk:",
                '  max_order_notional: "100"',
                "live:",
                "  enabled: false",
                "  require_confirmation: false",
                "  reconciliation_required: false",
            ]
        ),
        encoding="utf-8",
    )
    backtest_lines = ["mode: backtest"]
    if include_range:
        backtest_lines.extend(
            [
                "data:",
                '  start: "2026-01-01T00:00:00+00:00"',
                '  end: "2026-01-01T01:00:00+00:00"',
            ]
        )
    (config_dir / "backtest.yaml").write_text("\n".join(backtest_lines), encoding="utf-8")
    return config_dir


def sample_kline(open_hour: int, close_hour: int) -> BinanceKline:
    return (
        millis(timestamp(open_hour)),
        "100.00",
        "110.00",
        "90.00",
        "105.00",
        "12.5",
        millis(timestamp(close_hour) - timedelta(milliseconds=1)),
    )


def timestamp(hour: int) -> datetime:
    return datetime(2026, 1, 1, hour, tzinfo=UTC)


def millis(value: datetime) -> int:
    return int(value.timestamp() * 1000)

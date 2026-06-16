from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from cq.config import load_config
from cq.domain import Candle, RuntimeMode, Symbol
from cq.ports import HistoricalDataStorePort
from cq.storage import JsonlCandleStore


def test_config_domain_and_jsonl_storage_work_together(tmp_path: Path) -> None:
    config_dir = write_config(tmp_path)
    config = load_config(RuntimeMode.BACKTEST, config_dir)
    store: HistoricalDataStorePort = JsonlCandleStore(config.storage.root)
    candles = (
        candle(config.exchange.symbols[0], config.data.interval, timestamp(0)),
        candle(config.exchange.symbols[0], config.data.interval, timestamp(1)),
    )

    store.save_candles(candles)

    loaded = store.load_candles(
        config.exchange.symbols[0],
        config.data.interval,
        timestamp(0),
        timestamp(2),
    )
    assert loaded == candles


def write_config(tmp_path: Path) -> Path:
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
    (config_dir / "backtest.yaml").write_text(
        "\n".join(
            [
                "mode: backtest",
                "data:",
                '  start: "2026-01-01T00:00:00+00:00"',
                '  end: "2026-01-02T00:00:00+00:00"',
            ]
        ),
        encoding="utf-8",
    )
    return config_dir


def candle(symbol: Symbol, interval: str, open_time: datetime) -> Candle:
    return Candle(
        symbol=symbol,
        interval=interval,
        open_time=open_time,
        close_time=open_time + timedelta(hours=1),
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("90"),
        close=Decimal("105"),
        volume=Decimal("1"),
    )


def timestamp(hour: int) -> datetime:
    return datetime(2026, 1, 1, hour, tzinfo=UTC)

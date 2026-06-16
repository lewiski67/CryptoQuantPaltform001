import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

from tests.unit.domain.helpers import assert_value_error

from cq.domain import Symbol
from cq.exchanges.binance import kline_to_candle, klines_to_candles


def test_kline_to_candle_maps_binance_ohlcv_fields() -> None:
    candle = kline_to_candle(btc_usdt(), "1h", sample_kline())

    assert candle.symbol == btc_usdt()
    assert candle.interval == "1h"
    assert candle.open_time == timestamp(0)
    assert candle.close_time == timestamp(1)
    assert candle.open == Decimal("100.00")
    assert candle.high == Decimal("110.00")
    assert candle.low == Decimal("90.00")
    assert candle.close == Decimal("105.00")
    assert candle.volume == Decimal("12.5")


def test_klines_to_candles_maps_multiple_records() -> None:
    candles = klines_to_candles(
        btc_usdt(),
        "1h",
        (sample_kline(), sample_kline(open_hour=1, close_hour=2)),
    )

    assert len(candles) == 2
    assert candles[0].close_time == candles[1].open_time


def test_kline_to_candle_rejects_short_record() -> None:
    def map_short_record() -> object:
        return kline_to_candle(btc_usdt(), "1h", cast(Any, [1, "100"]))

    assert_value_error("Binance kline must contain at least 7 fields", map_short_record)


def test_kline_to_candle_rejects_bad_decimal() -> None:
    record = list(sample_kline())
    record[1] = "not-a-decimal"

    def map_bad_record() -> object:
        return kline_to_candle(btc_usdt(), "1h", record)

    assert_value_error("invalid Binance kline", map_bad_record)


def test_kline_to_candle_maps_fixture_sample() -> None:
    candle = kline_to_candle(btc_usdt(), "1h", load_fixture()[0])

    assert candle.open_time == timestamp(0)
    assert candle.close_time == timestamp(1)
    assert candle.open == Decimal("87648.21000000")
    assert candle.close == Decimal("87809.23000000")


def load_fixture() -> list[list[object]]:
    path = Path("tests/fixtures/klines_sample.json")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, list):
        raise AssertionError("fixture must contain a list")
    return cast(list[list[object]], loaded)


def sample_kline(open_hour: int = 0, close_hour: int = 1) -> tuple[object, ...]:
    return (
        millis(timestamp(open_hour)),
        "100.00",
        "110.00",
        "90.00",
        "105.00",
        "12.5",
        millis(timestamp(close_hour) - timedelta(milliseconds=1)),
        "0",
        1,
        "0",
        "0",
        "0",
    )


def btc_usdt() -> Symbol:
    return Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")


def timestamp(hour: int) -> datetime:
    return datetime(2026, 1, 1, hour, tzinfo=UTC)


def millis(value: datetime) -> int:
    return int(value.timestamp() * 1000)

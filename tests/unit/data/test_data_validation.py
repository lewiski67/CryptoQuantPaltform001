from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, cast

from tests.unit.domain.helpers import assert_value_error

from cq.data import find_missing_ranges, validate_candle_series
from cq.domain import Candle, Symbol


def test_validate_candle_series_accepts_continuous_candles() -> None:
    validate_candle_series((candle(0), candle(1)))


def test_validate_candle_series_rejects_duplicate_open_times() -> None:
    def validate() -> None:
        validate_candle_series((candle(0), candle(0)))

    assert_value_error("candles must have unique open times", validate)


def test_validate_candle_series_rejects_non_candle_items() -> None:
    def validate() -> None:
        validate_candle_series(cast(Any, ("not-a-candle",)))

    assert_value_error("candles must contain only Candle", validate)


def test_validate_candle_series_rejects_missing_interval() -> None:
    def validate() -> None:
        validate_candle_series((candle(0), candle(2)))

    assert_value_error("candles must be continuous", validate)


def test_find_missing_ranges_reports_gaps_without_requiring_continuity() -> None:
    missing = find_missing_ranges(
        (candle(0), candle(2)),
        timestamp(0),
        timestamp(3),
    )

    assert missing == ((timestamp(1), timestamp(2)),)


def test_find_missing_ranges_reports_empty_input_as_full_range() -> None:
    missing = find_missing_ranges((), timestamp(0), timestamp(2))

    assert missing == ((timestamp(0), timestamp(2)),)


def candle(hour: int) -> Candle:
    return Candle(
        symbol=Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT"),
        interval="1h",
        open_time=timestamp(hour),
        close_time=timestamp(hour + 1),
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("90"),
        close=Decimal("105"),
        volume=Decimal("1"),
    )


def timestamp(hour: int) -> datetime:
    return datetime(2026, 1, 1, hour, tzinfo=UTC)

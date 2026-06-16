from datetime import UTC, datetime
from decimal import Decimal

from tests.unit.domain.helpers import assert_value_error

from cq.domain import Candle, Symbol
from cq.features import close_to_close_returns


def test_close_to_close_returns_calculates_decimal_returns() -> None:
    returns = close_to_close_returns(
        (
            candle(0, close=Decimal("100")),
            candle(1, close=Decimal("105")),
            candle(2, close=Decimal("102")),
        )
    )

    assert returns == (Decimal("0.05"), Decimal("-0.02857142857142857142857142857"))


def test_close_to_close_returns_accepts_unsorted_candles() -> None:
    returns = close_to_close_returns(
        (
            candle(1, close=Decimal("105")),
            candle(0, close=Decimal("100")),
        )
    )

    assert returns == (Decimal("0.05"),)


def test_close_to_close_returns_returns_empty_tuple_for_short_input() -> None:
    assert close_to_close_returns(()) == ()
    assert close_to_close_returns((candle(0),)) == ()


def test_close_to_close_returns_rejects_non_continuous_candles() -> None:
    def calculate_returns() -> object:
        return close_to_close_returns((candle(0), candle(2)))

    assert_value_error("candles must be continuous", calculate_returns)


def candle(hour: int, close: Decimal = Decimal("100")) -> Candle:
    high = max(Decimal("100"), close)
    low = min(Decimal("100"), close)
    return Candle(
        symbol=Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT"),
        interval="1h",
        open_time=timestamp(hour),
        close_time=timestamp(hour + 1),
        open=Decimal("100"),
        high=high,
        low=low,
        close=close,
        volume=Decimal("1"),
    )


def timestamp(hour: int) -> datetime:
    return datetime(2026, 1, 1, hour, tzinfo=UTC)

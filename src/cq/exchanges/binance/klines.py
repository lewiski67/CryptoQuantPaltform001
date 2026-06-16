"""Binance kline mapping helpers."""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from decimal import Decimal, DecimalException

from cq.domain import Candle, Symbol

BinanceKline = tuple[object, ...]


def kline_to_candle(symbol: Symbol, interval: str, kline: Sequence[object]) -> Candle:
    if len(kline) < 7:
        raise ValueError("Binance kline must contain at least 7 fields")
    try:
        open_time = datetime_from_millis(kline[0])
        # Binance close time is inclusive; domain candles use exclusive close_time.
        close_time = datetime_from_millis(kline[6]) + timedelta(milliseconds=1)
        return Candle(
            symbol=symbol,
            interval=interval,
            open_time=open_time,
            close_time=close_time,
            open=parse_decimal(kline[1], "open"),
            high=parse_decimal(kline[2], "high"),
            low=parse_decimal(kline[3], "low"),
            close=parse_decimal(kline[4], "close"),
            volume=parse_decimal(kline[5], "volume"),
        )
    except (TypeError, ValueError, DecimalException) as exc:
        raise ValueError("invalid Binance kline") from exc


def klines_to_candles(
    symbol: Symbol,
    interval: str,
    klines: Sequence[Sequence[object]],
) -> tuple[Candle, ...]:
    return tuple(kline_to_candle(symbol, interval, kline) for kline in klines)


def datetime_from_millis(value: object) -> datetime:
    if not isinstance(value, int):
        raise ValueError("timestamp must be an integer millisecond value")
    return datetime.fromtimestamp(value / 1000, tz=UTC)


def millis_from_datetime(value: datetime) -> int:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime must be timezone-aware")
    return int(value.timestamp() * 1000)


def parse_decimal(value: object, field_name: str) -> Decimal:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    return Decimal(value)

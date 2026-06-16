"""Validation helpers for market data sequences."""

from datetime import datetime

from cq.domain import Candle


def validate_candle_series(candles: tuple[Candle, ...]) -> None:
    if not candles:
        return

    validate_candle_members(candles)
    ordered = sorted(candles, key=lambda candle: candle.open_time)

    for previous, current in zip(ordered, ordered[1:], strict=False):
        if current.open_time != previous.close_time:
            raise ValueError("candles must be continuous")


def validate_candle_members(candles: tuple[Candle, ...]) -> None:
    if not candles:
        return

    if not all(isinstance(candle, Candle) for candle in candles):
        raise ValueError("candles must contain only Candle")

    ordered = sorted(candles, key=lambda candle: candle.open_time)
    seen_open_times: set[datetime] = set()
    first = ordered[0]

    for candle in ordered:
        if candle.symbol != first.symbol:
            raise ValueError("candles must have the same symbol")
        if candle.interval != first.interval:
            raise ValueError("candles must have the same interval")
        if candle.open_time in seen_open_times:
            raise ValueError("candles must have unique open times")
        seen_open_times.add(candle.open_time)


def find_missing_ranges(
    candles: tuple[Candle, ...],
    start: datetime,
    end: datetime,
) -> tuple[tuple[datetime, datetime], ...]:
    require_aware_datetime(start, "start")
    require_aware_datetime(end, "end")
    if end <= start:
        raise ValueError("end must be after start")
    if not candles:
        return ((start, end),)

    ordered = tuple(sorted(candles, key=lambda candle: candle.open_time))
    validate_candle_members(ordered)

    missing: list[tuple[datetime, datetime]] = []
    cursor = start
    for candle in ordered:
        if candle.close_time <= start or candle.open_time >= end:
            continue
        if candle.open_time > cursor:
            missing.append((cursor, candle.open_time))
        if candle.close_time > cursor:
            cursor = candle.close_time
    if cursor < end:
        missing.append((cursor, end))
    return tuple(missing)


def require_aware_datetime(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")

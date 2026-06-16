"""Return feature calculations."""

from decimal import Decimal

from cq.data import validate_candle_series
from cq.domain import Candle


def close_to_close_returns(candles: tuple[Candle, ...]) -> tuple[Decimal, ...]:
    if len(candles) < 2:
        return ()

    ordered = tuple(sorted(candles, key=lambda candle: candle.open_time))
    validate_candle_series(ordered)
    return tuple(
        (current.close - previous.close) / previous.close
        for previous, current in zip(ordered, ordered[1:], strict=False)
    )

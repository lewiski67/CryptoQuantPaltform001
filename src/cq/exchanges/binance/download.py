"""Download Binance historical candles into a candle store."""

from datetime import datetime
from typing import Protocol

from cq.data import validate_candle_series
from cq.domain import Candle, Symbol
from cq.exchanges.binance.klines import BinanceKline, klines_to_candles
from cq.ports import HistoricalDataStorePort


class BinanceKlineClient(Protocol):
    def fetch_klines(
        self,
        symbol: Symbol,
        interval: str,
        start: datetime,
        end: datetime,
        limit: int = 1000,
    ) -> tuple[BinanceKline, ...]: ...


def download_historical_candles(
    client: BinanceKlineClient,
    store: HistoricalDataStorePort,
    symbol: Symbol,
    interval: str,
    start: datetime,
    end: datetime,
    limit: int = 1000,
) -> tuple[int, int]:
    if end <= start:
        raise ValueError("end must be after start")
    if limit <= 0 or limit > 1000:
        raise ValueError("limit must be between 1 and 1000")

    fetched_count = 0
    saved_count = 0
    cursor = start
    while cursor < end:
        raw_klines = client.fetch_klines(symbol, interval, cursor, end, limit=limit)
        if not raw_klines:
            break

        candles = klines_to_candles(symbol, interval, raw_klines)
        validate_candle_series(candles)
        fetched_count += len(candles)

        new_candles = filter_existing_candles(store, symbol, interval, start, end, candles)
        if new_candles:
            store.save_candles(new_candles)
            saved_count += len(new_candles)

        next_cursor = candles[-1].close_time
        if next_cursor <= cursor:
            raise ValueError("Binance klines did not advance cursor")
        cursor = next_cursor

    return fetched_count, saved_count


def filter_existing_candles(
    store: HistoricalDataStorePort,
    symbol: Symbol,
    interval: str,
    start: datetime,
    end: datetime,
    candles: tuple[Candle, ...],
) -> tuple[Candle, ...]:
    existing = store.load_candles(symbol, interval, start, end)
    existing_open_times = {candle.open_time for candle in existing}
    return tuple(candle for candle in candles if candle.open_time not in existing_open_times)

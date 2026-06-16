"""Download Binance historical candles into a candle store."""

from datetime import datetime
from typing import Protocol

from cq.data import find_missing_ranges, validate_candle_series
from cq.domain import Symbol
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

    existing = store.load_candles(symbol, interval, start, end)
    missing_ranges = find_missing_ranges(existing, start, end)
    fetched_count = 0
    saved_count = 0
    for missing_start, missing_end in missing_ranges:
        fetched, saved = download_missing_range(
            client,
            store,
            symbol,
            interval,
            missing_start,
            missing_end,
            limit,
        )
        fetched_count += fetched
        saved_count += saved
    return fetched_count, saved_count


def download_missing_range(
    client: BinanceKlineClient,
    store: HistoricalDataStorePort,
    symbol: Symbol,
    interval: str,
    start: datetime,
    end: datetime,
    limit: int,
) -> tuple[int, int]:
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

        store.save_candles(candles)
        saved_count += len(candles)

        next_cursor = candles[-1].close_time
        if next_cursor <= cursor:
            raise ValueError("Binance klines did not advance cursor")
        cursor = next_cursor
    return fetched_count, saved_count

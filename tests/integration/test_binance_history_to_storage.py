from datetime import UTC, datetime, timedelta
from pathlib import Path

from tests.unit.domain.helpers import assert_value_error

from cq.domain import Symbol
from cq.exchanges.binance import BinanceKline, download_historical_candles
from cq.storage import JsonlCandleStore


def test_binance_history_download_saves_candles_to_jsonl_store(tmp_path: Path) -> None:
    symbol = btc_usdt()
    store = JsonlCandleStore(tmp_path)
    client = FakeBinanceClient(
        (
            sample_kline(open_hour=0, close_hour=1),
            sample_kline(open_hour=1, close_hour=2),
        )
    )

    fetched_count, saved_count = download_historical_candles(
        client,
        store,
        symbol,
        "1h",
        timestamp(0),
        timestamp(2),
        limit=1,
    )

    loaded = store.load_candles(symbol, "1h", timestamp(0), timestamp(2))
    assert fetched_count == 2
    assert saved_count == 2
    assert client.requests == ((timestamp(0), timestamp(2), 1), (timestamp(1), timestamp(2), 1))
    assert len(loaded) == 2
    assert loaded[0].open_time == timestamp(0)
    assert loaded[1].close_time == timestamp(2)


def test_binance_history_download_skips_existing_candles(tmp_path: Path) -> None:
    symbol = btc_usdt()
    store = JsonlCandleStore(tmp_path)
    client = FakeBinanceClient((sample_kline(open_hour=0, close_hour=1),))
    download_historical_candles(client, store, symbol, "1h", timestamp(0), timestamp(1))

    fetched_count, saved_count = download_historical_candles(
        client,
        store,
        symbol,
        "1h",
        timestamp(0),
        timestamp(1),
    )

    loaded = store.load_candles(symbol, "1h", timestamp(0), timestamp(1))
    assert fetched_count == 1
    assert saved_count == 0
    assert len(loaded) == 1


def test_binance_history_download_rejects_invalid_limit(tmp_path: Path) -> None:
    symbol = btc_usdt()
    store = JsonlCandleStore(tmp_path)
    client = FakeBinanceClient(())

    def download_with_invalid_limit() -> object:
        return download_historical_candles(
            client,
            store,
            symbol,
            "1h",
            timestamp(0),
            timestamp(1),
            limit=0,
        )

    assert_value_error("limit must be between 1 and 1000", download_with_invalid_limit)
    assert client.requests == ()


class FakeBinanceClient:
    def __init__(self, klines: tuple[BinanceKline, ...]) -> None:
        self.klines = klines
        self.requests: tuple[tuple[datetime, datetime, int], ...] = ()

    def fetch_klines(
        self,
        symbol: Symbol,
        interval: str,
        start: datetime,
        end: datetime,
        limit: int = 1000,
    ) -> tuple[BinanceKline, ...]:
        self.requests = (*self.requests, (start, end, limit))
        return tuple(
            kline
            for kline in self.klines
            if start <= timestamp_from_millis(kline[0]) < end
        )[:limit]


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


def btc_usdt() -> Symbol:
    return Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")


def timestamp(hour: int) -> datetime:
    return datetime(2026, 1, 1, hour, tzinfo=UTC)


def timestamp_from_millis(value: object) -> datetime:
    if not isinstance(value, int):
        raise ValueError("timestamp must be int")
    return datetime.fromtimestamp(value / 1000, tz=UTC)


def millis(value: datetime) -> int:
    return int(value.timestamp() * 1000)

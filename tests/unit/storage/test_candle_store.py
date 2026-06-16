from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from tests.unit.domain.helpers import assert_value_error

from cq.domain import Candle, Symbol
from cq.ports import HistoricalDataStorePort
from cq.storage import JsonlCandleStore


def test_jsonl_candle_store_saves_and_loads_domain_candles(tmp_path: Path) -> None:
    store: HistoricalDataStorePort = JsonlCandleStore(tmp_path)
    candles = (candle(0), candle(1), candle(2))

    store.save_candles(candles)

    loaded = store.load_candles(btc_usdt(), "1h", timestamp(1), timestamp(3))
    assert loaded == (candle(1), candle(2))


def test_jsonl_candle_store_returns_empty_tuple_for_missing_file(tmp_path: Path) -> None:
    store = JsonlCandleStore(tmp_path)

    loaded = store.load_candles(btc_usdt(), "1h", timestamp(0), timestamp(1))

    assert loaded == ()


def test_jsonl_candle_store_rejects_duplicate_open_time(tmp_path: Path) -> None:
    store = JsonlCandleStore(tmp_path)
    store.save_candles((candle(0),))

    def save_duplicate() -> None:
        store.save_candles((candle(0),))

    assert_value_error("candle store already contains open time", save_duplicate)


def test_jsonl_candle_store_rejects_non_continuous_append(tmp_path: Path) -> None:
    store = JsonlCandleStore(tmp_path)
    store.save_candles((candle(0),))

    def save_gap() -> None:
        store.save_candles((candle(2),))

    assert_value_error("candles must be continuous", save_gap)


def test_jsonl_candle_store_rejects_corrupt_jsonl_line(tmp_path: Path) -> None:
    path = tmp_path / "candles" / "BTCUSDT" / "1h.jsonl"
    path.parent.mkdir(parents=True)
    path.write_text("{bad json\n", encoding="utf-8")
    store = JsonlCandleStore(tmp_path)

    def load_corrupt_file() -> None:
        store.load_candles(btc_usdt(), "1h", timestamp(0), timestamp(1))

    assert_value_error("invalid candle record", load_corrupt_file)


def test_jsonl_candle_store_rejects_bad_decimal_record(tmp_path: Path) -> None:
    path = tmp_path / "candles" / "BTCUSDT" / "1h.jsonl"
    path.parent.mkdir(parents=True)
    path.write_text(store_record(candle(0), open_price="not-a-decimal") + "\n", encoding="utf-8")
    store = JsonlCandleStore(tmp_path)

    def load_bad_decimal() -> None:
        store.load_candles(btc_usdt(), "1h", timestamp(0), timestamp(1))

    assert_value_error("invalid candle record", load_bad_decimal)


def test_jsonl_candle_store_rejects_interval_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "candles" / "BTCUSDT" / "1h.jsonl"
    path.parent.mkdir(parents=True)
    store = JsonlCandleStore(tmp_path)
    record = store_record(candle(0), interval="5m")
    path.write_text(record + "\n", encoding="utf-8")

    def load_mismatched_file() -> None:
        store.load_candles(btc_usdt(), "1h", timestamp(0), timestamp(1))

    assert_value_error("candle interval does not match path", load_mismatched_file)


def test_jsonl_candle_store_rejects_unsafe_symbol_path_component(tmp_path: Path) -> None:
    store = JsonlCandleStore(tmp_path)

    def save_unsafe_symbol() -> None:
        store.save_candles((candle(0, symbol=Symbol("../BTCUSDT", "BTC", "USDT")),))

    assert_value_error("symbol must be a safe path component", save_unsafe_symbol)


def test_jsonl_candle_store_rejects_unsafe_interval_path_component(tmp_path: Path) -> None:
    store = JsonlCandleStore(tmp_path)

    def load_unsafe_interval() -> None:
        store.load_candles(btc_usdt(), "../1h", timestamp(0), timestamp(1))

    assert_value_error("interval must be a safe path component", load_unsafe_interval)


def store_record(
    candle_value: Candle,
    interval: str | None = None,
    open_price: str | None = None,
) -> str:
    stored_interval = candle_value.interval if interval is None else interval
    stored_open = str(candle_value.open) if open_price is None else open_price
    return (
        "{"
        f'"base_asset": "{candle_value.symbol.base_asset}", '
        f'"close": "{candle_value.close}", '
        f'"close_time": "{candle_value.close_time.isoformat()}", '
        f'"high": "{candle_value.high}", '
        f'"interval": "{stored_interval}", '
        f'"low": "{candle_value.low}", '
        f'"open": "{stored_open}", '
        f'"open_time": "{candle_value.open_time.isoformat()}", '
        f'"quote_asset": "{candle_value.symbol.quote_asset}", '
        f'"symbol": "{candle_value.symbol.value}", '
        f'"volume": "{candle_value.volume}"'
        "}"
    )


def candle(hour: int, symbol: Symbol | None = None) -> Candle:
    return Candle(
        symbol=btc_usdt() if symbol is None else symbol,
        interval="1h",
        open_time=timestamp(hour),
        close_time=timestamp(hour) + timedelta(hours=1),
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("90"),
        close=Decimal("105"),
        volume=Decimal("1"),
    )


def btc_usdt() -> Symbol:
    return Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")


def timestamp(hour: int) -> datetime:
    return datetime(2026, 1, 1, hour, tzinfo=UTC)

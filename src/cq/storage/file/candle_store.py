"""JSONL-backed local candle store."""

import json
from datetime import datetime
from decimal import Decimal, DecimalException
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from cq.data.validation import require_aware_datetime, validate_candle_series
from cq.domain import Candle, Symbol


class JsonlCandleStore:
    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)

    def save_candles(self, candles: tuple[Candle, ...]) -> None:
        if not candles:
            return
        validate_candle_series(candles)

        symbol = candles[0].symbol
        interval = candles[0].interval
        path = self._path_for(symbol, interval)
        existing = self._read_file(path, symbol, interval)
        existing_open_times = {candle.open_time for candle in existing}
        if any(candle.open_time in existing_open_times for candle in candles):
            raise ValueError("candle store already contains open time")

        merged = tuple(sorted((*existing, *candles), key=lambda candle: candle.open_time))
        validate_candle_series(merged)
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = (
            json.dumps(candle_to_record(candle), sort_keys=True) + "\n"
            for candle in merged
        )
        path.write_text(
            "".join(lines),
            encoding="utf-8",
        )

    def load_candles(
        self,
        symbol: Symbol,
        interval: str,
        start: datetime,
        end: datetime,
    ) -> tuple[Candle, ...]:
        require_aware_datetime(start, "start")
        require_aware_datetime(end, "end")
        if end <= start:
            raise ValueError("end must be after start")

        candles = self._read_file(self._path_for(symbol, interval), symbol, interval)
        selected = tuple(
            candle
            for candle in candles
            if candle.open_time >= start and candle.close_time <= end
        )
        validate_candle_series(selected)
        return selected

    def _path_for(self, symbol: Symbol, interval: str) -> Path:
        symbol_component = safe_path_component(symbol.value, "symbol")
        interval_component = safe_path_component(interval, "interval")
        return self.root / "candles" / symbol_component / f"{interval_component}.jsonl"

    def _read_file(
        self,
        path: Path,
        expected_symbol: Symbol,
        expected_interval: str,
    ) -> tuple[Candle, ...]:
        if not path.exists():
            return ()

        candles: list[Candle] = []
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            try:
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise ValueError("line must contain a JSON object")
                candle = record_to_candle(record)
            except (JSONDecodeError, ValueError, KeyError, DecimalException) as exc:
                raise ValueError(f"invalid candle record in {path}:{line_number}") from exc
            if candle.symbol != expected_symbol:
                raise ValueError(f"candle symbol does not match path in {path}:{line_number}")
            if candle.interval != expected_interval:
                raise ValueError(f"candle interval does not match path in {path}:{line_number}")
            candles.append(candle)

        result = tuple(candles)
        validate_candle_series(result)
        return result


def candle_to_record(candle: Candle) -> dict[str, str]:
    return {
        "symbol": candle.symbol.value,
        "base_asset": candle.symbol.base_asset,
        "quote_asset": candle.symbol.quote_asset,
        "interval": candle.interval,
        "open_time": candle.open_time.isoformat(),
        "close_time": candle.close_time.isoformat(),
        "open": str(candle.open),
        "high": str(candle.high),
        "low": str(candle.low),
        "close": str(candle.close),
        "volume": str(candle.volume),
    }


def record_to_candle(record: dict[str, Any]) -> Candle:
    symbol = Symbol(
        parse_str(record, "symbol"),
        base_asset=parse_str(record, "base_asset"),
        quote_asset=parse_str(record, "quote_asset"),
    )
    return Candle(
        symbol=symbol,
        interval=parse_str(record, "interval"),
        open_time=parse_datetime(record, "open_time"),
        close_time=parse_datetime(record, "close_time"),
        open=parse_decimal(record, "open"),
        high=parse_decimal(record, "high"),
        low=parse_decimal(record, "low"),
        close=parse_decimal(record, "close"),
        volume=parse_decimal(record, "volume"),
    )


def parse_str(record: dict[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    return value


def parse_decimal(record: dict[str, Any], key: str) -> Decimal:
    return Decimal(parse_str(record, key))


def parse_datetime(record: dict[str, Any], key: str) -> datetime:
    value = datetime.fromisoformat(parse_str(record, key))
    require_aware_datetime(value, key)
    return value


def safe_path_component(value: str, field_name: str) -> str:
    if value in {"", ".", ".."} or "/" in value or "\\" in value or "\x00" in value:
        raise ValueError(f"{field_name} must be a safe path component")
    return value

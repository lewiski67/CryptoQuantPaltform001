import json
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

from tests.unit.domain.helpers import assert_value_error

from cq.exchanges.binance import symbol_rules_from_exchange_info


def test_symbol_rules_from_exchange_info_maps_fixture_filters() -> None:
    rules = symbol_rules_from_exchange_info(load_exchange_info(), "BTCUSDT")

    assert rules.symbol.value == "BTCUSDT"
    assert rules.symbol.base_asset == "BTC"
    assert rules.symbol.quote_asset == "USDT"
    assert rules.tick_size == Decimal("0.01000000")
    assert rules.step_size == Decimal("0.00001000")
    assert rules.min_qty == Decimal("0.00001000")
    assert rules.min_notional == Decimal("5.00000000")
    assert rules.max_qty == Decimal("9000.00000000")


def test_symbol_rules_from_exchange_info_rejects_missing_symbol() -> None:
    def parse_missing_symbol() -> object:
        return symbol_rules_from_exchange_info(load_exchange_info(), "ETHUSDT")

    assert_value_error(
        "Binance exchange info does not contain symbol: ETHUSDT",
        parse_missing_symbol,
    )


def test_symbol_rules_from_exchange_info_rejects_missing_filter() -> None:
    exchange_info = load_exchange_info()
    symbol_info = exchange_info["symbols"][0]
    symbol_info["filters"] = [
        item for item in symbol_info["filters"] if item["filterType"] != "MIN_NOTIONAL"
    ]

    def parse_missing_filter() -> object:
        return symbol_rules_from_exchange_info(exchange_info, "BTCUSDT")

    assert_value_error("Binance symbol missing filter: MIN_NOTIONAL", parse_missing_filter)


def test_symbol_rules_from_exchange_info_rejects_bad_decimal() -> None:
    exchange_info = load_exchange_info()
    price_filter = exchange_info["symbols"][0]["filters"][0]
    price_filter["tickSize"] = "not-a-decimal"

    def parse_bad_decimal() -> object:
        return symbol_rules_from_exchange_info(exchange_info, "BTCUSDT")

    assert_value_error("Binance filter tickSize must be a decimal string", parse_bad_decimal)


def load_exchange_info() -> dict[str, Any]:
    path = Path("tests/fixtures/exchange_info.json")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise AssertionError("fixture must contain an object")
    return cast(dict[str, Any], loaded)

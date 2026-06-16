"""Binance exchange info filter mapping."""

from collections.abc import Mapping, Sequence
from decimal import Decimal, DecimalException
from typing import Any

from cq.domain import Symbol, SymbolRules


def symbol_rules_from_exchange_info(data: Mapping[str, Any], symbol_value: str) -> SymbolRules:
    symbols = data.get("symbols")
    if not isinstance(symbols, list):
        raise ValueError("Binance exchange info symbols must be a list")

    for item in symbols:
        if isinstance(item, Mapping) and item.get("symbol") == symbol_value:
            return symbol_rules_from_symbol_info(item)
    raise ValueError(f"Binance exchange info does not contain symbol: {symbol_value}")


def symbol_rules_from_symbol_info(data: Mapping[str, Any]) -> SymbolRules:
    symbol = Symbol(
        parse_str(data, "symbol"),
        base_asset=parse_str(data, "baseAsset"),
        quote_asset=parse_str(data, "quoteAsset"),
    )
    filters = parse_filters(data.get("filters"))
    price_filter = require_filter(filters, "PRICE_FILTER")
    lot_size = require_filter(filters, "LOT_SIZE")
    min_notional = require_filter(filters, "MIN_NOTIONAL")
    return SymbolRules(
        symbol=symbol,
        tick_size=parse_decimal(price_filter, "tickSize"),
        step_size=parse_decimal(lot_size, "stepSize"),
        min_qty=parse_decimal(lot_size, "minQty"),
        min_notional=parse_decimal(min_notional, "minNotional"),
        max_qty=parse_decimal(lot_size, "maxQty"),
    )


def parse_filters(value: object) -> dict[str, Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, str):
        raise ValueError("Binance symbol filters must be a list")

    filters: dict[str, Mapping[str, Any]] = {}
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError("Binance symbol filter must be an object")
        filter_type = item.get("filterType")
        if not isinstance(filter_type, str):
            raise ValueError("Binance symbol filterType must be a string")
        filters[filter_type] = item
    return filters


def require_filter(
    filters: Mapping[str, Mapping[str, Any]],
    filter_type: str,
) -> Mapping[str, Any]:
    if filter_type not in filters:
        raise ValueError(f"Binance symbol missing filter: {filter_type}")
    return filters[filter_type]


def parse_str(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise ValueError(f"Binance symbol {key} must be a string")
    return value


def parse_decimal(data: Mapping[str, Any], key: str) -> Decimal:
    value = data.get(key)
    if not isinstance(value, str):
        raise ValueError(f"Binance filter {key} must be a string")
    try:
        return Decimal(value)
    except DecimalException as exc:
        raise ValueError(f"Binance filter {key} must be a decimal string") from exc

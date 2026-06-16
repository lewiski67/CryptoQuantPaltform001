from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, cast

from tests.unit.domain.helpers import assert_value_error

from cq.domain import Candle, MarketSnapshot, Side, Symbol, SymbolRules, TradeTick


def test_symbol_rules_hold_spot_precision_constraints() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    rules = SymbolRules(
        symbol=symbol,
        tick_size=Decimal("0.01"),
        step_size=Decimal("0.00001"),
        min_qty=Decimal("0.0001"),
        min_notional=Decimal("5"),
        max_qty=Decimal("100"),
    )

    assert rules.symbol == symbol
    assert rules.tick_size == Decimal("0.01")
    assert rules.max_qty == Decimal("100")


def test_symbol_rejects_blank_values() -> None:
    def create_symbol() -> Symbol:
        return Symbol("   ", base_asset="BTC", quote_asset="USDT")

    assert_value_error("symbol value must not be empty", create_symbol)


def test_symbol_rejects_surrounding_whitespace() -> None:
    def create_symbol() -> Symbol:
        return Symbol(" BTCUSDT", base_asset="BTC", quote_asset="USDT")

    assert_value_error("symbol value must not have surrounding whitespace", create_symbol)


def test_symbol_rejects_same_base_and_quote_asset() -> None:
    def create_symbol() -> Symbol:
        return Symbol("BTCBTC", base_asset="BTC", quote_asset="BTC")

    assert_value_error("base asset and quote asset must differ", create_symbol)


def test_symbol_rules_reject_non_positive_constraints() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_rules() -> SymbolRules:
        return SymbolRules(
            symbol=symbol,
            tick_size=Decimal("0"),
            step_size=Decimal("0.00001"),
            min_qty=Decimal("0.0001"),
            min_notional=Decimal("5"),
        )

    assert_value_error("tick_size must be positive", create_rules)


def test_symbol_rules_rejects_invalid_symbol() -> None:
    def create_rules() -> SymbolRules:
        return SymbolRules(
            symbol=cast(Any, "BTCUSDT"),
            tick_size=Decimal("0.01"),
            step_size=Decimal("0.00001"),
            min_qty=Decimal("0.0001"),
            min_notional=Decimal("5"),
        )

    assert_value_error("symbol must be a Symbol", create_rules)


def test_symbol_rules_reject_non_finite_constraints() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_rules() -> SymbolRules:
        return SymbolRules(
            symbol=symbol,
            tick_size=Decimal("Infinity"),
            step_size=Decimal("0.00001"),
            min_qty=Decimal("0.0001"),
            min_notional=Decimal("5"),
        )

    assert_value_error("tick_size must be finite", create_rules)


def test_symbol_rules_reject_max_qty_below_min_qty() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_rules() -> SymbolRules:
        return SymbolRules(
            symbol=symbol,
            tick_size=Decimal("0.01"),
            step_size=Decimal("0.00001"),
            min_qty=Decimal("0.0001"),
            min_notional=Decimal("5"),
            max_qty=Decimal("0.00001"),
        )

    assert_value_error("max_qty must be greater than or equal to min_qty", create_rules)


def test_candle_represents_valid_ohlcv_bar() -> None:
    open_time = datetime(2026, 1, 1, tzinfo=UTC)

    candle = Candle(
        symbol=Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT"),
        interval="1h",
        open_time=open_time,
        close_time=open_time + timedelta(hours=1),
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("95"),
        close=Decimal("105"),
        volume=Decimal("12.5"),
    )

    assert candle.interval == "1h"
    assert candle.close == Decimal("105")


def test_candle_rejects_naive_time() -> None:
    def create_candle() -> Candle:
        return Candle(
            symbol=Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT"),
            interval="1h",
            open_time=datetime(2026, 1, 1),
            close_time=datetime(2026, 1, 1, 1),
            open=Decimal("100"),
            high=Decimal("110"),
            low=Decimal("95"),
            close=Decimal("105"),
            volume=Decimal("12.5"),
        )

    assert_value_error("open time must be timezone-aware", create_candle)


def test_candle_rejects_invalid_symbol() -> None:
    open_time = datetime(2026, 1, 1, tzinfo=UTC)

    def create_candle() -> Candle:
        return Candle(
            symbol=cast(Any, "BTCUSDT"),
            interval="1h",
            open_time=open_time,
            close_time=open_time + timedelta(hours=1),
            open=Decimal("100"),
            high=Decimal("110"),
            low=Decimal("95"),
            close=Decimal("105"),
            volume=Decimal("12.5"),
        )

    assert_value_error("symbol must be a Symbol", create_candle)


def test_candle_rejects_non_finite_ohlc_values() -> None:
    open_time = datetime(2026, 1, 1, tzinfo=UTC)

    def create_candle() -> Candle:
        return Candle(
            symbol=Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT"),
            interval="1h",
            open_time=open_time,
            close_time=open_time + timedelta(hours=1),
            open=Decimal("NaN"),
            high=Decimal("110"),
            low=Decimal("95"),
            close=Decimal("105"),
            volume=Decimal("12.5"),
        )

    assert_value_error("open must be finite", create_candle)


def test_candle_rejects_non_positive_ohlc_values() -> None:
    open_time = datetime(2026, 1, 1, tzinfo=UTC)

    def create_candle() -> Candle:
        return Candle(
            symbol=Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT"),
            interval="1h",
            open_time=open_time,
            close_time=open_time + timedelta(hours=1),
            open=Decimal("0"),
            high=Decimal("110"),
            low=Decimal("95"),
            close=Decimal("105"),
            volume=Decimal("12.5"),
        )

    assert_value_error("open must be positive", create_candle)


def test_candle_rejects_invalid_ohlc_bounds() -> None:
    open_time = datetime(2026, 1, 1, tzinfo=UTC)

    def create_candle() -> Candle:
        return Candle(
            symbol=Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT"),
            interval="1h",
            open_time=open_time,
            close_time=open_time + timedelta(hours=1),
            open=Decimal("120"),
            high=Decimal("110"),
            low=Decimal("95"),
            close=Decimal("105"),
            volume=Decimal("12.5"),
        )

    assert_value_error("open must be between low and high", create_candle)


def test_trade_tick_and_market_snapshot_use_decimal_prices() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    tick = TradeTick(
        symbol=symbol,
        trade_id="123",
        timestamp=timestamp,
        price=Decimal("100.5"),
        quantity=Decimal("0.25"),
        side=Side.BUY,
    )
    snapshot = MarketSnapshot(
        symbol=symbol,
        timestamp=timestamp,
        bid_price=Decimal("100.4"),
        ask_price=Decimal("100.6"),
        last_price=Decimal("100.5"),
    )

    assert tick.price == snapshot.last_price
    assert tick.side is Side.BUY


def test_market_snapshot_rejects_crossed_prices() -> None:
    def create_snapshot() -> MarketSnapshot:
        return MarketSnapshot(
            symbol=Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT"),
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            bid_price=Decimal("101"),
            ask_price=Decimal("100"),
            last_price=Decimal("100.5"),
        )

    assert_value_error("bid price must not exceed ask price", create_snapshot)


def test_market_snapshot_rejects_empty_price_snapshot() -> None:
    def create_snapshot() -> MarketSnapshot:
        return MarketSnapshot(
            symbol=Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT"),
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            bid_price=None,
            ask_price=None,
            last_price=None,
        )

    assert_value_error("market snapshot must contain at least one price", create_snapshot)

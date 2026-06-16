from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, cast

from tests.unit.domain.helpers import assert_value_error

from cq.domain import (
    ClientOrderId,
    Fill,
    LiquiditySide,
    Order,
    OrderIntent,
    OrderStatus,
    OrderType,
    Side,
    Symbol,
    TimeInForce,
)


def test_limit_order_intent_requires_positive_price() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")
    created_at = datetime(2026, 1, 1, tzinfo=UTC)

    intent = OrderIntent(
        symbol=symbol,
        side=Side.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("0.1"),
        price=Decimal("100"),
        time_in_force=TimeInForce.GTC,
        client_order_id=ClientOrderId("strategy-a-1"),
        created_at=created_at,
    )

    assert intent.symbol == symbol
    assert intent.price == Decimal("100")


def test_order_intent_rejects_naive_created_at() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_intent() -> OrderIntent:
        return OrderIntent(
            symbol=symbol,
            side=Side.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.1"),
            created_at=datetime(2026, 1, 1),
        )

    assert_value_error("created at must be timezone-aware", create_intent)


def test_order_intent_rejects_invalid_symbol() -> None:
    def create_intent() -> OrderIntent:
        return OrderIntent(
            symbol=cast(Any, "BTCUSDT"),
            side=Side.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.1"),
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    assert_value_error("symbol must be a Symbol", create_intent)


def test_order_intent_rejects_invalid_client_order_id() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_intent() -> OrderIntent:
        return OrderIntent(
            symbol=symbol,
            side=Side.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.1"),
            client_order_id=cast(Any, "strategy-a-1"),
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    assert_value_error("client order id must be a ClientOrderId", create_intent)


def test_order_intent_rejects_unparsed_order_type() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_intent() -> OrderIntent:
        return OrderIntent(
            symbol=symbol,
            side=Side.BUY,
            order_type=cast(Any, "market"),
            quantity=Decimal("0.1"),
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    assert_value_error("order type must be a valid OrderType", create_intent)


def test_order_intent_rejects_unparsed_time_in_force() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_intent() -> OrderIntent:
        return OrderIntent(
            symbol=symbol,
            side=Side.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("0.1"),
            price=Decimal("100"),
            time_in_force=cast(Any, "gtc"),
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    assert_value_error("time in force must be a valid TimeInForce", create_intent)


def test_limit_order_intent_rejects_missing_price() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_intent() -> OrderIntent:
        return OrderIntent(
            symbol=symbol,
            side=Side.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("0.1"),
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    assert_value_error("limit order price is required", create_intent)


def test_order_intent_rejects_zero_quantity() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_intent() -> OrderIntent:
        return OrderIntent(
            symbol=symbol,
            side=Side.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0"),
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    assert_value_error("quantity must be positive", create_intent)


def test_limit_order_intent_rejects_missing_time_in_force() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_intent() -> OrderIntent:
        return OrderIntent(
            symbol=symbol,
            side=Side.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("0.1"),
            price=Decimal("100"),
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    assert_value_error("limit order time in force is required", create_intent)


def test_market_order_intent_rejects_price() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_intent() -> OrderIntent:
        return OrderIntent(
            symbol=symbol,
            side=Side.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.1"),
            price=Decimal("100"),
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    assert_value_error("market order price must be empty", create_intent)


def test_market_order_intent_rejects_time_in_force() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_intent() -> OrderIntent:
        return OrderIntent(
            symbol=symbol,
            side=Side.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.1"),
            time_in_force=TimeInForce.GTC,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    assert_value_error("market order time in force must be empty", create_intent)


def test_order_represents_submitted_order_lifecycle_state() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")
    client_order_id = ClientOrderId("strategy-a-1")

    order = Order(
        order_id="local-1",
        symbol=symbol,
        side=Side.BUY,
        order_type=OrderType.LIMIT,
        status=OrderStatus.NEW,
        quantity=Decimal("0.1"),
        price=Decimal("100"),
        time_in_force=TimeInForce.GTC,
        client_order_id=client_order_id,
        submitted_at=datetime(2026, 1, 1, tzinfo=UTC),
        exchange_order_id="binance-1",
    )

    assert order.client_order_id == client_order_id
    assert order.status is OrderStatus.NEW
    assert order.exchange_order_id == "binance-1"


def test_fill_represents_execution_without_position_update() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    fill = Fill(
        fill_id="fill-1",
        order_id="local-1",
        symbol=symbol,
        side=Side.BUY,
        price=Decimal("100"),
        quantity=Decimal("0.05"),
        fee_amount=Decimal("0.00005"),
        fee_asset="BTC",
        liquidity_side=LiquiditySide.TAKER,
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        exchange_trade_id="trade-1",
    )

    assert fill.order_id == "local-1"
    assert fill.liquidity_side is LiquiditySide.TAKER


def test_fill_rejects_negative_fee() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_fill() -> Fill:
        return Fill(
            fill_id="fill-1",
            order_id="local-1",
            symbol=symbol,
            side=Side.BUY,
            price=Decimal("100"),
            quantity=Decimal("0.05"),
            fee_amount=Decimal("-0.00005"),
            fee_asset="BTC",
            liquidity_side=LiquiditySide.TAKER,
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        )

    assert_value_error("fee amount must not be negative", create_fill)


def test_fill_rejects_blank_optional_exchange_trade_id() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_fill() -> Fill:
        return Fill(
            fill_id="fill-1",
            order_id="local-1",
            symbol=symbol,
            side=Side.BUY,
            price=Decimal("100"),
            quantity=Decimal("0.05"),
            fee_amount=Decimal("0"),
            fee_asset="BTC",
            liquidity_side=LiquiditySide.TAKER,
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            exchange_trade_id="   ",
        )

    assert_value_error("exchange trade id must not be empty", create_fill)

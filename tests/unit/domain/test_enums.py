from cq.domain import (
    LiquiditySide,
    MarketType,
    OrderStatus,
    OrderType,
    RuntimeMode,
    Side,
    TimeInForce,
)


def test_order_side_values_are_stable_strings() -> None:
    assert Side.BUY == "buy"
    assert Side.SELL == "sell"


def test_order_enums_cover_initial_spot_order_lifecycle() -> None:
    assert OrderType.MARKET == "market"
    assert OrderType.LIMIT == "limit"
    assert TimeInForce.GTC == "gtc"
    assert OrderStatus.NEW == "new"
    assert OrderStatus.PARTIALLY_FILLED == "partially_filled"
    assert OrderStatus.FILLED == "filled"
    assert OrderStatus.CANCELED == "canceled"
    assert OrderStatus.REJECTED == "rejected"
    assert OrderStatus.EXPIRED == "expired"


def test_runtime_market_and_liquidity_enums_are_explicit() -> None:
    assert MarketType.SPOT == "spot"
    assert RuntimeMode.BACKTEST == "backtest"
    assert RuntimeMode.PAPER == "paper"
    assert RuntimeMode.LIVE == "live"
    assert LiquiditySide.MAKER == "maker"
    assert LiquiditySide.TAKER == "taker"

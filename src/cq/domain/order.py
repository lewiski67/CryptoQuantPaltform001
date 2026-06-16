"""Order domain models."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from cq.domain._validation import (
    require_aware_datetime,
    require_enum,
    require_instance,
    require_non_empty,
    require_non_negative,
    require_positive,
)
from cq.domain.enums import LiquiditySide, OrderStatus, OrderType, Side, TimeInForce
from cq.domain.market import Symbol


@dataclass(frozen=True, slots=True)
class ClientOrderId:
    value: str

    def __post_init__(self) -> None:
        require_non_empty(self.value, "client order id")


@dataclass(frozen=True, slots=True)
class OrderIntent:
    symbol: Symbol
    side: Side
    order_type: OrderType
    quantity: Decimal
    created_at: datetime
    price: Decimal | None = None
    time_in_force: TimeInForce | None = None
    client_order_id: ClientOrderId | None = None

    def __post_init__(self) -> None:
        require_instance(self.symbol, Symbol, "symbol")
        require_aware_datetime(self.created_at, "created at")
        require_enum(self.side, Side, "side")
        if self.client_order_id is not None:
            require_instance(self.client_order_id, ClientOrderId, "client order id")
        _validate_order_request(self.order_type, self.quantity, self.price, self.time_in_force)


@dataclass(frozen=True, slots=True)
class Order:
    order_id: str
    symbol: Symbol
    side: Side
    order_type: OrderType
    status: OrderStatus
    quantity: Decimal
    submitted_at: datetime
    client_order_id: ClientOrderId
    price: Decimal | None = None
    time_in_force: TimeInForce | None = None
    exchange_order_id: str | None = None

    def __post_init__(self) -> None:
        require_non_empty(self.order_id, "order id")
        require_instance(self.symbol, Symbol, "symbol")
        require_aware_datetime(self.submitted_at, "submitted at")
        require_enum(self.side, Side, "side")
        require_enum(self.status, OrderStatus, "order status")
        require_instance(self.client_order_id, ClientOrderId, "client order id")
        if self.exchange_order_id is not None:
            require_non_empty(self.exchange_order_id, "exchange order id")
        _validate_order_request(self.order_type, self.quantity, self.price, self.time_in_force)


@dataclass(frozen=True, slots=True)
class Fill:
    fill_id: str
    order_id: str
    symbol: Symbol
    side: Side
    price: Decimal
    quantity: Decimal
    fee_amount: Decimal
    fee_asset: str
    liquidity_side: LiquiditySide
    timestamp: datetime
    exchange_trade_id: str | None = None

    def __post_init__(self) -> None:
        require_non_empty(self.fill_id, "fill id")
        require_non_empty(self.order_id, "order id")
        require_instance(self.symbol, Symbol, "symbol")
        require_aware_datetime(self.timestamp, "timestamp")
        if self.exchange_trade_id is not None:
            require_non_empty(self.exchange_trade_id, "exchange trade id")
        require_enum(self.side, Side, "side")
        require_enum(self.liquidity_side, LiquiditySide, "liquidity side")
        require_positive(self.price, "price")
        require_positive(self.quantity, "quantity")
        require_non_negative(self.fee_amount, "fee amount")
        require_non_empty(self.fee_asset, "fee asset")


def _validate_order_request(
    order_type: OrderType,
    quantity: Decimal,
    price: Decimal | None,
    time_in_force: TimeInForce | None,
) -> None:
    require_enum(order_type, OrderType, "order type")
    if time_in_force is not None:
        require_enum(time_in_force, TimeInForce, "time in force")
    require_positive(quantity, "quantity")
    if price is not None:
        require_positive(price, "price")
    if order_type is OrderType.LIMIT and price is None:
        raise ValueError("limit order price is required")
    if order_type is OrderType.LIMIT and time_in_force is None:
        raise ValueError("limit order time in force is required")
    if order_type is OrderType.MARKET and price is not None:
        raise ValueError("market order price must be empty")
    if order_type is OrderType.MARKET and time_in_force is not None:
        raise ValueError("market order time in force must be empty")

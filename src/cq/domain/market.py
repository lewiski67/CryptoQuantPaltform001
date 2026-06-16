"""Market data domain models."""

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
from cq.domain.enums import MarketType, Side


@dataclass(frozen=True, slots=True)
class Symbol:
    value: str
    base_asset: str
    quote_asset: str
    market_type: MarketType = MarketType.SPOT

    def __post_init__(self) -> None:
        require_non_empty(self.value, "symbol value")
        require_non_empty(self.base_asset, "base asset")
        require_non_empty(self.quote_asset, "quote asset")
        if self.base_asset == self.quote_asset:
            raise ValueError("base asset and quote asset must differ")
        require_enum(self.market_type, MarketType, "market type")


@dataclass(frozen=True, slots=True)
class SymbolRules:
    symbol: Symbol
    tick_size: Decimal
    step_size: Decimal
    min_qty: Decimal
    min_notional: Decimal
    max_qty: Decimal | None = None

    def __post_init__(self) -> None:
        require_instance(self.symbol, Symbol, "symbol")
        for field_name in ("tick_size", "step_size", "min_qty", "min_notional"):
            require_positive(getattr(self, field_name), field_name)
        if self.max_qty is not None:
            require_positive(self.max_qty, "max_qty")
            if self.max_qty < self.min_qty:
                raise ValueError("max_qty must be greater than or equal to min_qty")


@dataclass(frozen=True, slots=True)
class Candle:
    symbol: Symbol
    interval: str
    open_time: datetime
    close_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    def __post_init__(self) -> None:
        require_instance(self.symbol, Symbol, "symbol")
        require_non_empty(self.interval, "interval")
        require_aware_datetime(self.open_time, "open time")
        require_aware_datetime(self.close_time, "close time")
        require_positive(self.open, "open")
        require_positive(self.high, "high")
        require_positive(self.low, "low")
        require_positive(self.close, "close")
        if self.close_time <= self.open_time:
            raise ValueError("close time must be after open time")
        if self.low > self.high:
            raise ValueError("low must not exceed high")
        if not self.low <= self.open <= self.high:
            raise ValueError("open must be between low and high")
        if not self.low <= self.close <= self.high:
            raise ValueError("close must be between low and high")
        require_non_negative(self.volume, "volume")


@dataclass(frozen=True, slots=True)
class TradeTick:
    symbol: Symbol
    trade_id: str
    timestamp: datetime
    price: Decimal
    quantity: Decimal
    side: Side

    def __post_init__(self) -> None:
        require_instance(self.symbol, Symbol, "symbol")
        require_aware_datetime(self.timestamp, "timestamp")
        require_non_empty(self.trade_id, "trade id")
        require_positive(self.price, "price")
        require_positive(self.quantity, "quantity")
        require_enum(self.side, Side, "side")


@dataclass(frozen=True, slots=True)
class MarketSnapshot:
    symbol: Symbol
    timestamp: datetime
    bid_price: Decimal | None
    ask_price: Decimal | None
    last_price: Decimal | None

    def __post_init__(self) -> None:
        require_instance(self.symbol, Symbol, "symbol")
        require_aware_datetime(self.timestamp, "timestamp")
        if self.bid_price is None and self.ask_price is None and self.last_price is None:
            raise ValueError("market snapshot must contain at least one price")
        for field_name in ("bid_price", "ask_price", "last_price"):
            value = getattr(self, field_name)
            if value is not None:
                require_positive(value, field_name)
        if (
            self.bid_price is not None
            and self.ask_price is not None
            and self.bid_price > self.ask_price
        ):
            raise ValueError("bid price must not exceed ask price")

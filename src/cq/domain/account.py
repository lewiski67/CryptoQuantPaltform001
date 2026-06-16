"""Account and portfolio domain models."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from cq.domain._validation import (
    require_aware_datetime,
    require_instance,
    require_non_empty,
    require_non_negative,
    require_positive,
    require_tuple_of,
    require_unique,
)
from cq.domain.market import Symbol


@dataclass(frozen=True, slots=True)
class Balance:
    asset: str
    free: Decimal
    locked: Decimal

    @property
    def total(self) -> Decimal:
        return self.free + self.locked

    def __post_init__(self) -> None:
        require_non_empty(self.asset, "asset")
        require_non_negative(self.free, "free balance")
        require_non_negative(self.locked, "locked balance")


@dataclass(frozen=True, slots=True)
class AccountState:
    account_id: str
    timestamp: datetime
    balances: tuple[Balance, ...]

    def __post_init__(self) -> None:
        require_non_empty(self.account_id, "account id")
        require_aware_datetime(self.timestamp, "timestamp")
        require_tuple_of(self.balances, Balance, "balances")
        require_unique(
            (balance.asset for balance in self.balances),
            "balances must have unique assets",
        )


@dataclass(frozen=True, slots=True)
class Position:
    symbol: Symbol
    quantity: Decimal
    average_entry_price: Decimal | None = None

    def __post_init__(self) -> None:
        require_instance(self.symbol, Symbol, "symbol")
        require_non_negative(self.quantity, "position quantity")
        if self.average_entry_price is not None:
            require_positive(self.average_entry_price, "average entry price")
        if self.quantity == 0 and self.average_entry_price is not None:
            raise ValueError("flat position must not have average entry price")


@dataclass(frozen=True, slots=True)
class PortfolioState:
    account_id: str
    timestamp: datetime
    balances: tuple[Balance, ...]
    positions: tuple[Position, ...]

    def __post_init__(self) -> None:
        require_non_empty(self.account_id, "account id")
        require_aware_datetime(self.timestamp, "timestamp")
        require_tuple_of(self.balances, Balance, "balances")
        require_tuple_of(self.positions, Position, "positions")
        require_unique(
            (balance.asset for balance in self.balances),
            "balances must have unique assets",
        )
        require_unique(
            (position.symbol.value for position in self.positions),
            "positions must have unique symbols",
        )


@dataclass(frozen=True, slots=True)
class EquitySnapshot:
    account_id: str
    timestamp: datetime
    quote_asset: str
    total_equity: Decimal
    cash: Decimal
    position_value: Decimal

    def __post_init__(self) -> None:
        require_non_empty(self.account_id, "account id")
        require_aware_datetime(self.timestamp, "timestamp")
        require_non_empty(self.quote_asset, "quote asset")
        require_non_negative(self.total_equity, "total equity")
        require_non_negative(self.cash, "cash")
        require_non_negative(self.position_value, "position value")
        if self.total_equity != self.cash + self.position_value:
            raise ValueError("total equity must equal cash plus position value")

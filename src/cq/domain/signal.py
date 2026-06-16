"""Strategy signal domain models."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from cq.domain._validation import (
    require_aware_datetime,
    require_enum,
    require_instance,
    require_non_empty,
    require_non_negative,
    require_unit_interval,
)
from cq.domain.enums import Side
from cq.domain.market import Symbol


@dataclass(frozen=True, slots=True)
class Signal:
    signal_id: str
    strategy_id: str
    symbol: Symbol
    side: Side
    strength: Decimal
    created_at: datetime
    reason: str | None = None

    def __post_init__(self) -> None:
        require_non_empty(self.signal_id, "signal id")
        require_non_empty(self.strategy_id, "strategy id")
        require_instance(self.symbol, Symbol, "symbol")
        require_aware_datetime(self.created_at, "created at")
        require_enum(self.side, Side, "side")
        require_unit_interval(self.strength, "strength")
        if self.reason is not None:
            require_non_empty(self.reason, "reason")


@dataclass(frozen=True, slots=True)
class TargetPosition:
    strategy_id: str
    symbol: Symbol
    target_quantity: Decimal
    created_at: datetime
    signal_id: str | None = None

    def __post_init__(self) -> None:
        require_non_empty(self.strategy_id, "strategy id")
        require_instance(self.symbol, Symbol, "symbol")
        require_aware_datetime(self.created_at, "created at")
        require_non_negative(self.target_quantity, "target quantity")
        if self.signal_id is not None:
            require_non_empty(self.signal_id, "signal id")

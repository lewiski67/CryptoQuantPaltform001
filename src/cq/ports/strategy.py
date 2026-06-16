"""Strategy decision port."""

from typing import Protocol, TypeAlias

from cq.domain import (
    Candle,
    MarketSnapshot,
    OrderIntent,
    PortfolioState,
    Signal,
    TargetPosition,
    TradeTick,
)

MarketDataEvent: TypeAlias = Candle | TradeTick | MarketSnapshot
StrategyOutput: TypeAlias = Signal | TargetPosition | OrderIntent


class StrategyPort(Protocol):
    def on_market_event(
        self,
        event: MarketDataEvent,
        portfolio: PortfolioState,
    ) -> tuple[StrategyOutput, ...]: ...

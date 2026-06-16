"""Pre-trade risk rule port."""

from typing import Protocol

from cq.domain import OrderIntent, PortfolioState


class RiskRulePort(Protocol):
    def check(self, intent: OrderIntent, portfolio: PortfolioState) -> bool: ...

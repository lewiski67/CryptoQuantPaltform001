"""Execution model ports for simulated fills, fees, and slippage."""

from decimal import Decimal
from typing import Protocol

from cq.domain import Fill, MarketSnapshot, Order, Side


class FillModelPort(Protocol):
    def generate_fills(self, order: Order, market: MarketSnapshot) -> tuple[Fill, ...]: ...


class CommissionModelPort(Protocol):
    def calculate_fee(self, fill: Fill) -> Decimal: ...


class SlippageModelPort(Protocol):
    def apply_slippage(self, price: Decimal, side: Side) -> Decimal: ...

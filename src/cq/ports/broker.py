"""Order execution port."""

from typing import Protocol

from cq.domain import Order, OrderIntent, Symbol


class BrokerPort(Protocol):
    def submit_order(self, intent: OrderIntent) -> Order: ...

    def cancel_order(self, order_id: str) -> None: ...

    def get_order(self, order_id: str) -> Order | None: ...

    def list_open_orders(self, symbol: Symbol | None = None) -> tuple[Order, ...]: ...

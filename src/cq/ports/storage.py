"""Persistence ports for domain objects."""

from typing import Protocol

from cq.domain import Fill, Order


class OrderStorePort(Protocol):
    def save_order(self, order: Order) -> None: ...

    def get_order(self, order_id: str) -> Order | None: ...

    def load_open_orders(self) -> tuple[Order, ...]: ...


class FillStorePort(Protocol):
    def save_fill(self, fill: Fill) -> None: ...

    def list_fills_for_order(self, order_id: str) -> tuple[Fill, ...]: ...

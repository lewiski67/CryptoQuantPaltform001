"""Market data input and historical candle storage ports."""

from collections.abc import Iterable
from datetime import datetime
from typing import Protocol

from cq.domain import Candle, Symbol, TradeTick


class MarketDataFeedPort(Protocol):
    def subscribe_klines(self, symbols: tuple[Symbol, ...], interval: str) -> Iterable[Candle]: ...

    def subscribe_trades(self, symbols: tuple[Symbol, ...]) -> Iterable[TradeTick]: ...


class HistoricalDataStorePort(Protocol):
    def save_candles(self, candles: tuple[Candle, ...]) -> None: ...

    def load_candles(
        self,
        symbol: Symbol,
        interval: str,
        start: datetime,
        end: datetime,
    ) -> tuple[Candle, ...]: ...

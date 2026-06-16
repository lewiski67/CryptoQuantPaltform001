"""Strongly typed application configuration models."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from cq.domain import RuntimeMode, Symbol


@dataclass(frozen=True, slots=True)
class ExchangeConfig:
    name: str
    symbols: tuple[Symbol, ...]


@dataclass(frozen=True, slots=True)
class DataConfig:
    interval: str
    start: datetime | None = None
    end: datetime | None = None


@dataclass(frozen=True, slots=True)
class StorageConfig:
    root: Path


@dataclass(frozen=True, slots=True)
class RiskConfig:
    max_order_notional: Decimal


@dataclass(frozen=True, slots=True)
class LiveConfig:
    enabled: bool = False
    require_confirmation: bool = False
    reconciliation_required: bool = False


@dataclass(frozen=True, slots=True)
class AppConfig:
    mode: RuntimeMode
    exchange: ExchangeConfig
    data: DataConfig
    storage: StorageConfig
    risk: RiskConfig
    live: LiveConfig

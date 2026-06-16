"""Configuration validation rules."""

from cq.config.schema import AppConfig
from cq.domain import RuntimeMode


class ConfigError(ValueError):
    """Raised when project configuration is invalid."""


def validate_config(config: AppConfig) -> None:
    if not config.exchange.name:
        raise ConfigError("exchange name must not be empty")
    if not config.exchange.symbols:
        raise ConfigError("exchange symbols must not be empty")
    if not config.data.interval:
        raise ConfigError("data interval must not be empty")
    if (
        config.data.start is not None
        and config.data.end is not None
        and config.data.end <= config.data.start
    ):
        raise ConfigError("data end must be after data start")
    if str(config.storage.root) == "":
        raise ConfigError("storage root must not be empty")
    if config.risk.max_order_notional <= 0:
        raise ConfigError("risk max_order_notional must be positive")
    if config.mode is RuntimeMode.LIVE:
        validate_live_config(config)


def validate_live_config(config: AppConfig) -> None:
    if not config.live.enabled:
        raise ConfigError("live mode must be explicitly enabled")
    if not config.live.require_confirmation:
        raise ConfigError("live mode must require confirmation")
    if not config.live.reconciliation_required:
        raise ConfigError("live mode must require reconciliation")

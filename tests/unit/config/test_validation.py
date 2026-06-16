from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from tests.unit.domain.helpers import assert_value_error

from cq.config import (
    AppConfig,
    DataConfig,
    ExchangeConfig,
    LiveConfig,
    RiskConfig,
    StorageConfig,
    validate_config,
)
from cq.domain import RuntimeMode, Symbol


def test_validation_accepts_minimum_backtest_config() -> None:
    validate_config(valid_config())


def test_validation_rejects_empty_symbols() -> None:
    def create_config() -> None:
        config = valid_config()
        validate_config(replace(config, exchange=replace(config.exchange, symbols=())))

    assert_value_error("exchange symbols must not be empty", create_config)


def test_validation_rejects_non_positive_max_order_notional() -> None:
    def create_config() -> None:
        config = valid_config()
        validate_config(
            replace(
                config,
                risk=RiskConfig(max_order_notional=Decimal("0")),
            )
        )

    assert_value_error("risk max_order_notional must be positive", create_config)


def test_validation_rejects_live_mode_without_explicit_enable() -> None:
    def create_config() -> None:
        config = valid_config()
        validate_config(
            replace(
                config,
                mode=RuntimeMode.LIVE,
                live=LiveConfig(
                    enabled=False,
                    require_confirmation=True,
                    reconciliation_required=True,
                ),
            )
        )

    assert_value_error("live mode must be explicitly enabled", create_config)


def test_validation_rejects_live_mode_without_reconciliation() -> None:
    def create_config() -> None:
        config = valid_config()
        validate_config(
            replace(
                config,
                mode=RuntimeMode.LIVE,
                live=LiveConfig(
                    enabled=True,
                    require_confirmation=True,
                    reconciliation_required=False,
                ),
            )
        )

    assert_value_error("live mode must require reconciliation", create_config)


def valid_config() -> AppConfig:
    return AppConfig(
        mode=RuntimeMode.BACKTEST,
        exchange=ExchangeConfig(
            name="binance",
            symbols=(Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT"),),
        ),
        data=DataConfig(interval="1h"),
        storage=StorageConfig(root=Path("data")),
        risk=RiskConfig(max_order_notional=Decimal("100")),
        live=LiveConfig(),
    )

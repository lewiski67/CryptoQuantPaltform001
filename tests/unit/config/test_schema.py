from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from cq.config import (
    AppConfig,
    DataConfig,
    ExchangeConfig,
    LiveConfig,
    RiskConfig,
    StorageConfig,
)
from cq.domain import RuntimeMode, Symbol


def test_config_schema_groups_runtime_settings() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    config = AppConfig(
        mode=RuntimeMode.BACKTEST,
        exchange=ExchangeConfig(name="binance", symbols=(symbol,)),
        data=DataConfig(
            interval="1h",
            start=datetime(2026, 1, 1, tzinfo=UTC),
            end=datetime(2026, 2, 1, tzinfo=UTC),
        ),
        storage=StorageConfig(root=Path("data")),
        risk=RiskConfig(max_order_notional=Decimal("100")),
        live=LiveConfig(),
    )

    assert config.exchange.symbols == (symbol,)
    assert config.storage.root == Path("data")
    assert config.risk.max_order_notional == Decimal("100")

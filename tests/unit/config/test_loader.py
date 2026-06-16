from pathlib import Path
from typing import Any, cast

from tests.unit.domain.helpers import assert_value_error

from cq.config import config_from_mapping, load_config
from cq.domain import RuntimeMode


def test_config_from_mapping_builds_domain_aware_config() -> None:
    config = config_from_mapping(valid_mapping())

    assert config.mode is RuntimeMode.BACKTEST
    assert config.exchange.symbols[0].value == "BTCUSDT"
    assert config.risk.max_order_notional == 100


def test_config_from_mapping_rejects_unknown_keys() -> None:
    def create_config() -> object:
        mapping = valid_mapping()
        mapping["unexpected"] = True
        return config_from_mapping(mapping)

    assert_value_error("unknown config key: unexpected", create_config)


def test_config_from_mapping_rejects_unimplemented_symbol_fields() -> None:
    def create_config() -> object:
        mapping = valid_mapping()
        symbols = cast(Any, mapping["exchange"])["symbols"]
        symbols[0]["market_type"] = "spot"
        return config_from_mapping(mapping)

    assert_value_error("unknown exchange symbol config key: market_type", create_config)


def test_load_config_merges_base_and_mode_files(tmp_path: Path) -> None:
    write_config(
        tmp_path / "base.yaml",
        """
mode: backtest
exchange:
  name: binance
  symbols:
    - value: BTCUSDT
      base_asset: BTC
      quote_asset: USDT
data:
  interval: 1h
storage:
  root: data/base
risk:
  max_order_notional: "100"
live:
  enabled: false
  require_confirmation: false
  reconciliation_required: false
""",
    )
    write_config(
        tmp_path / "backtest.yaml",
        """
data:
  interval: 5m
storage:
  root: data/backtest
""",
    )

    config = load_config("backtest", tmp_path)

    assert config.mode is RuntimeMode.BACKTEST
    assert config.data.interval == "5m"
    assert config.storage.root == Path("data/backtest")


def test_load_config_rejects_disabled_live_config(tmp_path: Path) -> None:
    write_config(
        tmp_path / "base.yaml",
        """
exchange:
  name: binance
  symbols:
    - value: BTCUSDT
      base_asset: BTC
      quote_asset: USDT
data:
  interval: 1h
storage:
  root: data
risk:
  max_order_notional: "100"
live:
  enabled: false
  require_confirmation: true
  reconciliation_required: true
""",
    )
    write_config(tmp_path / "live.yaml", "mode: live\n")

    def load_live_config() -> object:
        return load_config("live", tmp_path)

    assert_value_error("live mode must be explicitly enabled", load_live_config)


def test_load_config_reports_missing_file(tmp_path: Path) -> None:
    def load_missing_config() -> object:
        return load_config("backtest", tmp_path)

    assert_value_error("config file not found", load_missing_config)


def test_load_config_wraps_invalid_yaml_errors(tmp_path: Path) -> None:
    write_config(tmp_path / "base.yaml", "exchange: [")
    write_config(tmp_path / "backtest.yaml", "mode: backtest")

    def load_invalid_config() -> object:
        return load_config("backtest", tmp_path)

    assert_value_error("invalid YAML config file", load_invalid_config)


def valid_mapping() -> dict[str, object]:
    return {
        "mode": "backtest",
        "exchange": {
            "name": "binance",
            "symbols": [
                {
                    "value": "BTCUSDT",
                    "base_asset": "BTC",
                    "quote_asset": "USDT",
                }
            ],
        },
        "data": {"interval": "1h"},
        "storage": {"root": "data"},
        "risk": {"max_order_notional": "100"},
        "live": {
            "enabled": False,
            "require_confirmation": False,
            "reconciliation_required": False,
        },
    }


def write_config(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n", encoding="utf-8")

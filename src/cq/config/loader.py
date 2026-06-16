"""Load and parse project configuration files."""

from collections.abc import Mapping
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml  # type: ignore[reportMissingModuleSource]

from cq.config.schema import (
    AppConfig,
    DataConfig,
    ExchangeConfig,
    LiveConfig,
    RiskConfig,
    StorageConfig,
)
from cq.config.validation import ConfigError, validate_config
from cq.domain import RuntimeMode, Symbol


def load_config(mode: RuntimeMode | str, config_dir: Path | str = "config") -> AppConfig:
    runtime_mode = parse_runtime_mode(mode)
    root = Path(config_dir)
    base = load_yaml_mapping(root / "base.yaml")
    override = load_yaml_mapping(root / f"{runtime_mode.value}.yaml")
    merged = deep_merge(base, override)
    merged["mode"] = runtime_mode.value
    config = config_from_mapping(merged)
    validate_config(config)
    return config


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"config file not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as file:
            loaded = yaml.safe_load(file) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML config file: {path}") from exc
    if not isinstance(loaded, dict):
        raise ConfigError(f"config file must contain a mapping: {path}")
    return loaded


def deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = dict(base)
    for key, value in override.items():
        current = result.get(key)
        if isinstance(current, dict) and isinstance(value, Mapping):
            result[key] = deep_merge(current, value)
        else:
            result[key] = value
    return result


def config_from_mapping(data: Mapping[str, Any]) -> AppConfig:
    require_known_keys(
        data,
        {"mode", "exchange", "data", "storage", "risk", "live"},
        "config",
    )
    return AppConfig(
        mode=parse_runtime_mode(require_value(data, "mode")),
        exchange=parse_exchange_config(require_mapping(data, "exchange")),
        data=parse_data_config(require_mapping(data, "data")),
        storage=parse_storage_config(require_mapping(data, "storage")),
        risk=parse_risk_config(require_mapping(data, "risk")),
        live=parse_live_config(optional_mapping(data, "live")),
    )


def parse_exchange_config(data: Mapping[str, Any]) -> ExchangeConfig:
    require_known_keys(data, {"name", "symbols"}, "exchange")
    symbols = require_value(data, "symbols")
    if not isinstance(symbols, list):
        raise ConfigError("exchange symbols must be a list")
    return ExchangeConfig(
        name=parse_str(require_value(data, "name"), "exchange name"),
        symbols=tuple(parse_symbol(item) for item in symbols),
    )


def parse_data_config(data: Mapping[str, Any]) -> DataConfig:
    require_known_keys(data, {"interval", "start", "end"}, "data")
    return DataConfig(
        interval=parse_str(require_value(data, "interval"), "data interval"),
        start=parse_optional_datetime(data.get("start"), "data start"),
        end=parse_optional_datetime(data.get("end"), "data end"),
    )


def parse_storage_config(data: Mapping[str, Any]) -> StorageConfig:
    require_known_keys(data, {"root"}, "storage")
    root = parse_str(require_value(data, "root"), "storage root")
    return StorageConfig(root=Path(root))


def parse_risk_config(data: Mapping[str, Any]) -> RiskConfig:
    require_known_keys(data, {"max_order_notional"}, "risk")
    return RiskConfig(
        max_order_notional=parse_decimal(
            require_value(data, "max_order_notional"),
            "risk max_order_notional",
        )
    )


def parse_live_config(data: Mapping[str, Any]) -> LiveConfig:
    require_known_keys(
        data,
        {"enabled", "require_confirmation", "reconciliation_required"},
        "live",
    )
    return LiveConfig(
        enabled=parse_bool(data.get("enabled", False), "live enabled"),
        require_confirmation=parse_bool(
            data.get("require_confirmation", False),
            "live require_confirmation",
        ),
        reconciliation_required=parse_bool(
            data.get("reconciliation_required", False),
            "live reconciliation_required",
        ),
    )


def parse_symbol(value: object) -> Symbol:
    if not isinstance(value, Mapping):
        raise ConfigError("exchange symbol must be a mapping")
    require_known_keys(value, {"value", "base_asset", "quote_asset"}, "exchange symbol")
    return Symbol(
        value=parse_str(require_value(value, "value"), "symbol value"),
        base_asset=parse_str(require_value(value, "base_asset"), "base asset"),
        quote_asset=parse_str(require_value(value, "quote_asset"), "quote asset"),
    )


def parse_runtime_mode(value: RuntimeMode | object) -> RuntimeMode:
    if isinstance(value, RuntimeMode):
        return value
    if not isinstance(value, str):
        raise ConfigError("mode must be a string")
    try:
        return RuntimeMode(value)
    except ValueError as exc:
        raise ConfigError(f"unsupported mode: {value}") from exc


def parse_str(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ConfigError(f"{field_name} must be a string")
    stripped = value.strip()
    if not stripped:
        raise ConfigError(f"{field_name} must not be empty")
    if stripped != value:
        raise ConfigError(f"{field_name} must not have surrounding whitespace")
    return value


def parse_bool(value: object, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ConfigError(f"{field_name} must be a boolean")
    return value


def parse_decimal(value: object, field_name: str) -> Decimal:
    try:
        decimal = Decimal(str(value))
    except Exception as exc:
        raise ConfigError(f"{field_name} must be a Decimal") from exc
    if not decimal.is_finite():
        raise ConfigError(f"{field_name} must be finite")
    return decimal


def parse_optional_datetime(value: object, field_name: str) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ConfigError(f"{field_name} must be an ISO datetime string")
    text = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ConfigError(f"{field_name} must be an ISO datetime string") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ConfigError(f"{field_name} must be timezone-aware")
    return parsed


def require_mapping(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = require_value(data, key)
    if not isinstance(value, Mapping):
        raise ConfigError(f"{key} must be a mapping")
    return value


def optional_mapping(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = data.get(key, {})
    if not isinstance(value, Mapping):
        raise ConfigError(f"{key} must be a mapping")
    return value


def require_value(data: Mapping[str, Any], key: str) -> Any:
    if key not in data:
        raise ConfigError(f"missing config key: {key}")
    return data[key]


def require_known_keys(data: Mapping[str, Any], allowed: set[str], section: str) -> None:
    unknown = set(data) - allowed
    if unknown:
        if section == "config":
            raise ConfigError(f"unknown config key: {sorted(unknown)[0]}")
        raise ConfigError(f"unknown {section} config key: {sorted(unknown)[0]}")

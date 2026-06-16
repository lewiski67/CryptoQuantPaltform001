"""Shared validation helpers for domain models."""

from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal
from enum import Enum


def require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} must not be empty")
    if stripped != value:
        raise ValueError(f"{field_name} must not have surrounding whitespace")


def require_aware_datetime(value: datetime, field_name: str) -> None:
    if not isinstance(value, datetime):
        raise ValueError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


def require_instance(value: object, expected_type: type[object], field_name: str) -> None:
    if not isinstance(value, expected_type):
        raise ValueError(f"{field_name} must be a {expected_type.__name__}")


def require_tuple_of(
    value: object,
    expected_type: type[object],
    field_name: str,
) -> None:
    if not isinstance(value, tuple):
        raise ValueError(f"{field_name} must be a tuple")
    if not all(isinstance(item, expected_type) for item in value):
        raise ValueError(f"{field_name} must contain only {expected_type.__name__}")


def require_enum(value: object, enum_type: type[Enum], field_name: str) -> None:
    if not isinstance(value, enum_type):
        raise ValueError(f"{field_name} must be a valid {enum_type.__name__}")


def require_finite_decimal(value: Decimal, field_name: str) -> None:
    if not isinstance(value, Decimal):
        raise ValueError(f"{field_name} must be a Decimal")
    if not value.is_finite():
        raise ValueError(f"{field_name} must be finite")


def require_positive(value: Decimal, field_name: str) -> None:
    require_finite_decimal(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def require_non_negative(value: Decimal, field_name: str) -> None:
    require_finite_decimal(value, field_name)
    if value < 0:
        raise ValueError(f"{field_name} must not be negative")


def require_unit_interval(value: Decimal, field_name: str) -> None:
    require_finite_decimal(value, field_name)
    if value < 0 or value > 1:
        raise ValueError(f"{field_name} must be between 0 and 1")


def require_unique(values: Iterable[str], message: str) -> None:
    items = list(values)
    if len(items) != len(set(items)):
        raise ValueError(message)

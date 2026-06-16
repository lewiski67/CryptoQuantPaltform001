from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, cast

from tests.unit.domain.helpers import assert_value_error

from cq.domain import Side, Signal, Symbol, TargetPosition


def test_signal_represents_strategy_direction_without_order_details() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    signal = Signal(
        signal_id="signal-1",
        strategy_id="mean-reversion",
        symbol=symbol,
        side=Side.BUY,
        strength=Decimal("0.75"),
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        reason="oversold",
    )

    assert signal.symbol == symbol
    assert signal.side is Side.BUY
    assert signal.strength == Decimal("0.75")


def test_signal_rejects_strength_outside_unit_interval() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_signal() -> Signal:
        return Signal(
            signal_id="signal-1",
            strategy_id="mean-reversion",
            symbol=symbol,
            side=Side.BUY,
            strength=Decimal("1.1"),
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    assert_value_error("strength must be between 0 and 1", create_signal)


def test_signal_allows_unit_interval_boundaries() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")
    created_at = datetime(2026, 1, 1, tzinfo=UTC)

    flat = Signal(
        signal_id="signal-1",
        strategy_id="mean-reversion",
        symbol=symbol,
        side=Side.BUY,
        strength=Decimal("0"),
        created_at=created_at,
    )
    full = Signal(
        signal_id="signal-2",
        strategy_id="mean-reversion",
        symbol=symbol,
        side=Side.BUY,
        strength=Decimal("1"),
        created_at=created_at,
    )

    assert flat.strength == Decimal("0")
    assert full.strength == Decimal("1")


def test_signal_rejects_non_finite_strength() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_signal() -> Signal:
        return Signal(
            signal_id="signal-1",
            strategy_id="mean-reversion",
            symbol=symbol,
            side=Side.BUY,
            strength=Decimal("NaN"),
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    assert_value_error("strength must be finite", create_signal)


def test_signal_rejects_naive_created_at() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_signal() -> Signal:
        return Signal(
            signal_id="signal-1",
            strategy_id="mean-reversion",
            symbol=symbol,
            side=Side.BUY,
            strength=Decimal("0.5"),
            created_at=datetime(2026, 1, 1),
        )

    assert_value_error("created at must be timezone-aware", create_signal)


def test_signal_rejects_invalid_symbol() -> None:
    def create_signal() -> Signal:
        return Signal(
            signal_id="signal-1",
            strategy_id="mean-reversion",
            symbol=cast(Any, "BTCUSDT"),
            side=Side.BUY,
            strength=Decimal("0.5"),
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    assert_value_error("symbol must be a Symbol", create_signal)


def test_signal_rejects_blank_optional_reason() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_signal() -> Signal:
        return Signal(
            signal_id="signal-1",
            strategy_id="mean-reversion",
            symbol=symbol,
            side=Side.BUY,
            strength=Decimal("0.5"),
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            reason="   ",
        )

    assert_value_error("reason must not be empty", create_signal)


def test_target_position_represents_desired_position_size() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    target = TargetPosition(
        strategy_id="mean-reversion",
        symbol=symbol,
        target_quantity=Decimal("0.25"),
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        signal_id="signal-1",
    )

    assert target.symbol == symbol
    assert target.target_quantity == Decimal("0.25")
    assert target.signal_id == "signal-1"


def test_target_position_allows_flat_position() -> None:
    target = TargetPosition(
        strategy_id="mean-reversion",
        symbol=Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT"),
        target_quantity=Decimal("0"),
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert target.target_quantity == Decimal("0")


def test_target_position_rejects_negative_quantity() -> None:
    def create_target() -> TargetPosition:
        return TargetPosition(
            strategy_id="mean-reversion",
            symbol=Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT"),
            target_quantity=Decimal("-0.1"),
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    assert_value_error("target quantity must not be negative", create_target)

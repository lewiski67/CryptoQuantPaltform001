from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, cast

from tests.unit.domain.helpers import assert_value_error

from cq.domain import AccountState, Balance, EquitySnapshot, PortfolioState, Position, Symbol


def test_balance_exposes_total_without_mutating_amounts() -> None:
    balance = Balance(asset="USDT", free=Decimal("100"), locked=Decimal("25"))

    assert balance.total == Decimal("125")


def test_balance_rejects_negative_amounts() -> None:
    def create_balance() -> Balance:
        return Balance(asset="USDT", free=Decimal("-1"), locked=Decimal("0"))

    assert_value_error("free balance must not be negative", create_balance)


def test_balance_rejects_non_finite_amounts() -> None:
    def create_balance() -> Balance:
        return Balance(asset="USDT", free=Decimal("NaN"), locked=Decimal("0"))

    assert_value_error("free balance must be finite", create_balance)


def test_balance_rejects_non_decimal_amounts() -> None:
    def create_balance() -> Balance:
        return Balance(asset="USDT", free=cast(Any, 1.0), locked=Decimal("0"))

    assert_value_error("free balance must be a Decimal", create_balance)


def test_balance_rejects_non_string_asset() -> None:
    def create_balance() -> Balance:
        return Balance(asset=cast(Any, None), free=Decimal("1"), locked=Decimal("0"))

    assert_value_error("asset must be a string", create_balance)


def test_account_state_requires_unique_assets() -> None:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    account = AccountState(
        account_id="account-1",
        timestamp=timestamp,
        balances=(
            Balance(asset="BTC", free=Decimal("0.1"), locked=Decimal("0")),
            Balance(asset="USDT", free=Decimal("100"), locked=Decimal("25")),
        ),
    )

    assert account.account_id == "account-1"
    assert len(account.balances) == 2


def test_account_state_rejects_naive_timestamp() -> None:
    def create_account() -> AccountState:
        return AccountState(
            account_id="account-1",
            timestamp=datetime(2026, 1, 1),
            balances=(),
        )

    assert_value_error("timestamp must be timezone-aware", create_account)


def test_account_state_rejects_non_datetime_timestamp() -> None:
    def create_account() -> AccountState:
        return AccountState(
            account_id="account-1",
            timestamp=cast(Any, "2026-01-01T00:00:00Z"),
            balances=(),
        )

    assert_value_error("timestamp must be a datetime", create_account)


def test_account_state_rejects_duplicate_assets() -> None:
    def create_account() -> AccountState:
        return AccountState(
            account_id="account-1",
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            balances=(
                Balance(asset="USDT", free=Decimal("100"), locked=Decimal("0")),
                Balance(asset="USDT", free=Decimal("25"), locked=Decimal("0")),
            ),
        )

    assert_value_error("balances must have unique assets", create_account)


def test_account_state_rejects_mutable_balance_collection() -> None:
    def create_account() -> AccountState:
        return AccountState(
            account_id="account-1",
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            balances=cast(
                Any,
                [Balance(asset="USDT", free=Decimal("100"), locked=Decimal("0"))],
            ),
        )

    assert_value_error("balances must be a tuple", create_account)


def test_account_state_rejects_invalid_balance_item() -> None:
    def create_account() -> AccountState:
        return AccountState(
            account_id="account-1",
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            balances=cast(Any, ("USDT",)),
        )

    assert_value_error("balances must contain only Balance", create_account)


def test_position_allows_flat_or_long_spot_position() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    flat = Position(symbol=symbol, quantity=Decimal("0"))
    long = Position(symbol=symbol, quantity=Decimal("0.5"), average_entry_price=Decimal("100"))

    assert flat.quantity == Decimal("0")
    assert long.average_entry_price == Decimal("100")


def test_position_rejects_negative_spot_quantity() -> None:
    def create_position() -> Position:
        return Position(
            symbol=Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT"),
            quantity=Decimal("-0.1"),
        )

    assert_value_error("position quantity must not be negative", create_position)


def test_position_rejects_invalid_symbol() -> None:
    def create_position() -> Position:
        return Position(symbol=cast(Any, "BTCUSDT"), quantity=Decimal("0.1"))

    assert_value_error("symbol must be a Symbol", create_position)


def test_flat_position_rejects_stale_average_entry_price() -> None:
    def create_position() -> Position:
        return Position(
            symbol=Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT"),
            quantity=Decimal("0"),
            average_entry_price=Decimal("100"),
        )

    assert_value_error("flat position must not have average entry price", create_position)


def test_portfolio_state_groups_balances_and_positions() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    portfolio = PortfolioState(
        account_id="account-1",
        timestamp=timestamp,
        balances=(Balance(asset="USDT", free=Decimal("100"), locked=Decimal("0")),),
        positions=(Position(symbol=symbol, quantity=Decimal("0.5")),),
    )

    assert portfolio.positions[0].symbol == symbol
    assert portfolio.balances[0].asset == "USDT"


def test_portfolio_state_rejects_duplicate_positions() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_portfolio() -> PortfolioState:
        return PortfolioState(
            account_id="account-1",
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            balances=(),
            positions=(
                Position(symbol=symbol, quantity=Decimal("0.1")),
                Position(symbol=symbol, quantity=Decimal("0.2")),
            ),
        )

    assert_value_error("positions must have unique symbols", create_portfolio)


def test_portfolio_state_rejects_mutable_position_collection() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")

    def create_portfolio() -> PortfolioState:
        return PortfolioState(
            account_id="account-1",
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            balances=(),
            positions=cast(Any, [Position(symbol=symbol, quantity=Decimal("0.1"))]),
        )

    assert_value_error("positions must be a tuple", create_portfolio)


def test_portfolio_state_rejects_invalid_position_item() -> None:
    def create_portfolio() -> PortfolioState:
        return PortfolioState(
            account_id="account-1",
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            balances=(),
            positions=cast(Any, ("BTCUSDT",)),
        )

    assert_value_error("positions must contain only Position", create_portfolio)


def test_equity_snapshot_represents_portfolio_value_in_quote_asset() -> None:
    snapshot = EquitySnapshot(
        account_id="account-1",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        quote_asset="USDT",
        total_equity=Decimal("1000"),
        cash=Decimal("400"),
        position_value=Decimal("600"),
    )

    assert snapshot.total_equity == Decimal("1000")
    assert snapshot.quote_asset == "USDT"


def test_equity_snapshot_rejects_negative_values() -> None:
    def create_snapshot() -> EquitySnapshot:
        return EquitySnapshot(
            account_id="account-1",
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            quote_asset="USDT",
            total_equity=Decimal("-1"),
            cash=Decimal("0"),
            position_value=Decimal("0"),
        )

    assert_value_error("total equity must not be negative", create_snapshot)


def test_equity_snapshot_rejects_inconsistent_total() -> None:
    def create_snapshot() -> EquitySnapshot:
        return EquitySnapshot(
            account_id="account-1",
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            quote_asset="USDT",
            total_equity=Decimal("1000"),
            cash=Decimal("400"),
            position_value=Decimal("500"),
        )

    assert_value_error("total equity must equal cash plus position value", create_snapshot)

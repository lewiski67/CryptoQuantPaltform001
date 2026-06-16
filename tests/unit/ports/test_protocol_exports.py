import inspect
from datetime import datetime
from decimal import Decimal
from typing import get_args, get_type_hints

from cq.domain import (
    AccountState,
    Candle,
    Fill,
    MarketSnapshot,
    Order,
    OrderIntent,
    PortfolioState,
    Side,
    Signal,
    Symbol,
    SymbolRules,
    TargetPosition,
    TradeTick,
)
from cq.ports import (
    BrokerPort,
    ClockPort,
    CommissionModelPort,
    ExchangePort,
    FillModelPort,
    FillStorePort,
    HistoricalDataStorePort,
    MarketDataFeedPort,
    NotifierPort,
    OrderStorePort,
    RiskRulePort,
    SlippageModelPort,
    StrategyPort,
)


def test_ports_export_minimum_protocols() -> None:
    assert BrokerPort.__name__ == "BrokerPort"
    assert ClockPort.__name__ == "ClockPort"
    assert CommissionModelPort.__name__ == "CommissionModelPort"
    assert ExchangePort.__name__ == "ExchangePort"
    assert FillStorePort.__name__ == "FillStorePort"
    assert FillModelPort.__name__ == "FillModelPort"
    assert HistoricalDataStorePort.__name__ == "HistoricalDataStorePort"
    assert MarketDataFeedPort.__name__ == "MarketDataFeedPort"
    assert NotifierPort.__name__ == "NotifierPort"
    assert OrderStorePort.__name__ == "OrderStorePort"
    assert RiskRulePort.__name__ == "RiskRulePort"
    assert SlippageModelPort.__name__ == "SlippageModelPort"
    assert StrategyPort.__name__ == "StrategyPort"


def test_protocols_expose_expected_method_names() -> None:
    assert hasattr(BrokerPort, "submit_order")
    assert hasattr(ClockPort, "now")
    assert hasattr(ExchangePort, "place_order")
    assert hasattr(ExchangePort, "get_open_orders")
    assert hasattr(CommissionModelPort, "calculate_fee")
    assert hasattr(FillStorePort, "save_fill")
    assert hasattr(FillModelPort, "generate_fills")
    assert hasattr(HistoricalDataStorePort, "load_candles")
    assert hasattr(MarketDataFeedPort, "subscribe_klines")
    assert hasattr(NotifierPort, "notify")
    assert hasattr(OrderStorePort, "save_order")
    assert hasattr(RiskRulePort, "check")
    assert hasattr(SlippageModelPort, "apply_slippage")
    assert hasattr(StrategyPort, "on_market_event")


def test_exchange_port_method_contracts() -> None:
    assert_method_contract(
        ExchangePort,
        "get_symbol_rules",
        ["self", "symbol"],
        {"symbol": Symbol, "return": SymbolRules},
    )
    assert_method_contract(ExchangePort, "get_account", ["self"], {"return": AccountState})
    assert_method_contract(
        ExchangePort,
        "place_order",
        ["self", "intent"],
        {"intent": OrderIntent, "return": Order},
    )
    assert_method_contract(
        ExchangePort,
        "get_open_orders",
        ["self", "symbol"],
        {"symbol": Symbol | None, "return": tuple[Order, ...]},
    )


def test_broker_and_risk_port_method_contracts() -> None:
    assert_method_contract(
        BrokerPort,
        "submit_order",
        ["self", "intent"],
        {"intent": OrderIntent, "return": Order},
    )
    assert_method_contract(
        BrokerPort,
        "list_open_orders",
        ["self", "symbol"],
        {"symbol": Symbol | None, "return": tuple[Order, ...]},
    )
    assert_method_contract(
        RiskRulePort,
        "check",
        ["self", "intent", "portfolio"],
        {"intent": OrderIntent, "portfolio": PortfolioState, "return": bool},
    )


def test_market_data_and_storage_port_method_contracts() -> None:
    assert_method_contract(
        MarketDataFeedPort,
        "subscribe_klines",
        ["self", "symbols", "interval"],
        {"symbols": tuple[Symbol, ...], "interval": str},
    )
    assert_method_contract(
        MarketDataFeedPort,
        "subscribe_trades",
        ["self", "symbols"],
        {"symbols": tuple[Symbol, ...]},
    )
    assert_method_contract(
        HistoricalDataStorePort,
        "load_candles",
        ["self", "symbol", "interval", "start", "end"],
        {
            "symbol": Symbol,
            "interval": str,
            "start": datetime,
            "end": datetime,
            "return": tuple[Candle, ...],
        },
    )
    assert_method_contract(
        OrderStorePort,
        "save_order",
        ["self", "order"],
        {"order": Order, "return": type(None)},
    )
    assert_method_contract(
        FillStorePort,
        "save_fill",
        ["self", "fill"],
        {"fill": Fill, "return": type(None)},
    )


def test_execution_model_port_method_contracts() -> None:
    assert_method_contract(
        FillModelPort,
        "generate_fills",
        ["self", "order", "market"],
        {"order": Order, "market": MarketSnapshot, "return": tuple[Fill, ...]},
    )
    assert_method_contract(
        CommissionModelPort,
        "calculate_fee",
        ["self", "fill"],
        {"fill": Fill, "return": Decimal},
    )
    assert_method_contract(
        SlippageModelPort,
        "apply_slippage",
        ["self", "price", "side"],
        {"price": Decimal, "side": Side, "return": Decimal},
    )


def test_clock_notifier_and_strategy_port_method_contracts() -> None:
    assert_method_contract(ClockPort, "now", ["self"], {"return": datetime})
    assert_method_contract(
        NotifierPort,
        "notify",
        ["self", "message"],
        {"message": str, "return": type(None)},
    )
    signature = inspect.signature(StrategyPort.on_market_event)
    assert list(signature.parameters) == ["self", "event", "portfolio"]
    hints = get_type_hints(StrategyPort.on_market_event)
    event_types = get_args(hints["event"])
    output_types = get_args(get_args(hints["return"])[0])
    assert Candle in event_types
    assert MarketSnapshot in event_types
    assert TradeTick in event_types
    assert OrderIntent in output_types
    assert Signal in output_types
    assert TargetPosition in output_types
    assert hints["portfolio"] == PortfolioState


def assert_method_contract(
    protocol: type[object],
    method_name: str,
    parameter_names: list[str],
    expected_hints: dict[str, object],
) -> None:
    method = getattr(protocol, method_name)
    signature = inspect.signature(method)
    hints = get_type_hints(method)

    assert list(signature.parameters) == parameter_names
    for name, expected_hint in expected_hints.items():
        assert hints[name] == expected_hint

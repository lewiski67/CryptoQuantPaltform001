from datetime import UTC, datetime, timedelta
from decimal import Decimal

from cq.domain import (
    AccountState,
    Balance,
    Candle,
    ClientOrderId,
    Fill,
    LiquiditySide,
    MarketSnapshot,
    Order,
    OrderIntent,
    OrderStatus,
    OrderType,
    PortfolioState,
    Side,
    Symbol,
    SymbolRules,
    TimeInForce,
)
from cq.ports import (
    BrokerPort,
    CommissionModelPort,
    ExchangePort,
    FillModelPort,
    FillStorePort,
    HistoricalDataStorePort,
    OrderStorePort,
    RiskRulePort,
    SlippageModelPort,
    StrategyPort,
)
from cq.ports.strategy import MarketDataEvent


def test_order_flow_ports_accept_and_return_domain_objects() -> None:
    symbol = btc_usdt()
    intent = limit_buy_intent(symbol)
    exchange: ExchangePort = FakeExchange(symbol)
    broker: BrokerPort = FakeBroker()
    order_store: OrderStorePort = InMemoryOrderStore()
    risk_rule: RiskRulePort = AllowAllRiskRule()
    portfolio = PortfolioState(
        account_id="account-1",
        timestamp=timestamp(),
        balances=(Balance(asset="USDT", free=Decimal("1000"), locked=Decimal("0")),),
        positions=(),
    )

    assert risk_rule.check(intent, portfolio) is True

    exchange_order = exchange.place_order(intent)
    broker_order = broker.submit_order(intent)
    order_store.save_order(exchange_order)

    assert exchange.get_symbol_rules(symbol).symbol == symbol
    assert exchange.get_account().balances[0].asset == "USDT"
    assert exchange.get_order(exchange_order.order_id) == exchange_order
    assert exchange.get_open_orders(symbol) == (exchange_order,)
    assert broker.get_order(broker_order.order_id) == broker_order
    assert broker.list_open_orders(symbol) == (broker_order,)
    assert order_store.get_order(exchange_order.order_id) == exchange_order
    assert order_store.load_open_orders() == (exchange_order,)


def test_market_and_execution_ports_share_domain_types() -> None:
    symbol = btc_usdt()
    order = submitted_order(symbol)
    fill_store: FillStorePort = InMemoryFillStore()
    candle_store: HistoricalDataStorePort = InMemoryCandleStore()
    fill_model: FillModelPort = LastPriceFillModel()
    commission_model: CommissionModelPort = ZeroCommissionModel()
    slippage_model: SlippageModelPort = NoSlippageModel()
    market = MarketSnapshot(
        symbol=symbol,
        timestamp=timestamp(),
        bid_price=Decimal("99"),
        ask_price=Decimal("101"),
        last_price=Decimal("100"),
    )
    candle = Candle(
        symbol=symbol,
        interval="1m",
        open_time=timestamp(),
        close_time=timestamp() + timedelta(minutes=1),
        open=Decimal("99"),
        high=Decimal("101"),
        low=Decimal("98"),
        close=Decimal("100"),
        volume=Decimal("12"),
    )

    fills = fill_model.generate_fills(order, market)
    fill_store.save_fill(fills[0])
    candle_store.save_candles((candle,))

    assert commission_model.calculate_fee(fills[0]) == Decimal("0")
    assert slippage_model.apply_slippage(Decimal("100"), Side.BUY) == Decimal("100")
    assert fill_store.list_fills_for_order(order.order_id) == fills
    loaded_candles = candle_store.load_candles(
        symbol,
        "1m",
        timestamp(),
        timestamp() + timedelta(minutes=1),
    )
    assert loaded_candles == (candle,)


def test_strategy_port_consumes_market_events_and_portfolio_context() -> None:
    symbol = btc_usdt()
    strategy: StrategyPort = BuySignalStrategy()
    portfolio = PortfolioState(
        account_id="account-1",
        timestamp=timestamp(),
        balances=(Balance(asset="USDT", free=Decimal("1000"), locked=Decimal("0")),),
        positions=(),
    )
    market = MarketSnapshot(
        symbol=symbol,
        timestamp=timestamp(),
        bid_price=Decimal("99"),
        ask_price=Decimal("101"),
        last_price=Decimal("100"),
    )

    outputs = strategy.on_market_event(market, portfolio)

    assert outputs[0].symbol == symbol


class FakeExchange:
    def __init__(self, symbol: Symbol) -> None:
        self.symbol = symbol
        self.order: Order | None = None

    def get_symbol_rules(self, symbol: Symbol) -> SymbolRules:
        return SymbolRules(
            symbol=symbol,
            tick_size=Decimal("0.01"),
            step_size=Decimal("0.00001"),
            min_qty=Decimal("0.0001"),
            min_notional=Decimal("5"),
        )

    def get_account(self) -> AccountState:
        return AccountState(
            account_id="account-1",
            timestamp=timestamp(),
            balances=(Balance(asset="USDT", free=Decimal("1000"), locked=Decimal("0")),),
        )

    def place_order(self, intent: OrderIntent) -> Order:
        self.order = submitted_order(intent.symbol)
        return self.order

    def cancel_order(self, order_id: str) -> None:
        self.order = None

    def get_order(self, order_id: str) -> Order | None:
        if self.order is None or self.order.order_id != order_id:
            return None
        return self.order

    def get_open_orders(self, symbol: Symbol | None = None) -> tuple[Order, ...]:
        if self.order is None:
            return ()
        if symbol is not None and self.order.symbol != symbol:
            return ()
        return (self.order,)


class FakeBroker:
    def __init__(self) -> None:
        self.order: Order | None = None

    def submit_order(self, intent: OrderIntent) -> Order:
        self.order = submitted_order(intent.symbol)
        return self.order

    def cancel_order(self, order_id: str) -> None:
        self.order = None

    def get_order(self, order_id: str) -> Order | None:
        if self.order is None or self.order.order_id != order_id:
            return None
        return self.order

    def list_open_orders(self, symbol: Symbol | None = None) -> tuple[Order, ...]:
        if self.order is None:
            return ()
        if symbol is not None and self.order.symbol != symbol:
            return ()
        return (self.order,)


class InMemoryOrderStore:
    def __init__(self) -> None:
        self.orders: dict[str, Order] = {}

    def save_order(self, order: Order) -> None:
        self.orders[order.order_id] = order

    def get_order(self, order_id: str) -> Order | None:
        return self.orders.get(order_id)

    def load_open_orders(self) -> tuple[Order, ...]:
        return tuple(order for order in self.orders.values() if order.status is OrderStatus.NEW)


class InMemoryFillStore:
    def __init__(self) -> None:
        self.fills: list[Fill] = []

    def save_fill(self, fill: Fill) -> None:
        self.fills.append(fill)

    def list_fills_for_order(self, order_id: str) -> tuple[Fill, ...]:
        return tuple(fill for fill in self.fills if fill.order_id == order_id)


class InMemoryCandleStore:
    def __init__(self) -> None:
        self.candles: list[Candle] = []

    def save_candles(self, candles: tuple[Candle, ...]) -> None:
        self.candles.extend(candles)

    def load_candles(
        self,
        symbol: Symbol,
        interval: str,
        start: datetime,
        end: datetime,
    ) -> tuple[Candle, ...]:
        return tuple(
            candle
            for candle in self.candles
            if candle.symbol == symbol
            and candle.interval == interval
            and start <= candle.open_time
            and candle.close_time <= end
        )


class AllowAllRiskRule:
    def check(self, intent: OrderIntent, portfolio: PortfolioState) -> bool:
        return True


class LastPriceFillModel:
    def generate_fills(self, order: Order, market: MarketSnapshot) -> tuple[Fill, ...]:
        if market.last_price is None:
            return ()
        return (
            Fill(
                fill_id="fill-1",
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                price=market.last_price,
                quantity=order.quantity,
                fee_amount=Decimal("0"),
                fee_asset=order.symbol.quote_asset,
                liquidity_side=LiquiditySide.TAKER,
                timestamp=market.timestamp,
            ),
        )


class ZeroCommissionModel:
    def calculate_fee(self, fill: Fill) -> Decimal:
        return Decimal("0")


class NoSlippageModel:
    def apply_slippage(self, price: Decimal, side: Side) -> Decimal:
        return price


class BuySignalStrategy:
    def on_market_event(
        self,
        event: MarketDataEvent,
        portfolio: PortfolioState,
    ) -> tuple[OrderIntent, ...]:
        return (limit_buy_intent(event.symbol),)


def btc_usdt() -> Symbol:
    return Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")


def timestamp() -> datetime:
    return datetime(2026, 1, 1, tzinfo=UTC)


def limit_buy_intent(symbol: Symbol) -> OrderIntent:
    return OrderIntent(
        symbol=symbol,
        side=Side.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("0.1"),
        price=Decimal("100"),
        time_in_force=TimeInForce.GTC,
        created_at=timestamp(),
        client_order_id=ClientOrderId("client-1"),
    )


def submitted_order(symbol: Symbol) -> Order:
    return Order(
        order_id="order-1",
        symbol=symbol,
        side=Side.BUY,
        order_type=OrderType.LIMIT,
        status=OrderStatus.NEW,
        quantity=Decimal("0.1"),
        price=Decimal("100"),
        time_in_force=TimeInForce.GTC,
        client_order_id=ClientOrderId("client-1"),
        submitted_at=timestamp(),
    )

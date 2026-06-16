# 接口设计

接口只用于隔离真实变化点。不要为了形式上的面向对象给稳定数据模型增加接口。

置信度：High。

## 必须接口化的变化点

建议在 `src/cq/ports/` 中逐步定义：

```text
ExchangePort
MarketDataFeedPort
HistoricalDataStorePort
OrderStorePort
TradeStorePort
StrategyPort
RiskRulePort
BrokerPort
ClockPort
NotifierPort
FillModelPort
CommissionModelPort
SlippageModelPort
```

## 不建议接口化的对象

这些是领域数据，应保持简单、可读、可测试：

```text
Order
Trade
Position
AccountSnapshot
Money
Kline
Signal
OrderIntent
```

不建议创建：

```text
OrderInterface
TradeInterface
PositionInterface
AccountInterface
MoneyInterface
KlineInterface
SignalInterface
```

## Port 命名规则

- port 文件放在 `src/cq/ports/`。
- port 名称使用业务能力命名，例如 `ExchangePort`，不要使用实现细节命名，例如 `BinancePort`。
- port 只依赖 `domain`，不得依赖 `exchanges`、`storage`、`runtime`、`api`。
- 具体实现放在适配层，例如 `exchanges/binance/`、`storage/sqlite/`、`monitoring/`。

## 核心接口草案

```python
from typing import Protocol


class ExchangePort(Protocol):
    def get_exchange_info(self): ...
    def get_account(self): ...
    def place_order(self, order): ...
    def cancel_order(self, order_id: str): ...
    def get_open_orders(self, symbol: str | None = None): ...
    def get_order(self, order_id: str): ...
```

```python
from typing import Iterable, Protocol


class MarketDataFeedPort(Protocol):
    def subscribe_klines(self, symbols: list[str], interval: str) -> Iterable: ...
    def subscribe_trades(self, symbols: list[str]) -> Iterable: ...
```

```python
from typing import Protocol


class StrategyPort(Protocol):
    def on_market_event(self, event, context) -> list: ...
```

```python
from typing import Protocol


class RiskRulePort(Protocol):
    def check(self, order_intent, context): ...
```

```python
from typing import Protocol


class BrokerPort(Protocol):
    def submit(self, order): ...
    def cancel(self, order_id: str): ...
```

```python
from typing import Protocol


class OrderStorePort(Protocol):
    def save_order(self, order) -> None: ...
    def load_open_orders(self) -> list: ...
```

## 接口使用规则

1. 策略依赖 `StrategyPort` 和领域模型，不依赖具体交易所。
2. 风控依赖 `RiskRulePort` 和领域模型，不直接下单。
3. 执行层依赖 `BrokerPort`、`OrderStorePort` 和交易所 port。
4. 回测使用模拟 broker、模拟 fill model、模拟 commission model。
5. 实盘使用真实 exchange adapter，但仍必须通过 broker 和 risk。
6. API 和 dashboard 只能调用 runtime/application service，不能绕过接口边界。

## 新增接口前检查

新增接口前必须能回答：

1. 它隔离了哪个真实变化点？
2. 至少是否存在两个合理实现，或未来替换成本是否明确很高？
3. 是否能减少上层对外部系统的直接依赖？
4. 是否会让核心流程更难读？

如果第 1 点说不清楚，不要新增接口。

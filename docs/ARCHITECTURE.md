# 系统架构

本项目按长期维护的数字货币量化交易平台设计。目录结构优先服务于可读性、可维护性和可扩展性，而不是短期脚本开发速度。

置信度：High。

## 设计原则

1. 领域模型简单化
   - `src/cq/domain/` 只放稳定的核心概念，例如订单、成交、账户、仓位、交易品种、市场数据和事件。
   - 领域对象优先使用简单数据结构，例如 `dataclass`、`Enum` 或 Pydantic model。
   - 不为 `Order`、`Trade`、`Position` 这类纯数据对象创建无意义接口。

2. 外部依赖接口化
   - `src/cq/ports/` 定义系统依赖的抽象能力。
   - 交易所、行情源、存储、通知、时钟、执行通道等外部或可替换能力都应通过 port 访问。
   - 业务层不能直接依赖 Binance client、数据库 session 或 dashboard。

3. 运行流程组合化
   - `src/cq/runtime/` 负责编排 backtest、paper、live 等运行模式。
   - `runtime/container.py` 是依赖组装入口。
   - `scripts/` 只调用 runtime，不承载核心业务逻辑。

4. 策略、交易所、存储、执行可插拔
   - 新交易所放入 `src/cq/exchanges/<exchange>/`，实现 `ports/exchange.py` 和相关行情接口。
   - 新存储后端放入 `src/cq/storage/<backend>/`，实现 `ports/storage.py`。
   - 新策略放入 `src/cq/strategies/`，通过 registry 注册。
   - 实盘、模拟和回测执行都应复用统一订单语义，差异放在 broker、fill model、slippage、commission 等实现中。

5. Dashboard 只做观察和受控操作
   - `dashboard/` 不能直接调用交易所 API。
   - Dashboard 必须通过 `src/cq/api/` 访问后端。
   - 所有下单、撤单、启停策略、kill switch 等操作必须经过 runtime、risk、execution。

## 推荐依赖方向

```text
domain
  ↑
ports
  ↑
strategies / risk / portfolio / execution / backtest / runtime
  ↑
exchanges / storage / monitoring / api
```

禁止反向依赖：

```text
domain -> exchanges
domain -> storage
strategies -> exchanges.binance
risk -> exchanges.binance
backtest -> exchanges.binance.client
dashboard -> exchanges.binance
```

## 关键目录职责

```text
src/cq/domain/      核心领域对象，不依赖外部系统
src/cq/ports/       接口协议，隔离外部依赖和可替换能力
src/cq/data/        历史与实时行情输入、清洗、重采样、校验
src/cq/exchanges/   交易所适配器，当前重点是 Binance
src/cq/storage/     SQLite、PostgreSQL、Parquet 等持久化实现
src/cq/features/    指标和特征计算，不做交易决策
src/cq/strategies/  策略逻辑，输出信号或订单意图
src/cq/portfolio/   仓位、估值、收益和会计处理
src/cq/risk/        交易前风控、敞口限制、熔断和 kill switch
src/cq/execution/   订单状态机、broker、成交模型、滑点、手续费、对账
src/cq/backtest/    事件驱动与向量化回测
src/cq/runtime/     backtest、paper、live 的运行编排和恢复
src/cq/api/         Dashboard 和外部系统访问后端的 API
src/cq/monitoring/  日志、指标、告警、健康检查
dashboard/          前端可视化应用
research/           研究、实验、报告，不被 src/cq 反向 import
scripts/            命令入口，不写核心业务逻辑
```

## 数据流

```text
data
-> features
-> strategies
-> portfolio / risk
-> execution
-> exchanges
```

## 事件流

```text
MarketEvent
-> SignalEvent
-> OrderIntent
-> RiskCheckedOrder
-> Order
-> Fill
-> PositionUpdate
-> AccountUpdate
```

## 运行模式

```text
backtest  使用历史数据、模拟撮合、模拟手续费和滑点
paper     使用实时或准实时行情、模拟执行、不真实下单
live      使用真实账户、真实订单、强制风控和对账
```

三种模式应尽量共用领域模型、策略接口、风控接口和订单语义。差异应集中在数据源、broker、fill model、storage 和 runtime 组装逻辑。

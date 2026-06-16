# 开发指南

本指南约束后续代码演进，目标是保持模块边界清晰、代码可读、可测试、可替换。

置信度：High。

## 基本约束

1. `src/cq/domain/` 不能 import `exchanges`、`storage`、`runtime`、`api`。
2. `src/cq/ports/` 只依赖 `domain`。
3. `src/cq/strategies/` 不能 import 具体交易所 client。
4. `src/cq/risk/` 不能直接下单。
5. `src/cq/execution/` 不能计算策略信号。
6. `src/cq/exchanges/` 只做 API 适配，不做业务决策。
7. `src/cq/api/` 只能调用 runtime/application service，不能绕过风控和执行层。
8. `scripts/` 只做参数解析和入口调用。
9. `research/` 不能被 `src/cq/` 反向依赖。
10. 新增抽象前必须能说清楚它隔离了哪个真实变化点。

## 代码风格

- 优先写小而直接的模块。
- 不做 speculative engineering。
- 不新增暂时没有调用方的复杂抽象。
- 不把业务逻辑写进 `scripts/`。
- 不把实验逻辑写进 `src/cq/`。
- 不用 `utils/` 承载领域逻辑。

## 金额、价格和数量

核心交易逻辑不得随意使用 float。

建议：

- 订单价格、数量、手续费、余额使用 `Decimal` 或明确的定点表示。
- Binance 精度处理集中在 `exchanges/binance/filters.py`。
- 指标计算和研究分析可以使用 float，但进入订单、成交、账户层前必须转换并校验。

## 新增策略

新增策略时：

1. 放入 `src/cq/strategies/`。
2. 实现策略 port 约定。
3. 只输出信号、目标仓位或订单意图。
4. 不直接下单。
5. 不直接访问 Binance client。
6. 在 `strategies/registry.py` 注册。
7. 增加对应 unit test。

## 新增交易所

新增交易所时：

1. 放入 `src/cq/exchanges/<exchange>/`。
2. 实现 `ExchangePort` 和相关行情 port。
3. 将交易所私有错误转换为项目内错误。
4. 将交易所私有字段转换为 domain 对象。
5. 不向策略、风控、回测泄露原始 API response。

## 新增存储后端

新增存储后端时：

1. 放入 `src/cq/storage/<backend>/`。
2. 实现 storage port。
3. repository 返回 domain 对象或明确 schema。
4. 不让业务层直接依赖数据库 session。

## 测试分层

```text
tests/unit/         不联网、快速、覆盖领域模型和纯业务逻辑
tests/integration/  可连接测试服务或 Binance testnet
tests/e2e/          覆盖 backtest、paper trading 等完整流程
tests/fixtures/     固定样本，例如 exchange_info、klines、trades
```

长期必须重点测试：

- Binance filters 精度处理。
- 订单状态转换。
- 风控拒单。
- 对账恢复。
- 回测成交模型。
- paper/live 共用订单语义的一致性。

## Pull Request 检查清单

提交前检查：

- 是否引入了反向依赖？
- 是否绕过了 port？
- 是否绕过了 risk？
- 是否新增了没有真实变化点的接口？
- 是否增加了必要测试？
- 是否影响 live 模式安全边界？
- 是否需要更新文档？

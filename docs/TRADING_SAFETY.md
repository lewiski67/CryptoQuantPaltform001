# 交易安全

实盘安全优先级高于策略收益。任何 live 交易能力都必须先满足风控、幂等、对账和恢复要求。

置信度：High。

## Binance 精度和过滤规则

实盘下单前必须处理：

- `tickSize`
- `stepSize`
- `minNotional`
- `minQty`
- `maxQty`
- `pricePrecision`
- `quantityPrecision`
- maker / taker fee
- spot、margin、futures 的规则差异

所有 Binance 交易规则应集中在：

```text
src/cq/exchanges/binance/filters.py
```

业务层不得散落手写 rounding 逻辑。

## 下单前检查

所有实盘订单必须经过：

```text
src/cq/risk/pre_trade.py
```

至少检查：

- 单笔最大名义金额。
- 单币种最大仓位。
- 总敞口限制。
- 每分钟最大订单数。
- 每日最大亏损。
- 价格偏离保护。
- 重复订单保护。
- exchange info 是否过期。
- 当前是否触发 kill switch。

## 订单幂等

实盘下单必须使用稳定的 client order id。

目标：

- 防止网络超时后重复下单。
- 支持重启后恢复订单状态。
- 支持 API 返回不确定状态时重新查询确认。

相关模块：

```text
src/cq/execution/idempotency.py
src/cq/execution/order_manager.py
src/cq/execution/reconciliation.py
```

## 对账和恢复

实盘启动前必须执行：

```text
src/cq/execution/reconciliation.py
```

至少恢复：

- open orders
- recent fills
- balances
- positions
- 本地订单状态
- 策略运行状态

本地状态和交易所状态冲突时，默认以交易所状态为准，并记录审计日志。

## WebSocket 和 API 失败

必须处理：

- websocket 断线重连。
- listen key 过期。
- REST API 限频。
- 请求超时。
- 下单结果未知。
- 部分成交。
- 撤单失败。

实时数据断线恢复后，应补齐缺失区间，不能假设行情连续。

## Kill Switch

kill switch 必须能停止：

- 新信号生成。
- 新订单提交。
- 策略自动加仓。

是否自动撤销 open orders 需要明确配置，不能隐式执行。

相关模块：

```text
src/cq/risk/kill_switch.py
src/cq/risk/circuit_breaker.py
```

## 实盘禁止事项

禁止：

- 绕过 `risk/pre_trade.py` 直接下单。
- dashboard 直接调用 Binance API。
- 策略直接 import Binance client。
- 使用 float 作为核心金额、价格、数量计算的唯一表示。
- 忽略部分成交。
- 进程重启后直接继续交易而不对账。
- 在 live 模式复用 research 脚本中的实验逻辑。

## 审计日志

这些操作必须记录审计日志：

- live 模式启动和停止。
- 策略启停。
- 参数变更。
- 手动撤单。
- 手动下单。
- kill switch 触发和解除。
- 风控拒单。
- 对账差异。

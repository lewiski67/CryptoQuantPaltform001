# Dashboard 指南

Dashboard 是观察、监控和受控操作入口，不是交易业务逻辑所在地。

置信度：High。

## 依赖方向

```text
dashboard
  ↓ HTTP / WebSocket
api
  ↓
runtime
  ↓
strategy / risk / portfolio / execution
  ↓
ports
  ↓
exchanges / storage / monitoring
```

禁止：

```text
dashboard -> exchanges.binance
dashboard -> database session
dashboard -> execution.order_manager
```

Dashboard 必须通过 `src/cq/api/` 访问后端。

## 推荐页面

```text
Overview     总览：权益曲线、当日盈亏、敞口、运行状态
Positions    当前仓位、成本、浮盈亏、风险占用
Orders       open orders、历史订单、部分成交、撤单
Trades       成交记录、手续费、滑点估计
Strategies   策略状态、参数、信号、启停
Backtests    回测任务、收益曲线、指标、交易明细
Risk         风控限制、kill switch、风险事件
Market       行情、K线、盘口、成交
System       websocket 状态、延迟、任务状态、错误日志
```

## API 边界

推荐只暴露查询和受控操作：

```text
GET  /account
GET  /positions
GET  /orders
GET  /trades
GET  /strategies
GET  /backtests
GET  /risk/status
GET  /system/health

POST /strategies/{id}/enable
POST /strategies/{id}/disable
POST /orders/{id}/cancel
POST /risk/kill-switch
POST /backtests/run
```

## 允许操作

- 查看账户、仓位、订单、成交、策略状态、系统状态。
- 停止策略。
- 撤销订单。
- 触发 kill switch。
- 启动回测任务。

## 谨慎开放的操作

- 手动下单。
- 修改策略参数。
- 切换 live 模式。
- 提高风险限额。

这些操作必须要求后端确认、审计日志和权限控制。

## 禁止操作

- 页面直接调用 Binance API。
- 页面绕过 `risk/pre_trade.py` 下单。
- 页面直接修改核心交易状态。
- 页面直接写数据库核心表。
- 页面内实现策略逻辑。

## 实时数据

实时数据优先使用：

```text
WebSocket
Server-Sent Events
轮询查询接口
```

早期可以先用轮询，等 API 和状态模型稳定后再接 WebSocket。

## 技术选型建议

长期推荐：

```text
后端：FastAPI
前端：React + Vite + TypeScript
图表：ECharts 或 Lightweight Charts
状态管理：Zustand
数据请求：TanStack Query
实时更新：WebSocket 或 Server-Sent Events
```

如果只做临时内部看板，可以先用 Streamlit 或 Dash，但不要让它进入核心交易链路。

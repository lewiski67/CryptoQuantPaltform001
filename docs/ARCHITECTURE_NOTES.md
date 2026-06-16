# 架构文档索引

本文件保留为入口，避免旧链接失效。后续开发以拆分后的文档为准。

置信度：High。

## 文档列表

- [ARCHITECTURE.md](ARCHITECTURE.md)：系统原则、目录职责、依赖方向、数据流和运行模式。
- [INTERFACES.md](INTERFACES.md)：port 接口边界、可插拔能力、禁止过度抽象的对象。
- [TRADING_SAFETY.md](TRADING_SAFETY.md)：Binance 实盘安全、风控、订单幂等、对账和 kill switch。
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)：开发约束、模块新增规则、测试分层和代码边界。
- [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)：dashboard 页面、API 调用方向、允许和禁止的操作。

## 总原则

```text
领域模型简单化
外部依赖接口化
运行流程组合化
策略 / 交易所 / 存储 / 执行可插拔
dashboard 只做可视化、监控和受控操作入口
```

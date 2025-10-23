# 📚 TradingAgents 项目文档

欢迎来到 TradingAgents 项目的文档中心。本指南将帮助你快速了解项目架构、核心概念和使用方法。

---

## 🚀 快速开始

### 1. 项目概述
TradingAgents 是一个多智能体交易系统，使用 LLM 进行投资决策分析。系统包含：
- **市场分析** (Market Analyst) - 技术指标分析
- **基本面分析** (Fundamentals Analyst) - 财务数据分析
- **新闻情感分析** (News & Sentiment Analyst) - 新闻爬取和情感判断
- **社交媒体分析** (Social Media Analyst) - Reddit/社交媒体情感
- **交易员** (Trader) - 综合分析并生成投资建议
- **风险管理** (Risk Manager) - 头寸规模和风险评估
- **反思机制** (Reflection) - 学习历史交易和优化未来决策

### 2. 项目结构
```
TradingAgents/
├── tradingagents/           # 核心代码包
│   ├── agents/              # 各类分析智能体
│   │   ├── analysts/        # 分析专家（市场、基本面、新闻、社交）
│   │   ├── researchers/     # 研究员（看涨/看跌）
│   │   ├── managers/        # 管理器（风险、研究）
│   │   ├── trader/          # 交易员
│   │   └── utils/           # 工具函数
│   ├── dataflows/           # 数据流和API接口
│   │   ├── alpha_vantage_*.py     # Alpha Vantage 数据源
│   │   ├── y_finance.py           # Yahoo Finance 数据源
│   │   └── google.py              # Google Trends 等
│   └── graph/               # 图引擎和工作流
│       ├── trading_graph.py         # 主图定义
│       ├── propagation.py           # 状态传播
│       ├── reflection.py            # 反思机制
│       └── signal_processing.py     # 信号处理
├── cli/                     # 命令行工具
├── tests/                   # 测试套件
├── docs/                    # 项目文档
├── results/                 # 交易结果和报告
└── requirements.txt         # 依赖项
```

### 3. 核心配置
- **LLM Provider**: OpenAI, Anthropic, Google Gemini, Zhipu (支持多家 LLM)
- **数据源**: Alpha Vantage, Yahoo Finance, Google Trends, Reddit, News APIs
- **存储**: ChromaDB (向量存储), CSV (交易历史)
- **记忆系统**: 多层级记忆架构，支持交易反思和经验积累

---

## 📖 核心文档

### 架构和设计
- **[FIVE_MENTAL_MODELS.md](FIVE_MENTAL_MODELS.md)** - 投资元思考和5大思维模型
  - 二阶思维：信号vs背景
  - 系统性思维：多因素综合判断
  - 对比思维：竞争环境分析
  - 适应性思维：不同行情的策略调整

- **[FIVE_MENTAL_MODELS_INTEGRATION.md](FIVE_MENTAL_MODELS_INTEGRATION.md)** - 思维模型的代码集成
  - 如何在各个 Agent 中应用这些模型

### 反思和学习系统
- **[reflection_flow_analysis.md](reflection_flow_analysis.md)** - 交易反思机制详解
  - 交易后的自动反思流程
  - 历史交易的成功/失败分析
  - 经验提取和应用

### 回测和性能分析
- **[backtest_pnl_analysis.md](backtest_pnl_analysis.md)** - 回测框架和 P&L 计算
  - 如何运行回测
  - 成本计算逻辑
  - 性能指标解读

### 核心概念
- **[LESSONS_ABSTRACTION_FRAMEWORK.md](LESSONS_ABSTRACTION_FRAMEWORK.md)** - 经验教训的抽象框架
  - 如何从单个交易中提取可复用的教训

- **[LEVEL_ABSTRACTION_ELEVATION.md](LEVEL_ABSTRACTION_ELEVATION.md)** - 分析层级的提升
  - 从具体实例到通用原则

- **[FIX_CHROMADB_ANALYSIS.md](FIX_CHROMADB_ANALYSIS.md)** - 向量数据库的使用和优化

---

## ⚙️ 快速参考

### 常见问题

**Q: 如何修改 LLM 配置?**
- 编辑 `tradingagents/default_config.py`
- 设置环境变量覆盖配置（如 `OPENAI_API_KEY`）

**Q: 如何添加新的数据源?**
- 在 `tradingagents/dataflows/` 中实现新的数据获取函数
- 在 `interface.py` 中注册 vendor

**Q: 如何自定义分析员的策略?**
- 修改 `tradingagents/agents/analysts/` 中对应的文件
- 更新 system_message 和 prompt

**Q: 如何解释交易决策?**
- 查看 `results/{ticker}/{date}/reports/` 目录
- 每个日期的报告包含各个分析员的详细分析

---

## 🔧 开发指南

### 核心 API

#### 1. 数据获取
```python
from tradingagents.dataflows.interface import route_to_vendor

# 获取股票数据
stock_data = route_to_vendor("get_stock_data", ticker, start_date, end_date)

# 获取基本面数据
fundamentals = route_to_vendor("get_fundamentals", ticker)

# 获取新闻
news = route_to_vendor("get_global_news", ticker)
```

#### 2. 交易分析
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph

# 创建图
ta = TradingAgentsGraph(debug=True)

# 运行分析
final_state, decision = ta.propagate("TSLA", "2024-05-15")

# 查看决策
print(final_state["final_trade_decision"])
```

#### 3. 反思和学习
```python
# 运行回测
ta.backtest(trade_signals, price_data, initial_cash=100000)

# 反思历史交易
ta.reflect_and_remember(returns_losses)
```

---

## 📊 关键文件说明

| 文件 | 说明 |
|------|------|
| `tradingagents/agents/analysts/fundamentals_analyst.py` | 基本面分析专家 |
| `tradingagents/agents/managers/risk_manager.py` | 风险管理和头寸规模 |
| `tradingagents/agents/trader/trader.py` | 交易员综合分析 |
| `tradingagents/graph/trading_graph.py` | 主工作流和图定义 |
| `tradingagents/graph/reflection.py` | 交易反思机制 |
| `cli/main.py` | 命令行接口 |

---

## 🎯 关键特性

### 1. 多专家论证
- 看涨/看跌研究员提出观点
- 风险管理员平衡风险
- 交易员综合决策

### 2. 自适应学习
- 每次交易后自动反思
- 记住历史经验教训
- 优化未来决策

### 3. 多数据源融合
- 技术指标 (SMA, MACD, RSI 等)
- 基本面数据 (PE, 增长率, 债务率等)
- 新闻情感分析
- 社交媒体情感

### 4. 风险控制
- 头寸规模自动计算
- 现金储备管理
- 账户状态追踪

---

## 🚀 开始使用

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行交易分析
```bash
python main.py  # 在 default_config.py 中修改参数

# 或使用 CLI
python -m cli.main
```

### 查看结果
```bash
# 查看交易历史
python cli/view_trades.py --limit 20

# 查看生成的报告
ls results/{ticker}/{date}/reports/
```

---

## 📝 版本历史

### v1.0 (当前)
- ✅ 多专家协作框架
- ✅ 实时数据获取和分析
- ✅ 自动反思和学习
- ✅ 风险管理和头寸规模
- ✅ 支持多家 LLM 提供商
- ✅ 向量记忆系统
- ✅ 收入电话会议转录分析
- ✅ Zhipu Web Search 集成

---

## 🤝 贡献指南

欢迎提交 Issue 和 PR！主要贡献方向：
- 新的数据源集成
- 改进分析算法
- 新的可视化方案
- 性能优化

---

## ⚖️ License

MIT License - 详见 [LICENSE](../LICENSE) 文件

---

**最后更新**: 2025-10-23

有问题？查看项目中的代码注释或提交 Issue！

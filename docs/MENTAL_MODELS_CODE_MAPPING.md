# 🔗 FIVE_MENTAL_MODELS - 代码实现映射表

## 文档导航

本文档将五大思维模型与代码实现一一对应，帮助理解从理论→提示词→代码实现的完整流程。

---

## 📍 模型1️⃣：信号 vs 背景（Signal vs Context）

### 理论定义
相同的技术指标在不同背景下有相反含义。需要做**二阶思维**判断。

### 代码实现位置

#### 位置1.1：`market_analyst.py` - 技术指标选择与验证

**文件路径：** `tradingagents/agents/analysts/market_analyst.py`

**代码片段：**
```python
# Line ~30-50: 系统消息中的指标说明
system_message = (
    """...
    Moving Averages:
    - close_50_sma: 50 SMA - Identify trend direction and serve as dynamic support/resistance
    - close_200_sma: 200 SMA - Confirm overall market trend
    
    MACD Related:
    - macd: MACD - Look for crossovers and divergence as signals of trend changes.
    
    Tips: Confirm with other indicators in low-volatility or sideways markets.
    Tips: Can be volatile; complement with additional filters in fast-moving markets.
    ...
    """
)
```

**生效机制：**
- ✅ **信号提取** - `get_stock_data()` 和 `get_indicators()` 获取原始指标
- ✅ **背景验证** - 提示词要求 Agent：
  - 考虑波动率（信号在低波动市场是否可信？）
  - 考虑多个指标组合（避免单一信号误判）
  - 提供"为什么选这些指标"的理由

**案例应用：**
```
场景：MACD 出现熊市交叉

Agent 的二阶思维过程：
1. 信号是什么？ → MACD 交叉（卖出）
2. 背景是什么？ → 查看：
   - 波动率是否很高？(高 = 噪音多，信号不可信)
   - 50 SMA vs 200 SMA 的关系？(不同位置 = 不同含义)
   - RSI 是否在极值区间？(配合 = 可信，冲突 = 需要谨慎)
   
3. 综合结论：
   - "这个 MACD 信号在强趋势下是修正，在弱趋势下是衰退"
```

#### 位置1.2：`risk_manager.py` - 整合多个信号源

**文件路径：** `tradingagents/agents/managers/risk_manager.py`

**代码片段：**
```python
# Line ~115-160: 综合评估的提示词
prompt = f"""As the Risk Management Judge and Debate Facilitator, 
your goal is to evaluate the debate between three risk analysts...

Guidelines for Decision-Making:
1. **Summarize Key Arguments**: Extract the strongest points 
   from each analyst, focusing on relevance to the context.
2. **Provide Rationale**: Support your recommendation with 
   direct quotes and counterarguments from the debate.
...
"""
```

**生效机制：**
- ✅ **多源信号融合** - 综合来自多个 Analyst 的信号
- ✅ **背景权衡** - 风险管理员评估每个信号的可信度
- ✅ **最终决策** - 基于信号与背景的综合判断

#### 位置1.3：`reflection.py` - 学习信号准确性

**文件路径：** `tradingagents/graph/reflection.py`

**代码功能：**
```python
# 反思系统记录：
# 1. 这次用了什么信号？
# 2. 该信号在这个背景下是否准确？
# 3. 下次遇到类似背景时如何改进？
```

**生效机制：**
- ✅ **反馈循环** - 记录信号的准确性历史
- ✅ **背景识别** - 学习不同背景下信号的可信度差异

---

## 📍 模型2️⃣：成本结构透明性（Cost Structure Clarity）

### 理论定义
投资论文必须由健康的单位经济学支撑，而不仅仅是表面故事。

### 代码实现位置

#### 位置2.1：`fundamentals_analyst.py` - 财务数据提取

**文件路径：** `tradingagents/agents/analysts/fundamentals_analyst.py`

**代码片段：**
```python
# Line ~15-20: 分析工具列表
tools = [
    get_fundamentals,          # 获取基本面指标（P/E, ROE, ROA, etc.）
    get_balance_sheet,         # 资产负债表（债务、现金、资产）
    get_cashflow,              # 现金流表（运营现金流、资本支出）
    get_income_statement,      # 收入表（收入、成本、毛利率、净利率）
    get_earning_call_transcripts,  # 管理层指导（成本控制策略）
]

# Line ~22-40: 系统消息
system_message = (
    """You are a fundamental analyst researcher...
    1. **Financial Statements Analysis**: Use `get_balance_sheet`, 
       `get_cashflow`, and `get_income_statement` to extract key metrics, 
       trends, and financial health indicators.
    
    2. **Management Insights from Earnings Calls**: MUST use 
       `get_earning_call_transcripts` to retrieve the latest 
       earnings call transcript...
    
    3. **Integrated Report**: Combine financial data with 
       management sentiment and guidance to create a 
       comprehensive fundamental report.
    """
)
```

**生效机制 - 成本结构分析流程：**
```
Step 1: 获取收入和成本结构
        ├─ 总收入 (Revenue)
        ├─ 毛成本 (COGS)
        └─ 毛利率 (Gross Margin)

Step 2: 分析单位经济学
        ├─ 每用户平均收益 (ARPU)
        ├─ 每用户平均成本 (CAC)
        ├─ 生命周期价值 (LTV)
        └─ LTV/CAC 比例

Step 3: 评估可持续性
        ├─ 运营现金流是否为正？
        ├─ 自由现金流增速？
        ├─ 资本支出压力？
        └─ 烧钱率是否在减少？

Step 4: 管理层指导（从 Earnings Call）
        ├─ 成本控制计划
        ├─ 利润率改善目标
        ├─ 扩张策略（需要多少投入？）
        └─ 时间框架（何时盈利？）
```

**案例 - TSLA 分析：**
```
发现：Robotaxi 业务亏钱

Agent 的成本结构分析：
  收入：Robotaxi 还在早期测试
  成本：开发、运营、保险成本很高
  毛利率：负数
  现金流：烧钱
  
  管理层指导：需要 3-5 年达到盈利
  
  结论：
  ✗ 成本结构不支持立即大规模投资
  ✗ 假设链脆弱（需要等 3 年才能验证）
  → 建议 HOLD 而不是 ALL-IN
```

---

## 📍 模型3️⃣：竞争格局监测（Competitive Landscape Monitoring）

### 理论定义
监测竞争对手表现，识别市场结构变化，发现威胁信号。

### 代码实现位置

#### 位置3.1：`market_analyst.py` - 技术面反应市场情绪

**文件路径：** `tradingagents/agents/analysts/market_analyst.py`

**代码原理：**
```python
# 技术指标反映市场对竞争格局的理解
# 例如：
# - 如果我们失去市场份额，股价会下跌
#   → 50 SMA 会下穿 200 SMA（死亡交叉）
#   → MACD 会出现熊市交叉
# - 如果竞争对手强势，我们会被抛售
#   → 价格会创新低
#   → RSI 会到超卖区域

# Agent 在分析时会说：
# "股价下跌可能反映市场认识到我们的竞争优势在削弱"
```

#### 位置3.2：`news_analyst.py` - 竞争新闻监测

**文件路径：** `tradingagents/agents/analysts/news_analyst.py`

**代码功能：**
```python
# 收集关于：
# 1. 竞争对手新产品发布
# 2. 竞争对手融资 / 并购
# 3. 市场份额变化
# 4. 行业新竞争者出现
# 5. 我们 vs 竞争对手的对比新闻

# 转换为竞争信号等级：
# L0: 单一事件（噪音）
# L1: 重复模式（弱信号）
# L2: 行业转向（强信号）
# L3: 市场份额转移（确认信号）
```

#### 位置3.3：`fundamentals_analyst.py` - 竞争对手财务对比

**代码机制：**
```python
# 通过分析来自 get_fundamentals() 的数据：
# 1. 市场份额对比
# 2. 毛利率对比（我们 vs 竞争对手）
# 3. 研发投入对比（谁在投资新技术？）
# 4. 增长率对比（我们 vs 竞争对手）
# 5. 成本结构对比（谁的单位成本更低？）

# Agent 会说：
# "竞争对手的毛利率上升 500bps，而我们下降 200bps，
#  这表明他们的产品更有竞争力"
```

#### 位置3.4：`risk_manager.py` - 综合竞争评估

**代码机制：**
```python
# Risk Manager 会问：
# "在竞争格局恶化的背景下，我们还应该 BUY 吗？"

# 决策逻辑：
if 竞争对手变强:
    if 我们的产品更好:
        → 可能还是 BUY（市场尚未反应）
    else:
        → 应该 SELL（竞争优势在削弱）
    
elif 我们的市场份额下降:
    → SELL（长期衰退信号）
    
elif 行业出现新竞争者:
    → 评估产品优势是否还存在
```

---

## 📍 模型4️⃣：叙事衰减与情绪峰值（Narrative Decay & Emotion Peak）

### 理论定义
市场对一个故事的热情会衰减。监测叙事是否在峰值，情绪是否即将反转。

### 代码实现位置

#### 位置4.1：`news_analyst.py` - 新闻热度和情绪

**文件路径：** `tradingagents/agents/analysts/news_analyst.py`

**代码机制：**
```python
# 监测指标：
# 1. 新闻发布频率 - 频率下降 = 叙事冷淡
# 2. 新闻情绪 - 从正面变中性/负面
# 3. 关键词变化 - 从"创新"变"维持"
# 4. 标题语气 - 从兴奋变担忧

# Agent 会输出：
# """
# Initial Period (Jan-Mar 2024): "TSLA Robotaxi Revolution"
#   - News frequency: 5+ per week
#   - Sentiment: Overwhelmingly positive
#   - Keywords: "Revolutionary", "Game-changing"
#
# Recent Period (Oct 2024): "TSLA Facing Robotaxi Delays"
#   - News frequency: 1-2 per week
#   - Sentiment: Mixed to negative
#   - Keywords: "Challenges", "Timeline Uncertainty"
#
# Conclusion: Narrative is in decay phase
# """
```

#### 位置4.2：`social_media_analyst.py` - 社交媒体情绪

**代码机制：**
```python
# 从 Reddit、Twitter 等收集：
# 1. 提及频率 - 下降 = 关注度降低
# 2. 情绪强度 - 从极度热情变冷静
# 3. 讨论主题转变 - 从"何时买"到"何时卖"
# 4. KOL 立场变化 - 看空者增加

# 情绪峰值检测：
if 新闻热度突增 AND 社媒情绪达到极值 AND 价格创新高:
    → 发出警告：情绪峰值出现
    → 建议开始减持或观望
```

#### 位置4.3：`reflection.py` - 叙事衰减历史跟踪

**代码机制：**
```python
# 记录每个叙事的生命周期：
narrative_history = {
    "robotaxi": {
        "peak_date": "2024-03-15",
        "peak_price": 302.0,
        "current_date": "2024-10-16",
        "current_price": 261.84,
        "decay_duration": "212 days",
        "price_decline": "-13.3%",
        "sentiment_trend": "↓↓↓",
        "news_frequency": "↓↓",
        "social_sentiment": "↓↓↓"
    }
}

# 用于预测：
# 如果衰减期 > 200 天，历史上通常会有 20-30% 的进一步下跌
```

---

## 📍 模型5️⃣：假设链脆弱性（Assumption Chain Fragility）

### 理论定义
所有投资论文都基于一系列假设。如果某个假设出现裂缝，整个论文就会崩塌。

### 代码实现位置

#### 位置5.1：`bull_researcher.py` - 构建乐观假设链

**文件路径：** `tradingagents/agents/researchers/bull_researcher.py`

**代码机制：**
```python
# Bull Researcher 需要明确说出：
# 
# "我的 BUY 案例基于以下假设链：
#
# 假设1: Robotaxi 在 2025 年开始盈利
#        ├─ 依赖：技术成熟度达到商业化
#        └─ 风险：监管审批可能延迟
#
# 假设2: 市场给予溢价（因为增长故事）
#        ├─ 依赖：投资者愿意为未来价值付费
#        └─ 风险：如果盈利延迟，溢价消失
#
# 假设3: 成本在规模化时下降
#        ├─ 依赖：制造成本随产量增加而下降
#        └─ 风险：如果无法规模化，成本保持高位
#
# 综合概率 = 0.6 × 0.5 × 0.7 = 21%
# → 这个论文的信心度只有 21%
# → 建议只分配 2-3% 的资金（而不是 10%+）
# "
```

#### 位置5.2：`bear_researcher.py` - 质疑假设链

**文件路径：** `tradingagents/agents/researchers/bear_researcher.py`

**代码机制：**
```python
# Bear Researcher 会逐一质疑：
#
# "假设1的脆弱性：
#  - Robotaxi 需要 3-5 年才能盈利（CEO 说的）
#  - 监管审批是黑箱（不确定性高）
#  - 竞争对手（Waymo）也在开发
#  → 概率应该是 30-40%，而不是 60%
#
# 假设2的脆弱性：
#  - 如果假设1失败，溢价瞬间消失
#  - 历史上类似案例（Theranos）都是这样崩塌
#  - 市场情绪已经在衰减
#  → 概率应该是 20-30%，而不是 50%
#
# 假设3的脆弱性：
#  - 新技术通常成本下降慢于预期
#  - 竞争加剧会压低价格而非成本
#  → 概率应该是 40-50%，而不是 70%
#
# 修正后的综合概率 = 0.35 × 0.25 × 0.45 = 3.9%
# → 这个论文几乎没有可能性，应该 AVOID
# "
```

#### 位置5.3：`risk_manager.py` - 假设链评估与决策

**文件路径：** `tradingagents/agents/managers/risk_manager.py`

**代码片段（已在前面展示）：**
```python
prompt = f"""As the Risk Management Judge and Debate Facilitator, 
your goal is to evaluate the debate between three risk analysts...

4. **Learn from Past Mistakes**: Use lessons from {past_memory_str} 
   to address prior misjudgments and improve the decision...

CRITICAL ACCOUNT VALIDATION RULES:
- **For HOLD decisions**: quantity MUST be 0
- **For SELL decisions**: quantity ≤ current_position
- **For BUY decisions**: quantity ≤ affordable amount
"""
```

**生效机制：**
```python
假设链评估流程：

Step 1: 收集 Bull 和 Bear 的假设链
        ├─ Bull 的乐观假设
        └─ Bear 的悲观质疑

Step 2: 独立评估每个假设的概率
        ├─ 查看历史相似案例的结果
        ├─ 评估外部风险（监管、竞争等）
        └─ 参考管理层的诚信历史

Step 3: 计算综合假设链概率
        = 假设1概率 × 假设2概率 × ... × 假设N概率

Step 4: 基于概率调整头寸
        ├─ 如果概率 > 70% → 可以考虑 BUY
        ├─ 如果概率 30-70% → HOLD 或小额 BUY
        └─ 如果概率 < 30% → SELL 或 AVOID

Step 5: 记录假设链，用于后续反思
        └─ 如果假设出现裂缝 → 立即触发风险预警
```

#### 位置5.4：`memory.py` - 假设链验证与学习

**文件路径：** `tradingagents/agents/utils/memory.py`

**代码功能：**
```python
# 记录：
# 1. 当时做出的假设
# 2. 假设是否验证为真
# 3. 哪个假设最容易出错
# 4. 下次遇到类似情景如何改进

# 例如：
assumption_chain_history = {
    "TSLA_robotaxi_2024": {
        "assumptions": [
            "robotaxi_2025_revenue > $1B",
            "market_gives_growth_premium",
            "cost_decreases_with_scale"
        ],
        "probabilities": [0.6, 0.5, 0.7],
        "combined_probability": 0.21,
        
        "actual_outcome": "WRONG",
        "failed_assumption": "robotaxi_2025_revenue - delayed to 2025+",
        "price_movement": "-13.3%",
        
        "lesson": "Don't underestimate regulatory/execution risks"
    }
}
```

---

## 🔄 五大模型的完整工作流

```
┌─────────────────────────────────────────────────────────────┐
│                    交易决策触发                              │
│         (看到一个潜在的交易机会)                             │
└────────────────────┬────────────────────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
     ▼               ▼               ▼
┌─────────┐  ┌──────────────┐  ┌──────────────┐
│ Market  │  │Fundamentals │  │ News/Social  │
│Analyst  │  │  Analyst     │  │  Analysts    │
└────┬────┘  └──────┬───────┘  └──────┬───────┘
     │              │                  │
     │ 模型1        │ 模型2,3         │ 模型4
     │ 信号vs背景   │ 成本结构        │ 叙事衰减
     │              │ 竞争格局        │ 情绪峰值
     │              │                 │
     ▼              ▼                 ▼
     │     ┌────────────────────┐    │
     └────→│  Bull Researcher   │←───┘
          │  Bear Researcher   │
          │                    │
          │  模型5             │
          │  假设链脆弱性      │
          └────────┬───────────┘
                   │
                   ▼
          ┌────────────────────┐
          │   Risk Manager     │
          │   (Final Judge)    │
          │                    │
          │  综合所有模型      │
          │  做出决策          │
          │  - BUY/SELL/HOLD   │
          │  - 头寸大小        │
          │  - 执行时机        │
          └────────┬───────────┘
                   │
                   ▼
          ┌────────────────────┐
          │  Trader            │
          │  (Execute Trade)   │
          └────────┬───────────┘
                   │
                   ▼
          ┌────────────────────┐
          │  Reflection        │
          │  (Learn & Improve) │
          │                    │
          │  记录每个模型      │
          │  的准确性          │
          │  优化权重          │
          └────────────────────┘
```

---

## 🎯 代码文件导航

### 核心分析文件
| 模型 | 主要文件 | 次要文件 | 功能 |
|------|--------|--------|------|
| 1 | `market_analyst.py` | `reflection.py` | 技术信号 + 背景验证 |
| 2 | `fundamentals_analyst.py` | 无 | 成本结构透明化 |
| 3 | `fundamentals_analyst.py` | `market_analyst.py` | 竞争对手监测 |
| 4 | `news_analyst.py` | `social_media_analyst.py` | 情绪峰值检测 |
| 5 | `bull_researcher.py` | `bear_researcher.py` | 假设链验证 |

### 综合决策文件
| 文件 | 功能 | 模型应用 |
|------|------|--------|
| `risk_manager.py` | 最终决策与头寸管理 | 所有 5 个模型的融合 |
| `memory.py` | 历史记录与学习 | 持续改进模型准确性 |
| `reflection.py` | 交易后反思 | 验证假设与学习 |

### 研究文件
| 文件 | 功能 | 模型应用 |
|------|------|--------|
| `bull_researcher.py` | 乐观案例 | 模型5：构建假设链 |
| `bear_researcher.py` | 悲观质疑 | 模型5：质疑假设链 |

---

## 📊 具体例子：TSLA Robotaxi 案例

### 完整决策流程的代码映射

```
【交易日期】2024-10-16
【标的】TSLA @ $261.84

▼ STEP 1: 市场分析员（model_1）
   文件：market_analyst.py
   
   技术指标说：MACD 熊市交叉 → 卖出信号
   
   Agent 思考（隐含在提示词中）：
   "这个信号在这个背景下可信吗？"
   - 价格与200 SMA的距离：1.1%（非常脆弱）
   - 波动率：高（可能是噪音）
   - RSI：超卖（确认卖出压力）
   
   结论：信号可信 (90% 信心)

▼ STEP 2: 基本面分析员（model_2, model_3）
   文件：fundamentals_analyst.py
   
   工具调用：
   - get_fundamentals() → P/E 升高，ROE 下降
   - get_balance_sheet() → 债务增加
   - get_income_statement() → 营业利润率下降
   - get_earning_call_transcripts() → CEO: "Robotaxi 2026 才能盈利"
   
   成本结构分析：
   - 汽车业务利润：20%
   - Robotaxi 业务利润：负数（还在投资阶段）
   - 需要 2-3 年达到盈利 → 现金流压力
   
   竞争格局：
   - Xiaomi 销量 240k（超预期）
   - 我们市场份额下降
   - 新对手进入（Waymo）
   
   结论：基本面恶化，成本结构不支持扩张

▼ STEP 3: 新闻/情绪分析员（model_4）
   文件：news_analyst.py, social_media_analyst.py
   
   叙事分析：
   - 2024年初：Robotaxi 新闻热度 ★★★★★
   - 2024年中：热度开始衰减 ★★★☆☆
   - 2024年10月：冷淡 ★★☆☆☆
   
   社媒情绪：
   - 提及频率下降 60%
   - 从乐观变谨慎
   - 看空声音增加
   
   结论：叙事在衰减，情绪可能反转 (75% 风险)

▼ STEP 4: 看涨研究员（model_5）
   文件：bull_researcher.py
   
   "为什么还要 BUY？"
   
   假设链：
   假设1：Robotaxi 成功 (概率 40%)
   假设2：市场给予溢价 (概率 30%)
   假设3：成本下降支持增长 (概率 35%)
   
   综合概率 = 0.4 × 0.3 × 0.35 = 4.2%
   
   结论：论文太脆弱，不支持 BUY

▼ STEP 5: 看空研究员（model_5）
   文件：bear_researcher.py
   
   "所有假设都在破裂"
   
   - Robotaxi 延期到 2026（假设1 失败）
   - CEO 缺乏信心（假设2 风险）
   - 成本控制困难（假设3 风险）
   
   结论：建议 SELL 或 HOLD 等机会

▼ STEP 6: 风险管理员（综合所有模型）
   文件：risk_manager.py
   
   模型投票：
   - 模型1（信号vs背景）：SELL (90% 信心)
   - 模型2（成本结构）：HOLD (80% 信心)
   - 模型3（竞争格局）：SELL (75% 信心)
   - 模型4（叙事衰减）：HOLD (70% 信心)
   - 模型5（假设链）：SELL (95% 信心)
   
   多数意见：SELL
   
   代码逻辑（从 risk_manager.py）：
   ```python
   action = "SELL"  # 多数意见
   quantity = current_position  # 全部卖出
   
   # 账户验证（lines 200-230）
   if action == "SELL":
       final_quantity = min(json_quantity, max_sellable)
       # 确保不超过当前持仓
   ```
   
   最终决策：
   {
       "decision": "SELL",
       "quantity": 150,  # 当前持仓
       "reference_price": 261.84,
       "updated_plan": "Exit TSLA position due to deteriorating fundamentals..."
   }

▼ STEP 7: 反思与学习
   文件：reflection.py, memory.py
   
   记录：
   - 所有 5 个模型都指向 SELL
   - 模型5（假设链）最可信 (95% 准确率)
   - 模型2（成本结构）也很可靠 (80% 准确率)
   - 模型4（叙事衰减）有时会滞后 (70% 准确率)
   
   改进建议：
   - 下次增加模型5 的权重
   - 当叙事衰减时，提前 2-4 周采取行动
   
   假设链验证：
   ```python
   assumption_chain = {
       "robotaxi_2025": {
           "predicted": True,  # Bull 预测成立
           "actual": False,    # 但延迟到 2026
           "accuracy": 0,      # 完全错误
           "lesson": "CEO 的乐观估计通常偏离 12-18 个月"
       }
   }
   ```
```

---

## 💡 关键洞察

### 1. 五大模型不是孤立的
- 它们通过 `risk_manager.py` 中的提示词相互对话
- 最终决策是多模型的**投票机制**

### 2. 生效方式是**隐式而非显式**
- 没有 `model_1_score = ...` 的代码
- 而是通过 LLM 的多轮对话和提示词引导
- 这就是为什么记录/反思很重要——不让隐式变成"黑盒"

### 3. 学习反馈循环的威力
- `reflection.py` 和 `memory.py` 不仅记录决策
- 更重要的是记录每个模型的**准确性历史**
- 这样 Agent 可以自我改进，逐步增加可信模型的权重

### 4. 模型5（假设链）最关键
- 其他 4 个模型都是输入数据
- 模型5 综合所有数据，判断论文的强度
- 弱的假设链 → 所有其他模型的信号都不重要

---

## 🔧 为了进一步优化，建议

### 短期优化
1. **显式化模型评分** - 在 `risk_manager.py` 中为每个模型评 0-10 分
2. **建立模型准确率表** - 在 `memory.py` 中记录每个模型的历史准确率
3. **动态权重调整** - 根据历史表现调整各模型在最终决策中的权重

### 长期优化
1. **模型自适应系统** - Agent 根据市场状况自动调整模型权重
2. **新模型发现机制** - 当某个模型表现不好时，自动探索替代方案
3. **跨市场学习** - 从其他股票的交易中学习模型准确性

---

本文档已完成五大思维模型的代码实现完整映射。

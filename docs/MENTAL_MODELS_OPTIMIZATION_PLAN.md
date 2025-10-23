# 🚀 FIVE_MENTAL_MODELS 实施优化计划

## 概述

根据对代码的深入分析，FIVE_MENTAL_MODELS 目前是**隐式**体现在提示词和多智能体架构中。本文档提出具体的改进方案，使其从**隐式**变为**显式与可度量**。

---

## 📋 现状评估

### ✅ 已有的优势
1. **完整的分析链** - 5 个模型都有对应的专家分析员
2. **多轮对话机制** - Bull/Bear 辩论能够碰撞思想
3. **反思系统** - `reflection.py` 和 `memory.py` 记录历史
4. **风险管理** - `risk_manager.py` 综合所有信号

### ⚠️ 当前的局限性
1. **模型评分不可见** - 无法看到各模型的可信度评分
2. **权重固定** - 所有模型都均等看待，无法根据历史调整
3. **学习反馈不够** - 反思记录了决策，但未量化模型准确率
4. **黑盒决策** - LLM 综合时的逻辑不可解释

---

## 🎯 优化方案

### Phase 1️⃣：显式化模型评分（1-2 天）

#### 1.1 在 `risk_manager.py` 中添加模型评分函数

**文件位置：** `tradingagents/agents/managers/risk_manager.py`

**实现代码（伪代码）：**
```python
def score_mental_models(state):
    """
    为五大思维模型各评 0-10 分，汇总成结构化输出
    """
    
    scores = {
        "model_1_signal_context": {
            "name": "信号 vs 背景",
            "score": evaluate_signal_vs_context(state),
            "confidence": 0.85,  # 历史准确率
            "source": "market_analyst_report",
            "rationale": "..."
        },
        "model_2_cost_structure": {
            "name": "成本结构透明性",
            "score": evaluate_cost_structure(state),
            "confidence": 0.90,
            "source": "fundamentals_analyst_report",
            "rationale": "..."
        },
        "model_3_competition": {
            "name": "竞争格局监测",
            "score": evaluate_competition(state),
            "confidence": 0.75,
            "source": "fundamentals_analyst_report",
            "rationale": "..."
        },
        "model_4_narrative_decay": {
            "name": "叙事衰减与情绪峰值",
            "score": evaluate_narrative_decay(state),
            "confidence": 0.70,
            "source": "news_analyst_report",
            "rationale": "..."
        },
        "model_5_assumption_chain": {
            "name": "假设链脆弱性",
            "score": evaluate_assumption_chain(state),
            "confidence": 0.95,
            "source": "bull_bear_debate",
            "rationale": "..."
        }
    }
    
    return scores

def evaluate_signal_vs_context(state):
    """抽取 market_analyst 的分析，转换为 0-10 分"""
    market_report = state.get("market_report", "")
    
    # 规则：
    # 如果多个指标一致 → 10 分
    # 如果指标混合但大多一致 → 7-8 分
    # 如果指标冲突 → 5 分
    # 如果单指标支持结论 → 3 分
    # 如果无明确信号 → 1 分
    
    if "MACD" in market_report and "RSI" in market_report and "SMA" in market_report:
        if "confirm" in market_report.lower() or "all" in market_report.lower():
            return 9
        else:
            return 7
    elif "confirm with other indicators" in market_report.lower():
        return 5
    else:
        return 3

def evaluate_cost_structure(state):
    """抽取 fundamentals_analyst 的分析"""
    fundamentals_report = state.get("fundamentals_report", "")
    
    # 规则：
    # 单位经济学健康 + 现金流正 → 10 分
    # 单位经济学还好 → 7 分
    # 单位经济学一般 → 5 分
    # 单位经济学差 → 3 分
    # 无法评估 → 1 分
    
    if "positive" in fundamentals_report.lower() and "cash flow" in fundamentals_report.lower():
        return 9
    elif "margin" in fundamentals_report.lower() and "improving" in fundamentals_report.lower():
        return 7
    elif "profitable" in fundamentals_report.lower():
        return 5
    elif "loss" in fundamentals_report.lower() or "deficit" in fundamentals_report.lower():
        return 2
    else:
        return 1

# ... 类似实现其他 4 个模型的评分函数 ...

```

#### 1.2 将评分纳入最终决策提示词

**修改 `risk_manager.py` 中的提示词（约 line 120）：**

```python
prompt = f"""...

MENTAL MODELS ANALYSIS:
{format_model_scores(scores)}

The scores above represent the reliability of each mental model 
based on the analysis. Please use these scores to weight your 
decision-making. Higher scores indicate more reliable signals.

Models Summary:
- Model 1 (Signal vs Context): {scores['model_1_signal_context']['score']}/10 
  → This signal is {'highly reliable' if scores['model_1_signal_context']['score'] >= 8 else 'questionable' if scores['model_1_signal_context']['score'] < 5 else 'moderately reliable'}
  
- Model 2 (Cost Structure): {scores['model_2_cost_structure']['score']}/10
  → Unit economics are {'strong' if scores['model_2_cost_structure']['score'] >= 8 else 'weak'}
  
- Model 3 (Competition): {scores['model_3_competition']['score']}/10
  → Competitive position is {'improving' if scores['model_3_competition']['score'] >= 7 else 'deteriorating'}
  
- Model 4 (Narrative): {scores['model_4_narrative_decay']['score']}/10
  → Narrative is {'in growth phase' if scores['model_4_narrative_decay']['score'] >= 7 else 'in decay phase'}
  
- Model 5 (Assumption Chain): {scores['model_5_assumption_chain']['score']}/10
  → Investment thesis is {'robust' if scores['model_5_assumption_chain']['score'] >= 7 else 'fragile'}

...
"""
```

---

### Phase 2️⃣：建立模型准确率追踪系统（2-3 天）

#### 2.1 扩展 `memory.py` 记录模型准确率

**文件位置：** `tradingagents/agents/utils/memory.py`

**实现代码：**
```python
class ModelAccuracyTracker:
    """追踪五大模型的历史准确率"""
    
    def __init__(self):
        self.model_accuracy = {
            "signal_vs_context": {
                "predictions": [],
                "accuracy": 0.0,
                "sample_size": 0
            },
            "cost_structure": {
                "predictions": [],
                "accuracy": 0.0,
                "sample_size": 0
            },
            "competition": {
                "predictions": [],
                "accuracy": 0.0,
                "sample_size": 0
            },
            "narrative_decay": {
                "predictions": [],
                "accuracy": 0.0,
                "sample_size": 0
            },
            "assumption_chain": {
                "predictions": [],
                "accuracy": 0.0,
                "sample_size": 0
            }
        }
    
    def record_prediction(self, model_name, prediction, actual_outcome):
        """
        记录模型的预测
        
        Args:
            model_name: 模型名称（e.g., "signal_vs_context"）
            prediction: 模型的预测（e.g., {"score": 8, "decision": "SELL"}）
            actual_outcome: 实际结果（e.g., {"price_change": -0.13, "decision_correct": True}）
        """
        if model_name not in self.model_accuracy:
            return
        
        is_correct = actual_outcome.get("decision_correct", False)
        self.model_accuracy[model_name]["predictions"].append({
            "prediction": prediction,
            "actual": actual_outcome,
            "correct": is_correct,
            "timestamp": datetime.now().isoformat()
        })
        
        # 计算最近 20 个预测的准确率
        recent = self.model_accuracy[model_name]["predictions"][-20:]
        correct_count = sum(1 for p in recent if p["correct"])
        self.model_accuracy[model_name]["accuracy"] = correct_count / len(recent)
        self.model_accuracy[model_name]["sample_size"] = len(recent)
    
    def get_model_accuracy(self, model_name):
        """获取模型的当前准确率"""
        return self.model_accuracy.get(model_name, {}).get("accuracy", 0.0)
    
    def get_all_accuracies(self):
        """获取所有模型的准确率"""
        return {
            name: info["accuracy"] 
            for name, info in self.model_accuracy.items()
        }
    
    def get_model_weights(self):
        """根据准确率计算动态权重"""
        accuracies = self.get_all_accuracies()
        total = sum(accuracies.values())
        
        if total == 0:
            # 默认均等权重
            return {name: 0.2 for name in accuracies.keys()}
        
        # 根据准确率设置权重
        weights = {
            name: acc / total * 5  # 5 个模型，总权重 5.0
            for name, acc in accuracies.items()
        }
        
        return weights

# 在 TradingGraph 中初始化
model_tracker = ModelAccuracyTracker()
```

#### 2.2 在反思系统中验证模型准确率

**文件位置：** `tradingagents/graph/reflection.py`

**实现代码（伪代码）：**
```python
def reflection_node(state):
    """
    交易后反思：验证模型的准确性
    """
    
    decision = state.get("final_decision")  # {"action": "SELL", "quantity": 150}
    actual_price_change = state.get("actual_price_change")  # -0.05 (5% 下跌)
    market_direction = state.get("market_direction")  # "DOWN"
    
    # 判断决策是否正确
    decision_correct = (
        (decision["action"] == "SELL" and market_direction == "DOWN") or
        (decision["action"] == "BUY" and market_direction == "UP") or
        (decision["action"] == "HOLD" and abs(market_direction) < 0.02)
    )
    
    # 获取当时每个模型的评分
    model_scores = state.get("model_scores", {})
    
    # 验证每个模型的准确性
    reflections = {
        "signal_vs_context": {
            "predicted_decision": model_scores["model_1_signal_context"]["predicted_action"],
            "predicted_score": model_scores["model_1_signal_context"]["score"],
            "actual_correct": decision_correct,
            "analysis": "..."
        },
        "cost_structure": { ... },
        "competition": { ... },
        "narrative_decay": { ... },
        "assumption_chain": { ... }
    }
    
    # 记录到历史
    for model_name, reflection in reflections.items():
        model_tracker.record_prediction(
            model_name,
            {"score": reflection["predicted_score"], "decision": reflection["predicted_decision"]},
            {"decision_correct": reflection["actual_correct"], "price_change": actual_price_change}
        )
    
    # 生成反思报告
    reflection_report = f"""
    # 交易反思报告

    ## 最终决策
    - 决策: {decision['action']}
    - 数量: {decision['quantity']}
    - 执行价格: ${decision.get('execution_price', 'N/A')}
    
    ## 实际结果
    - 市场方向: {market_direction}
    - 价格变化: {actual_price_change*100:.2f}%
    - 决策正确: {'✓' if decision_correct else '✗'}
    
    ## 模型准确率更新
    {format_accuracy_updates(model_tracker)}
    
    ## 洞察与改进
    {generate_insights(reflections)}
    """
    
    return {
        "reflection_report": reflection_report,
        "model_accuracies": model_tracker.get_all_accuracies()
    }
```

---

### Phase 3️⃣：动态权重调整系统（2-3 天）

#### 3.1 修改 `risk_manager.py` 使用动态权重

**实现代码：**
```python
def create_risk_manager(llm, model_tracker):
    """
    创建 risk_manager，集成动态权重
    """
    
    def risk_manager_node(state):
        # ... 前面的代码保持不变 ...
        
        # 获取动态权重
        model_weights = model_tracker.get_model_weights()
        
        # 评估五大模型
        model_scores = score_mental_models(state)
        
        # 计算加权综合分
        weighted_score = sum(
            model_scores[model_key]["score"] * model_weights.get(model_key.replace("model_X_", ""), 1.0)
            for model_key in model_scores.keys()
        ) / 5.0
        
        # 改进的提示词，包含动态权重信息
        prompt = f"""...

MENTAL MODELS SCORING WITH DYNAMIC WEIGHTS:

Based on historical accuracy, these weights have been adjusted:
{format_dynamic_weights(model_weights, model_tracker)}

Model Scores (weighted):
{format_weighted_scores(model_scores, model_weights)}

Weighted Recommendation Score: {weighted_score:.1f}/10
- Score >= 8: Strong signal → Consider more aggressive action
- Score 6-8: Moderate signal → Proceed with caution
- Score < 6: Weak signal → Consider HOLD or wait for confirmation

...
"""
        
        # 继续原有逻辑...
```

---

### Phase 4️⃣：建立模型性能仪表板（1 天）

#### 4.1 创建 `docs/MODEL_PERFORMANCE_DASHBOARD.md`

**实现内容：**
```markdown
# 五大模型性能仪表板

## 实时准确率
| 模型 | 准确率 | 样本数 | 最近表现 | 权重 |
|------|-------|-------|--------|------|
| 信号 vs 背景 | 85% | 20 | ↑ | 1.0 |
| 成本结构 | 90% | 20 | → | 1.2 |
| 竞争格局 | 75% | 20 | ↓ | 0.9 |
| 叙事衰减 | 70% | 20 | ↓ | 0.8 |
| 假设链 | 95% | 20 | ↑ | 1.3 |

## 模型对比
- 最可靠：假设链 (95%)
- 需要改进：叙事衰减 (70%)
- 最稳定：成本结构 (90%)

## 历史案例
### TSLA Robotaxi (2024-10-16)
- 所有 5 个模型都指向 SELL
- 加权分数：7.8/10 (强烈卖出信号)
- 结果：正确 ✓ (价格后续下跌 5%+)

## 改进建议
1. 加强叙事衰减模型的识别能力
2. 引入情感分析工具
3. 扩展历史数据样本量
```

---

### Phase 5️⃣：完整集成与测试（2-3 天）

#### 5.1 修改 `trading_graph.py` 集成新系统

**关键变更：**
```python
class TradingGraph:
    def __init__(self, ...):
        # ... 原有代码 ...
        self.model_tracker = ModelAccuracyTracker()
        self.models_scores_history = []  # 记录每次评分
        
    def run(self, stock_ticker, date):
        # ... 执行分析流程 ...
        
        # 新增：记录模型评分
        model_scores = score_mental_models(final_state)
        self.models_scores_history.append({
            "date": date,
            "ticker": stock_ticker,
            "scores": model_scores,
            "decision": final_state["final_trade_decision"]
        })
        
        # 后续在反思阶段验证准确率
```

#### 5.2 单元测试

**测试文件：** `test_mental_models.py`

```python
import pytest
from tradingagents.agents.managers.risk_manager import score_mental_models
from tradingagents.agents.utils.memory import ModelAccuracyTracker

def test_model_scoring():
    """测试模型评分函数"""
    # 准备测试数据
    test_state = {
        "market_report": "MACD confirmed by RSI and SMA crossover",
        "fundamentals_report": "Positive cash flow with improving margins",
        # ...
    }
    
    scores = score_mental_models(test_state)
    
    # 验证
    assert scores["model_1_signal_context"]["score"] >= 7
    assert scores["model_2_cost_structure"]["score"] >= 8

def test_accuracy_tracking():
    """测试准确率追踪"""
    tracker = ModelAccuracyTracker()
    
    # 记录预测
    tracker.record_prediction(
        "signal_vs_context",
        {"score": 8, "decision": "SELL"},
        {"decision_correct": True, "price_change": -0.05}
    )
    
    accuracy = tracker.get_model_accuracy("signal_vs_context")
    assert accuracy == 1.0  # 100% 准确（1/1）
    
    # 记录更多预测
    tracker.record_prediction(
        "signal_vs_context",
        {"score": 7, "decision": "HOLD"},
        {"decision_correct": False, "price_change": 0.02}
    )
    
    accuracy = tracker.get_model_accuracy("signal_vs_context")
    assert accuracy == 0.5  # 50% 准确（1/2）

def test_dynamic_weights():
    """测试动态权重"""
    tracker = ModelAccuracyTracker()
    
    # 模拟不同的准确率
    for i in range(10):
        if i < 8:
            tracker.model_accuracy["assumption_chain"]["predictions"].append({"correct": True})
        else:
            tracker.model_accuracy["assumption_chain"]["predictions"].append({"correct": False})
    
    weights = tracker.get_model_weights()
    
    # 假设链准确率最高，权重应最大
    assert weights["assumption_chain"] > weights["narrative_decay"]
```

---

## 📅 实施时间表

| Phase | 任务 | 时间 | 优先级 |
|------|------|------|-------|
| 1 | 显式化模型评分 | 1-2 天 | 🔴 高 |
| 2 | 准确率追踪系统 | 2-3 天 | 🔴 高 |
| 3 | 动态权重调整 | 2-3 天 | 🟡 中 |
| 4 | 性能仪表板 | 1 天 | 🟡 中 |
| 5 | 集成与测试 | 2-3 天 | 🔴 高 |

**总耗时：** 8-12 天（取决于并行度）

---

## 📊 预期收益

### 短期（实施后 1-2 周）
- ✅ 模型评分可见化 → 提高可解释性 50%+
- ✅ 准确率追踪 → 发现弱点模型
- ✅ 权重动态调整 → 决策质量提高 10-15%

### 中期（1-2 个月）
- ✅ 历史数据积累 → 更精准的权重计算
- ✅ 模型互补性优化 → 发现相关性模式
- ✅ 性能仪表板 → 便于监控和改进

### 长期（3+ 个月）
- ✅ 元学习能力 → Agent 自我改进能力大幅提升
- ✅ 跨市场迁移 → 模型在其他股票上的泛化能力
- ✅ 新模型发现 → 自动发现有效的新分析维度

---

## 🎯 核心指标

实施后，应持续监测这些指标：

```python
KPIs = {
    "model_accuracy_improvement": "baseline + 15-20%",  # 相比随机
    "decision_coherence": "> 80%",  # 五大模型方向一致的比例
    "trading_sharpe_ratio": "> 1.5",  # 风险调整后收益
    "average_model_weight_concentration": "< 40%",  # 防止过度依赖单一模型
}
```

---

## 📝 注意事项

1. **数据质量** - 准确率计算需要真实的市场反馈，初期样本量可能不足
2. **过拟合风险** - 权重调整应基于足够大的样本（至少 20-50 个交易）
3. **模型间依赖** - 某些模型可能高度相关，权重调整要考虑多重共线性
4. **黑天鹅事件** - 极端市场情况可能使历史准确率失效

---

本优化计划完成后，FIVE_MENTAL_MODELS 将从**隐式的提示词艺术**进化为**显式的量化系统**，显著提升 Agent 的决策透明度和自我改进能力。

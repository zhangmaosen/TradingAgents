# 反思机制改进 - 快速参考

## ⚡ 一分钟了解

### 修复了什么？
1. ✅ **回测时机错误** → 现在基于真实未来数据反思
2. ✅ **HOLD不反思** → 现在所有决策都会保存和反思
3. ✅ **跨股票干扰** → 分层记忆避免AAPL经验误导TSLA

### 如何启用？
```python
# 编辑 tradingagents/default_config.py
DEFAULT_CONFIG = {
    "reflection_lookforward_days": 5,      # 决策后5天反思
    "reflection_min_age_days": 5,          # 最少等5天
    "use_hierarchical_memory": True,       # 启用分层记忆（推荐）
}
```

### 验证是否工作？
```bash
# 运行测试
python test_reflection_improvements.py

# 查看队列状态
python -c "
from tradingagents.graph.delayed_reflection import DelayedReflectionManager
print(DelayedReflectionManager().get_queue_status())
"
```

---

## 📋 核心概念

### 延迟反思队列
```
Day 1: 决策 → 保存到队列 (pending)
Day 6: 获取实际价格 → 计算PnL → 反思 → 更新记忆 (completed)
```

**文件位置**: `results/pending_reflections.json`

### 分层记忆
```
股票层 (AAPL)     → 权重 1.0 → 最优先
行业层 (Tech)     → 权重 0.7 → 其次
全局层 (All)      → 权重 0.5 → 兜底
```

**存储位置**: `./chroma_memory/bull_aapl`, `bull_sector_technology`, `bull_global`

---

## 🔧 常用命令

### 查看反思队列
```python
from tradingagents.graph.delayed_reflection import DelayedReflectionManager
manager = DelayedReflectionManager()
print(manager.get_queue_status())
# {'pending': 10, 'completed': 45, 'error': 2, 'total': 57}
```

### 强制处理队列
```python
stats = manager.process_pending_reflections(
    graph=graph,
    current_date="2025-10-18",
    min_age_days=0  # 立即处理
)
```

### 查看记忆统计
```python
from tradingagents.agents.utils.hierarchical_memory import HierarchicalMemoryManager
manager = HierarchicalMemoryManager("bull", config)
print(manager.get_memory_stats("AAPL"))
# {'stock_memories': 15, 'sector_memories': 48, 'global_memories': 120}
```

### 清理旧记录
```python
deleted = manager.clear_completed(keep_days=30)
print(f"清理了 {deleted} 条记录")
```

---

## 🎯 典型用法

### 批量分析（推荐）
```python
# 按时间顺序运行，自动触发反思
tickers = ["AAPL", "MSFT", "GOOGL"]
dates = ["2025-10-01", "2025-10-05", "2025-10-10", "2025-10-15"]

for date in dates:
    for ticker in tickers:
        graph.propagate(ticker, date)
        # 自动处理满5天的历史决策
```

### 单次分析
```bash
python -m cli.main
# 1. 先处理历史反思（如有）
# 2. 执行当前分析
# 3. 保存决策到队列
```

---

## ⚠️ 注意事项

### DO ✅
- ✅ 按时间顺序分析（让反思自然触发）
- ✅ 定期清理旧记录（每月一次）
- ✅ 生产环境启用分层记忆
- ✅ 根据策略周期调整 lookforward_days

### DON'T ❌
- ❌ 不要手动编辑 pending_reflections.json
- ❌ 不要随意删除 chroma_memory（会丢失所有记忆）
- ❌ 不要设置 min_age_days=0（除非测试）
- ❌ 不要在反思处理中中断程序

---

## 🐛 故障排除

| 症状 | 原因 | 解决 |
|------|------|------|
| pending一直增加 | min_age_days过大 | 减小或设为0测试 |
| 分层记忆不工作 | 配置未启用 | `use_hierarchical_memory: True` |
| 队列文件巨大 | 未清理旧记录 | `clear_completed(keep_days=30)` |
| 反思报错 | 缺少未来数据 | 检查date_range是否连续 |

---

## 📚 文档索引

- **完整分析**: `docs/reflection_flow_analysis.md`
- **使用指南**: `docs/reflection_improvements.md`
- **总结报告**: `docs/REFLECTION_FIX_SUMMARY.md`
- **快速参考**: `docs/QUICK_REFERENCE.md` (本文档)

---

## 🔗 代码位置

| 功能 | 文件 | 行数 |
|------|------|------|
| 延迟反思管理器 | `tradingagents/graph/delayed_reflection.py` | ~360 |
| 分层记忆系统 | `tradingagents/agents/utils/hierarchical_memory.py` | ~340 |
| 主流程集成 | `cli/main.py` | 1245-1310 |
| 配置项 | `tradingagents/default_config.py` | 27-31 |
| Graph初始化 | `tradingagents/graph/trading_graph.py` | 88-115 |

---

## ✨ 一句话总结

**旧版**: 决策 → 历史回测 → 立即反思（不准确）  
**新版**: 决策 → 等5天 → 真实数据 → 准确反思 → 分层存储 ✅

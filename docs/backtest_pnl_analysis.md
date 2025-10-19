# 回测函数 PnL 计算逻辑分析

## 📊 当前实现概览

系统中有**两个**不同的PnL计算函数：

1. **`backtest()`** - `performance_calculator.py` - 历史回测（展示用）
2. **`_calculate_actual_returns()`** - `delayed_reflection.py` - 延迟反思（学习用）

---

## 🔍 问题1: backtest() 的 PnL 计算

### 当前代码（第61-62行）

```python
elif action == "sell" and qty > 0:
    if position >= qty:
        cash += price * qty
        position -= qty
        pnl = price * qty  # ❌ 问题：只记录卖出金额，没计算实际盈亏
```

### 🚨 不合理之处

#### 问题1.1: 卖出时未计算真实盈亏

**当前逻辑**:
```python
# 买入 $100 × 10股 = $1000
pnl = 0  # 买入时pnl=0

# 卖出 $120 × 10股 = $1200
pnl = 120 * 10 = 1200  # ❌ 错误：这是卖出金额，不是盈亏
```

**实际应该**:
```python
pnl = (卖出价 - 平均成本) × 数量
pnl = (120 - 100) × 10 = 200  # ✅ 真实盈亏
```

#### 问题1.2: 买入时 pnl 永远是 0

```python
if action == "buy" and qty > 0:
    cost = price * qty
    if cash >= cost:
        cash -= cost
        position += qty
    # ❌ 没有设置pnl，默认为0
```

**影响**:
- 买入后立即持有期间的未实现盈亏无法体现
- 反思时无法评估买入时机的好坏

#### 问题1.3: 未跟踪平均成本

```python
position = 0  # ❌ 只记录股数，不记录成本基础
```

**缺失信息**:
- 分批买入时的平均成本
- 部分卖出后剩余持仓的成本基础
- 无法计算已实现vs未实现盈亏

---

## 🔍 问题2: _calculate_actual_returns() 的逻辑

### 当前代码（第218-237行）

```python
# 计算盈亏
if action == "buy":
    # 如果买入，计算持有收益
    pnl = (future_price - decision_price) * quantity
    pnl_pct = (future_price - decision_price) / decision_price if decision_price > 0 else 0
    
elif action == "sell":
    # 如果卖出，计算避免的损失（反向）
    avg_cost = account_snapshot.get("positions", {}).get(
        signal.get("ticker", ""), {}
    ).get("avg_cost", decision_price)
    pnl = (decision_price - future_price) * quantity  # ⚠️ 概念有争议
    pnl_pct = (decision_price - future_price) / decision_price if decision_price > 0 else 0
    
else:  # hold
    # 持有期间的未实现收益变化
    position = account_snapshot.get("positions", {}).get(signal.get("ticker", ""), {})
    if position:
        avg_cost = position.get("avg_cost", decision_price)
        shares = position.get("shares", 0)
        pnl = (future_price - avg_cost) * shares
        pnl_pct = (future_price - avg_cost) / avg_cost if avg_cost > 0 else 0
    else:
        pnl = 0
        pnl_pct = 0
```

### ⚠️ 潜在问题

#### 问题2.1: SELL的"避免损失"概念混淆

**当前逻辑**:
```python
# 假设: 持有成本$100，卖出$120，5天后跌到$110
pnl = (120 - 110) * qty = +$10  # "避免的损失"
```

**问题**:
- ✅ **合理性**: 如果未来下跌，卖出确实避免了损失
- ❌ **不合理**: 如果未来上涨到$130，卖出反而错失了收益
  ```python
  pnl = (120 - 130) * qty = -$10  # 负数表示"错失收益"
  ```
- ⚠️ **混淆性**: 与传统PnL定义不一致

**传统定义**:
```python
# 卖出的PnL应该是：卖出价 - 成本价
realized_pnl = (120 - 100) * qty = +$20
# 与未来价格无关
```

#### 问题2.2: BUY的未来收益评估合理性

**当前逻辑**:
```python
# 买入$100，5天后$120
pnl = (120 - 100) * qty = +$20  # 未实现盈亏
```

**评价**:
- ✅ **合理**: 用于评估买入时机是否正确
- ✅ **适用场景**: 反思学习（"5天后看，买得好/不好"）
- ⚠️ **局限**: 没有考虑交易成本、滑点

---

## 📐 标准的盈亏计算方法

### 方法1: 已实现盈亏（Realized P&L）

```python
def calculate_realized_pnl(sell_price, avg_cost, quantity):
    """卖出时的真实盈亏"""
    return (sell_price - avg_cost) * quantity

# 例子
avg_cost = 100
sell_price = 120
quantity = 10
realized_pnl = (120 - 100) * 10 = 200  # 已实现盈亏
```

### 方法2: 未实现盈亏（Unrealized P&L）

```python
def calculate_unrealized_pnl(current_price, avg_cost, position):
    """持仓的账面盈亏"""
    return (current_price - avg_cost) * position

# 例子
avg_cost = 100
current_price = 120
position = 10
unrealized_pnl = (120 - 100) * 10 = 200  # 未实现盈亏
```

### 方法3: 总盈亏（Total P&L）

```python
total_pnl = realized_pnl + unrealized_pnl
```

---

## 🔧 修复建议

### 修复1: backtest() 函数

```python
def backtest(trade_signals: List[Dict[str, Any]], price_data: pd.DataFrame, initial_cash: float = 100000):
    """改进的回测函数"""
    
    cash = initial_cash
    position = 0
    avg_cost = 0.0  # 🔑 新增：跟踪平均成本
    returns_losses = []
    equity_curve = []
    
    for idx, row in df.iterrows():
        action = str(row.get("signal", "hold")).lower()
        price = row.get("close")
        qty = row.get("quantity", 0)
        date = row.get("date")
        
        realized_pnl = 0      # 已实现盈亏
        unrealized_pnl = 0    # 未实现盈亏
        
        if price is None or pd.isna(price):
            # 价格缺失时跳过
            total_value = cash + position * (avg_cost if position > 0 else 0)
            equity_curve.append(total_value)
            returns_losses.append({
                "date": date,
                "action": action,
                "price": price,
                "quantity": qty,
                "cash": cash,
                "position": position,
                "avg_cost": avg_cost,
                "total_value": total_value,
                "realized_pnl": 0,
                "unrealized_pnl": 0,
            })
            continue

        # === BUY ===
        if action == "buy" and qty > 0:
            cost = price * qty
            if cash >= cost:
                # 更新平均成本
                if position > 0:
                    avg_cost = (avg_cost * position + price * qty) / (position + qty)
                else:
                    avg_cost = price
                
                cash -= cost
                position += qty
                realized_pnl = 0  # 买入时无已实现盈亏
        
        # === SELL ===
        elif action == "sell" and qty > 0:
            if position >= qty:
                # 🔑 计算真实盈亏
                realized_pnl = (price - avg_cost) * qty
                
                cash += price * qty
                position -= qty
                
                # 卖光后重置成本
                if position == 0:
                    avg_cost = 0.0
        
        # === HOLD 或其他 ===
        # 不做操作
        
        # 计算未实现盈亏
        if position > 0:
            unrealized_pnl = (price - avg_cost) * position
        
        # 总市值
        total_value = cash + position * price
        equity_curve.append(total_value)
        
        returns_losses.append({
            'date': date,
            'action': action,
            'price': price,
            'quantity': qty,
            'cash': cash,
            'position': position,
            'avg_cost': avg_cost,
            'total_value': total_value,
            'realized_pnl': realized_pnl,        # 🔑 已实现
            'unrealized_pnl': unrealized_pnl,    # 🔑 未实现
            'total_pnl': realized_pnl + unrealized_pnl,  # 🔑 总盈亏
        })
    
    returns_df = pd.DataFrame(returns_losses)
    
    # 计算累计已实现盈亏
    returns_df['cumulative_realized_pnl'] = returns_df['realized_pnl'].cumsum()
    
    summary = {
        'final_value': equity_curve[-1] if equity_curve else initial_cash,
        'total_return': (equity_curve[-1] - initial_cash) / initial_cash if equity_curve else 0,
        'total_realized_pnl': returns_df['realized_pnl'].sum(),
        'final_unrealized_pnl': unrealized_pnl,
        'max_drawdown': _calculate_max_drawdown(equity_curve),
    }
    
    return returns_df, summary

def _calculate_max_drawdown(equity_curve: List[float]) -> float:
    """计算最大回撤"""
    if not equity_curve:
        return 0.0
    
    peak = equity_curve[0]
    max_dd = 0.0
    
    for value in equity_curve:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak
        if drawdown > max_dd:
            max_dd = drawdown
    
    return max_dd
```

### 修复2: _calculate_actual_returns() 函数

```python
def _calculate_actual_returns(
    self,
    trade_signals: List[Dict[str, Any]],
    future_prices: pd.DataFrame,
    account_snapshot: Dict[str, Any]
) -> pd.DataFrame:
    """改进的实际收益计算"""
    
    if not trade_signals or future_prices.empty:
        return pd.DataFrame()
    
    # 确保日期列格式统一
    if 'date' not in future_prices.columns and 'Date' in future_prices.columns:
        future_prices = future_prices.rename(columns={'Date': 'date'})
    
    returns_list = []
    
    for signal in trade_signals:
        signal_date = signal.get("date")
        action = signal.get("signal", "").lower()
        quantity = signal.get("quantity", 0)
        ticker = signal.get("ticker", "")
        
        # 查找信号日期及之后的价格
        matching_prices = future_prices[future_prices["date"] >= signal_date].sort_values("date")
        
        if matching_prices.empty:
            continue
        
        # 决策时的价格
        decision_price = signal.get("reference_price", 0) or matching_prices.iloc[0]["close"]
        
        # 未来价格（lookforward期间的最后价格）
        if len(matching_prices) > 1:
            future_price = matching_prices.iloc[-1]["close"]
        else:
            future_price = decision_price
        
        # 获取持仓信息
        position = account_snapshot.get("positions", {}).get(ticker, {})
        avg_cost = position.get("avg_cost", decision_price) if position else decision_price
        
        # 🔑 改进的盈亏计算
        if action == "buy":
            # BUY: 评估买入后的表现
            # 方案A: 未实现盈亏（持有到future_price）
            unrealized_pnl = (future_price - decision_price) * quantity
            
            # 方案B: 机会成本（如果不买会怎样）
            opportunity_cost = 0  # 不买则资金闲置，无收益
            
            pnl = unrealized_pnl
            pnl_pct = (future_price - decision_price) / decision_price if decision_price > 0 else 0
            pnl_type = "unrealized_gain" if pnl > 0 else "unrealized_loss"
            
        elif action == "sell":
            # SELL: 评估卖出决策的合理性
            
            # 🔑 方案1: 已实现盈亏（传统定义）
            realized_pnl = (decision_price - avg_cost) * quantity
            
            # 🔑 方案2: 机会成本（卖出后的价格变化）
            opportunity_cost = (future_price - decision_price) * quantity
            # > 0: 卖早了（后续上涨）
            # < 0: 卖对了（后续下跌，避免损失）
            
            # 综合评估
            pnl = realized_pnl  # 主要指标：实际赚了多少
            pnl_pct = (decision_price - avg_cost) / avg_cost if avg_cost > 0 else 0
            
            # 额外信息
            sell_timing_score = -opportunity_cost  # 负数表示卖得好
            pnl_type = "realized_gain" if pnl > 0 else "realized_loss"
            
        else:  # HOLD
            # HOLD: 评估持有期间的表现
            if position:
                shares = position.get("shares", 0)
                unrealized_pnl = (future_price - avg_cost) * shares
                pnl_pct = (future_price - avg_cost) / avg_cost if avg_cost > 0 else 0
                pnl = unrealized_pnl
                pnl_type = "unrealized_gain" if pnl > 0 else "unrealized_loss"
            else:
                # 无持仓，HOLD就是什么都不做
                pnl = 0
                pnl_pct = 0
                pnl_type = "no_position"
        
        result = {
            "date": signal_date,
            "action": action,
            "decision_price": decision_price,
            "future_price": future_price,
            "avg_cost": avg_cost,
            "quantity": quantity,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "pnl_type": pnl_type,
            "evaluation_method": "actual_future_performance"
        }
        
        # 卖出时添加额外信息
        if action == "sell":
            result["realized_pnl"] = realized_pnl
            result["opportunity_cost"] = opportunity_cost
            result["sell_timing_score"] = sell_timing_score
        
        returns_list.append(result)
    
    return pd.DataFrame(returns_list)
```

---

## 📊 对比表格

| 场景 | 旧逻辑 | 问题 | 新逻辑 | 改进 |
|------|--------|------|--------|------|
| **BUY** | pnl=0 | ❌ 无法评估买入表现 | pnl=(未来价-买入价)×qty | ✅ 评估买入时机 |
| **SELL** | pnl=卖出金额 | ❌ 不是真实盈亏 | pnl=(卖出价-成本)×qty | ✅ 真实已实现盈亏 |
| **HOLD** | pnl=0 (无持仓时) | ⚠️ 合理但信息少 | pnl=(当前价-成本)×持仓 | ✅ 未实现盈亏 |
| **平均成本** | 未跟踪 | ❌ 无法正确计算 | 动态更新 | ✅ 准确计算 |
| **分批交易** | 不支持 | ❌ 成本基础错误 | 加权平均 | ✅ 正确处理 |

---

## 🎯 建议优先级

### 🔴 高优先级（必须修复）

1. **backtest() 中的 SELL pnl计算**
   - 当前: `pnl = price * qty` (错误)
   - 应改为: `pnl = (price - avg_cost) * qty`

2. **跟踪平均成本**
   - 当前: 只记录position数量
   - 应添加: `avg_cost` 变量并动态更新

### 🟡 中优先级（建议改进）

3. **BUY 时的 pnl 计算**
   - 当前: 默认为0
   - 建议: 计算未实现盈亏（用于评估）

4. **区分已实现/未实现盈亏**
   - 当前: 只有一个pnl字段
   - 建议: 分为 `realized_pnl` 和 `unrealized_pnl`

### 🟢 低优先级（可选优化）

5. **SELL 的机会成本分析**
   - 当前: 没有
   - 建议: 添加 `opportunity_cost` 字段评估卖出时机

6. **最大回撤计算优化**
   - 当前: 简单的 max-min
   - 建议: 从峰值计算真实回撤

---

## 💡 总结

### 主要不合理之处

1. ❌ **SELL的pnl只是卖出金额，不是真实盈亏**
2. ❌ **未跟踪平均成本，无法正确计算盈亏**
3. ⚠️ **BUY时pnl=0，无法评估买入表现**
4. ⚠️ **混淆已实现vs未实现盈亏**
5. ⚠️ **延迟反思中SELL的"避免损失"概念不标准**

### 修复后的好处

- ✅ 准确计算真实盈亏（已实现+未实现）
- ✅ 支持分批买入/卖出
- ✅ 正确评估交易决策质量
- ✅ 为反思提供可靠的数据基础
- ✅ 符合金融行业标准

### 下一步

建议按优先级修复，先修复 **高优先级** 的关键bug，再逐步完善其他功能。

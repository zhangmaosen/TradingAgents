import pandas as pd
from typing import List, Dict, Any, Tuple

def backtest(trade_signals: List[Dict[str, Any]], price_data: pd.DataFrame, initial_cash: float = 100000) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    简单回测主循环：根据交易信号和历史价格，计算每步收益/损失。
    
    trade_signals: List[Dict]，每个dict包含日期、信号（'buy'/'sell'/'hold'）、数量等
    price_data: DataFrame，包含日期和价格（如收盘价）
    initial_cash: 初始资金
    返回: returns_losses（DataFrame），以及整体统计结果（dict）
    """
    if not trade_signals:
        summary = {
            "final_value": initial_cash,
            "total_return": 0.0,
            "max_drawdown": 0.0,
        }
        return pd.DataFrame(), summary

    # 合并信号和价格数据
    df_signals = pd.DataFrame(trade_signals)
    if "date" not in df_signals.columns:
        raise ValueError("trade_signals 缺少 date 字段")
    price_df = price_data.rename(columns={"Date": "date", "Close": "close"})
    df = pd.merge(df_signals, price_df, on="date", how="left")
    
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
        
        realized_pnl = 0      # 已实现盈亏（卖出时）
        unrealized_pnl = 0    # 未实现盈亏（持仓账面）
        
        if price is None or pd.isna(price):
            # 价格缺失时，使用上次已知价格估算
            total_value = cash + position * (avg_cost if position > 0 else 0)
            equity_curve.append(total_value)
            returns_losses.append(
                {
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
                    "total_pnl": 0,
                }
            )
            continue

        # === BUY ===
        if action == "buy" and qty > 0:
            cost = price * qty
            if cash >= cost:
                # 🔑 更新平均成本（加权平均）
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
                # 🔑 修复：计算真实已实现盈亏
                realized_pnl = (price - avg_cost) * qty
                
                cash += price * qty
                position -= qty
                
                # 全部卖出后重置成本
                if position == 0:
                    avg_cost = 0.0
        
        # === HOLD 或其他 ===
        # 不做操作
        
        # 🔑 计算未实现盈亏（当前持仓的账面盈亏）
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
            'realized_pnl': realized_pnl,        # 🔑 已实现盈亏
            'unrealized_pnl': unrealized_pnl,    # 🔑 未实现盈亏
            'total_pnl': realized_pnl + unrealized_pnl,  # 🔑 总盈亏
        })
    
    returns_df = pd.DataFrame(returns_losses)
    
    # 🔑 计算累计已实现盈亏
    if not returns_df.empty:
        returns_df['cumulative_realized_pnl'] = returns_df['realized_pnl'].cumsum()
    
    # 🔑 改进的统计摘要
    summary = {
        'final_value': equity_curve[-1] if equity_curve else initial_cash,
        'total_return': (equity_curve[-1] - initial_cash) / initial_cash if equity_curve else 0,
        'total_realized_pnl': returns_df['realized_pnl'].sum() if not returns_df.empty else 0,
        'final_unrealized_pnl': unrealized_pnl if 'unrealized_pnl' in locals() else 0,
        'max_drawdown': _calculate_max_drawdown(equity_curve),
        'total_trades': len([r for r in returns_losses if r['action'] in ['buy', 'sell']]),
        'winning_trades': len([r for r in returns_losses if r.get('realized_pnl', 0) > 0]),
        'losing_trades': len([r for r in returns_losses if r.get('realized_pnl', 0) < 0]),
    }
    
    return returns_df, summary


def _calculate_max_drawdown(equity_curve: list) -> float:
    """
    计算最大回撤
    
    最大回撤 = (峰值 - 谷值) / 峰值
    """
    if not equity_curve or len(equity_curve) == 0:
        return 0.0
    
    peak = equity_curve[0]
    max_dd = 0.0
    
    for value in equity_curve:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak if peak > 0 else 0
        if drawdown > max_dd:
            max_dd = drawdown
    
    return max_dd

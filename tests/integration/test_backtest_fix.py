#!/usr/bin/env python3
"""
回测函数修复验证脚本
"""

import sys
from pathlib import Path
import pandas as pd

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tradingagents.graph.performance_calculator import backtest, _calculate_max_drawdown


def test_basic_buy_sell():
    """测试基本的买入卖出场景"""
    print("=" * 60)
    print("测试1: 基本买入卖出盈亏计算")
    print("=" * 60)
    
    # 构造测试数据
    trade_signals = [
        {"date": "2025-10-01", "signal": "buy", "quantity": 10},
        {"date": "2025-10-05", "signal": "sell", "quantity": 10},
    ]
    
    price_data = pd.DataFrame({
        "date": ["2025-10-01", "2025-10-05"],
        "close": [100.0, 120.0]  # 买入$100，卖出$120
    })
    
    returns_df, summary = backtest(trade_signals, price_data, initial_cash=10000)
    
    print("\n交易记录:")
    print(returns_df[['date', 'action', 'price', 'quantity', 'avg_cost', 'realized_pnl', 'unrealized_pnl']])
    
    # 验证结果
    buy_row = returns_df[returns_df['action'] == 'buy'].iloc[0]
    sell_row = returns_df[returns_df['action'] == 'sell'].iloc[0]
    
    print(f"\n买入时:")
    print(f"  价格: ${buy_row['price']:.2f}")
    print(f"  数量: {buy_row['quantity']}")
    print(f"  平均成本: ${buy_row['avg_cost']:.2f}")
    print(f"  已实现盈亏: ${buy_row['realized_pnl']:.2f}")
    
    print(f"\n卖出时:")
    print(f"  价格: ${sell_row['price']:.2f}")
    print(f"  数量: {sell_row['quantity']}")
    print(f"  平均成本: ${sell_row['avg_cost']:.2f}")
    print(f"  已实现盈亏: ${sell_row['realized_pnl']:.2f} ✓")
    
    # 验证盈亏计算
    expected_pnl = (120 - 100) * 10
    actual_pnl = sell_row['realized_pnl']
    
    assert abs(actual_pnl - expected_pnl) < 0.01, f"盈亏计算错误: 期望{expected_pnl}, 实际{actual_pnl}"
    
    print(f"\n✅ 盈亏计算正确: (120 - 100) × 10 = ${expected_pnl:.2f}")
    
    print(f"\n统计摘要:")
    print(f"  总收益: ${summary['total_realized_pnl']:.2f}")
    print(f"  收益率: {summary['total_return']:.2%}")
    print(f"  最大回撤: {summary['max_drawdown']:.2%}")
    

def test_multiple_buys():
    """测试分批买入的平均成本计算"""
    print("\n" + "=" * 60)
    print("测试2: 分批买入的平均成本")
    print("=" * 60)
    
    trade_signals = [
        {"date": "2025-10-01", "signal": "buy", "quantity": 5},   # $100 × 5
        {"date": "2025-10-03", "signal": "buy", "quantity": 5},   # $120 × 5
        {"date": "2025-10-05", "signal": "sell", "quantity": 10}, # $130 × 10
    ]
    
    price_data = pd.DataFrame({
        "date": ["2025-10-01", "2025-10-03", "2025-10-05"],
        "close": [100.0, 120.0, 130.0]
    })
    
    returns_df, summary = backtest(trade_signals, price_data, initial_cash=20000)
    
    print("\n交易记录:")
    print(returns_df[['date', 'action', 'price', 'quantity', 'avg_cost', 'position', 'realized_pnl']])
    
    # 验证平均成本
    buy1 = returns_df[returns_df['date'] == '2025-10-01'].iloc[0]
    buy2 = returns_df[returns_df['date'] == '2025-10-03'].iloc[0]
    sell = returns_df[returns_df['date'] == '2025-10-05'].iloc[0]
    
    print(f"\n第一次买入:")
    print(f"  价格: ${buy1['price']:.2f}, 数量: {buy1['quantity']}, 平均成本: ${buy1['avg_cost']:.2f}")
    
    print(f"\n第二次买入:")
    print(f"  价格: ${buy2['price']:.2f}, 数量: {buy2['quantity']}, 持仓: {buy2['position']}")
    print(f"  平均成本: ${buy2['avg_cost']:.2f} = (100×5 + 120×5) / 10")
    
    expected_avg_cost = (100 * 5 + 120 * 5) / 10
    assert abs(buy2['avg_cost'] - expected_avg_cost) < 0.01, f"平均成本错误"
    
    print(f"\n卖出:")
    print(f"  价格: ${sell['price']:.2f}, 数量: {sell['quantity']}")
    print(f"  已实现盈亏: ${sell['realized_pnl']:.2f} = (130 - 110) × 10")
    
    expected_pnl = (130 - 110) * 10
    actual_pnl = sell['realized_pnl']
    assert abs(actual_pnl - expected_pnl) < 0.01, f"盈亏计算错误"
    
    print(f"\n✅ 分批买入平均成本计算正确!")


def test_partial_sell():
    """测试部分卖出"""
    print("\n" + "=" * 60)
    print("测试3: 部分卖出")
    print("=" * 60)
    
    trade_signals = [
        {"date": "2025-10-01", "signal": "buy", "quantity": 10},  # $100 × 10
        {"date": "2025-10-03", "signal": "sell", "quantity": 5},  # $120 × 5 (部分卖出)
        {"date": "2025-10-05", "signal": "sell", "quantity": 5},  # $140 × 5 (剩余卖出)
    ]
    
    price_data = pd.DataFrame({
        "date": ["2025-10-01", "2025-10-03", "2025-10-05"],
        "close": [100.0, 120.0, 140.0]
    })
    
    returns_df, summary = backtest(trade_signals, price_data, initial_cash=5000)
    
    print("\n交易记录:")
    print(returns_df[['date', 'action', 'price', 'quantity', 'avg_cost', 'position', 'realized_pnl', 'unrealized_pnl']])
    
    sell1 = returns_df[returns_df['date'] == '2025-10-03'].iloc[0]
    sell2 = returns_df[returns_df['date'] == '2025-10-05'].iloc[0]
    
    print(f"\n第一次卖出 (部分):")
    print(f"  已实现盈亏: ${sell1['realized_pnl']:.2f} = (120 - 100) × 5")
    print(f"  剩余持仓: {sell1['position']} 股")
    print(f"  未实现盈亏: ${sell1['unrealized_pnl']:.2f} = (120 - 100) × 5")
    
    print(f"\n第二次卖出 (全部清仓):")
    print(f"  已实现盈亏: ${sell2['realized_pnl']:.2f} = (140 - 100) × 5")
    print(f"  剩余持仓: {sell2['position']} 股")
    print(f"  未实现盈亏: ${sell2['unrealized_pnl']:.2f}")
    
    total_realized = sell1['realized_pnl'] + sell2['realized_pnl']
    expected_total = (120 - 100) * 5 + (140 - 100) * 5
    
    print(f"\n总已实现盈亏: ${total_realized:.2f}")
    print(f"期望值: ${expected_total:.2f}")
    
    assert abs(total_realized - expected_total) < 0.01, "部分卖出盈亏计算错误"
    
    print(f"\n✅ 部分卖出计算正确!")


def test_hold_unrealized_pnl():
    """测试持有期间的未实现盈亏"""
    print("\n" + "=" * 60)
    print("测试4: 持有期间的未实现盈亏")
    print("=" * 60)
    
    trade_signals = [
        {"date": "2025-10-01", "signal": "buy", "quantity": 10},
        {"date": "2025-10-02", "signal": "hold", "quantity": 0},
        {"date": "2025-10-03", "signal": "hold", "quantity": 0},
    ]
    
    price_data = pd.DataFrame({
        "date": ["2025-10-01", "2025-10-02", "2025-10-03"],
        "close": [100.0, 110.0, 120.0]
    })
    
    returns_df, summary = backtest(trade_signals, price_data, initial_cash=5000)
    
    print("\n交易记录:")
    print(returns_df[['date', 'action', 'price', 'avg_cost', 'position', 'unrealized_pnl']])
    
    for idx, row in returns_df.iterrows():
        print(f"\n{row['date']} - {row['action'].upper()}:")
        print(f"  价格: ${row['price']:.2f}")
        print(f"  持仓: {row['position']} 股")
        print(f"  未实现盈亏: ${row['unrealized_pnl']:.2f}")
    
    # 验证最后一天的未实现盈亏
    last_row = returns_df.iloc[-1]
    expected_unrealized = (120 - 100) * 10
    
    assert abs(last_row['unrealized_pnl'] - expected_unrealized) < 0.01, "未实现盈亏计算错误"
    
    print(f"\n✅ 未实现盈亏计算正确: (120 - 100) × 10 = ${expected_unrealized:.2f}")


def test_max_drawdown():
    """测试最大回撤计算"""
    print("\n" + "=" * 60)
    print("测试5: 最大回撤计算")
    print("=" * 60)
    
    equity_curve = [10000, 12000, 11000, 13000, 9000, 10000]
    # 最高峰值是13000（不是12000）
    # 从13000跌到9000，回撤 = (13000-9000)/13000 ≈ 30.77%
    
    max_dd = _calculate_max_drawdown(equity_curve)
    expected_dd = (13000 - 9000) / 13000  # 正确的计算
    
    print(f"\n权益曲线: {equity_curve}")
    print(f"峰值: $13000, 谷值: $9000")
    print(f"最大回撤: {max_dd:.2%}")
    print(f"期望值: {expected_dd:.2%}")
    
    assert abs(max_dd - expected_dd) < 0.0001, "最大回撤计算错误"
    
    print(f"\n✅ 最大回撤计算正确!")


def test_old_vs_new():
    """对比修复前后的差异"""
    print("\n" + "=" * 60)
    print("测试6: 修复前后对比")
    print("=" * 60)
    
    trade_signals = [
        {"date": "2025-10-01", "signal": "buy", "quantity": 10},
        {"date": "2025-10-05", "signal": "sell", "quantity": 10},
    ]
    
    price_data = pd.DataFrame({
        "date": ["2025-10-01", "2025-10-05"],
        "close": [100.0, 120.0]
    })
    
    returns_df, summary = backtest(trade_signals, price_data, initial_cash=10000)
    
    sell_row = returns_df[returns_df['action'] == 'sell'].iloc[0]
    
    print("\n修复前的逻辑:")
    print(f"  pnl = price × qty = 120 × 10 = $1200 ❌ (错误: 这是卖出金额)")
    
    print("\n修复后的逻辑:")
    print(f"  realized_pnl = (sell_price - avg_cost) × qty")
    print(f"  realized_pnl = (120 - 100) × 10 = ${sell_row['realized_pnl']:.2f} ✅")
    
    print("\n修复带来的改进:")
    print("  ✅ 准确计算真实盈亏")
    print("  ✅ 跟踪平均成本")
    print("  ✅ 区分已实现/未实现盈亏")
    print("  ✅ 支持分批买入/卖出")
    print("  ✅ 正确计算最大回撤")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🔍 回测函数修复验证")
    print("=" * 60)
    
    try:
        test_basic_buy_sell()
        test_multiple_buys()
        test_partial_sell()
        test_hold_unrealized_pnl()
        test_max_drawdown()
        test_old_vs_new()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！修复成功！")
        print("=" * 60)
        print("\n修复内容:")
        print("  1. ✅ 添加了平均成本跟踪")
        print("  2. ✅ 修正了SELL的盈亏计算")
        print("  3. ✅ 区分了已实现/未实现盈亏")
        print("  4. ✅ 改进了最大回撤计算")
        print("  5. ✅ 添加了更多统计指标")
        print("\n详细分析文档: docs/backtest_pnl_analysis.md")
        
    except AssertionError as e:
        print("\n" + "=" * 60)
        print(f"❌ 测试失败: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ 运行错误: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

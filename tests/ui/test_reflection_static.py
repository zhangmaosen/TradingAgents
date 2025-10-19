#!/usr/bin/env python3
"""
简单的反思布局测试 - 静态快照
"""
from rich.console import Console
import cli.main

console = Console()

# 使用全局消息缓冲区
message_buffer = cli.main.message_buffer

# 添加模拟反思数据
console.print("[yellow]添加模拟反思数据...[/yellow]")
message_buffer.add_reflection(
    ticker="AAPL",
    date="2025-10-10",
    action="BUY",
    actual_return=0.15,
    lesson="✓ 决策成功：利用市场低迷买入，获得15%收益"
)

message_buffer.add_reflection(
    ticker="TSLA",
    date="2025-10-11",
    action="SELL",
    actual_return=-0.08,
    lesson="✗ 决策失败：过早卖出，错过反弹机会"
)

message_buffer.add_reflection(
    ticker="NVDA",
    date="2025-10-12",
    action="HOLD",
    actual_return=0.03,
    lesson="→ 决策平庸：持有期间小幅上涨3%"
)

message_buffer.add_reflection(
    ticker="META",
    date="2025-10-13",
    action="BUY",
    actual_return=0.22,
    lesson="✓ 决策成功：把握财报利好，获得22%收益"
)

message_buffer.add_reflection(
    ticker="GOOGL",
    date="2025-10-14",
    action="SELL",
    actual_return=0.05,
    lesson="→ 决策平庸：小幅盈利5%后止盈"
)

message_buffer.add_reflection(
    ticker="MSFT",
    date="2025-10-15",
    action="BUY",
    actual_return=-0.12,
    lesson="✗ 决策失败：未能预测市场下跌，损失12%"
)

# 更新统计信息
message_buffer.update_reflection_stats({
    "total_reflections": 6,
    "successful_decisions": 2,
    "failed_decisions": 2,
    "pending_queue": 3,
    "avg_return": 0.042  # (0.15 - 0.08 + 0.03 + 0.22 + 0.05 - 0.12) / 6
})

# 添加一些消息
message_buffer.add_message("System", "测试反思布局显示功能")
message_buffer.add_message("Info", "当前有6条反思记录")
message_buffer.add_message("Reflection", "反思机制正常运行")

# 设置一些代理状态
message_buffer.update_agent_status("Market Analyst", "completed")
message_buffer.update_agent_status("Social Analyst", "completed")
message_buffer.update_agent_status("News Analyst", "in_progress")

# 创建并显示布局
console.print("\n[bold green]╔══════════════════════════════════════╗[/bold green]")
console.print("[bold green]║     反思布局显示测试 - 静态快照     ║[/bold green]")
console.print("[bold green]╚══════════════════════════════════════╝[/bold green]\n")

layout = cli.main.create_layout()
cli.main.update_display(layout)

# 渲染一次
console.print(layout)

console.print("\n[green]✓ 布局渲染完成！[/green]")
console.print(f"[cyan]反思记录数: {len(message_buffer.reflections)}[/cyan]")
console.print(f"[cyan]统计信息: {message_buffer.reflection_stats}[/cyan]")

#!/usr/bin/env python3
"""
测试反思布局显示
"""
import time
from rich.console import Console
from rich.live import Live
import cli.main

console = Console()

# 使用全局消息缓冲区
message_buffer = cli.main.message_buffer

# 添加一些模拟反思数据
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
    lesson="→ 决策平庸：持有期间小幅上涨"
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
    lesson="→ 决策平庸：小幅盈利后止盈"
)

# 更新统计信息
message_buffer.update_reflection_stats({
    "total_reflections": 5,
    "successful_decisions": 2,
    "failed_decisions": 1,
    "pending_queue": 3,
    "avg_return": 0.074  # (0.15 - 0.08 + 0.03 + 0.22 + 0.05) / 5
})

# 添加一些消息
message_buffer.add_message("System", "测试反思布局显示功能")
message_buffer.add_message("Info", "当前有5条反思记录")
message_buffer.add_message("Reflection", "反思机制正在运行...")

# 设置代理状态
message_buffer.update_agent_status("Market Analyst", "completed")
message_buffer.update_agent_status("Social Analyst", "in_progress")

# 创建布局
layout = cli.main.create_layout()

# 显示布局
console.print("\n[bold green]测试反思布局[/bold green]\n")
console.print("[yellow]提示：使用 Ctrl+C 退出[/yellow]\n")

try:
    with Live(layout, refresh_per_second=4, console=console) as live:
        for i in range(30):  # 运行30秒
            cli.main.update_display(layout, spinner_text=f"测试中... ({i+1}/30)")
            time.sleep(1)
            
            # 每5秒添加一条新反思
            if (i + 1) % 5 == 0:
                message_buffer.add_reflection(
                    ticker=f"TEST{i}",
                    date=f"2025-10-{15+i}",
                    action=["BUY", "SELL", "HOLD"][i % 3],
                    actual_return=(i % 3 - 1) * 0.05,  # -0.05, 0, 0.05
                    lesson=f"测试反思 #{i+1}"
                )
                message_buffer.add_message("Info", f"添加了新反思记录 (总计: {len(message_buffer.reflections)})")
                
    console.print("\n[green]✓ 布局测试完成！[/green]\n")
    
except KeyboardInterrupt:
    console.print("\n\n[yellow]测试已中断[/yellow]\n")

#!/usr/bin/env python3
"""
交易历史查看和分析工具
Usage: python -m cli.view_trades [options]
"""

import pandas as pd
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

app = typer.Typer(
    name="Trade History Viewer",
    help="查看和分析交易历史记录",
)
console = Console()


def load_trade_history(trade_file: Path = Path("results/trade_history.csv")):
    """加载交易历史记录"""
    if not trade_file.exists():
        console.print(f"[red]交易历史文件不存在: {trade_file}[/red]")
        return None
    
    df = pd.read_csv(trade_file)
    return df


@app.command()
def view(
    limit: int = typer.Option(20, "--limit", "-n", help="显示最近N条记录"),
    ticker: str = typer.Option(None, "--ticker", "-t", help="筛选特定股票"),
    action: str = typer.Option(None, "--action", "-a", help="筛选交易类型 (BUY/SELL/HOLD)"),
):
    """查看交易历史记录"""
    df = load_trade_history()
    if df is None or df.empty:
        console.print("[yellow]暂无交易记录[/yellow]")
        return
    
    # 应用筛选
    if ticker:
        df = df[df["ticker"].str.upper() == ticker.upper()]
    if action:
        df = df[df["action"].str.upper() == action.upper()]
    
    # 按时间排序并限制数量
    df = df.sort_values("timestamp", ascending=False).head(limit)
    
    # 创建展示表格
    table = Table(
        title=f"交易历史记录 (最近{len(df)}条)",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    
    table.add_column("时间", style="cyan", width=19)
    table.add_column("股票", style="green", width=8)
    table.add_column("日期", style="blue", width=10)
    table.add_column("操作", style="yellow", width=6)
    table.add_column("数量", justify="right", width=8)
    table.add_column("价格", justify="right", width=10)
    table.add_column("交易额", justify="right", width=12)
    table.add_column("现金变化", justify="right", width=12)
    table.add_column("持仓变化", justify="right", width=10)
    
    for _, row in df.iterrows():
        action_color = {
            "BUY": "[green]BUY[/green]",
            "SELL": "[red]SELL[/red]",
            "HOLD": "[yellow]HOLD[/yellow]",
        }.get(row["action"], row["action"])
        
        cash_change = row["cash_after"] - row["cash_before"]
        cash_change_str = f"${cash_change:+,.2f}" if cash_change != 0 else "-"
        
        position_change = row["position_after"] - row["position_before"]
        position_change_str = f"{position_change:+d}" if position_change != 0 else "-"
        
        table.add_row(
            row["timestamp"],
            row["ticker"],
            row["date"],
            action_color,
            str(row["quantity"]),
            f"${row['reference_price']:.2f}",
            f"${row['trade_value']:,.2f}",
            cash_change_str,
            position_change_str,
        )
    
    console.print(table)


@app.command()
def summary(
    ticker: str = typer.Option(None, "--ticker", "-t", help="筛选特定股票"),
):
    """交易统计摘要"""
    df = load_trade_history()
    if df is None or df.empty:
        console.print("[yellow]暂无交易记录[/yellow]")
        return
    
    # 应用筛选
    if ticker:
        df = df[df["ticker"].str.upper() == ticker.upper()]
        title_suffix = f" - {ticker.upper()}"
    else:
        title_suffix = ""
    
    # 统计各类交易
    buy_count = len(df[df["action"] == "BUY"])
    sell_count = len(df[df["action"] == "SELL"])
    hold_count = len(df[df["action"] == "HOLD"])
    
    buy_volume = df[df["action"] == "BUY"]["quantity"].sum()
    sell_volume = df[df["action"] == "SELL"]["quantity"].sum()
    
    buy_value = df[df["action"] == "BUY"]["trade_value"].sum()
    sell_value = df[df["action"] == "SELL"]["trade_value"].sum()
    
    # 创建统计表格
    stats_table = Table(
        title=f"交易统计摘要{title_suffix}",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    
    stats_table.add_column("指标", style="cyan")
    stats_table.add_column("买入 (BUY)", style="green", justify="right")
    stats_table.add_column("卖出 (SELL)", style="red", justify="right")
    stats_table.add_column("持有 (HOLD)", style="yellow", justify="right")
    
    stats_table.add_row(
        "交易次数",
        str(buy_count),
        str(sell_count),
        str(hold_count),
    )
    stats_table.add_row(
        "交易数量",
        f"{buy_volume:,} 股",
        f"{sell_volume:,} 股",
        "-",
    )
    stats_table.add_row(
        "交易金额",
        f"${buy_value:,.2f}",
        f"${sell_value:,.2f}",
        "-",
    )
    
    console.print(stats_table)
    
    # 按股票分组统计
    if not ticker:
        console.print("\n")
        ticker_table = Table(
            title="各股票交易统计",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
        )
        
        ticker_table.add_column("股票", style="cyan")
        ticker_table.add_column("买入次数", justify="right")
        ticker_table.add_column("卖出次数", justify="right")
        ticker_table.add_column("买入金额", justify="right")
        ticker_table.add_column("卖出金额", justify="right")
        ticker_table.add_column("净投入", justify="right")
        
        for ticker_name in df["ticker"].unique():
            ticker_df = df[df["ticker"] == ticker_name]
            t_buy = len(ticker_df[ticker_df["action"] == "BUY"])
            t_sell = len(ticker_df[ticker_df["action"] == "SELL"])
            t_buy_val = ticker_df[ticker_df["action"] == "BUY"]["trade_value"].sum()
            t_sell_val = ticker_df[ticker_df["action"] == "SELL"]["trade_value"].sum()
            net_investment = t_buy_val - t_sell_val
            
            ticker_table.add_row(
                ticker_name,
                str(t_buy),
                str(t_sell),
                f"${t_buy_val:,.2f}",
                f"${t_sell_val:,.2f}",
                f"${net_investment:+,.2f}",
            )
        
        console.print(ticker_table)


@app.command()
def export(
    output: str = typer.Option("trade_analysis.xlsx", "--output", "-o", help="输出文件名"),
    ticker: str = typer.Option(None, "--ticker", "-t", help="筛选特定股票"),
):
    """导出交易记录到Excel"""
    df = load_trade_history()
    if df is None or df.empty:
        console.print("[yellow]暂无交易记录[/yellow]")
        return
    
    if ticker:
        df = df[df["ticker"].str.upper() == ticker.upper()]
    
    try:
        df.to_excel(output, index=False, engine="openpyxl")
        console.print(f"[green]✓ 交易记录已导出到 {output}[/green]")
    except ImportError:
        console.print("[yellow]需要安装 openpyxl: pip install openpyxl[/yellow]")
        # 导出为CSV作为备选
        csv_output = output.replace(".xlsx", ".csv")
        df.to_csv(csv_output, index=False)
        console.print(f"[green]✓ 交易记录已导出到 {csv_output} (CSV格式)[/green]")
    except Exception as e:
        console.print(f"[red]导出失败: {e}[/red]")


@app.command()
def analyze(
    ticker: str = typer.Argument(..., help="要分析的股票代码"),
):
    """分析特定股票的交易表现"""
    df = load_trade_history()
    if df is None or df.empty:
        console.print("[yellow]暂无交易记录[/yellow]")
        return
    
    ticker = ticker.upper()
    df = df[df["ticker"] == ticker]
    
    if df.empty:
        console.print(f"[yellow]未找到 {ticker} 的交易记录[/yellow]")
        return
    
    # 计算持仓成本和盈亏
    console.print(f"\n[bold cyan]{ticker} 交易分析[/bold cyan]\n")
    
    # 交易时间线
    timeline_table = Table(
        title=f"{ticker} 交易时间线",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    
    timeline_table.add_column("日期", style="cyan")
    timeline_table.add_column("操作", style="yellow")
    timeline_table.add_column("数量", justify="right")
    timeline_table.add_column("价格", justify="right")
    timeline_table.add_column("持仓", justify="right")
    timeline_table.add_column("平均成本", justify="right")
    timeline_table.add_column("现金", justify="right")
    
    for _, row in df.sort_values("date").iterrows():
        action_color = {
            "BUY": "[green]买入[/green]",
            "SELL": "[red]卖出[/red]",
            "HOLD": "[yellow]持有[/yellow]",
        }.get(row["action"], row["action"])
        
        timeline_table.add_row(
            row["date"],
            action_color,
            str(row["quantity"]),
            f"${row['reference_price']:.2f}",
            f"{row['position_after']} 股",
            f"${row['avg_cost_after']:.2f}",
            f"${row['cash_after']:,.2f}",
        )
    
    console.print(timeline_table)
    
    # 统计摘要
    total_bought = df[df["action"] == "BUY"]["quantity"].sum()
    total_sold = df[df["action"] == "SELL"]["quantity"].sum()
    total_buy_value = df[df["action"] == "BUY"]["trade_value"].sum()
    total_sell_value = df[df["action"] == "SELL"]["trade_value"].sum()
    
    console.print("\n[bold]交易汇总:[/bold]")
    console.print(f"  累计买入: {total_bought} 股，金额 ${total_buy_value:,.2f}")
    console.print(f"  累计卖出: {total_sold} 股，金额 ${total_sell_value:,.2f}")
    console.print(f"  净持仓: {total_bought - total_sold} 股")
    if total_sold > 0:
        realized_pnl = total_sell_value - (total_sell_value / total_bought * total_buy_value if total_bought > 0 else 0)
        console.print(f"  已实现盈亏: ${realized_pnl:+,.2f}")


if __name__ == "__main__":
    app()

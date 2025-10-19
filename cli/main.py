from typing import Optional
import datetime
import copy
import typer
from pathlib import Path
from functools import wraps
from rich.console import Console
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.columns import Columns
from rich.markdown import Markdown
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
from rich.table import Table
from collections import deque
import time
from rich.tree import Tree
from rich import box
from rich.align import Align
from rich.rule import Rule

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from cli.models import AnalystType
from cli.utils import *

console = Console()

app = typer.Typer(
    name="TradingAgents",
    help="TradingAgents CLI: Multi-Agents LLM Financial Trading Framework",
    add_completion=True,  # Enable shell completion
)


# Create a deque to store recent messages with a maximum length
class MessageBuffer:
    def __init__(self, max_length=100):
        self.messages = deque(maxlen=max_length)
        self.tool_calls = deque(maxlen=max_length)
        self.current_report = None
        self.final_report = None  # Store the complete final report
        self.log_file = None
        self.report_dir = None
        self.agent_status = {
            # Analyst Team
            "Market Analyst": "pending",
            "Social Analyst": "pending",
            "News Analyst": "pending",
            "Fundamentals Analyst": "pending",
            # Research Team
            "Bull Researcher": "pending",
            "Bear Researcher": "pending",
            "Research Manager": "pending",
            # Trading Team
            "Trader": "pending",
            # Risk Management Team
            "Risky Analyst": "pending",
            "Neutral Analyst": "pending",
            "Safe Analyst": "pending",
            # Portfolio Management Team
            "Portfolio Manager": "pending",
        }
        self.current_agent = None
        self.report_sections = {
            "market_report": None,
            "sentiment_report": None,
            "news_report": None,
            "fundamentals_report": None,
            "investment_plan": None,
            "trader_investment_plan": None,
            "final_trade_decision": None,
        }
        # 反思和教训数据
        self.reflections = deque(maxlen=20)  # 存储最近的反思记录
        self.reflection_stats = {
            "total_reflections": 0,
            "successful_decisions": 0,
            "failed_decisions": 0,
            "pending_queue": 0,
            "avg_return": 0.0,
        }

    def add_message(self, message_type, content):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.messages.append((timestamp, message_type, content))

    def add_tool_call(self, tool_name, args):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.tool_calls.append((timestamp, tool_name, args))

    def update_agent_status(self, agent, status):
        if agent in self.agent_status:
            self.agent_status[agent] = status
            self.current_agent = agent

    def add_reflection(self, ticker, date, action, actual_return, lesson):
        """添加反思记录"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.reflections.append({
            "timestamp": timestamp,
            "ticker": ticker,
            "date": date,
            "action": action,
            "actual_return": actual_return,
            "lesson": lesson
        })
        
    def update_reflection_stats(self, stats):
        """更新反思统计信息"""
        self.reflection_stats.update(stats)

    def update_report_section(self, section_name, content):
        if section_name in self.report_sections:
            self.report_sections[section_name] = content
            self._update_current_report()

    def _update_current_report(self):
        # For the panel display, only show the most recently updated section
        latest_section = None
        latest_content = None

        # Find the most recently updated section
        for section, content in self.report_sections.items():
            if content is not None:
                latest_section = section
                latest_content = content
               
        if latest_section and latest_content:
            # Format the current section for display
            section_titles = {
                "market_report": "Market Analysis",
                "sentiment_report": "Social Sentiment",
                "news_report": "News Analysis",
                "fundamentals_report": "Fundamentals Analysis",
                "investment_plan": "Research Team Decision",
                "trader_investment_plan": "Trading Team Plan",
                "final_trade_decision": "Portfolio Management Decision",
            }
            self.current_report = (
                f"### {section_titles[latest_section]}\n{latest_content}"
            )

        # Update the final complete report
        self._update_final_report()

    def _update_final_report(self):
        report_parts = []

        # Analyst Team Reports
        if any(
            self.report_sections[section]
            for section in [
                "market_report",
                "sentiment_report",
                "news_report",
                "fundamentals_report",
            ]
        ):
            report_parts.append("## Analyst Team Reports")
            if self.report_sections["market_report"]:
                report_parts.append(
                    f"### Market Analysis\n{self.report_sections['market_report']}"
                )
            if self.report_sections["sentiment_report"]:
                report_parts.append(
                    f"### Social Sentiment\n{self.report_sections['sentiment_report']}"
                )
            if self.report_sections["news_report"]:
                report_parts.append(
                    f"### News Analysis\n{self.report_sections['news_report']}"
                )
            if self.report_sections["fundamentals_report"]:
                report_parts.append(
                    f"### Fundamentals Analysis\n{self.report_sections['fundamentals_report']}"
                )

        # Research Team Reports
        if self.report_sections["investment_plan"]:
            report_parts.append("## Research Team Decision")
            report_parts.append(f"{self.report_sections['investment_plan']}")

        # Trading Team Reports
        if self.report_sections["trader_investment_plan"]:
            report_parts.append("## Trading Team Plan")
            report_parts.append(f"{self.report_sections['trader_investment_plan']}")

        # Portfolio Management Decision
        if self.report_sections["final_trade_decision"]:
            report_parts.append("## Portfolio Management Decision")
            report_parts.append(f"{self.report_sections['final_trade_decision']}")

        self.final_report = "\n\n".join(report_parts) if report_parts else None


message_buffer = MessageBuffer()


def create_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3),
    )
    layout["main"].split_column(
        Layout(name="upper", ratio=3), 
        Layout(name="reflection", ratio=2),  # 新增反思区域
        Layout(name="analysis", ratio=5)
    )
    layout["upper"].split_row(
        Layout(name="progress", ratio=2), Layout(name="messages", ratio=3)
    )
    return layout


def update_display(layout, spinner_text=None):
    # Header with welcome message
    layout["header"].update(
        Panel(
            "[bold green]Welcome to TradingAgents CLI[/bold green]\n"
            "[dim]© [Tauric Research](https://github.com/TauricResearch)[/dim]",
            title="Welcome to TradingAgents",
            border_style="green",
            padding=(1, 2),
            expand=True,
        )
    )

    # Progress panel showing agent status
    progress_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        box=box.SIMPLE_HEAD,  # Use simple header with horizontal lines
        title=None,  # Remove the redundant Progress title
        padding=(0, 2),  # Add horizontal padding
        expand=True,  # Make table expand to fill available space
    )
    progress_table.add_column("Team", style="cyan", justify="center", width=20)
    progress_table.add_column("Agent", style="green", justify="center", width=20)
    progress_table.add_column("Status", style="yellow", justify="center", width=20)

    # Group agents by team
    teams = {
        "Analyst Team": [
            "Market Analyst",
            "Social Analyst",
            "News Analyst",
            "Fundamentals Analyst",
        ],
        "Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],
        "Trading Team": ["Trader"],
        "Risk Management": ["Risky Analyst", "Neutral Analyst", "Safe Analyst"],
        "Portfolio Management": ["Portfolio Manager"],
    }

    for team, agents in teams.items():
        # Add first agent with team name
        first_agent = agents[0]
        status = message_buffer.agent_status[first_agent]
        if status == "in_progress":
            spinner = Spinner(
                "dots", text="[blue]in_progress[/blue]", style="bold cyan"
            )
            status_cell = spinner
        else:
            status_color = {
                "pending": "yellow",
                "completed": "green",
                "error": "red",
            }.get(status, "white")
            status_cell = f"[{status_color}]{status}[/{status_color}]"
        progress_table.add_row(team, first_agent, status_cell)

        # Add remaining agents in team
        for agent in agents[1:]:
            status = message_buffer.agent_status[agent]
            if status == "in_progress":
                spinner = Spinner(
                    "dots", text="[blue]in_progress[/blue]", style="bold cyan"
                )
                status_cell = spinner
            else:
                status_color = {
                    "pending": "yellow",
                    "completed": "green",
                    "error": "red",
                }.get(status, "white")
                status_cell = f"[{status_color}]{status}[/{status_color}]"
            progress_table.add_row("", agent, status_cell)

        # Add horizontal line after each team
        progress_table.add_row("─" * 20, "─" * 20, "─" * 20, style="dim")

    layout["progress"].update(
        Panel(progress_table, title="Progress", border_style="cyan", padding=(1, 2))
    )

    # Messages panel showing recent messages and tool calls
    messages_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        expand=True,  # Make table expand to fill available space
        box=box.MINIMAL,  # Use minimal box style for a lighter look
        show_lines=True,  # Keep horizontal lines
        padding=(0, 1),  # Add some padding between columns
    )
    messages_table.add_column("Time", style="cyan", width=8, justify="center")
    messages_table.add_column("Type", style="green", width=10, justify="center")
    messages_table.add_column(
        "Content", style="white", no_wrap=False, ratio=1
    )  # Make content column expand

    # Combine tool calls and messages
    all_messages = []

    # Add tool calls
    for timestamp, tool_name, args in message_buffer.tool_calls:
        # Truncate tool call args if too long
        if isinstance(args, str) and len(args) > 100:
            args = args[:97] + "..."
        all_messages.append((timestamp, "Tool", f"{tool_name}: {args}"))

    # Add regular messages
    for timestamp, msg_type, content in message_buffer.messages:
        # Convert content to string if it's not already
        content_str = content
        if isinstance(content, list):
            # Handle list of content blocks (Anthropic format)
            text_parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                    elif item.get('type') == 'tool_use':
                        text_parts.append(f"[Tool: {item.get('name', 'unknown')}]")
                else:
                    text_parts.append(str(item))
            content_str = ' '.join(text_parts)
        elif not isinstance(content_str, str):
            content_str = str(content)
            
        # Truncate message content if too long
        if len(content_str) > 200:
            content_str = content_str[:197] + "..."
        all_messages.append((timestamp, msg_type, content_str))

    # Sort by timestamp
    all_messages.sort(key=lambda x: x[0])

    # Calculate how many messages we can show based on available space
    # Start with a reasonable number and adjust based on content length
    max_messages = 12  # Increased from 8 to better fill the space

    # Get the last N messages that will fit in the panel
    recent_messages = all_messages[-max_messages:]

    # Add messages to table
    for timestamp, msg_type, content in recent_messages:
        # Format content with word wrapping
        wrapped_content = Text(content, overflow="fold")
        messages_table.add_row(timestamp, msg_type, wrapped_content)

    if spinner_text:
        messages_table.add_row("", "Spinner", spinner_text)

    # Add a footer to indicate if messages were truncated
    if len(all_messages) > max_messages:
        messages_table.footer = (
            f"[dim]Showing last {max_messages} of {len(all_messages)} messages[/dim]"
        )

    layout["messages"].update(
        Panel(
            messages_table,
            title="Messages & Tools",
            border_style="blue",
            padding=(1, 2),
        )
    )

    # Reflection panel showing learnings and lessons
    if len(message_buffer.reflections) > 0:
        reflection_content = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE,
            expand=True,
            padding=(0, 1),
        )
        reflection_content.add_column("Time", style="cyan", width=8, justify="center")
        reflection_content.add_column("Ticker", style="green", width=8, justify="center")
        reflection_content.add_column("Action", style="yellow", width=8, justify="center")
        reflection_content.add_column("Return", style="white", width=10, justify="right")
        reflection_content.add_column("Lesson", style="white", ratio=1, no_wrap=False)

        # 显示最近的反思记录
        recent_reflections = list(message_buffer.reflections)[-6:]  # 显示最近6条
        for reflection in recent_reflections:
            return_value = reflection.get("actual_return", 0.0)
            return_color = "green" if return_value > 0 else "red" if return_value < 0 else "yellow"
            return_text = f"[{return_color}]{return_value:+.2%}[/{return_color}]"
            
            lesson_text = reflection.get("lesson", "N/A")
            if len(lesson_text) > 100:
                lesson_text = lesson_text[:97] + "..."
            
            reflection_content.add_row(
                reflection.get("timestamp", ""),
                reflection.get("ticker", ""),
                reflection.get("action", ""),
                return_text,
                Text(lesson_text, overflow="fold")
            )

        # 添加统计信息
        stats = message_buffer.reflection_stats
        stats_table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
        stats_table.add_column("Stat", style="dim", justify="left")
        stats_table.add_column("Value", justify="right")
        
        stats_table.add_row("总反思:", f"{stats.get('total_reflections', 0)}")
        stats_table.add_row("成功决策:", f"[green]{stats.get('successful_decisions', 0)}[/green]")
        stats_table.add_row("失败决策:", f"[red]{stats.get('failed_decisions', 0)}[/red]")
        stats_table.add_row("待处理:", f"[yellow]{stats.get('pending_queue', 0)}[/yellow]")
        
        avg_ret = stats.get('avg_return', 0.0)
        avg_color = "green" if avg_ret > 0 else "red" if avg_ret < 0 else "yellow"
        stats_table.add_row("平均收益:", f"[{avg_color}]{avg_ret:+.2%}[/{avg_color}]")

        reflection_panel = Panel(
            Columns([reflection_content, Panel(stats_table, title="统计", border_style="dim", padding=(1, 1))], equal=False, expand=True),
            title="Reflections & Lessons Learned",
            border_style="magenta",
            padding=(1, 2),
        )
    else:
        # 如果没有反思数据，显示占位信息
        reflection_panel = Panel(
            "[italic dim]等待反思数据...[/italic dim]",
            title="Reflections & Lessons Learned",
            border_style="magenta",
            padding=(1, 2),
        )

    layout["reflection"].update(reflection_panel)

    # Analysis panel showing current report
    if message_buffer.current_report:
        layout["analysis"].update(
            Panel(
                Markdown(message_buffer.current_report),
                title="Current Report",
                border_style="green",
                padding=(1, 2),
            )
        )
    else:
        layout["analysis"].update(
            Panel(
                "[italic]Waiting for analysis report...[/italic]",
                title="Current Report",
                border_style="green",
                padding=(1, 2),
            )
        )

    # Footer with statistics
    tool_calls_count = len(message_buffer.tool_calls)
    llm_calls_count = sum(
        1 for _, msg_type, _ in message_buffer.messages if msg_type == "Reasoning"
    )
    reports_count = sum(
        1 for content in message_buffer.report_sections.values() if content is not None
    )

    stats_table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
    stats_table.add_column("Stats", justify="center")
    stats_table.add_row(
        f"Tool Calls: {tool_calls_count} | LLM Calls: {llm_calls_count} | Generated Reports: {reports_count}"
    )

    layout["footer"].update(Panel(stats_table, border_style="grey50"))


def get_user_selections():
    """Get all user selections before starting the analysis display."""
    # Display ASCII art welcome message
    with open("./cli/static/welcome.txt", "r") as f:
        welcome_ascii = f.read()

    # Create welcome box content
    welcome_content = f"{welcome_ascii}\n"
    welcome_content += "[bold green]TradingAgents: Multi-Agents LLM Financial Trading Framework - CLI[/bold green]\n\n"
    welcome_content += "[bold]Workflow Steps:[/bold]\n"
    welcome_content += "I. Analyst Team → II. Research Team → III. Trader → IV. Risk Management → V. Portfolio Management\n\n"
    welcome_content += (
        "[dim]Built by [Tauric Research](https://github.com/TauricResearch)[/dim]"
    )

    # Create and center the welcome box
    welcome_box = Panel(
        welcome_content,
        border_style="green",
        padding=(1, 2),
        title="Welcome to TradingAgents",
        subtitle="Multi-Agents LLM Financial Trading Framework",
    )
    console.print(Align.center(welcome_box))
    console.print()  # Add a blank line after the welcome box

    # Create a boxed questionnaire for each step
    def create_question_box(title, prompt, default=None):
        box_content = f"[bold]{title}[/bold]\n"
        box_content += f"[dim]{prompt}[/dim]"
        if default:
            box_content += f"\n[dim]Default: {default}[/dim]"
        return Panel(box_content, border_style="blue", padding=(1, 2))

    # Step 1: Ticker symbols
    console.print(
        create_question_box(
            "Step 1: Ticker Symbols",
            "Enter the comma-separated ticker symbols to analyze",
            "AAPL,MSFT,GOOGL,AMZN,NVDA,META,TSLA",
        )
    )
    selected_tickers = get_tickers()

    # Step 2: Start date
    default_end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    default_start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    console.print(
        create_question_box(
            "Step 2: Start Date",
            "Enter the start date (YYYY-MM-DD)",
            default_start_date,
        )
    )
    start_date = get_date_input(default_start_date)
    start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()

    # Step 3: End date
    console.print(
        create_question_box(
            "Step 3: End Date",
            "Enter the end date (YYYY-MM-DD)",
            default_end_date,
        )
    )
    end_date = get_date_input(default_end_date, min_date=start_date_obj)

    console.print(
        f"[green]Selected tickers:[/green] {', '.join(selected_tickers)}"
    )
    console.print(f"[green]Date range:[/green] {start_date} → {end_date}")

    # Step 4: Select analysts
    console.print(
        create_question_box(
            "Step 4: Analysts Team", "Select your LLM analyst agents for the analysis"
        )
    )
    selected_analysts = select_analysts()
    console.print(
        f"[green]Selected analysts:[/green] {', '.join(analyst.value for analyst in selected_analysts)}"
    )

    # Step 5: Research depth
    console.print(
        create_question_box(
            "Step 5: Research Depth", "Select your research depth level"
        )
    )
    selected_research_depth = select_research_depth()

    # Step 6: OpenAI backend
    console.print(
        create_question_box(
            "Step 6: OpenAI backend", "Select which service to talk to"
        )
    )
    selected_llm_provider, backend_url = select_llm_provider()
    
    # Step 7: Thinking agents
    console.print(
        create_question_box(
            "Step 7: Thinking Agents", "Select your thinking agents for analysis"
        )
    )
    selected_shallow_thinker = select_shallow_thinking_agent(selected_llm_provider)
    selected_deep_thinker = select_deep_thinking_agent(selected_llm_provider)

    return {
        "tickers": selected_tickers,
        "start_date": start_date,
        "end_date": end_date,
        "analysts": selected_analysts,
        "research_depth": selected_research_depth,
        "llm_provider": selected_llm_provider.lower(),
        "backend_url": backend_url,
        "shallow_thinker": selected_shallow_thinker,
        "deep_thinker": selected_deep_thinker,
    }


def get_tickers():
    """Get list of ticker symbols from user input."""
    tickers_str = typer.prompt("", default="AAPL,MSFT,GOOGL,AMZN,NVDA,META,TSLA")
    tickers = [ticker.strip().upper() for ticker in tickers_str.split(",") if ticker.strip()]
    return tickers or ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]


def get_date_input(default_value, min_date=None):
    """Prompt user for a date string within constraints."""
    while True:
        date_str = typer.prompt("", default=default_value)
        try:
            parsed_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            console.print("[red]Error: Invalid date format. Please use YYYY-MM-DD[/red]")
            continue

        today = datetime.datetime.now().date()
        if parsed_date > today:
            console.print("[red]Error: Date cannot be in the future[/red]")
            continue

        if min_date and parsed_date < min_date:
            console.print(
                f"[red]Error: Date cannot be earlier than {min_date.isoformat()}[/red]"
            )
            continue

        return parsed_date.isoformat()


def display_complete_report(final_state):
    """Display the complete analysis report with team-based panels."""
    console.print("\n[bold green]Complete Analysis Report[/bold green]\n")

    # I. Analyst Team Reports
    analyst_reports = []

    # Market Analyst Report
    if final_state.get("market_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["market_report"]),
                title="Market Analyst",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # Social Analyst Report
    if final_state.get("sentiment_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["sentiment_report"]),
                title="Social Analyst",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # News Analyst Report
    if final_state.get("news_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["news_report"]),
                title="News Analyst",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # Fundamentals Analyst Report
    if final_state.get("fundamentals_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["fundamentals_report"]),
                title="Fundamentals Analyst",
                border_style="blue",
                padding=(1, 2),
            )
        )

    if analyst_reports:
        console.print(
            Panel(
                Columns(analyst_reports, equal=True, expand=True),
                title="I. Analyst Team Reports",
                border_style="cyan",
                padding=(1, 2),
            )
        )

    # II. Research Team Reports
    if final_state.get("investment_debate_state"):
        research_reports = []
        debate_state = final_state["investment_debate_state"]

        # Bull Researcher Analysis
        if debate_state.get("bull_history"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["bull_history"]),
                    title="Bull Researcher",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # Bear Researcher Analysis
        if debate_state.get("bear_history"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["bear_history"]),
                    title="Bear Researcher",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # Research Manager Decision
        if debate_state.get("judge_decision"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["judge_decision"]),
                    title="Research Manager",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        if research_reports:
            console.print(
                Panel(
                    Columns(research_reports, equal=True, expand=True),
                    title="II. Research Team Decision",
                    border_style="magenta",
                    padding=(1, 2),
                )
            )

    # III. Trading Team Reports
    if final_state.get("trader_investment_plan"):
        console.print(
            Panel(
                Panel(
                    Markdown(final_state["trader_investment_plan"]),
                    title="Trader",
                    border_style="blue",
                    padding=(1, 2),
                ),
                title="III. Trading Team Plan",
                border_style="yellow",
                padding=(1, 2),
            )
        )

    # IV. Risk Management Team Reports
    if final_state.get("risk_debate_state"):
        risk_reports = []
        risk_state = final_state["risk_debate_state"]

        # Aggressive (Risky) Analyst Analysis
        if risk_state.get("risky_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["risky_history"]),
                    title="Aggressive Analyst",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # Conservative (Safe) Analyst Analysis
        if risk_state.get("safe_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["safe_history"]),
                    title="Conservative Analyst",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # Neutral Analyst Analysis
        if risk_state.get("neutral_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["neutral_history"]),
                    title="Neutral Analyst",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        if risk_reports:
            console.print(
                Panel(
                    Columns(risk_reports, equal=True, expand=True),
                    title="IV. Risk Management Team Decision",
                    border_style="red",
                    padding=(1, 2),
                )
            )

        # V. Portfolio Manager Decision
        if risk_state.get("judge_decision"):
            console.print(
                Panel(
                    Panel(
                        Markdown(risk_state["judge_decision"]),
                        title="Portfolio Manager",
                        border_style="blue",
                        padding=(1, 2),
                    ),
                    title="V. Portfolio Manager Decision",
                    border_style="green",
                    padding=(1, 2),
                )
            )


def update_research_team_status(status):
    """Update status for all research team members and trader."""
    research_team = ["Bull Researcher", "Bear Researcher", "Research Manager", "Trader"]
    for agent in research_team:
        message_buffer.update_agent_status(agent, status)

def extract_content_string(content):
    """Extract string content from various message formats."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # Handle Anthropic's list format
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))
                elif item.get('type') == 'tool_use':
                    text_parts.append(f"[Tool: {item.get('name', 'unknown')}]")
            else:
                text_parts.append(str(item))
        return ' '.join(text_parts)
    else:
        return str(content)

def run_analysis():
    selections = get_user_selections()

    base_config = DEFAULT_CONFIG.copy()
    base_config["max_debate_rounds"] = selections["research_depth"]
    base_config["max_risk_discuss_rounds"] = selections["research_depth"]
    base_config["quick_think_llm"] = selections["shallow_thinker"]
    base_config["deep_think_llm"] = selections["deep_thinker"]
    base_config["backend_url"] = selections["backend_url"]
    base_config["llm_provider"] = selections["llm_provider"].lower()

    analyst_values = [analyst.value for analyst in selections["analysts"]]
    analyst_value_set = set(analyst_values)

    start_date_obj = datetime.datetime.strptime(selections["start_date"], "%Y-%m-%d").date()
    end_date_obj = datetime.datetime.strptime(selections["end_date"], "%Y-%m-%d").date()
    date_range = []
    current_date = start_date_obj
    while current_date <= end_date_obj:
        date_range.append(current_date.isoformat())
        current_date += datetime.timedelta(days=1)

    results_root = Path(base_config["results_dir"])
    results_root.mkdir(parents=True, exist_ok=True)

    # Load global account state if available
    account_file = results_root / "account_state.json"
    current_account_state = None
    account_notice = None
    if account_file.exists():
        try:
            import json
            with open(account_file, "r") as f:
                current_account_state = json.load(f)
            account_notice = ("System", f"已自动加载全局账户状态: {account_file}")
        except Exception as exc:
            account_notice = ("Error", f"全局账户状态加载失败: {exc}")

    account_notice_delivered = False

    # Prepare reusable graph to maintain reflection memory across runs
    graph = TradingAgentsGraph(analyst_values, config=copy.deepcopy(base_config), debug=True)

    def save_message_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            if not obj.messages:
                return
            log_file = getattr(obj, "log_file", None)
            if not log_file:
                return
            timestamp, message_type, content = obj.messages[-1]
            content = content.replace("\n", " ")
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [{message_type}] {content}\n")
        return wrapper
    
    def save_tool_call_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            if not obj.tool_calls:
                return
            log_file = getattr(obj, "log_file", None)
            if not log_file:
                return
            timestamp, tool_name, args = obj.tool_calls[-1]
            if isinstance(args, dict):
                args_str = ", ".join(f"{k}={v}" for k, v in args.items())
            else:
                args_str = str(args)
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [Tool Call] {tool_name}({args_str})\n")
        return wrapper

    def save_report_section_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(section_name, content):
            func(section_name, content)
            report_dir = getattr(obj, "report_dir", None)
            if not report_dir:
                return
            if section_name in obj.report_sections and obj.report_sections[section_name] is not None:
                section_content = obj.report_sections[section_name]
                if section_content:
                    file_name = f"{section_name}.md"
                    with open(report_dir / file_name, "w") as f:
                        f.write(section_content)
        return wrapper

    message_buffer.add_message = save_message_decorator(message_buffer, "add_message")
    message_buffer.add_tool_call = save_tool_call_decorator(message_buffer, "add_tool_call")
    message_buffer.update_report_section = save_report_section_decorator(message_buffer, "update_report_section")

    # Now start the display layout
    layout = create_layout()

    with Live(layout, refresh_per_second=4) as live:
        update_display(layout)

        total_runs = len(selections["tickers"]) * len(date_range)
        run_index = 0

        for ticker in selections["tickers"]:
            for analysis_date in date_range:
                run_index += 1

                graph.ticker = ticker

                results_dir = results_root / ticker / analysis_date
                results_dir.mkdir(parents=True, exist_ok=True)
                report_dir = results_dir / "reports"
                report_dir.mkdir(parents=True, exist_ok=True)
                log_file = results_dir / "message_tool.log"
                log_file.touch(exist_ok=True)

                message_buffer.log_file = log_file
                message_buffer.report_dir = report_dir

                message_buffer.messages.clear()
                message_buffer.tool_calls.clear()
                for agent in message_buffer.agent_status:
                    message_buffer.agent_status[agent] = "pending"
                for section in message_buffer.report_sections:
                    message_buffer.report_sections[section] = None
                message_buffer.current_report = None
                message_buffer.final_report = None

                update_display(layout)

                analyst_display = (
                    ", ".join(analyst.value for analyst in selections["analysts"])
                    if selections["analysts"]
                    else "N/A"
                )
                message_buffer.add_message("System", f"[{run_index}/{total_runs}] Ticker: {ticker}")
                message_buffer.add_message("System", f"Analysis date: {analysis_date}")
                message_buffer.add_message("System", f"Selected analysts: {analyst_display}")

                if not account_notice_delivered and account_notice:
                    message_buffer.add_message(account_notice[0], account_notice[1])
                    account_notice_delivered = True

                if current_account_state is not None:
                    message_buffer.add_message("System", "延续全局账户状态。")
                else:
                    message_buffer.add_message("System", "使用默认账户初始配置。")

                update_display(layout)

                if analyst_values:
                    first_analyst = f"{analyst_values[0].capitalize()} Analyst"
                    if first_analyst in message_buffer.agent_status:
                        message_buffer.update_agent_status(first_analyst, "in_progress")

                update_display(layout)

                spinner_text = f"Analyzing {ticker} on {analysis_date}..."
                update_display(layout, spinner_text)

                init_agent_state = graph.propagator.create_initial_state(ticker, analysis_date)
                if current_account_state is not None:
                    init_agent_state["account_state"] = copy.deepcopy(current_account_state)
                args = graph.propagator.get_graph_args()

                trace = []
                for chunk in graph.graph.stream(init_agent_state, **args):
                    if len(chunk["messages"]) > 0:
                        # Get the last message from the chunk
                        last_message = chunk["messages"][-1]

                        # Extract message content and type
                        if hasattr(last_message, "content"):
                            content = extract_content_string(last_message.content)
                            msg_type = "Reasoning"
                        else:
                            content = str(last_message)
                            msg_type = "System"

                        # Add message to buffer
                        message_buffer.add_message(msg_type, content)

                        # If it's a tool call, add it to tool calls
                        if hasattr(last_message, "tool_calls"):
                            for tool_call in last_message.tool_calls:
                                if isinstance(tool_call, dict):
                                    message_buffer.add_tool_call(
                                        tool_call["name"], tool_call["args"]
                                    )
                                else:
                                    message_buffer.add_tool_call(
                                        tool_call.name, tool_call.args
                                    )

                        # Update reports and agent status based on chunk content
                        if "market_report" in chunk and chunk["market_report"]:
                            message_buffer.update_report_section(
                                "market_report", chunk["market_report"]
                            )
                            message_buffer.update_agent_status(
                                "Market Analyst", "completed"
                            )
                            if "social" in analyst_value_set:
                                message_buffer.update_agent_status(
                                    "Social Analyst", "in_progress"
                                )

                        if "sentiment_report" in chunk and chunk["sentiment_report"]:
                            message_buffer.update_report_section(
                                "sentiment_report", chunk["sentiment_report"]
                            )
                            message_buffer.update_agent_status(
                                "Social Analyst", "completed"
                            )
                            if "news" in analyst_value_set:
                                message_buffer.update_agent_status(
                                    "News Analyst", "in_progress"
                                )

                        if "news_report" in chunk and chunk["news_report"]:
                            message_buffer.update_report_section(
                                "news_report", chunk["news_report"]
                            )
                            message_buffer.update_agent_status(
                                "News Analyst", "completed"
                            )
                            if "fundamentals" in analyst_value_set:
                                message_buffer.update_agent_status(
                                    "Fundamentals Analyst", "in_progress"
                                )

                        if "fundamentals_report" in chunk and chunk["fundamentals_report"]:
                            message_buffer.update_report_section(
                                "fundamentals_report", chunk["fundamentals_report"]
                            )
                            message_buffer.update_agent_status(
                                "Fundamentals Analyst", "completed"
                            )
                            update_research_team_status("in_progress")

                        if (
                            "investment_debate_state" in chunk
                            and chunk["investment_debate_state"]
                        ):
                            debate_state = chunk["investment_debate_state"]

                            if "bull_history" in debate_state and debate_state["bull_history"]:
                                update_research_team_status("in_progress")
                                bull_responses = debate_state["bull_history"].split("\n")
                                latest_bull = bull_responses[-1] if bull_responses else ""
                                if latest_bull:
                                    message_buffer.add_message("Reasoning", latest_bull)
                                    message_buffer.update_report_section(
                                        "investment_plan",
                                        f"### Bull Researcher Analysis\n{latest_bull}",
                                    )

                            if "bear_history" in debate_state and debate_state["bear_history"]:
                                update_research_team_status("in_progress")
                                bear_responses = debate_state["bear_history"].split("\n")
                                latest_bear = bear_responses[-1] if bear_responses else ""
                                if latest_bear:
                                    message_buffer.add_message("Reasoning", latest_bear)
                                    message_buffer.update_report_section(
                                        "investment_plan",
                                        f"{message_buffer.report_sections['investment_plan']}\n\n### Bear Researcher Analysis\n{latest_bear}",
                                    )

                            if (
                                "judge_decision" in debate_state
                                and debate_state["judge_decision"]
                            ):
                                update_research_team_status("in_progress")
                                message_buffer.add_message(
                                    "Reasoning",
                                    f"Research Manager: {debate_state['judge_decision']}",
                                )
                                message_buffer.update_report_section(
                                    "investment_plan",
                                    f"{message_buffer.report_sections['investment_plan']}\n\n### Research Manager Decision\n{debate_state['judge_decision']}",
                                )
                                update_research_team_status("completed")
                                message_buffer.update_agent_status(
                                    "Risky Analyst", "in_progress"
                                )

                        if (
                            "trader_investment_plan" in chunk
                            and chunk["trader_investment_plan"]
                        ):
                            message_buffer.update_report_section(
                                "trader_investment_plan", chunk["trader_investment_plan"]
                            )
                            message_buffer.update_agent_status(
                                "Risky Analyst", "in_progress"
                            )

                        if "risk_debate_state" in chunk and chunk["risk_debate_state"]:
                            risk_state = chunk["risk_debate_state"]

                            if (
                                "current_risky_response" in risk_state
                                and risk_state["current_risky_response"]
                            ):
                                message_buffer.update_agent_status(
                                    "Risky Analyst", "in_progress"
                                )
                                message_buffer.add_message(
                                    "Reasoning",
                                    f"Risky Analyst: {risk_state['current_risky_response']}",
                                )
                                message_buffer.update_report_section(
                                    "final_trade_decision",
                                    f"### Risky Analyst Analysis\n{risk_state['current_risky_response']}",
                                )

                            if (
                                "current_safe_response" in risk_state
                                and risk_state["current_safe_response"]
                            ):
                                message_buffer.update_agent_status(
                                    "Safe Analyst", "in_progress"
                                )
                                message_buffer.add_message(
                                    "Reasoning",
                                    f"Safe Analyst: {risk_state['current_safe_response']}",
                                )
                                message_buffer.update_report_section(
                                    "final_trade_decision",
                                    f"### Safe Analyst Analysis\n{risk_state['current_safe_response']}",
                                )

                            if (
                                "current_neutral_response" in risk_state
                                and risk_state["current_neutral_response"]
                            ):
                                message_buffer.update_agent_status(
                                    "Neutral Analyst", "in_progress"
                                )
                                message_buffer.add_message(
                                    "Reasoning",
                                    f"Neutral Analyst: {risk_state['current_neutral_response']}",
                                )
                                message_buffer.update_report_section(
                                    "final_trade_decision",
                                    f"### Neutral Analyst Analysis\n{risk_state['current_neutral_response']}",
                                )

                            if "judge_decision" in risk_state and risk_state["judge_decision"]:
                                message_buffer.update_agent_status(
                                    "Portfolio Manager", "in_progress"
                                )
                                message_buffer.add_message(
                                    "Reasoning",
                                    f"Portfolio Manager: {risk_state['judge_decision']}",
                                )
                                message_buffer.update_report_section(
                                    "final_trade_decision",
                                    f"### Portfolio Manager Decision\n{risk_state['judge_decision']}",
                                )
                                message_buffer.update_agent_status("Risky Analyst", "completed")
                                message_buffer.update_agent_status("Safe Analyst", "completed")
                                message_buffer.update_agent_status(
                                    "Neutral Analyst", "completed"
                                )
                                message_buffer.update_agent_status(
                                    "Portfolio Manager", "completed"
                                )

                        update_display(layout)

                    trace.append(chunk)

                if not trace:
                    message_buffer.add_message("Error", "分析流程未产生有效结果。")
                    update_display(layout)
                    continue

                final_state = trace[-1]
                trade_signals = graph.attach_trade_signals(final_state)
                decision = final_state.get("processed_trade_decision", "")
                graph.curr_state = final_state

                # 记录交易到全局交易日志
                if trade_signals:
                    trade_log_file = results_root / "trade_history.csv"
                    try:
                        import csv
                        import os
                        
                        # 检查文件是否存在，决定是否写入表头
                        file_exists = trade_log_file.exists()
                        
                        with open(trade_log_file, "a", newline="") as f:
                            fieldnames = [
                                "timestamp",
                                "ticker",
                                "date",
                                "action",
                                "quantity",
                                "reference_price",
                                "trade_value",
                                "cash_before",
                                "cash_after",
                                "position_before",
                                "position_after",
                                "avg_cost_before",
                                "avg_cost_after",
                                "notes"
                            ]
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            
                            if not file_exists:
                                writer.writeheader()
                            
                            for signal in trade_signals:
                                # 获取交易前后的账户信息
                                old_account = current_account_state or {}
                                new_account = final_state.get("account_state", {})
                                
                                old_positions = old_account.get("positions", {})
                                new_positions = new_account.get("positions", {})
                                
                                old_ticker_pos = old_positions.get(ticker, {})
                                new_ticker_pos = new_positions.get(ticker, {})
                                
                                trade_record = {
                                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "ticker": signal.get("ticker", ticker),
                                    "date": signal.get("date", analysis_date),
                                    "action": signal.get("action", "").upper(),
                                    "quantity": signal.get("quantity", 0),
                                    "reference_price": signal.get("reference_price", 0.0),
                                    "trade_value": signal.get("quantity", 0) * signal.get("reference_price", 0.0),
                                    "cash_before": old_account.get("cash_balance", 0.0),
                                    "cash_after": new_account.get("cash_balance", 0.0),
                                    "position_before": old_ticker_pos.get("shares", 0),
                                    "position_after": new_ticker_pos.get("shares", 0),
                                    "avg_cost_before": old_ticker_pos.get("avg_cost", 0.0),
                                    "avg_cost_after": new_ticker_pos.get("avg_cost", 0.0),
                                    "notes": signal.get("notes", "")[:200]  # 限制长度
                                }
                                writer.writerow(trade_record)
                        
                        message_buffer.add_message("System", f"交易记录已保存到 {trade_log_file}")
                    except Exception as exc:
                        message_buffer.add_message("Error", f"交易记录保存失败: {exc}")

                account_state = final_state.get("account_state")
                if account_state:
                    try:
                        import json
                        with open(account_file, "w") as f:
                            json.dump(account_state, f, ensure_ascii=False, indent=2)
                        message_buffer.add_message("System", f"全局账户状态已保存到 {account_file}")
                    except Exception as exc:
                        message_buffer.add_message("Error", f"全局账户状态保存失败: {exc}")
                    current_account_state = copy.deepcopy(account_state)

                for agent in message_buffer.agent_status:
                    message_buffer.update_agent_status(agent, "completed")

                decision_msg = decision if decision else "N/A"
                message_buffer.add_message(
                    "Analysis",
                    f"Completed analysis for {analysis_date} (decision: {decision_msg})",
                )

                for section in message_buffer.report_sections.keys():
                    if section in final_state:
                        message_buffer.update_report_section(section, final_state[section])

                display_complete_report(final_state)

                # ========== 延迟反思机制 ==========
                # 新逻辑：不再立即回测反思，而是：
                # 1. 保存当前决策到待反思队列
                # 2. 处理过去的待反思决策（已有足够未来数据）
                
                from tradingagents.graph.delayed_reflection import DelayedReflectionManager
                
                reflection_manager = DelayedReflectionManager()
                
                # 先处理历史待反思项（使用当前日期作为参考）
                try:
                    reflection_stats = reflection_manager.process_pending_reflections(
                        graph=graph,
                        current_date=analysis_date,
                        lookforward_days=base_config.get("reflection_lookforward_days", 5),
                        min_age_days=base_config.get("reflection_min_age_days", 5)
                    )
                    
                    if reflection_stats["processed"] > 0:
                        message_buffer.add_message(
                            "Reflection",
                            f"✓ 完成 {reflection_stats['processed']} 个历史决策的反思学习 "
                            f"(成功: {reflection_stats.get('successful_decisions', 0)}, "
                            f"失败: {reflection_stats.get('failed_decisions', 0)}, "
                            f"平均收益: {reflection_stats.get('avg_return', 0.0):+.2%})"
                        )
                        
                        # 更新反思记录到显示缓冲区
                        if "reflections" in reflection_stats:
                            for refl in reflection_stats["reflections"]:
                                message_buffer.add_reflection(
                                    ticker=refl.get("ticker", ""),
                                    date=refl.get("date", ""),
                                    action=refl.get("action", ""),
                                    actual_return=refl.get("actual_return", 0.0),
                                    lesson=refl.get("lesson", "")
                                )
                        
                        # 更新反思统计信息
                        message_buffer.update_reflection_stats({
                            "total_reflections": message_buffer.reflection_stats.get("total_reflections", 0) + reflection_stats["processed"],
                            "successful_decisions": message_buffer.reflection_stats.get("successful_decisions", 0) + reflection_stats.get("successful_decisions", 0),
                            "failed_decisions": message_buffer.reflection_stats.get("failed_decisions", 0) + reflection_stats.get("failed_decisions", 0),
                            "avg_return": reflection_stats.get("avg_return", 0.0),
                        })
                        
                        # 更新显示
                        update_display(layout)
                        
                except Exception as exc:
                    message_buffer.add_message("Warning", f"处理历史反思时出错: {exc}")
                
                # 保存当前决策到待反思队列（无论HOLD/BUY/SELL都保存）
                if trade_signals or final_state.get("final_trade_decision"):
                    try:
                        reflection_id = reflection_manager.save_pending_reflection(
                            ticker=ticker,
                            decision_date=analysis_date,
                            final_state=final_state,
                            trade_signals=trade_signals,
                            account_state=current_account_state
                        )
                        
                        message_buffer.add_message(
                            "System",
                            f"决策已保存到反思队列 (ID: {reflection_id[:12]}...)，将在未来数据充足后进行反思学习"
                        )
                        
                        # 显示队列状态
                        queue_status = reflection_manager.get_queue_status()
                        message_buffer.add_message(
                            "Info",
                            f"反思队列状态: {queue_status['pending']} 待处理, "
                            f"{queue_status['completed']} 已完成, "
                            f"{queue_status['error']} 失败"
                        )
                        
                        # 更新反思统计信息
                        message_buffer.update_reflection_stats({
                            "pending_queue": queue_status['pending'],
                            "total_reflections": queue_status['completed'] + queue_status['error'],
                        })
                        
                        # 更新显示
                        update_display(layout)
                        
                    except Exception as exc:
                        message_buffer.add_message("Warning", f"保存反思队列失败: {exc}")
                
                # 可选：仍然执行即时回测用于展示（但不用于反思）
                if trade_signals:
                    try:
                        from tradingagents.graph.performance_calculator import backtest
                        from tradingagents.agents.utils.core_stock_tools import get_stock_data
                        import pandas as pd
                        from io import StringIO
                        
                        lookback_days = base_config.get("backtest_lookback_days", 30)
                        analysis_dt = datetime.datetime.strptime(
                            analysis_date, "%Y-%m-%d"
                        ).date()
                        start_bt = (
                            analysis_dt - datetime.timedelta(days=lookback_days)
                        ).isoformat()
                        end_bt = analysis_dt.isoformat()
                        
                        price_data_str = get_stock_data.invoke({
                            "symbol": ticker,
                            "start_date": start_bt,
                            "end_date": end_bt,
                        })
                        
                        price_data = pd.read_csv(StringIO(price_data_str), comment="#")
                        price_data.columns = price_data.columns.str.strip().str.lower()
                        
                        required_cols = {"date", "close"}
                        if required_cols.issubset(price_data.columns):
                            returns_losses, summary = backtest(trade_signals, price_data)
                            
                            if summary and "total_return" in summary:
                                message_buffer.add_message(
                                    "Analysis",
                                    f"历史回测收益率: {summary['total_return']:.2%} "
                                    f"(注意：这是历史模拟，不用于反思学习)"
                                )
                    except Exception as exc:
                        message_buffer.add_message("Debug", f"即时回测失败（不影响主流程）: {exc}")

                update_display(layout)


@app.command()
def analyze():
    run_analysis()


if __name__ == "__main__":
    app()

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_fundamentals, get_balance_sheet, get_cashflow, get_cash_flow, get_income_statement, get_earnings_call_transcript, get_insider_sentiment, get_insider_transactions
from tradingagents.dataflows.config import get_config


def create_fundamentals_analyst(llm):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_fundamentals,
            get_balance_sheet,
            get_cashflow,
            get_cash_flow,
            get_income_statement,
            get_earnings_call_transcript,
        ]

        print(f"DEBUG: Fundamentals analyst tools: {[tool.name for tool in tools]}")

        system_message = (
            "You are a researcher tasked with analyzing fundamental information about a company. Your report should focus on the latest week, but you must also pay special attention to the most recent earnings call transcript, which may cover quarterly or annual results."
            " Please write a comprehensive report that integrates insights from the company's financial documents, company profile, basic financials, financial history, and especially the latest earnings call transcript."
            " When analyzing the earnings call transcript, highlight key management commentary, guidance, and any material changes or risks discussed, and connect these insights to the most recent weekly developments."
            " Make sure to include as much detail as possible. Do not simply state the trends are mixed—provide detailed and fine-grained analysis and insights that may help traders make decisions."
            " Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."
            " Use the available tools: `get_fundamentals` for comprehensive company analysis, `get_balance_sheet`, `get_cashflow` (also available as `get_cash_flow`), `get_income_statement` for specific financial statements, and `get_earnings_call_transcript` for recent earnings call transcripts."
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. The company we want to look at is {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement, get_earning_call_transcripts, get_insider_sentiment, get_insider_transactions
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
            get_income_statement,
            get_earning_call_transcripts,
        ]

        system_message = (
            "You are a fundamental analyst researcher tasked with providing deep, comprehensive analysis of a company's financial health and future prospects. Your analysis must include:\n"
            "1. **Financial Statements Analysis**: Use `get_balance_sheet`, `get_cashflow`, and `get_income_statement` to extract key metrics, trends, and financial health indicators.\n"
            "2. **Management Insights from Earnings Calls (CRITICAL)**: MUST use `get_earning_call_transcripts` to retrieve the latest earnings call transcript. This is essential because:\n"
            "   - Management guidance provides forward-looking statements about the company's strategy and expectations\n"
            "   - Earnings calls contain crucial sentiment and tone indicators about company performance and market conditions\n"
            "   - CEO/CFO commentary reveals management confidence level and strategic priorities\n"
            "   - Q&A sections expose investor concerns and company responses to challenges\n"
            "   - These insights are critical for traders to understand management's view on future performance\n"
            "3. **Integrated Report**: Combine financial data with management sentiment and guidance to create a comprehensive fundamental report.\n\n"
            "IMPORTANT: You MUST call `get_earning_call_transcripts` as part of your analysis - do not skip this step as it is essential for complete fundamental analysis.\n"
            "Write in detail with specific numbers, percentages, and forward-looking insights. Include a Markdown table at the end organizing key findings."
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
                    "For your reference, the current date is {current_date}. The company's stock symbol we want to look at is {ticker}",
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

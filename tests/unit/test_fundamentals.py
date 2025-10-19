#!/usr/bin/env python3

import sys
sys.path.append('/home/maosen/dev/TradingAgents')

from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Create LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# Create analyst node
analyst_node = create_fundamentals_analyst(llm)

# Create mock state
state = {
    "trade_date": "2025-10-16",
    "company_of_interest": "TSLA",
    "messages": [HumanMessage(content="Analyze TSLA fundamentals")]
}

# Call the node
result = analyst_node(state)
print("Result:", result)

# TradingAgents/graph/propagation.py

from typing import Dict, Any, Optional
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)


class Propagator:
    """Handles state initialization and propagation through the graph."""

    def __init__(self, max_recur_limit=100, config: Optional[Dict[str, Any]] = None):
        """Initialize with configuration parameters."""
        self.max_recur_limit = max_recur_limit
        self.config = config or {}

    def create_initial_state(
        self, company_name: str, trade_date: str
    ) -> Dict[str, Any]:
        """Create the initial state for the agent graph."""
        initial_cash = float(self.config.get("account_initial_cash", 100000.0))
        current_position = int(self.config.get("account_current_position", 0))
        max_allocation_pct = float(self.config.get("account_max_allocation_pct", 0.1))
        min_cash_reserve = float(self.config.get("account_min_cash_reserve", 0.0))

        return {
            "messages": [("human", company_name)],
            "company_of_interest": company_name,
            "trade_date": str(trade_date),
            "investment_debate_state": InvestDebateState(
                {"history": "", "current_response": "", "count": 0}
            ),
            "risk_debate_state": RiskDebateState(
                {
                    "history": "",
                    "current_risky_response": "",
                    "current_safe_response": "",
                    "current_neutral_response": "",
                    "count": 0,
                    "recommended_quantity": 0,
                    "reference_price": 0.0,
                }
            ),
            "market_report": "",
            "fundamentals_report": "",
            "sentiment_report": "",
            "news_report": "",
            "processed_trade_decision": "",
            "trade_signals": [],
            "account_state": {
                "cash_balance": self.config.get("initial_cash", 100000.0),
                "positions": {},  # 多品种持仓字典: {ticker: {'shares': int, 'avg_cost': float}}
                "max_allocation_pct": self.config.get("max_allocation_pct", 0.1),
                "min_cash_reserve": self.config.get("min_cash_reserve", 10000.0),
            },
            "recommended_trade": {},
        }

    def get_graph_args(self) -> Dict[str, Any]:
        """Get arguments for the graph invocation."""
        return {
            "stream_mode": "values",
            "config": {"recursion_limit": self.max_recur_limit},
        }

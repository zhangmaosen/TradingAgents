import json
import re
from datetime import datetime, timedelta
from io import StringIO
from typing import Any, Dict

import pandas as pd

from tradingagents.dataflows.interface import route_to_vendor


def create_risk_manager(llm, memory):
    def risk_manager_node(state) -> dict:

        company_name = state["company_of_interest"]

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        sentiment_report = state["sentiment_report"]
        trader_plan = state.get("trader_investment_plan") or state.get(
            "investment_plan", ""
        )

        account_state = state.get("account_state", {})

        def _safe_float(value: Any, default: float = 0.0) -> float:
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        def _safe_int(value: Any, default: int = 0) -> int:
            try:
                return int(float(value))
            except (TypeError, ValueError):
                return default

        cash_balance = _safe_float(account_state.get("cash_balance"), 0.0)
        
        # 获取多品种持仓字典
        positions = account_state.get("positions", {})
        if not isinstance(positions, dict):
            positions = {}
        
        # 获取当前股票的持仓信息
        current_ticker_position = positions.get(company_name, {})
        current_position = _safe_int(current_ticker_position.get("shares", 0), 0)
        avg_cost = _safe_float(current_ticker_position.get("avg_cost", 0.0), 0.0)
        
        allocation_pct = _safe_float(account_state.get("max_allocation_pct"), 0.1)
        allocation_pct = max(min(allocation_pct, 1.0), 0.0)
        min_cash_reserve = _safe_float(account_state.get("min_cash_reserve"), 0.0)
        usable_cash = max(cash_balance - min_cash_reserve, 0.0)
        allocation_budget = usable_cash * allocation_pct

        # 每次实时获取当前股票的最新价格，避免使用全局 last_close_price
        latest_price = 0.0
        try:
            trade_date_str = state.get("trade_date")
            if trade_date_str:
                trade_date = datetime.strptime(trade_date_str, "%Y-%m-%d").date()
                start_date = (trade_date - timedelta(days=10)).isoformat()
                price_data = route_to_vendor(
                    "get_stock_data",
                    company_name,
                    start_date,
                    trade_date_str,
                )
                if isinstance(price_data, (list, tuple)):
                    price_data = price_data[0]
                price_df = pd.read_csv(StringIO(price_data), comment="#")
                price_df.columns = price_df.columns.str.strip().str.lower()
                price_df = price_df.sort_values("date")
                if not price_df.empty and "close" in price_df.columns:
                    latest_price = _safe_float(price_df.iloc[-1]["close"], 0.0)
        except Exception as e:
            # 获取失败时记录错误但继续
            latest_price = 0.0

        latest_price = latest_price if latest_price > 0 else 0.0
        updated_account_state = dict(account_state)
        # 不再保存 last_close_price 到全局账户状态

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # 构建全局持仓概览
        positions_summary = ""
        if positions:
            positions_summary = "**Current Portfolio:**\n"
            for ticker, pos_info in positions.items():
                shares = pos_info.get("shares", 0)
                cost = pos_info.get("avg_cost", 0.0)
                positions_summary += f"  - {ticker}: {shares} shares @ ${cost:.2f} avg cost\n"
        else:
            positions_summary = "**Current Portfolio:** Empty (no positions)\n"

        account_snapshot = (
            f"Cash balance: ${cash_balance:,.2f}\n"
            f"{positions_summary}"
            f"**Current Ticker ({company_name}):** {current_position} share(s)"
            + (f" @ ${avg_cost:.2f} avg cost\n" if avg_cost > 0 else "\n")
            + f"Usable cash after reserves: ${usable_cash:,.2f}\n"
            f"Allocation budget ({allocation_pct * 100:.1f}%): ${allocation_budget:,.2f}\n"
            f"Minimum cash reserve: ${min_cash_reserve:,.2f}\n"
            f"Latest close price: {'$' + format(latest_price, '.2f') if latest_price > 0 else 'Unavailable'}\n"
        )

        prompt = f"""As the Risk Management Judge and Debate Facilitator, your goal is to evaluate the debate between three risk analysts—Risky, Neutral, and Safe/Conservative—and determine the best course of action for the trader. Your decision must result in a clear recommendation: Buy, Sell, or Hold. Choose Hold only if strongly justified by specific arguments, not as a fallback when all sides seem valid. Strive for clarity and decisiveness.

Guidelines for Decision-Making:
1. **Summarize Key Arguments**: Extract the strongest points from each analyst, focusing on relevance to the context.
2. **Provide Rationale**: Support your recommendation with direct quotes and counterarguments from the debate.
3. **Refine the Trader's Plan**: Start with the trader's original plan, **{trader_plan}**, and adjust it based on the analysts' insights.
4. **Learn from Past Mistakes**: Use lessons from **{past_memory_str}** to address prior misjudgments and improve the decision you are making now to make sure you don't make a wrong BUY/SELL/HOLD call that loses money.

Deliverables:
- A clear and actionable recommendation: Buy, Sell, or Hold.
- Detailed reasoning anchored in the debate and past reflections.
- Ensure your final position sizing recommendation respects the account constraints below.

---

**Account Snapshot (for position sizing):**
{account_snapshot}

---

**Analysts Debate History:**  
{history}

---

Focus on actionable insights and continuous improvement. Build on past lessons, critically evaluate all perspectives, and ensure each decision advances better outcomes.

When you deliver the final answer, end with a JSON object inside a fenced code block (```json ... ```). The JSON must have the following keys:
- `decision`: one of BUY, SELL, or HOLD (uppercase).
- `quantity`: integer number of shares to trade that respects the account snapshot and trader plan.
- `updated_plan`: concise summary (<200 tokens) of the revised trading plan.
- `notes`: any additional execution considerations.
"""

        response = llm.invoke(prompt)

        response_text = response.content if hasattr(response, "content") else str(response)

        def _extract_json_payload(text: str) -> Dict[str, Any]:
            if not text:
                return {}
            fenced_match = re.search(
                r"```json\s*(\{.*?\})\s*```",
                text,
                re.DOTALL | re.IGNORECASE,
            )
            if fenced_match:
                candidate = fenced_match.group(1)
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    pass
            brace_match = re.search(r"(\{.*\})", text, re.DOTALL)
            if brace_match:
                candidate = brace_match.group(1)
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    return {}
            return {}

        structured = _extract_json_payload(response_text)

        def _infer_action(text: str) -> str:
            upper_text = (text or "").upper()
            for candidate in ("BUY", "SELL", "HOLD"):
                if candidate in upper_text:
                    return candidate
            return ""

        action = (structured.get("decision") or "").strip().upper()
        if action not in {"BUY", "SELL", "HOLD"}:
            action = _infer_action(response_text) or "HOLD"

        json_quantity = structured.get("quantity")
        if isinstance(json_quantity, str) and json_quantity.isdigit():
            json_quantity = int(json_quantity)
        try:
            json_quantity = int(json_quantity)
        except (TypeError, ValueError):
            json_quantity = None

        max_sellable = max(current_position, 0)
        computed_quantity = 0
        if action == "BUY":
            if latest_price > 0:
                affordable = int(allocation_budget // latest_price)
                computed_quantity = max(affordable, 0)
                if computed_quantity == 0 and allocation_budget >= latest_price:
                    computed_quantity = 1
            else:
                computed_quantity = 0
        elif action == "SELL":
            computed_quantity = max_sellable
        else:
            computed_quantity = 0

        final_quantity = computed_quantity
        if json_quantity is not None and json_quantity >= 0:
            final_quantity = json_quantity
            if action == "BUY" and latest_price > 0:
                affordable = int(allocation_budget // latest_price)
                final_quantity = min(final_quantity, max(affordable, 0))
            if action == "SELL" and max_sellable >= 0:
                final_quantity = min(final_quantity, max_sellable)

        final_quantity = max(final_quantity, 0)

        recommended_trade = {
            "action": action,
            "quantity": final_quantity,
            "reference_price": latest_price if latest_price > 0 else None,
            "cash_balance": cash_balance,
            "allocation_pct": allocation_pct,
            "min_cash_reserve": min_cash_reserve,
        }

        if latest_price > 0 and final_quantity > 0:
            recommended_trade["trade_value"] = round(final_quantity * latest_price, 2)

        sizing_summary_lines = [
            "**Automated Position Sizing**",
            f"- Decision: {action}",
            f"- Recommended Quantity: {final_quantity} share(s)",
            f"- Cash Balance Considered: ${cash_balance:,.2f}",
            f"- Allocation Budget: ${allocation_budget:,.2f} ({allocation_pct * 100:.1f}%)",
            f"- Minimum Cash Reserve: ${min_cash_reserve:,.2f}",
        ]

        if latest_price > 0:
            sizing_summary_lines.insert(
                2, f"- Reference Price Used: ${latest_price:.2f}"
            )

        sizing_summary = "\n".join(sizing_summary_lines)

        final_json_block = json.dumps(recommended_trade, ensure_ascii=False, indent=2)
        augmented_decision = (
            response_text.strip()
            + "\n\n"
            + sizing_summary
            + "\n```json\n"
            + final_json_block
            + "\n```"
        )

        new_risk_debate_state = {
            "judge_decision": augmented_decision,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
            "recommended_quantity": final_quantity,
            "reference_price": latest_price,
        }

        # 更新账户状态：模拟交易执行，更新现金和持仓
        updated_positions = dict(positions)  # 深拷贝持仓字典
        updated_cash = cash_balance
        
        if action == "BUY" and final_quantity > 0 and latest_price > 0:
            # 买入：扣除现金，增加持仓
            trade_cost = final_quantity * latest_price
            updated_cash -= trade_cost
            
            if company_name in updated_positions:
                # 已有持仓：更新平均成本
                old_shares = updated_positions[company_name].get("shares", 0)
                old_cost = updated_positions[company_name].get("avg_cost", 0.0)
                new_shares = old_shares + final_quantity
                new_avg_cost = ((old_shares * old_cost) + trade_cost) / new_shares if new_shares > 0 else latest_price
                updated_positions[company_name] = {
                    "shares": new_shares,
                    "avg_cost": round(new_avg_cost, 2)
                }
            else:
                # 新建持仓
                updated_positions[company_name] = {
                    "shares": final_quantity,
                    "avg_cost": round(latest_price, 2)
                }
        
        elif action == "SELL" and final_quantity > 0 and latest_price > 0:
            # 卖出：增加现金，减少持仓
            trade_proceeds = final_quantity * latest_price
            updated_cash += trade_proceeds
            
            if company_name in updated_positions:
                old_shares = updated_positions[company_name].get("shares", 0)
                new_shares = max(old_shares - final_quantity, 0)
                
                if new_shares > 0:
                    # 部分卖出：保留持仓
                    updated_positions[company_name]["shares"] = new_shares
                else:
                    # 全部卖出：删除持仓
                    del updated_positions[company_name]
        
        # 更新账户状态
        updated_account_state["cash_balance"] = round(updated_cash, 2)
        updated_account_state["positions"] = updated_positions

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": augmented_decision,
            "account_state": updated_account_state,
            "recommended_trade": recommended_trade,
            "processed_trade_decision": action,
        }

    return risk_manager_node

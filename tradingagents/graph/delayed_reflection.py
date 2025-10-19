"""
延迟反思管理器
解决回测时机滞后问题：在决策后等待实际结果再反思
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
from io import StringIO


class DelayedReflectionManager:
    """管理延迟反思队列"""
    
    def __init__(self, storage_path: str = "results/pending_reflections.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
    def save_pending_reflection(
        self,
        ticker: str,
        decision_date: str,
        final_state: Dict[str, Any],
        trade_signals: List[Dict[str, Any]],
        account_state: Dict[str, Any]
    ):
        """保存待反思的决策"""
        # 加载现有队列
        pending_queue = self._load_queue()
        
        # 创建反思记录
        reflection_id = f"{ticker}_{decision_date}_{datetime.now().strftime('%H%M%S')}"
        
        pending_item = {
            "id": reflection_id,
            "ticker": ticker,
            "decision_date": decision_date,
            "created_at": datetime.now().isoformat(),
            "final_state": {
                "company_of_interest": final_state.get("company_of_interest"),
                "market_report": final_state.get("market_report"),
                "sentiment_report": final_state.get("sentiment_report"),
                "news_report": final_state.get("news_report"),
                "fundamentals_report": final_state.get("fundamentals_report"),
                "investment_debate_state": final_state.get("investment_debate_state"),
                "trader_investment_plan": final_state.get("trader_investment_plan"),
                "risk_debate_state": final_state.get("risk_debate_state"),
                "investment_plan": final_state.get("investment_plan"),
                "final_trade_decision": final_state.get("final_trade_decision"),
            },
            "trade_signals": trade_signals,
            "account_state_snapshot": account_state,
            "status": "pending"
        }
        
        # 添加到队列
        pending_queue.append(pending_item)
        
        # 保存
        self._save_queue(pending_queue)
        
        return reflection_id
    
    def process_pending_reflections(
        self,
        graph,
        current_date: str,
        lookforward_days: int = 5,
        min_age_days: int = 5
    ) -> Dict[str, Any]:
        """
        处理待反思队列
        
        Args:
            graph: TradingAgentsGraph实例
            current_date: 当前分析日期
            lookforward_days: 向前看多少天计算实际收益
            min_age_days: 最小反思延迟（确保有足够未来数据）
        
        Returns:
            处理统计信息
        """
        from tradingagents.agents.utils.core_stock_tools import get_stock_data
        
        pending_queue = self._load_queue()
        current_dt = datetime.strptime(current_date, "%Y-%m-%d").date()
        
        processed_count = 0
        skipped_count = 0
        failed_count = 0
        
        updated_queue = []
        reflections_details = []  # 存储反思详情供UI显示
        
        for item in pending_queue:
            if item["status"] != "pending":
                updated_queue.append(item)
                continue
            
            decision_dt = datetime.strptime(item["decision_date"], "%Y-%m-%d").date()
            age_days = (current_dt - decision_dt).days
            
            # 检查是否已经有足够的未来数据
            if age_days < min_age_days:
                updated_queue.append(item)
                skipped_count += 1
                continue
            
            try:
                # 获取决策日期之后的价格数据
                end_date = (decision_dt + timedelta(days=lookforward_days)).isoformat()
                
                price_data_str = get_stock_data.invoke({
                    "symbol": item["ticker"],
                    "start_date": item["decision_date"],
                    "end_date": end_date,
                })
                
                price_data = pd.read_csv(StringIO(price_data_str), comment="#")
                price_data.columns = price_data.columns.str.strip().str.lower()
                
                if price_data.empty:
                    updated_queue.append(item)
                    skipped_count += 1
                    continue
                
                # 计算实际收益
                returns_losses = self._calculate_actual_returns(
                    item["trade_signals"],
                    price_data,
                    item["account_state_snapshot"]
                )
                
                # 执行反思
                graph.curr_state = item["final_state"]
                graph.reflect_and_remember(returns_losses)
                
                # 提取反思详情用于UI显示
                action = "HOLD"
                if item["trade_signals"]:
                    action = item["trade_signals"][0].get("signal", "HOLD").upper()
                
                actual_return = 0.0
                lesson = "No return data available"
                
                if isinstance(returns_losses, pd.DataFrame) and not returns_losses.empty:
                    if "total_return" in returns_losses.columns:
                        actual_return = returns_losses["total_return"].iloc[-1]
                    elif "pnl" in returns_losses.columns:
                        actual_return = returns_losses["pnl"].sum() / 10000.0  # 假设初始资金10000
                    
                    # 生成教训摘要
                    if actual_return > 0.05:
                        lesson = f"✓ 决策成功：获得 {actual_return:.2%} 收益"
                    elif actual_return < -0.05:
                        lesson = f"✗ 决策失败：损失 {abs(actual_return):.2%}"
                    else:
                        lesson = f"→ 决策平庸：收益 {actual_return:.2%}"
                
                reflections_details.append({
                    "ticker": item["ticker"],
                    "date": item["decision_date"],
                    "action": action,
                    "actual_return": actual_return,
                    "lesson": lesson
                })
                
                # 更新状态
                item["status"] = "completed"
                item["reflected_at"] = datetime.now().isoformat()
                item["reflection_results"] = {
                    "returns_summary": returns_losses.to_dict() if hasattr(returns_losses, 'to_dict') else str(returns_losses),
                    "lookforward_days": lookforward_days,
                    "actual_return": actual_return
                }
                
                updated_queue.append(item)
                processed_count += 1
                
            except Exception as e:
                # 失败的标记为error，但保留在队列中供后续重试
                item["status"] = "error"
                item["error_message"] = str(e)
                item["error_at"] = datetime.now().isoformat()
                updated_queue.append(item)
                failed_count += 1
        
        # 保存更新后的队列
        self._save_queue(updated_queue)
        
        # 计算成功/失败统计
        successful = sum(1 for r in reflections_details if r["actual_return"] > 0)
        failed = sum(1 for r in reflections_details if r["actual_return"] < 0)
        avg_return = sum(r["actual_return"] for r in reflections_details) / len(reflections_details) if reflections_details else 0.0
        
        return {
            "processed": processed_count,
            "skipped": skipped_count,
            "failed": failed_count,
            "total": len(pending_queue),
            "reflections": reflections_details,
            "successful_decisions": successful,
            "failed_decisions": failed,
            "avg_return": avg_return
        }
    
    def _calculate_actual_returns(
        self,
        trade_signals: List[Dict[str, Any]],
        future_prices: pd.DataFrame,
        account_snapshot: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        基于实际未来价格计算收益
        
        这与backtest不同：
        - backtest: 用历史价格模拟交易
        - 这里: 用决策后的真实价格计算实际表现
        """
        if not trade_signals or future_prices.empty:
            return pd.DataFrame()
        
        # 确保日期列格式统一
        if 'date' not in future_prices.columns and 'Date' in future_prices.columns:
            future_prices = future_prices.rename(columns={'Date': 'date'})
        
        returns_list = []
        
        for signal in trade_signals:
            signal_date = signal.get("date")
            action = signal.get("signal", "").lower()
            quantity = signal.get("quantity", 0)
            
            # 查找信号日期及之后的价格
            matching_prices = future_prices[future_prices["date"] >= signal_date].sort_values("date")
            
            if matching_prices.empty:
                continue
            
            # 决策时的价格（或最接近的价格）
            decision_price = signal.get("reference_price", 0) or matching_prices.iloc[0]["close"]
            
            # 计算持有期收益（使用lookforward期间的最后价格）
            if len(matching_prices) > 1:
                future_price = matching_prices.iloc[-1]["close"]
            else:
                future_price = decision_price
            
            # 获取持仓信息
            ticker = signal.get("ticker", "")
            position_info = account_snapshot.get("positions", {}).get(ticker, {})
            avg_cost = position_info.get("avg_cost", decision_price) if position_info else decision_price
            
            # 🔑 改进的盈亏计算
            if action == "buy":
                # BUY: 评估买入后的表现（未实现盈亏）
                pnl = (future_price - decision_price) * quantity
                pnl_pct = (future_price - decision_price) / decision_price if decision_price > 0 else 0
                pnl_type = "unrealized_gain" if pnl > 0 else "unrealized_loss"
                
                result = {
                    "date": signal_date,
                    "action": action,
                    "decision_price": decision_price,
                    "future_price": future_price,
                    "avg_cost": decision_price,  # 买入时就是成本
                    "quantity": quantity,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "pnl_type": pnl_type,
                    "evaluation_method": "actual_future_performance"
                }
                
            elif action == "sell":
                # SELL: 🔑 使用标准盈亏定义 + 时机评估
                
                # 主要指标：已实现盈亏（与未来价格无关）
                realized_pnl = (decision_price - avg_cost) * quantity
                realized_pnl_pct = (decision_price - avg_cost) / avg_cost if avg_cost > 0 else 0
                
                # 次要指标：时机评估（卖出后的价格变化）
                opportunity_cost = (future_price - decision_price) * quantity
                # > 0: 卖早了（后续上涨，错失收益）
                # < 0: 卖对了（后续下跌，避免损失）
                sell_timing_score = -opportunity_cost  # 负数转正，表示卖得好
                
                pnl = realized_pnl  # 主要用realized_pnl评估
                pnl_pct = realized_pnl_pct
                pnl_type = "realized_gain" if pnl > 0 else "realized_loss"
                
                result = {
                    "date": signal_date,
                    "action": action,
                    "decision_price": decision_price,
                    "future_price": future_price,
                    "avg_cost": avg_cost,
                    "quantity": quantity,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "pnl_type": pnl_type,
                    "realized_pnl": realized_pnl,  # 🔑 实际赚了多少
                    "opportunity_cost": opportunity_cost,  # 🔑 卖出后的价格变化
                    "sell_timing_score": sell_timing_score,  # 🔑 时机评分（正数=好）
                    "evaluation_method": "actual_future_performance"
                }
                
            else:  # hold
                # HOLD: 评估持有期间的表现
                if position_info:
                    shares = position_info.get("shares", 0)
                    pnl = (future_price - avg_cost) * shares
                    pnl_pct = (future_price - avg_cost) / avg_cost if avg_cost > 0 else 0
                    pnl_type = "unrealized_gain" if pnl > 0 else "unrealized_loss"
                else:
                    # 无持仓时的HOLD
                    pnl = 0
                    pnl_pct = 0
                    pnl_type = "no_position"
                
                result = {
                    "date": signal_date,
                    "action": action,
                    "decision_price": decision_price,
                    "future_price": future_price,
                    "avg_cost": avg_cost,
                    "quantity": quantity,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "pnl_type": pnl_type,
                    "evaluation_method": "actual_future_performance"
                }
            
            returns_list.append(result)
        
        return pd.DataFrame(returns_list)
    
    def _load_queue(self) -> List[Dict[str, Any]]:
        """加载待反思队列"""
        if not self.storage_path.exists():
            return []
        
        try:
            with open(self.storage_path, "r") as f:
                return json.load(f)
        except Exception:
            return []
    
    def _save_queue(self, queue: List[Dict[str, Any]]):
        """保存队列到磁盘"""
        with open(self.storage_path, "w") as f:
            json.dump(queue, f, indent=2)
    
    def get_queue_status(self) -> Dict[str, int]:
        """获取队列状态统计"""
        queue = self._load_queue()
        
        status_counts = {
            "pending": 0,
            "completed": 0,
            "error": 0,
            "total": len(queue)
        }
        
        for item in queue:
            status = item.get("status", "pending")
            if status in status_counts:
                status_counts[status] += 1
        
        return status_counts
    
    def clear_completed(self, keep_days: int = 30):
        """清理已完成的反思记录（保留最近N天）"""
        queue = self._load_queue()
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        filtered_queue = [
            item for item in queue
            if item["status"] != "completed" or 
               datetime.fromisoformat(item.get("reflected_at", "1970-01-01")) > cutoff_date
        ]
        
        self._save_queue(filtered_queue)
        
        return len(queue) - len(filtered_queue)

"""
分层记忆系统
解决跨股票记忆干扰问题
"""

from typing import Dict, Any, List
from pathlib import Path
from tradingagents.agents.utils.memory import FinancialSituationMemory


class HierarchicalMemoryManager:
    """
    分层记忆管理器
    
    架构:
    - 全局记忆: 跨股票通用经验（市场规律、策略原则）
    - 股票特定记忆: 针对特定股票的历史教训
    - 行业记忆: 针对行业特征的经验（科技、能源、金融等）
    """
    
    # 股票到行业的映射
    STOCK_TO_SECTOR = {
        "AAPL": "Technology",
        "MSFT": "Technology",
        "GOOGL": "Technology",
        "GOOG": "Technology",
        "AMZN": "Technology",
        "META": "Technology",
        "NVDA": "Technology",
        "TSLA": "Automotive",
        "JPM": "Financial",
        "BAC": "Financial",
        "XOM": "Energy",
        "CVX": "Energy",
        # 可扩展...
    }
    
    def __init__(self, agent_name: str, config: Dict[str, Any]):
        """
        初始化分层记忆
        
        Args:
            agent_name: agent名称（bull/bear/trader等）
            config: 配置字典
        """
        self.agent_name = agent_name
        self.config = config
        
        # 全局记忆（所有股票共享）
        self.global_memory = FinancialSituationMemory(
            f"{agent_name}_global",
            config
        )
        
        # 股票特定记忆缓存
        self.stock_memories: Dict[str, FinancialSituationMemory] = {}
        
        # 行业记忆缓存
        self.sector_memories: Dict[str, FinancialSituationMemory] = {}
    
    def get_stock_memory(self, ticker: str) -> FinancialSituationMemory:
        """获取或创建股票特定记忆"""
        if ticker not in self.stock_memories:
            self.stock_memories[ticker] = FinancialSituationMemory(
                f"{self.agent_name}_{ticker.lower()}",
                self.config
            )
        return self.stock_memories[ticker]
    
    def get_sector_memory(self, ticker: str) -> FinancialSituationMemory:
        """获取或创建行业记忆"""
        sector = self.STOCK_TO_SECTOR.get(ticker, "General")
        
        if sector not in self.sector_memories:
            self.sector_memories[sector] = FinancialSituationMemory(
                f"{self.agent_name}_sector_{sector.lower()}",
                self.config
            )
        return self.sector_memories[sector]
    
    def add_reflection(
        self,
        ticker: str,
        situation: str,
        reflection: str,
        scope: str = "auto"
    ):
        """
        添加反思到合适的记忆层
        
        Args:
            ticker: 股票代码
            situation: 市场情况描述
            reflection: 反思内容
            scope: 记忆范围
                - "stock": 仅存入股票特定记忆
                - "sector": 仅存入行业记忆
                - "global": 仅存入全局记忆
                - "auto": 自动判断（默认）
        """
        if scope == "auto":
            # 自动判断反思的适用范围
            scope = self._determine_scope(reflection)
        
        # 存入对应的记忆层
        if scope == "stock":
            stock_memory = self.get_stock_memory(ticker)
            stock_memory.add_situations([(situation, reflection)])
        
        elif scope == "sector":
            sector_memory = self.get_sector_memory(ticker)
            sector_memory.add_situations([(situation, reflection)])
        
        elif scope == "global":
            self.global_memory.add_situations([(situation, reflection)])
        
        elif scope == "all":
            # 通用性很强的经验，存入所有层级
            stock_memory = self.get_stock_memory(ticker)
            sector_memory = self.get_sector_memory(ticker)
            
            stock_memory.add_situations([(situation, reflection)])
            sector_memory.add_situations([(situation, reflection)])
            self.global_memory.add_situations([(situation, reflection)])
    
    def get_memories(
        self,
        ticker: str,
        current_situation: str,
        n_matches: int = 3
    ) -> List[Dict[str, Any]]:
        """
        分层检索记忆
        
        优先级:
        1. 股票特定记忆（权重最高，最相关）
        2. 行业记忆（中等权重）
        3. 全局记忆（基础权重）
        
        Args:
            ticker: 股票代码
            current_situation: 当前市场情况
            n_matches: 总共返回多少条记忆
        
        Returns:
            合并后的记忆列表，按相似度排序
        """
        all_memories = []
        
        # 1. 股票特定记忆（最高权重）
        stock_memory = self.get_stock_memory(ticker)
        stock_results = stock_memory.get_memories(current_situation, n_matches=max(1, n_matches // 2))
        
        for result in stock_results:
            result["source"] = f"stock_{ticker}"
            result["weight"] = 1.0  # 最高权重
            result["weighted_score"] = result["similarity_score"] * result["weight"]
            all_memories.append(result)
        
        # 2. 行业记忆（中等权重）
        sector_memory = self.get_sector_memory(ticker)
        sector_results = sector_memory.get_memories(current_situation, n_matches=max(1, n_matches // 3))
        
        for result in sector_results:
            result["source"] = f"sector_{self.STOCK_TO_SECTOR.get(ticker, 'General')}"
            result["weight"] = 0.7  # 行业权重
            result["weighted_score"] = result["similarity_score"] * result["weight"]
            all_memories.append(result)
        
        # 3. 全局记忆（基础权重）
        global_results = self.global_memory.get_memories(current_situation, n_matches=max(1, n_matches // 3))
        
        for result in global_results:
            result["source"] = "global"
            result["weight"] = 0.5  # 全局权重
            result["weighted_score"] = result["similarity_score"] * result["weight"]
            all_memories.append(result)
        
        # 按加权相似度排序并返回top N
        all_memories.sort(key=lambda x: x["weighted_score"], reverse=True)
        
        return all_memories[:n_matches]
    
    def _determine_scope(self, reflection: str) -> str:
        """
        基于反思内容判断适用范围
        
        启发式规则:
        - 包含具体股票特征 → stock
        - 包含行业特征词 → sector
        - 通用策略/市场规律 → global
        """
        reflection_lower = reflection.lower()
        
        # 股票特定关键词
        stock_keywords = [
            "该公司", "这支股票", "apple", "tesla", "nvidia",
            "其产品", "其业务", "公司特点", "管理层"
        ]
        
        # 行业关键词
        sector_keywords = [
            "科技股", "能源股", "金融股", "tech sector", "energy sector",
            "行业特征", "该行业", "同类公司", "sector"
        ]
        
        # 全局关键词
        global_keywords = [
            "市场规律", "投资原则", "风险管理", "通用策略",
            "市场情绪", "宏观环境", "经济周期", "利率影响"
        ]
        
        # 计分
        stock_score = sum(1 for kw in stock_keywords if kw in reflection_lower)
        sector_score = sum(1 for kw in sector_keywords if kw in reflection_lower)
        global_score = sum(1 for kw in global_keywords if kw in reflection_lower)
        
        # 判断
        if stock_score > sector_score and stock_score > global_score:
            return "stock"
        elif sector_score > global_score:
            return "sector"
        else:
            return "global"
    
    def get_memory_stats(self, ticker: str) -> Dict[str, int]:
        """获取记忆统计信息"""
        stock_memory = self.get_stock_memory(ticker)
        sector_memory = self.get_sector_memory(ticker)
        
        return {
            "stock_memories": stock_memory.situation_collection.count(),
            "sector_memories": sector_memory.situation_collection.count(),
            "global_memories": self.global_memory.situation_collection.count(),
            "total": (
                stock_memory.situation_collection.count() +
                sector_memory.situation_collection.count() +
                self.global_memory.situation_collection.count()
            )
        }


# 向后兼容的包装器
class BackwardCompatibleMemory:
    """
    向后兼容包装器
    使现有代码可以无缝切换到分层记忆
    """
    
    def __init__(self, agent_name: str, config: Dict[str, Any], ticker: str = None):
        self.hierarchical_manager = HierarchicalMemoryManager(agent_name, config)
        self.ticker = ticker  # 当前正在分析的股票
    
    def set_ticker(self, ticker: str):
        """设置当前分析的股票"""
        self.ticker = ticker
    
    def add_situations(self, situations_and_advice: List[tuple]):
        """添加记忆（自动路由到分层系统）"""
        if not self.ticker:
            raise ValueError("必须先设置ticker才能添加记忆")
        
        for situation, advice in situations_and_advice:
            self.hierarchical_manager.add_reflection(
                self.ticker,
                situation,
                advice,
                scope="auto"
            )
    
    def get_memories(self, current_situation: str, n_matches: int = 2):
        """获取记忆（从分层系统检索）"""
        if not self.ticker:
            # 如果没有设置ticker，回退到全局记忆
            return self.hierarchical_manager.global_memory.get_memories(
                current_situation,
                n_matches
            )
        
        return self.hierarchical_manager.get_memories(
            self.ticker,
            current_situation,
            n_matches
        )

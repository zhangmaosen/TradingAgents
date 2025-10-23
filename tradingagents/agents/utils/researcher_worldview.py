"""
Researcher Worldview System
为Bull和Bear Researcher赋予独立的价值判断能力

核心概念：
- 世界观：如何理解市场运作
- 人生观：为什么做研究/辩论
- 价值观：什么样的论据是好的

可解释性：每个决策步骤都记录详细的理由
"""

from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime


# ============ 三观的枚举定义 ============

class WorldView(Enum):
    """世界观：市场是如何运作的"""
    FUNDAMENTAL = "fundamental"       # 基本面观：长期价值驱动价格
    PSYCHOLOGICAL = "psychological"   # 心理观：情绪短期影响价格
    RISK_FOCUSED = "risk_focused"    # 风险观：不确定性主导市场
    MIXED = "mixed"                   # 混合观：三者都很重要


class ResearchPurpose(Enum):
    """研究目的：为什么做研究和辩论"""
    TRUTH_SEEKING = "truth_seeking"   # 寻求真相：通过辩论发现真理
    WEALTH_PROTECTION = "wealth_protection"  # 保护财富：避免投资损失
    OPPORTUNITY_FINDING = "opportunity_finding"  # 寻找机会：发现投资机会
    LEARNING = "learning"             # 学习成长：通过辩论深化理解


class ArgumentQuality(Enum):
    """论据质量标准"""
    EVIDENCE_BASED = "evidence_based"  # 基于证据：必须有数据支持
    LOGIC_FIRST = "logic_first"        # 逻辑优先：推理必须清晰
    BALANCED = "balanced"              # 平衡：证据和逻辑都要
    IMPACT_DRIVEN = "impact_driven"    # 影响导向：论据的说服力最重要


# ============ 三观配置数据结构 ============

@dataclass
class ResearcherWorldview:
    """Researcher的完整三观配置"""
    
    role: str  # "bull" or "bear"
    
    # 三观
    world_view: WorldView
    research_purpose: ResearchPurpose
    argument_quality: ArgumentQuality
    
    # 核心信念（固定部分）
    core_beliefs: Dict[str, str]
    
    # 数据优先级权重（动态调整部分）
    data_priorities: Dict[str, float]  # {"fundamentals": 0.4, "sentiment": 0.3, ...}
    
    # 论据质量标准（动态调整部分）
    quality_thresholds: Dict[str, float]  # {"evidence_strength": 0.8, ...}
    
    # 禁止的论据类型
    forbidden_argument_types: List[str]
    
    # 元数据
    created_at: str
    last_updated: str
    performance_history: List[Dict] = None  # 历史表现记录
    
    def __post_init__(self):
        if self.performance_history is None:
            self.performance_history = []
    
    def to_dict(self) -> Dict:
        """转换为字典（用于日志）"""
        return {
            "role": self.role,
            "world_view": self.world_view.value,
            "research_purpose": self.research_purpose.value,
            "argument_quality": self.argument_quality.value,
            "core_beliefs": self.core_beliefs,
            "data_priorities": self.data_priorities,
            "quality_thresholds": self.quality_thresholds,
            "forbidden_argument_types": self.forbidden_argument_types,
        }
    
    def to_json(self) -> str:
        """转换为JSON"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @staticmethod
    def create_bull_worldview() -> 'ResearcherWorldview':
        """创建Bull Researcher的三观"""
        return ResearcherWorldview(
            role="bull",
            world_view=WorldView.MIXED,  # 混合观：看重基本面，但理解心理
            research_purpose=ResearchPurpose.OPPORTUNITY_FINDING,  # 寻找机会
            argument_quality=ArgumentQuality.BALANCED,  # 平衡：证据+逻辑
            
            core_beliefs={
                "market_nature": "Driven by fundamentals in long term, influenced by emotions in short term",
                "opportunity_source": "Opportunities arise when markets undervalue quality companies",
                "risk_view": "Risks can be managed through research and understanding",
                "debate_goal": "Discover overlooked value through debate",
            },
            
            data_priorities={
                "fundamentals": 0.40,      # 基本面权重40%
                "sentiment": 0.25,         # 情绪权重25%
                "news": 0.20,              # 新闻权重20%
                "market_data": 0.15,       # 市场数据权重15%
            },
            
            quality_thresholds={
                "evidence_strength": 0.75,     # 证据强度 >= 75%
                "logic_clarity": 0.80,         # 逻辑清晰度 >= 80%
                "growth_potential": 0.15,      # 增长潜力 >= 15%
                "competitive_advantage": 0.70, # 竞争优势 >= 70%
            },
            
            forbidden_argument_types=[
                "pure_speculation",         # 纯粹投机
                "ignore_fundamentals",      # 忽视基本面
                "excessive_optimism",       # 过度乐观
            ],
            
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
        )
    
    @staticmethod
    def create_bear_worldview() -> 'ResearcherWorldview':
        """创建Bear Researcher的三观"""
        return ResearcherWorldview(
            role="bear",
            world_view=WorldView.RISK_FOCUSED,  # 风险观：关注不确定性
            research_purpose=ResearchPurpose.WEALTH_PROTECTION,  # 保护财富
            argument_quality=ArgumentQuality.EVIDENCE_BASED,  # 基于证据
            
            core_beliefs={
                "market_nature": "Full of uncertainty and risks, prices are often overly optimistic",
                "risk_source": "Overlooked risks often cause the greatest losses",
                "opportunity_view": "The best opportunity is avoiding major losses",
                "debate_goal": "Reveal overlooked risks through debate",
            },
            
            data_priorities={
                "fundamentals": 0.35,      # 基本面权重35%（关注财务风险）
                "sentiment": 0.30,         # 情绪权重30%（关注过度乐观）
                "news": 0.25,              # 新闻权重25%（关注负面消息）
                "market_data": 0.10,       # 市场数据权重10%
            },
            
            quality_thresholds={
                "evidence_strength": 0.80,     # 证据强度 >= 80%（更严格）
                "risk_identification": 0.75,   # 风险识别 >= 75%
                "downside_analysis": 0.70,     # 下行分析 >= 70%
                "challenge_depth": 0.75,       # 挑战深度 >= 75%
            },
            
            forbidden_argument_types=[
                "dismiss_risks",            # 忽视风险
                "unfounded_pessimism",      # 无根据的悲观
                "ignore_positive_data",     # 忽视正面数据
            ],
            
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
        )


# ============ 决策日志系统（可解释性核心）============

@dataclass
class WorldviewDecisionLog:
    """三观决策的详细日志（用于可解释性）"""
    
    timestamp: str
    step: str  # 决策步骤
    decision: str  # 做出的决策
    reasoning: str  # 详细理由
    worldview_influence: Dict  # 三观如何影响了这个决策
    data_used: Dict  # 使用了哪些数据
    alternatives_considered: List[str]  # 考虑过的其他选项
    confidence: float  # 决策信心（0-1）
    
    def to_dict(self) -> Dict:
        return asdict(self)


class WorldviewDecisionLogger:
    """决策日志记录器"""
    
    def __init__(self, role: str):
        self.role = role
        self.logs: List[WorldviewDecisionLog] = []
    
    def log_decision(
        self,
        step: str,
        decision: str,
        reasoning: str,
        worldview_influence: Dict,
        data_used: Dict = None,
        alternatives_considered: List[str] = None,
        confidence: float = 0.8
    ):
        """记录一个决策"""
        log = WorldviewDecisionLog(
            timestamp=datetime.now().isoformat(),
            step=step,
            decision=decision,
            reasoning=reasoning,
            worldview_influence=worldview_influence,
            data_used=data_used or {},
            alternatives_considered=alternatives_considered or [],
            confidence=confidence,
        )
        self.logs.append(log)
    
    def get_logs(self) -> List[Dict]:
        """获取所有日志"""
        return [log.to_dict() for log in self.logs]
    
    def generate_explanation(self) -> str:
        """生成可读的决策解释"""
        explanation = f"\n{'='*80}\n"
        explanation += f"【{self.role.upper()} RESEARCHER 三观决策过程】\n"
        explanation += f"{'='*80}\n\n"
        
        for i, log in enumerate(self.logs, 1):
            explanation += f"步骤 {i}: {log.step}\n"
            explanation += f"{'─'*80}\n"
            explanation += f"决策: {log.decision}\n\n"
            explanation += f"理由:\n{log.reasoning}\n\n"
            explanation += f"三观影响:\n"
            for key, value in log.worldview_influence.items():
                explanation += f"  • {key}: {value}\n"
            explanation += f"\n决策信心: {log.confidence:.1%}\n"
            explanation += f"\n"
        
        return explanation
    
    def save_to_file(self, filepath: str):
        """保存日志到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.generate_explanation())
            f.write("\n\n" + "="*80 + "\n")
            f.write("详细日志（JSON格式）\n")
            f.write("="*80 + "\n")
            f.write(json.dumps(self.get_logs(), indent=2, ensure_ascii=False))


# ============ 三观验证引擎 ============

class WorldviewValidator:
    """根据Researcher三观验证论据和决策"""
    
    def __init__(self, worldview: ResearcherWorldview):
        self.worldview = worldview
        self.logger = WorldviewDecisionLogger(worldview.role)
    
    def filter_data_by_worldview(self, all_data: Dict) -> Dict:
        """
        第一步：根据世界观过滤和加权数据
        
        这是最关键的一步 - 决定了Researcher关注什么
        """
        filtered_data = {}
        reasoning_parts = []
        
        # 根据数据优先级加权
        for data_type, weight in self.worldview.data_priorities.items():
            if data_type in all_data:
                filtered_data[data_type] = {
                    "content": all_data[data_type],
                    "weight": weight,
                }
                reasoning_parts.append(f"{data_type}(权重{weight:.1%})")
        
        # 记录决策
        self.logger.log_decision(
            step="数据过滤",
            decision=f"选择了 {len(filtered_data)} 类数据",
            reasoning=f"""
根据{self.worldview.role}的世界观（{self.worldview.world_view.value}），
我选择关注以下数据：{', '.join(reasoning_parts)}

核心信念：{self.worldview.core_beliefs['market_nature']}
因此，我给予不同数据源不同的权重。
            """.strip(),
            worldview_influence={
                "world_view": self.worldview.world_view.value,
                "core_belief": self.worldview.core_beliefs['market_nature'],
                "data_priorities": self.worldview.data_priorities,
            },
            data_used={"available_data": list(all_data.keys())},
            confidence=0.95,
        )
        
        return filtered_data
    
    def determine_argument_strategy(self, filtered_data: Dict, opponent_argument: str = None, round_number: int = 1) -> Dict:
        """
        Step 2: Determine argument strategy based on research purpose and debate round
        
        Strategy Evolution Across Rounds:
        - Round 1: Establish foundational position with key data points
        - Round 2: Deepen analysis by finding new angles and counterpoints
        - Round 3+: Aggressive rebuttal of opponent's weakest points
        """
        strategy = {
            "focus_areas": [],
            "tone": "",
            "approach": "",
            "round_number": round_number,
            "round_instruction": "",
        }
        
        purpose = self.worldview.research_purpose
        
        # Base strategy by research purpose
        if purpose == ResearchPurpose.OPPORTUNITY_FINDING:
            base_areas = ["growth_potential", "competitive_advantages", "market_opportunities"]
            base_tone = "Actively seeking value"
            base_approach = "Emphasize undervalued strengths"
        
        elif purpose == ResearchPurpose.WEALTH_PROTECTION:
            base_areas = ["risk_factors", "downside_scenarios", "warning_signs"]
            base_tone = "Prudently identifying risks"
            base_approach = "Reveal overlooked risks"
        
        elif purpose == ResearchPurpose.TRUTH_SEEKING:
            base_areas = ["comprehensive_analysis", "balanced_view", "data_accuracy"]
            base_tone = "Objectively seeking truth"
            base_approach = "Synthesize evidence from all aspects"
        
        elif purpose == ResearchPurpose.LEARNING:
            base_areas = ["deep_understanding", "pattern_recognition", "learning_insights"]
            base_tone = "Exploring and learning"
            base_approach = "Deepen understanding through debate"
        else:
            base_areas = ["comprehensive_analysis"]
            base_tone = "Balanced assessment"
            base_approach = "Balanced approach"
        
        strategy["focus_areas"] = base_areas
        strategy["tone"] = base_tone
        strategy["approach"] = base_approach
        
        # Dynamic round-based evolution
        if round_number == 1:
            strategy["round_instruction"] = "ROUND 1 - FOUNDATION: Establish your core position with strongest evidence and clear reasoning. Set the tone for the debate."
        elif round_number == 2:
            strategy["round_instruction"] = "ROUND 2 - DEPTH: Go deeper. Find new angles, unexamined data points, or subtle logical inconsistencies in opponent's argument. Expand your case beyond just responding."
            # Add counter-argument focus for round 2+
            if opponent_argument:
                strategy["focus_areas"].append("opponent_weaknesses")
        else:  # round 3+
            strategy["round_instruction"] = f"ROUND {round_number} - AGGRESSIVE: This is your chance to land decisive blows. Identify and ruthlessly exploit the weakest points in opponent's logic. Be direct and specific."
            strategy["approach"] = f"Aggressive rebuttal focused on opponent's weakest reasoning"
            if opponent_argument:
                strategy["focus_areas"].insert(0, "opponent_weaknesses")
        
        # Log decision
        self.logger.log_decision(
            step="Strategy Selection",
            decision=f"[Round {round_number}] {strategy['approach']}",
            reasoning=f"""
Based on my research purpose ({purpose.value}) and debate progress:
- Current round: {round_number}
- Round strategy: {strategy['round_instruction']}
- Focus areas: {', '.join(strategy['focus_areas'])}
- Argument tone: {strategy['tone']}
- Argumentation approach: {strategy['approach']}

Core belief: {self.worldview.core_beliefs['debate_goal']}
            """.strip(),
            worldview_influence={
                "research_purpose": purpose.value,
                "debate_goal": self.worldview.core_beliefs['debate_goal'],
                "round_number": round_number,
            },
            data_used={"filtered_data_types": list(filtered_data.keys())},
            alternatives_considered=[
                "Other possible strategies that don't align with my research purpose"
            ],
            confidence=0.90,
        )
        
        return strategy
    
    def validate_argument_quality(self, argument: str, evidence: Dict) -> Tuple[bool, Dict]:
        """
        Step 3: Validate argument quality based on values
        """
        quality_checks = {
            "passes": True,
            "scores": {},
            "issues": [],
            "strengths": [],
        }
        
        # Check evidence strength
        evidence_strength = evidence.get("strength", 0.5)
        quality_checks["scores"]["evidence_strength"] = evidence_strength
        
        threshold = self.worldview.quality_thresholds.get("evidence_strength", 0.75)
        if evidence_strength < threshold:
            quality_checks["passes"] = False
            quality_checks["issues"].append(
                f"Evidence strength ({evidence_strength:.1%}) below standard ({threshold:.1%})"
            )
        else:
            quality_checks["strengths"].append(
                f"Evidence strength ({evidence_strength:.1%}) meets standard"
            )
        
        # Check logic clarity
        logic_clarity = evidence.get("clarity", 0.5)
        quality_checks["scores"]["logic_clarity"] = logic_clarity
        
        threshold = self.worldview.quality_thresholds.get("logic_clarity", 0.75)
        if logic_clarity < threshold:
            quality_checks["passes"] = False
            quality_checks["issues"].append(
                f"Logic clarity ({logic_clarity:.1%}) below standard ({threshold:.1%})"
            )
        else:
            quality_checks["strengths"].append(
                f"Logic clarity ({logic_clarity:.1%}) meets standard"
            )
        
        # Check for forbidden types
        argument_type = evidence.get("type", "unknown")
        if argument_type in self.worldview.forbidden_argument_types:
            quality_checks["passes"] = False
            quality_checks["issues"].append(
                f"Argument type ({argument_type}) is in forbidden list"
            )
        
        # Log decision
        self.logger.log_decision(
            step="Quality Validation",
            decision="Pass" if quality_checks["passes"] else "Fail",
            reasoning=f"""
Based on my argument quality standard ({self.worldview.argument_quality.value}),
Validation results:

✓ Strengths:
{chr(10).join(f"  - {s}" for s in quality_checks["strengths"])}

✗ Issues:
{chr(10).join(f"  - {i}" for i in quality_checks["issues"]) if quality_checks["issues"] else "  None"}

Quality thresholds: {self.worldview.quality_thresholds}
            """.strip(),
            worldview_influence={
                "argument_quality": self.worldview.argument_quality.value,
                "quality_thresholds": self.worldview.quality_thresholds,
                "forbidden_types": self.worldview.forbidden_argument_types,
            },
            data_used={"quality_scores": quality_checks["scores"]},
            confidence=0.85 if quality_checks["passes"] else 0.60,
        )
        
        return quality_checks["passes"], quality_checks
    
    def get_decision_logs(self) -> List[Dict]:
        """获取所有决策日志"""
        return self.logger.get_logs()
    
    def generate_explanation_report(self) -> str:
        """生成可读的决策解释报告"""
        return self.logger.generate_explanation()
    
    def save_decision_log(self, filepath: str):
        """保存决策日志到文件"""
        self.logger.save_to_file(filepath)


# ============ 三观自我反思系统 ============

@dataclass
class WorldviewPerformance:
    """三观表现记录"""
    debate_id: str
    timestamp: str
    argument_accepted: bool  # 论据是否被采纳
    debate_outcome: str  # "won" / "lost" / "neutral"
    actual_market_outcome: Optional[float]  # 实际市场结果（如果有）
    what_worked: List[str]
    what_failed: List[str]
    adjustment_needed: bool


class WorldviewReflector:
    """三观自我反思引擎"""
    
    def __init__(self, worldview: ResearcherWorldview):
        self.worldview = worldview
    
    def reflect_on_debate(
        self,
        debate_id: str,
        my_arguments: List[str],
        opponent_arguments: List[str],
        debate_outcome: str,
        actual_market_outcome: Optional[float] = None
    ) -> WorldviewPerformance:
        """
        辩论后反思：我的三观在这次辩论中表现如何？
        """
        performance = WorldviewPerformance(
            debate_id=debate_id,
            timestamp=datetime.now().isoformat(),
            argument_accepted=True,  # 简化：假设论据都被采纳
            debate_outcome=debate_outcome,
            actual_market_outcome=actual_market_outcome,
            what_worked=[],
            what_failed=[],
            adjustment_needed=False,
        )
        
        # 分析Bull的表现
        if self.worldview.role == "bull":
            if debate_outcome == "bullish" and (actual_market_outcome is None or actual_market_outcome > 0):
                performance.what_worked.append("乐观论据得到验证")
                performance.what_worked.append("基本面分析准确")
            elif debate_outcome == "bearish" or (actual_market_outcome and actual_market_outcome < 0):
                performance.what_failed.append("忽略了关键风险")
                performance.what_failed.append("过度乐观评估")
                performance.adjustment_needed = True
        
        # 分析Bear的表现
        elif self.worldview.role == "bear":
            if debate_outcome == "bearish" and (actual_market_outcome is None or actual_market_outcome < 0):
                performance.what_worked.append("风险识别准确")
                performance.what_worked.append("审慎分析有效")
            elif debate_outcome == "bullish" or (actual_market_outcome and actual_market_outcome > 0):
                performance.what_failed.append("过度悲观")
                performance.what_failed.append("忽视了积极因素")
                performance.adjustment_needed = True
        
        # 记录到历史
        self.worldview.performance_history.append(performance.__dict__)
        
        return performance
    
    def should_adjust_worldview(self) -> Tuple[bool, str]:
        """
        判断是否需要调整三观
        
        规则：
        - 连续3次失败 → 需要调整
        - 成功率 < 40% → 需要调整
        """
        if len(self.worldview.performance_history) < 3:
            return False, "数据不足，需要更多辩论记录"
        
        recent_performances = self.worldview.performance_history[-5:]
        failures = sum(1 for p in recent_performances if p.get("adjustment_needed", False))
        
        if failures >= 3:
            return True, f"最近5次辩论中有{failures}次失败，需要调整"
        
        total = len(self.worldview.performance_history)
        total_failures = sum(1 for p in self.worldview.performance_history if p.get("adjustment_needed", False))
        success_rate = 1 - (total_failures / total)
        
        if success_rate < 0.4:
            return True, f"总体成功率{success_rate:.1%}过低，需要调整"
        
        return False, f"表现良好（成功率{success_rate:.1%}），暂不调整"
    
    def adjust_worldview(self, adjustment_type: str = "minor"):
        """
        动态调整三观
        
        调整策略：
        - 核心信念：固定不变
        - 数据优先级：可以微调（±5%）
        - 质量阈值：可以微调（±5%）
        """
        if adjustment_type == "minor":
            # 微调数据优先级（基于最近的失败）
            recent_failures = [
                p for p in self.worldview.performance_history[-5:]
                if p.get("adjustment_needed", False)
            ]
            
            # 示例：如果失败，提高基本面权重
            if self.worldview.role == "bull":
                self.worldview.data_priorities["fundamentals"] = min(
                    0.50, self.worldview.data_priorities["fundamentals"] + 0.05
                )
            elif self.worldview.role == "bear":
                self.worldview.data_priorities["sentiment"] = min(
                    0.40, self.worldview.data_priorities["sentiment"] + 0.05
                )
            
            # 微调质量阈值
            for key in self.worldview.quality_thresholds:
                current = self.worldview.quality_thresholds[key]
                # 随机微调 ±2%
                adjustment = 0.02 if len(recent_failures) > 2 else -0.02
                self.worldview.quality_thresholds[key] = max(0.60, min(0.90, current + adjustment))
        
        self.worldview.last_updated = datetime.now().isoformat()

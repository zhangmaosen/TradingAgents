"""
Philosophical Researcher
Bull/Bear Researcher with Complete Philosophical Worldview System

Core Features:
1. Filter data based on worldview
2. Select strategies based on research purpose
3. Validate argument quality based on values
4. Generate detailed decision logs (explainability)
5. Self-reflection and evolution after debates
"""

from typing import Dict, List, Optional
import json
from datetime import datetime

from tradingagents.agents.utils.researcher_worldview import (
    ResearcherWorldview,
    WorldviewValidator,
    WorldviewReflector,
)
from tradingagents.agents.utils.debate_separator import DEBATE_RESPONSE_SEPARATOR


class PhilosophicalResearcher:
    """Researcher with Investment Philosophy"""
    
    def __init__(
        self,
        role: str,
        llm,
        memory,
        worldview: Optional[ResearcherWorldview] = None,
        enable_logging: bool = True,
    ):
        """
        Initialize
        
        Args:
            role: "bull" or "bear"
            llm: LLM instance
            memory: Memory instance
            worldview: Worldview configuration (if None, use default config)
            enable_logging: Whether to enable detailed logging
        """
        self.role = role
        self.llm = llm
        self.memory = memory
        self.enable_logging = enable_logging
        
        # Initialize worldview
        if worldview is None:
            if role == "bull":
                self.worldview = ResearcherWorldview.create_bull_worldview()
            else:
                self.worldview = ResearcherWorldview.create_bear_worldview()
        else:
            self.worldview = worldview
        
        # Initialize validator and reflector
        self.validator = WorldviewValidator(self.worldview)
        self.reflector = WorldviewReflector(self.worldview)
        
        # Debate history
        self.debate_history = []
    
    def prepare_argument(self, state: Dict) -> Dict:
        """
        Complete workflow for preparing arguments (Core of Solution C)
        
        Process:
        1. Worldview filtering: Select data to focus on
        2. Purpose guidance: Determine argument strategy
        3. Value validation: Verify argument quality
        4. Generate final argument
        5. Record decision log
        """
        
        # Extract data
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        role_history = investment_debate_state.get(f"{self.role}_history", "")
        opponent_argument = investment_debate_state.get("current_response", "")
        
        all_data = {
            "fundamentals": state.get("fundamentals_report", ""),
            "sentiment": state.get("sentiment_report", ""),
            "news": state.get("news_report", ""),
            "market_data": state.get("market_report", ""),
        }
        
        # === Step 1: Worldview filters data ===
        filtered_data = self.validator.filter_data_by_worldview(all_data)
        
        # === Step 1.5: Calculate current debate round ===
        # Count how many times this role has spoken (debate round number)
        current_count = investment_debate_state.get("count", 0)
        round_number = current_count + 1
        
        # === Step 2: Purpose determines strategy (with round-aware evolution) ===
        strategy = self.validator.determine_argument_strategy(
            filtered_data,
            opponent_argument,
            round_number=round_number
        )
        
        # === Step 3: Retrieve past experiences from memory ===
        curr_situation = self._build_situation_string(filtered_data)
        past_memories = self.memory.get_memories(curr_situation, n_matches=2)
        
        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"
        
        # === Step 4: Generate argument with self-assessment ===
        argument, evidence = self._generate_argument_with_assessment(
            filtered_data=filtered_data,
            strategy=strategy,
            history=history,
            opponent_argument=opponent_argument,
            past_memories=past_memory_str,
        )
        
        # === Step 5: Quality validation ===
        passes_quality, quality_check = self.validator.validate_argument_quality(
            argument,
            evidence
        )
        
        # If quality is insufficient, regenerate (max 1 retry)
        if not passes_quality and self.enable_logging:
            print(f"\n⚠️  {self.role.upper()} argument quality insufficient, regenerating...\n")
            
            # Add quality feedback to prompt
            quality_feedback = "\n".join(quality_check["issues"])
            argument, evidence = self._regenerate_argument_with_assessment(
                original_argument=argument,
                quality_feedback=quality_feedback,
                filtered_data=filtered_data,
                strategy=strategy,
            )
            
            # Re-validate
            passes_quality, quality_check = self.validator.validate_argument_quality(
                argument,
                evidence
            )
        
        # === Step 6: Format output ===
        formatted_argument = f"{self.role.capitalize()} Analyst: {argument}"
        
        # === Step 7: Update state ===
        new_investment_debate_state = {
            "history": history + DEBATE_RESPONSE_SEPARATOR + formatted_argument if history else formatted_argument,
            f"{self.role}_history": role_history + DEBATE_RESPONSE_SEPARATOR + formatted_argument if role_history else formatted_argument,
            f"{'bear' if self.role == 'bull' else 'bull'}_history": investment_debate_state.get(f"{'bear' if self.role == 'bull' else 'bull'}_history", ""),
            "current_response": formatted_argument,
            "count": investment_debate_state["count"] + 1,
        }
        
        # === Step 8: Save decision log ===
        if self.enable_logging:
            # Use company_of_interest instead of ticker
            ticker = state.get("company_of_interest", state.get("ticker", "UNKNOWN"))
            self._save_decision_log(ticker)
        
        return {"investment_debate_state": new_investment_debate_state}
    
    def _build_situation_string(self, filtered_data: Dict) -> str:
        """Build situation description string"""
        parts = []
        for data_type, data_info in filtered_data.items():
            content = data_info["content"]
            # Truncate to first 500 characters
            truncated = content[:500] + "..." if len(content) > 500 else content
            parts.append(truncated)
        return "\n\n".join(parts)
    
    def _generate_argument(
        self,
        filtered_data: Dict,
        strategy: Dict,
        history: str,
        opponent_argument: str,
        past_memories: str,
    ) -> str:
        """
        Generate argument (legacy method, kept for backward compatibility)
        
        Use _generate_argument_with_assessment instead for quality validation
        """
        argument, _ = self._generate_argument_with_assessment(
            filtered_data, strategy, history, opponent_argument, past_memories
        )
        return argument
    
    def _generate_argument_with_assessment(
        self,
        filtered_data: Dict,
        strategy: Dict,
        history: str,
        opponent_argument: str,
        past_memories: str,
    ) -> tuple[str, Dict]:
        """
        Generate argument with self-assessment (core LLM call)
        
        Returns:
            tuple: (argument_text, evidence_dict)
        """
        
        # Build data section (sorted by weight)
        data_strings = []
        for data_type, data_info in sorted(
            filtered_data.items(),
            key=lambda x: x[1]["weight"],
            reverse=True
        ):
            data_strings.append(
                f"{data_type.upper()} (Weight {data_info['weight']:.0%}):\n{data_info['content']}"
            )
        data_section = "\n\n".join(data_strings)
        
        # Build prompt based on role
        if self.role == "bull":
            messages = self._build_bull_messages_with_assessment(
                data_section, strategy, history, opponent_argument, past_memories
            )
        else:
            messages = self._build_bear_messages_with_assessment(
                data_section, strategy, history, opponent_argument, past_memories
            )
        
        # Call LLM with proper message format
        response = self.llm.invoke(messages)
        
        # Parse JSON response with preprocessing
        try:
            # Preprocess the response content to handle various LLM formats
            json_str = self._preprocess_json_response(response.content)
            result = json.loads(json_str)
            argument = result.get("argument", response.content)
            evidence = {
                "strength": result.get("evidence_strength", 0.75),
                "clarity": result.get("logic_clarity", 0.75),
                "type": result.get("argument_type", "balanced_analysis"),
            }
        except json.JSONDecodeError as e:
            # Fallback: if LLM doesn't return valid JSON, use the raw response
            if self.enable_logging:
                print(f"⚠️  Warning: LLM did not return valid JSON, using raw response")
                print(f"   Error: {e}")
                print(f"   Raw content: {response.content[:200]}...")
            argument = response.content
            evidence = {
                "strength": 0.75,
                "clarity": 0.75,
                "type": "balanced_analysis",
            }
        
        return argument, evidence
    
    def _preprocess_json_response(self, content: str) -> str:
        """
        Preprocess LLM response to extract and clean JSON content.
        
        Handles various LLM response formats:
        - Zhipu: json\n{...}
        - OpenAI: ```json\n{...}\n```
        - Claude: ```\n{...}\n```
        - Raw: {...}
        
        Returns:
            str: Clean JSON string ready for parsing
        """
        if not content:
            raise ValueError("Empty response content")
        
        # Remove markdown code block markers (```json or ```)
        content = content.strip()
        
        # Handle markdown code blocks: ```json\n{...}\n``` or ```\n{...}\n```
        if content.startswith("```"):
            # Remove opening ```json or ```
            content = content[3:]  # Remove ```
            # Check if there's "json" after ```
            if content.startswith("json"):
                content = content[4:]  # Remove "json"
            # Remove leading whitespace and newlines
            content = content.lstrip()
            # Remove closing ```
            if content.endswith("```"):
                content = content[:-3]
            # Remove trailing whitespace
            content = content.rstrip()
        
        # Handle Zhipu format: json\n{...}
        if content.startswith("json"):
            content = content[4:]  # Remove "json"
            content = content.lstrip()  # Remove leading whitespace
        
        # Handle escaped newlines and quotes that some LLMs add
        # Be careful: only unescape if it's clearly escaped JSON content
        if "\\n" in content and not "\n" in content[:50]:  # Check if still escaped
            # This looks like escaped content, try to unescape it partially
            # But first verify it's actually JSON
            pass  # Keep escaped for now, json.loads will handle it
        
        # Final cleanup: strip any remaining whitespace
        content = content.strip()
        
        # Validate that it looks like JSON
        if not (content.startswith("{") and content.endswith("}")):
            # Try to find JSON object within the content
            import re
            # Look for first { and last }
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                content = match.group(0)
            else:
                raise ValueError(f"No valid JSON object found in: {content[:100]}")
        
        return content
    
    def _get_round_specific_guidance(self, round_number: int, opponent_argument: str) -> str:
        """Generate specific guidance for each debate round"""
        if round_number == 1:
            return """ROUND 1 GUIDANCE:
• You're opening the debate - make a strong first impression
• Lead with your strongest evidence and most convincing points
• Frame the narrative that will guide future arguments
• Set a high bar for clarity and evidence quality"""
        
        elif round_number == 2:
            if opponent_argument:
                return """ROUND 2 GUIDANCE:
• The bear has made their opening case - analyze their specific claims
• Find NEW angles that weren't covered in round 1 - don't just repeat
• Look for logical gaps or unsupported assumptions in their argument
• Deepen your analysis by introducing data the bear overlooked
• Expand your position while still directly engaging with their points"""
            else:
                return """ROUND 2 GUIDANCE:
• Deepen your position with additional evidence and insights
• Go beyond the basic case - explore nuances and subtleties
• Strengthen your argument through more sophisticated analysis"""
        
        else:  # Round 3+
            if opponent_argument:
                return f"""ROUND {round_number} GUIDANCE (FINAL AGGRESSIVE ROUND):
• This is your last opportunity - be decisive and direct
• Ruthlessly expose the weakest points in the bear's reasoning
• Don't hedge or qualify - make your strongest statements
• Use specific data to counter each specific bear claim
• Show how the bear's assumptions are flawed or outdated
• Conclude with the most compelling reason to invest NOW"""
            else:
                return f"""ROUND {round_number} GUIDANCE:
• Strengthen and crystallize your investment thesis
• Address any remaining uncertainties with compelling evidence
• Make your final, most convincing case"""
    
    def _build_bull_messages_with_assessment(
        self,
        data_section: str,
        strategy: Dict,
        history: str,
        opponent_argument: str,
        past_memories: str,
    ) -> list:
        """Build Bull's messages with self-assessment requirement"""
        
        # System message: Define role, philosophy, and rules
        system_content = f"""🎯 YOUR ROLE: Bull Analyst (Optimistic Case Builder)
You are responsible for evaluating MODEL 5: Assumption Chain Strength

Your task: Build a strong, evidence-based BULLISH case emphasizing growth potential, competitive advantages, and positive indicators. Engage directly with the bear argument using data-backed counterarguments.

## Your Workflow

### Step 1: Build Your Assumption Chain (CRITICAL)

Before stating conclusions, explicitly list your core assumptions:

**Assumption 1: Business Foundation** (Most critical)
- [What must be true for this company to succeed?]
- My probability estimate: __% 
- Reasoning: [historical precedent, execution evidence, external risks]

**Assumption 2: Growth Potential**
- [What must be true for revenue/market share to expand as predicted?]
- My probability estimate: __%
- Reasoning: [market size, competitive position, expansion pathway]

**Assumption 3: Financial Pathway**
- [What must be true for the company to achieve profitability/cash flow?]
- My probability estimate: __%
- Reasoning: [unit economics, margin expansion, cost control]

**Assumption 4: Market Recognition**
- [What must be true for the market to recognize and price this story?]
- My probability estimate: __%
- Reasoning: [narrative clarity, proof points, analyst coverage]

**Assumption 5 (Optional): Competitive Position**
- [What must be true for sustainable competitive advantages?]
- My probability estimate: __%
- Reasoning: [moat strength, pricing power, defensibility]

### Step 2: Calculate Synthetic Probability

**Combined Probability = Probability_A1 × Probability_A2 × Probability_A3 × Probability_A4**

This often reveals much lower real probability than general sentiment expects!

### Step 3: Meta-Cognitive Check

**Question 1: How objective am I really being?**
- Am I seeking supporting evidence? Or truth?
- Can I honestly list 3 reasons the bull case fails?

**Question 2: What's my biggest blind spot?**
- What assumption am I most likely underestimating risk on?
- Where would professional skeptics push back hardest?

**Question 3: Management execution credibility**
- Has this management team executed on past promises?
- Or do they have a pattern of missing?

**Question 4: Time horizon**
- This bull case—how long until market validates it?
- What if time horizon doubles? Still works?

**Question 5: Certainty Level**
- My certainty: [30% / 60% / 75% / 90%]
- If < 60%, reduce score by 1 point

## Output Requirements

YOU MUST respond with a JSON object:
{{
  "assumption_1_probability": 0.XX,  // Your estimate (0-1)
  "assumption_2_probability": 0.XX,
  "assumption_3_probability": 0.XX,
  "assumption_4_probability": 0.XX,
  "combined_probability_percent": X.X,  // Product of above 4 as percentage
  "argument": "Your argument here (200-400 words)",
  "evidence_strength": 0.85,  // How specific and data-backed?
  "logic_clarity": 0.90,      // How clear the reasoning?
  "certainty_level": 0.75,    // Your confidence in this assessment
  "biggest_risk": "What's most likely to break this thesis?"
}}

CRITICAL RULES:
- Your response MUST be valid JSON
- Do NOT include any text outside the JSON object
- Show your assumption probabilities explicitly
- Show combined probability calculation
- Your argument should reference actual data from the resources
- Be intellectually honest: Don't just list positives, quantify assumptions

WORLDVIEW CONTEXT:
- Philosophy: {self.worldview.world_view.value}
- Research Purpose: {self.worldview.research_purpose.value}
- Quality Threshold: Evidence ≥ {self.worldview.quality_thresholds['evidence_strength']:.0%}, Logic ≥ {self.worldview.quality_thresholds['logic_clarity']:.0%}"""
        
        # User message: Provide data and context
        user_content = f"""╔══════════════════════════════════════════════════════════════════════════════╗
║                      📊 AVAILABLE RESEARCH DATA                              ║
║              (Sorted by Bull Analyst worldview priorities)                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

{data_section}

╔══════════════════════════════════════════════════════════════════════════════╗
║                     💬 DEBATE CONTEXT & HISTORY                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Current Debate Round:
{history if history else "This is the OPENING of the debate - no prior arguments yet. Establish your position strongly."}

╔══════════════════════════════════════════════════════════════════════════════╗
║                  ⚠️ OPPONENT'S ARGUMENT (Bear's Position)                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

{opponent_argument if opponent_argument else "No bear argument yet - This is your opening statement opportunity."}

💡 YOUR TASK: Directly engage with these points if they exist. Show why the bull case is stronger.

╔══════════════════════════════════════════════════════════════════════════════╗
║                   📚 LESSONS FROM PAST SITUATIONS                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

Similar situations and reflections learned:
{past_memories if past_memories else "No past lessons available - approach this as a fresh analysis."}

╔══════════════════════════════════════════════════════════════════════════════╗
║                        🎯 YOUR SPECIFIC TASK                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

1. ANALYZE the available data through a BULL lens:
   - What growth signals are present?
   - What competitive advantages stand out?
   - What positive indicators support investment?

2. UNDERSTAND the opponent's position (if exists):
   - What specific claims did the bear make in round {strategy['round_number']-1 if strategy['round_number'] > 1 else 0}?
   - What data or logic are they relying on?
   - What assumptions underlie their concerns?

3. BUILD a compelling bull case by:
   - Starting with your strongest evidence
   - For Round 1: Establish core thesis with maximum clarity
   - For Round 2+: Introduce NEW angles and deeper insights not covered before
   - Connecting data points into a coherent narrative
   - Showing realistic upside scenarios

4. COUNTER the bear's concerns by:
   - If Round 1: Preemptively address likely bear concerns
   - If Round 2+: Directly refute the bear's specific claims from their last argument
   - Acknowledge valid points but contextualize them
   - Provide counterevidence that outweighs their negative points
   - Explain why bull opportunities are more compelling than bear risks

5. PRESENT your argument in:
   - Conversational, engaging language
   - 200-400 words total
   - Debate-ready format (directly addressing the bear's points)
   - For Round 3+: Be more aggressive and decisive

6. ASSESS your own argument's quality:
   - How many concrete data points did you use? (evidence_strength)
   - How clear is your reasoning chain? (logic_clarity)
   - What type of argument did you make? (argument_type)

ROUND {strategy['round_number']} FOCUS:
{strategy['round_instruction']}

Now generate your compelling BULL ANALYST argument with self-assessment in JSON format:
"""
        
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]
    

    
    def _build_bear_messages_with_assessment(
        self,
        data_section: str,
        strategy: Dict,
        history: str,
        opponent_argument: str,
        past_memories: str,
    ) -> list:
        """Build Bear's messages with self-assessment requirement"""
        
        # System message: Define role, philosophy, and rules
        system_content = f"""🎯 YOUR ROLE: Bear Analyst (Critical Case Challenger)
You are responsible for evaluating MODEL 5: Assumption Chain Fragility

Your task: Systematically challenge the bull case by examining WHICH assumptions are most fragile, likely to break, or underestimated in probability. Show where the bull's confidence exceeds the evidence.

## Your Workflow

### Step 1: Extract Bull's Assumption Chain

From the bull argument, identify their core assumptions:

**Assumption 1: Business Foundation**
- What they're assuming: [extracted from their argument]
- Their claimed probability: __%
- My assessment: [Overconfident? Underconfident?]

**Assumption 2: Growth Potential**
- What they're assuming: [extracted from their argument]
- Their claimed probability: __%
- My assessment: [Realistic? Too optimistic?]

**Assumption 3: Financial Pathway**
- What they're assuming: [extracted from their argument]
- Their claimed probability: __%
- My assessment: [Achievable? Too many steps?]

**Assumption 4: Market Recognition**
- What they're assuming: [extracted from their argument]
- Their claimed probability: __%
- My assessment: [Priced in? Or timing risk?]

### Step 2: Challenge Probabilities with Evidence

For EACH assumption, present a competing probability:

**Evidence for Lower Probability:**
- Historical pattern: [Similar companies failed because...]
- Execution risk: [Management hasn't shown ability to...]
- Market headwinds: [Industry trends suggest...]
- Financial constraints: [Cost structure shows...]
- Competitive reality: [Competitors are...]

**Recalibrated Probability: __%**
(Usually 20-40% lower than bull's estimate)

### Step 3: Calculate Fragility Score

**Fragility Index = 1 - (Recalibrated Combined Probability)**

If bull's combined probability = 45%, and my recalibrated = 25%
Fragility Score = 1 - 0.25 = 0.75 (75% fragile!)

**Identify Weakest Link:**
Which single assumption breaks the entire thesis if wrong?
- Usually this is Assumption 1 or 2
- Focus here: "If this fails, thesis collapses"

### Step 4: Meta-Cognitive Check (Honest Self-Review)

**Question 1: Am I being fairly skeptical or just negative?**
- Can I name 3 things the bull got RIGHT?
- Or am I just contrarian for contrarian's sake?

**Question 2: What would change my mind?**
- What specific evidence would make me 60% confident instead of 30%?
- Am I actually open to being wrong?

**Question 3: Timing vs Thesis**
- Is the company doomed? Or just wrong timing?
- (Very different outcomes!)

**Question 4: Where's my bias?**
- Am I naturally pessimistic about tech/growth stocks?
- Do I have incentive to be bearish?

**Question 5: Certainty Level**
- My certainty: [30% / 60% / 75% / 90%]
- If < 60%, reduce fragility by 1 point

## Output Requirements

YOU MUST respond with a JSON object:
{{
  "bull_combined_probability": 0.45,  // What the bull estimated
  "recalibrated_probability": 0.28,   // Your more realistic estimate
  "fragility_index": 0.72,            // 1 - recalibrated_probability
  "weakest_link": "Assumption 1: The market is growing fast enough",
  "argument": "Your argument here (200-400 words)",
  "evidence_strength": 0.80,  // How data-backed is your skepticism?
  "logic_clarity": 0.85,      // How clear is your reasoning?
  "certainty_level": 0.65     // Your confidence in this fragility assessment
}}

CRITICAL RULES:
- Your response MUST be valid JSON
- Do NOT include any text outside the JSON object
- Show recalibrated probabilities explicitly
- Identify the weakest link clearly
- Your argument should reference actual data
- Be intellectually honest: Acknowledge what bull got right, show specifically where overconfident

WORLDVIEW CONTEXT:
- Philosophy: {self.worldview.world_view.value}
- Research Purpose: {self.worldview.research_purpose.value}
- Risk View: {self.worldview.core_beliefs['risk_view']}
- Quality Threshold: Evidence ≥ {self.worldview.quality_thresholds['evidence_strength']:.0%}, Logic ≥ {self.worldview.quality_thresholds['logic_clarity']:.0%}"""
        
        # User message: Provide data and context
        user_content = f"""╔══════════════════════════════════════════════════════════════════════════════╗
║                      📊 AVAILABLE RESEARCH DATA                              ║
║              (Sorted by Bear Analyst worldview priorities)                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

{data_section}

╔══════════════════════════════════════════════════════════════════════════════╗
║                     💬 DEBATE CONTEXT & HISTORY                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Current Debate Round:
{history if history else "This is the OPENING of the debate - no prior arguments yet. Establish your defensive position strongly."}

╔══════════════════════════════════════════════════════════════════════════════╗
║                  ⚠️ OPPONENT'S ARGUMENT (Bull's Position)                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

{opponent_argument if opponent_argument else "No bull argument yet - This is your opening statement opportunity to raise critical concerns."}

💡 YOUR TASK: Directly challenge these points if they exist. Expose why the risks outweigh the opportunities.

╔══════════════════════════════════════════════════════════════════════════════╗
║                   📚 LESSONS FROM PAST SITUATIONS                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

Similar situations and reflections learned:
{past_memories if past_memories else "No past lessons available - approach this as a fresh risk analysis."}

╔══════════════════════════════════════════════════════════════════════════════╗
║                        🎯 YOUR SPECIFIC TASK                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

1. ANALYZE the available data through a BEAR lens:
   - What risks and challenges are present?
   - What competitive weaknesses stand out?
   - What negative indicators suggest caution?

2. UNDERSTAND the opponent's position (if exists):
   - What specific claims did the bull make in round {strategy['round_number']-1 if strategy['round_number'] > 1 else 0}?
   - What opportunities are they highlighting?
   - What assumptions underlie their bullish thesis?

3. BUILD a compelling bear case by:
   - Starting with the most critical risks
   - For Round 1: Establish core risk thesis with maximum clarity
   - For Round 2+: Introduce NEW risks and deeper analysis not covered before
   - Connecting risk factors into a coherent risk narrative
   - Showing realistic downside scenarios

4. COUNTER the bull's optimism by:
   - If Round 1: Preemptively expose likely bull blind spots
   - If Round 2+: Directly challenge the bull's specific claims from their last argument
   - Acknowledge their points but question assumptions and feasibility
   - Provide evidence that contradicts bull claims
   - Explain why the downside risk > upside opportunity

5. PRESENT your argument in:
   - Conversational, engaging language
   - 200-400 words total
   - Debate-ready format (directly challenging the bull's points)
   - For Round 3+: Be more aggressive and direct about flaws

6. ASSESS your own argument's quality:
   - How many concrete risk factors did you identify? (evidence_strength)
   - How clear is your risk analysis chain? (logic_clarity)
   - What type of argument did you make? (argument_type)

ROUND {strategy['round_number']} FOCUS:
{strategy['round_instruction']}

Now generate your compelling BEAR ANALYST argument with self-assessment in JSON format:
"""
        
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]
    
    def _regenerate_argument_with_assessment(
        self,
        original_argument: str,
        quality_feedback: str,
        filtered_data: Dict,
        strategy: Dict,
    ) -> tuple[str, Dict]:
        """Regenerate argument with self-assessment based on quality feedback"""
        
        # System message: Role as quality improver
        system_content = f"""You are a {self.role.capitalize()} Analyst who needs to improve an argument that didn't meet quality standards.

Your Investment Philosophy:
- Worldview: {self.worldview.world_view.value}
- Research Purpose: {self.worldview.research_purpose.value}
- Quality Standard: {self.worldview.argument_quality.value}

Quality Requirements:
- Evidence strength ≥ {self.worldview.quality_thresholds.get('evidence_strength', 0.75):.0%}
- Logic clarity ≥ {self.worldview.quality_thresholds.get('logic_clarity', 0.75):.0%}
- Forbidden argument types: {', '.join(self.worldview.forbidden_argument_types)}

╔══════════════════════════════════════════════════════════════════════════════╗
║                       OUTPUT REQUIREMENTS                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

You MUST respond with a JSON object in the following format:
{{
  "argument": "Your improved argument text here",
  "evidence_strength": 0.90,  // Score 0-1: Improved evidence strength
  "logic_clarity": 0.92,      // Score 0-1: Improved logic clarity
  "argument_type": "balanced_analysis"
}}

CRITICAL: Your response must be valid JSON. Do not include any text outside the JSON object.
"""
        
        # User message: Provide the feedback
        user_content = f"""╔══════════════════════════════════════════════════════════════════════════════╗
║                       ORIGINAL ARGUMENT                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

{original_argument}

╔══════════════════════════════════════════════════════════════════════════════╗
║                       QUALITY ISSUES                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

{quality_feedback}

╔══════════════════════════════════════════════════════════════════════════════╗
║                    IMPROVEMENT REQUIREMENTS                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

Regenerate your argument addressing the quality issues above. Ensure your self-assessment scores are higher than before.

Generate improved argument with self-assessment in JSON format:
"""
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]
        
        response = self.llm.invoke(messages)
        
        # Parse JSON response with preprocessing
        try:
            # Preprocess the response content
            json_str = self._preprocess_json_response(response.content)
            result = json.loads(json_str)
            argument = result.get("argument", response.content)
            evidence = {
                "strength": result.get("evidence_strength", 0.85),
                "clarity": result.get("logic_clarity", 0.85),
                "type": result.get("argument_type", "balanced_analysis"),
            }
        except json.JSONDecodeError as e:
            if self.enable_logging:
                print(f"⚠️  Warning: LLM did not return valid JSON in regeneration, using raw response")
                print(f"   Error: {e}")
            argument = response.content
            evidence = {
                "strength": 0.85,
                "clarity": 0.85,
                "type": "balanced_analysis",
            }
        
        return argument, evidence
    
    def _save_decision_log(self, ticker: str):
        """Save decision log to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = f"results/{ticker}/worldview_logs"
        
        import os
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = f"{log_dir}/{self.role}_{timestamp}.md"
        self.validator.save_decision_log(log_file)
        
        print(f"✓ {self.role.upper()} worldview decision log saved: {log_file}")
    
    def reflect_on_debate(
        self,
        debate_id: str,
        my_arguments: List[str],
        opponent_arguments: List[str],
        debate_outcome: str,
        actual_market_outcome: Optional[float] = None
    ):
        """
        Post-debate reflection
        
        Args:
            debate_id: Debate ID
            my_arguments: My list of arguments
            opponent_arguments: Opponent's list of arguments
            debate_outcome: Debate result ("bullish"/"bearish"/"neutral")
            actual_market_outcome: Actual market outcome (optional)
        """
        
        # Reflect
        performance = self.reflector.reflect_on_debate(
            debate_id=debate_id,
            my_arguments=my_arguments,
            opponent_arguments=opponent_arguments,
            debate_outcome=debate_outcome,
            actual_market_outcome=actual_market_outcome,
        )
        
        # Check if adjustment is needed
        should_adjust, reason = self.reflector.should_adjust_worldview()
        
        if should_adjust:
            print(f"\n{'='*80}")
            print(f"⚠️  {self.role.upper()} worldview needs adjustment")
            print(f"{'='*80}")
            print(f"Reason: {reason}")
            print(f"\nData priorities before adjustment: {self.worldview.data_priorities}")
            
            # Execute adjustment
            self.reflector.adjust_worldview(adjustment_type="minor")
            
            print(f"Data priorities after adjustment: {self.worldview.data_priorities}")
            print(f"{'='*80}\n")
        
        return performance
    
    def get_worldview_summary(self) -> str:
        """Get worldview summary (for reports)"""
        return f"""
{'='*80}
{self.role.upper()} RESEARCHER INVESTMENT PHILOSOPHY SUMMARY
{'='*80}

WORLDVIEW: {self.worldview.world_view.value}
{self.worldview.core_beliefs['market_nature']}

RESEARCH PURPOSE: {self.worldview.research_purpose.value}
{self.worldview.core_beliefs['debate_goal']}

ARGUMENT QUALITY STANDARD: {self.worldview.argument_quality.value}
Quality Thresholds: {json.dumps(self.worldview.quality_thresholds, indent=2, ensure_ascii=False)}

DATA PRIORITIES:
{json.dumps(self.worldview.data_priorities, indent=2, ensure_ascii=False)}

FORBIDDEN ARGUMENT TYPES:
{', '.join(self.worldview.forbidden_argument_types)}

HISTORICAL PERFORMANCE:
Total Debates: {len(self.worldview.performance_history)}
Last Updated: {self.worldview.last_updated}
{'='*80}
        """


def create_philosophical_bull_researcher(llm, memory, worldview=None, enable_logging=True):
    """Create Philosophical Bull Researcher"""
    researcher = PhilosophicalResearcher(
        role="bull",
        llm=llm,
        memory=memory,
        worldview=worldview,
        enable_logging=enable_logging,
    )
    return researcher.prepare_argument


def create_philosophical_bear_researcher(llm, memory, worldview=None, enable_logging=True):
    """Create Philosophical Bear Researcher"""
    researcher = PhilosophicalResearcher(
        role="bear",
        llm=llm,
        memory=memory,
        worldview=worldview,
        enable_logging=enable_logging,
    )
    return researcher.prepare_argument

from langchain_core.messages import AIMessage
import time
import json
from tradingagents.agents.utils.debate_separator import DEBATE_RESPONSE_SEPARATOR


def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""🎯 YOUR ROLE: Bull Analyst (Optimistic Case Builder)
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

Example:
- A1: 50% (business model works)
- A2: 60% (market grows as expected)
- A3: 70% (path to profitability achievable)
- A4: 50% (market recognizes story)
- Combined: 0.5 × 0.6 × 0.7 × 0.5 = **10.5%**

This may be MUCH lower than general bullish sentiment expects!

### Step 3: Assumption Chain Strength Score (0-10)

**Base Score from Combined Probability:**
- > 50% → 7 (Strong case)
- 30-50% → 5 (Medium case)
- 10-30% → 3 (Weak case)
- < 10% → 1 (Very weak case)

**Bonus Points:**
- Multiple independent value drivers (not all dependent on one thing) → +1
- Strong management execution history → +1
- Favorable market conditions → +1

**Penalty Points:**
- "All or nothing" characteristics (no middle ground) → -1
- Unproven management team → -1
- Adverse market trends → -1

**Final Score = Base + Bonuses - Penalties**

### Step 4: Meta-Cognitive Check

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

### Step 5: Output Format

Provide comprehensive bull argument containing:

1. **Assumption Chain**
   ```
   Assumption 1 (Foundation): __ %
   Assumption 2 (Growth): __ %
   Assumption 3 (Financials): __ %
   Assumption 4 (Recognition): __ %
   
   Combined Probability: ** __ % **
   Assumption Chain Strength: ** __ /10 **
   ```

2. **Key Growth Drivers**
   - Market opportunity: [specific TAM]
   - Competitive advantages: [defensibility]
   - Expansion pathway: [how to scale]

3. **Financial Health**
   - Unit economics: [positive or on path]
   - Margin trajectory: [improvement direction]
   - Cash burn assessment: [sustainability]

4. **Positive Indicators**
   - Market trends supporting: [relevant data]
   - Recent wins/momentum: [latest proof]
   - Sentiment signals: [bullish indicators]

5. **Counter to Bear Argument**
   - What's the bear's strongest point? [acknowledge]
   - Why it's overstated: [data-backed response]
   - Alternative interpretation: [your view]

6. **Risk Acknowledgment**
   - Biggest assumption at risk: [most fragile link]
   - Time sensitivity: [how urgent]
   - Failure condition: [when you'd be wrong]

---

**Key Guidance:**
- THIS IS NOT BLIND OPTIMISM. You must show synthetic probability calculation.
- Use specific numbers, not vague language.
- Directly address bear concerns with data, not dismissal.
- Most importantly: Be intellectually honest about probability, not just the direction.

**Remember:**
- Your job is to build the STRONGEST possible bull case
- NOT to convince—to illuminate
- Include assumption breakdown so readers can judge themselves
- Certainty is clarity, not confidence"""

        response = llm.invoke(prompt)

        argument = f"Bull Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + DEBATE_RESPONSE_SEPARATOR + argument if history else argument,
            "bull_history": bull_history + DEBATE_RESPONSE_SEPARATOR + argument if bull_history else argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node

from langchain_core.messages import AIMessage
import time
import json
from tradingagents.agents.utils.debate_separator import DEBATE_RESPONSE_SEPARATOR


def create_bear_researcher(llm, memory):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")

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

        prompt = f"""🎯 YOUR ROLE: Bear Analyst (Critical Case Builder)
You are responsible for questioning MODEL 5: Assumption Chain Fragility

Your task: Build a strong, evidence-based BEARISH case exposing risks and challenging optimistic assumptions. Systematically question each bull assumption with data-backed counterarguments.

## Your Workflow

### Step 1: Extract Bull's Assumptions

From the bull argument, identify the core assumptions:

**Question each one:** Does this really hold up?
- Assumption 1: [Bull claims this probability: __%, I assess: __%]
  Why I'm skeptical: [specific reasons]
  
- Assumption 2: [Bull claims: __%, I assess: __%]
  Why I'm skeptical: [specific reasons]
  
- Assumption 3: [Bull claims: __%, I assess: __%]
  Why I'm skeptical: [specific reasons]
  
- Assumption 4: [Bull claims: __%, I assess: __%]
  Why I'm skeptical: [specific reasons]

### Step 2: Challenge Probabilities With Evidence

Don't just say "risky"—provide specific recalibrations:

**Evidence-Based Downgrade:**
- Bull says: "Product-market fit achieved, 70% confidence"
- My assessment: "25% confidence"
- Reasons:
  * Historical precedent: Similar companies in this space took 3-5 years longer
  * Execution risk: Management has missed timelines before
  * Market saturation: Competitors already have 40% market share
  * Regulatory uncertainty: [specific risk]

### Step 3: Calculate Recalibrated Synthetic Probability

**Bear's version:**
- A1: 25% (Bull's 50%)
- A2: 35% (Bull's 60%)
- A3: 40% (Bull's 70%)
- A4: 30% (Bull's 50%)
- Combined: 0.25 × 0.35 × 0.4 × 0.3 = **1.05%**

vs. Bull's claimed 10.5%

This is the power of systematic assumption questioning.

### Step 4: Assumption Chain Fragility Score (0-10)

**Key Concept: Weakest Link = Chain Strength**

If the four assumptions are: 25%, 35%, 40%, 30%
- Weakest link = 25%
- This determines overall chain robustness

**Fragility Score Calculation:**
- Weakest assumption > 50% → Fragility score 1-2 (Strong)
- Weakest assumption 30-50% → Fragility score 3-4 (Medium)
- Weakest assumption 10-30% → Fragility score 5-7 (High fragility)
- Weakest assumption < 10% → Fragility score 8-10 (Extremely fragile)

**Additional Fragility Factors:**
- Assumptions highly correlated (all fail together) → +2
- Management execution history poor → +1
- "All or nothing" business model → +1

**Final Score = Base + Factors**

### Step 5: Identify Weakest Link

**This is critical:**
"If I had to bet my money on which assumption breaks first, it would be [Assumption X]"

Why? [Be specific]

### Step 6: Risk Acknowledgment Check

**Question for myself:**
- Am I being overly pessimistic?
- Could there be scenarios where bull is right?
- What conditions would make me change my mind?

**State this explicitly:**
"Bull could be right if [specific conditions], but probability is only __%"

### Step 7: Meta-Cognitive Check

**Question 1: Am I just being contrarian for contrarian's sake?**
- Can I point to specific, concrete evidence?
- Or am I just finding reasons to doubt?

**Question 2: What's the bull's strongest counter to my critique?**
- What would most undermine my argument?
- How do I respond?

**Question 3: Management credibility**
- Has this team failed before?
- Or is this their first major test?

**Question 4: Certainty Level**
- My certainty in the bear case: [30% / 60% / 75% / 90%]
- If < 60%, acknowledge the uncertainty

### Step 8: Output Format

Provide comprehensive bear argument containing:

1. **Bull Assumption Challenge**
   ```
   Bull's Assumption 1: 50% → My Assessment: 25% (75% more conservative)
   Bull's Assumption 2: 60% → My Assessment: 35%
   Bull's Assumption 3: 70% → My Assessment: 40%
   Bull's Assumption 4: 50% → My Assessment: 30%
   
   Bull's Combined Probability: 10.5%
   Bear's Combined Probability: ** 1.05% **
   
   Assumption Chain Fragility Score: ** __ /10 **
   Weakest Link: [Assumption X at __% ]
   ```

2. **Major Risks & Headwinds**
   - Market saturation: [specific data]
   - Financial sustainability: [burn rate, runway]
   - Competitive threats: [specific competitors]
   - Macro headwinds: [economic/regulatory risks]

3. **Historical Analogues**
   - Similar companies: [how they performed]
   - Similar situations: [what happened]
   - Lessons for this case: [implications]

4. **Counter to Bull's Strengths**
   - Bull highlighted: [their key strength]
   - Alternative interpretation: [your skeptical view]
   - Evidence supporting skepticism: [data]

5. **Execution Risk Assessment**
   - Management track record: [proven or unproven]
   - Timeline reliability: [history of delays/hits]
   - Critical milestones: [which ones most at risk]

6. **Survival Scenarios**
   - Worst case: [company failure probability: __% ]
   - Base case: [underperformance probability: __% ]
   - Best case: [bull case happens probability: __% ]

---

**Key Guidance:**
- THIS IS NOT BLIND PESSIMISM. Use specific probability recalibrations.
- Ground every critique in evidence or historical precedent.
- Acknowledge where bull makes valid points—then explain why it's not enough.
- Focus on assumption fragility, not just listing risks.

**Remember:**
- Your job is to expose the WEAKEST assumptions
- NOT to convince everyone to short
- Identify the "breaking point" where bull case collapses
- Show exactly what would have to happen for your bearish forecast to prove wrong"""

        response = llm.invoke(prompt)

        argument = f"Bear Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + DEBATE_RESPONSE_SEPARATOR + argument if history else argument,
            "bear_history": bear_history + DEBATE_RESPONSE_SEPARATOR + argument if bear_history else argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node

# ✅ Agent Prompts Updated to English - With Meta-Cognitive Layer

## Summary

All 5 key agent prompts have been updated from Chinese to English and enhanced with **meta-cognitive thinking layers** to prevent rigid, dogmatic analysis.

---

## What Was Changed

### 1️⃣ Market Analyst (`market_analyst.py`)
**MODEL 1: Signal vs Context (Second-Order Thinking)**

**Key Improvements:**
- ✅ Step 1-2: Data collection and technical signal analysis (existing)
- ✅ **Step 3 (NEW): Context Verification** - Analyzes 5 contextual factors:
  * Company lifecycle stage
  * Price position & trend strength
  * Competitive landscape
  * Fundamental direction
  * Market sentiment phase
  
- ✅ **Step 4 (NEW): Signal Reliability Scoring**
  * Base score from indicator consistency (0-10)
  * Context adjustments (-2 to +2)
  
- ✅ **Step 5 (NEW): Meta-Cognitive Check**
  * 5 critical questions before finalizing score
  * Certainty level assessment
  * Explicit assumption documentation

**Output Changes:**
- Adds explicit "Signal Reliability Score: __ /10"
- Includes context verification results
- Shows certainty level: [30% / 60% / 75% / 90%]

---

### 2️⃣ News Analyst (`news_analyst.py`)
**MODEL 4: Narrative Decay & Emotion Peak**

**Key Improvements:**
- ✅ Step 1-2: Data collection and sentiment analysis (existing)
- ✅ **Step 3 (NEW): Narrative Lifecycle Identification**
  * 5 stages: Early/Growth/Peak/Decay/Bottom
  * Characteristics of each stage
  
- ✅ **Step 4 (NEW): Emotion Peak Detection**
  * 6 specific conditions to check
  * Peak determined by 3+ conditions met
  
- ✅ **Step 5 (NEW): Lifecycle Analysis**
  * Risk level assessment
  * Expected direction prediction
  
- ✅ **Step 6 (NEW): Meta-Cognitive Check**
  * Question peak permanence
  * Historical comparison
  * Self-fulfilling prophecy recognition
  * Certainty assessment

**Output Changes:**
- Adds "⚠️ Emotion Peak Detection: YES/NO"
- Risk level: [Low/Medium/High/Extreme]
- Sentiment Score: 0-10 with adjustments visible
- Certainty level included

---

### 3️⃣ Fundamentals Analyst (`fundamentals_analyst.py`)
**MODEL 2 & 3: Cost Structure + Competitive Landscape**

**Key Improvements:**

**For MODEL 2 (Cost Structure):**
- ✅ **Step 2.1**: Gross margin analysis with trend
- ✅ **Step 2.2**: Unit economics (SaaS/E-commerce/Manufacturing specific)
- ✅ **Step 2.3**: Cash flow quality assessment
- ✅ **Step 2.4**: Sustainability check (Is it real or accounting magic?)

**For MODEL 3 (Competitive Landscape):**
- ✅ **Step 3.1**: Market share tracking
- ✅ **Step 3.2**: Competitive benchmarking table
- ✅ **Step 3.3**: Competitive signal level (L0-L4 framework)
  * L0: Noise (single event)
  * L1: Weak signal (repeated pattern)
  * L2: Strong signal (industry shift)
  * L3: Action signal (market share moving)
  * L4: Confirmation signal (long-term change)

**Meta-Cognitive Additions:**
- ✅ **Step 4**: 5 critical thinking questions
- ✅ **Step 5**: Cost structure score (0-10) with explicit adjustments
- ✅ **Step 6**: Competitive landscape score (0-10) with explicit adjustments

**Output Changes:**
- Separate scores for MODEL 2 and MODEL 3
- Competitive signal level clearly stated
- Sustainability assessment explicit
- Certainty levels for both scores

---

### 4️⃣ Bull Researcher (`bull_researcher.py`)
**MODEL 5: Assumption Chain Strength**

**Key Improvements:**
- ✅ **Step 1 (NEW): Build Assumption Chain**
  * 5 core assumptions explicitly listed:
    1. Business foundation (most critical)
    2. Growth potential
    3. Financial pathway
    4. Market recognition
    5. (Optional) Competitive position
  * Each with probability estimate: __%

- ✅ **Step 2 (NEW): Calculate Synthetic Probability**
  * Combined Probability = P(A1) × P(A2) × P(A3) × P(A4)
  * Often reveals much lower real probability than general sentiment

- ✅ **Step 3 (NEW): Assumption Chain Strength Score**
  * Base score from combined probability
  * Bonus points for diversity and execution history
  * Penalties for all-or-nothing characteristics

- ✅ **Step 4 (NEW): Meta-Cognitive Checks**
  * 5 critical self-assessment questions
  * Acknowledge biggest blind spot
  * Certainty level

**Output Format:**
- Explicit assumption chain with probabilities
- **Combined Probability: __ %** (highlighted)
- **Assumption Chain Strength: __ /10**
- Counter to bear argument with data
- Risk acknowledgment

---

### 5️⃣ Bear Researcher (`bear_researcher.py`)
**MODEL 5: Assumption Chain Fragility**

**Key Improvements:**
- ✅ **Step 1 (NEW): Extract Bull's Assumptions**
  * Identify each assumption bull made
  * Explicitly challenge each one

- ✅ **Step 2 (NEW): Challenge Probabilities**
  * Specific probability recalibrations with evidence
  * NOT just saying "risky"
  * Example: Bull 70% → Bear 25% with specific reasons

- ✅ **Step 3 (NEW): Recalibrated Synthetic Probability**
  * Show bear's combined probability
  * Direct comparison to bull's calculation

- ✅ **Step 4 (NEW): Fragility Score**
  * Key: "Weakest Link = Chain Strength"
  * Identify which assumption is most fragile
  * Score based on weakest link probability

- ✅ **Step 5 (NEW): Identify Weakest Link**
  * Explicitly state which assumption breaks first
  * Be specific about why

- ✅ **Step 6-7 (NEW): Meta-Cognitive Checks**
  * Honest assessment: Am I too pessimistic?
  * What conditions would make bear wrong?
  * Management credibility assessment

**Output Format:**
- Bull vs Bear probability recalibrations side-by-side
- **Bear's Combined Probability: __ %** (highlighted)
- **Fragility Score: __ /10**
- Weakest link clearly identified
- Conditions where bear could be wrong
- Certainty level stated

---

## Key Features of the New Approach

### 1. Meta-Cognitive Layer (Prevents Dogmatism)

Every agent now includes explicit self-questioning:

```
Common meta questions across all agents:
- What are my assumptions?
- Am I seeing all angles?
- How certain am I really?
- Where's my blind spot?
- Under what conditions am I wrong?
```

### 2. Explicit Probability Estimation

Bull and Bear researchers now calculate **synthetic probabilities** instead of vague sentiment:

- Bull: Combined assumption probability = 10.5%
- Bear: Combined assumption probability = 1.05%
- This makes disagreement concrete and testable

### 3. Context Matters

Market Analyst now explicitly checks:
- Is this signal in an early-stage company or mature company? (Different reliability)
- Is this signal at extreme valuations? (Different meaning)
- Are fundamentals improving or deteriorating? (Changes signal weight)

### 4. Narrative Lifecycle Awareness

News Analyst now identifies:
- Is the story in early stage (underappreciated) or peak (dangerous)?
- Peak detection uses 6 concrete criteria, not subjective feel
- Acknowledges that some peaks are new normals (e.g., AI enthusiasm)

### 5. Competitive Dynamics Explicit

Fundamentals Analyst now uses L0-L4 framework:
- Distinguishes between "one-time event" vs "long-term shift"
- Market share change tracked explicitly
- Competitive threat level clearly stated

### 6. Assumption Chain Transparency

Bull and Bear now:
- Make assumptions explicit (not hidden in narrative)
- Calculate combined probability (shows hidden dependencies)
- Enable readers to judge probabilities themselves
- Show "weakest link" (determines overall chain strength)

---

## What Didn't Change

❌ Core analysis capabilities—still using same data sources
❌ Tool calling logic—still same flow
❌ Debate structure—still Bull vs Bear framework
❌ Risk Manager integration—still receives reports (will be updated next phase)

✅ Language—now all English
✅ Rigor—much higher with explicit frameworks
✅ Transparency—assumptions now visible, not hidden
✅ Self-awareness—agents now acknowledge limitations and certainties

---

## Next Steps

### Phase 2: Risk Manager Integration
- Risk Manager receives 5 (or 6) explicit scores
- Calculates weighted combination based on market environment
- Detects and handles model conflicts explicitly
- See: `AGENTS_PROMPT_IMPLEMENTATION.md` for exact integration

### Phase 3: Learning System
- Track which model/agent predictions are most accurate
- Dynamically adjust weights based on history
- Build "credibility scores" for each analyst

---

## Testing Checklist

Before deployment, verify:

- [ ] Market Analyst outputs include "Signal Reliability Score: __ /10"
- [ ] News Analyst outputs include "⚠️ Emotion Peak Detection: YES/NO"
- [ ] Fundamentals outputs have TWO separate scores (cost structure + competition)
- [ ] Bull outputs show "Combined Probability: __ %"
- [ ] Bear outputs show "Fragility Score: __ /10" and "Weakest Link"
- [ ] All agents include certainty levels
- [ ] All agents show meta-cognitive questions or reasoning
- [ ] No Chinese language remains (all English)
- [ ] All syntax is valid Python (no errors)

---

## Key Philosophy

**From:** Rigid rules that fail on edge cases
**To:** Principled frameworks with explicit assumption-checking

The goal is NOT to create perfect predictions, but to:
1. Make analysis assumptions visible
2. Enable probability quantification
3. Encourage self-awareness about limitations
4. Support healthy skepticism without dogmatism
5. Make human/system disagreements productive (not defensive)

---

## Files Modified

1. `/tradingagents/agents/analysts/market_analyst.py`
   - Lines 20-175: Complete prompt rewrite with meta-cognitive layer

2. `/tradingagents/agents/analysts/news_analyst.py`
   - Lines 18-240: Complete prompt rewrite with lifecycle framework

3. `/tradingagents/agents/analysts/fundamentals_analyst.py`
   - Lines 20-230: Complete prompt rewrite with dual-model scoring

4. `/tradingagents/agents/researchers/bull_researcher.py`
   - Lines 26-80: Complete prompt rewrite with assumption chain

5. `/tradingagents/agents/researchers/bear_researcher.py`
   - Lines 26-88: Complete prompt rewrite with fragility assessment

---

## Status

✅ **COMPLETE** - All 5 agents updated to English with meta-cognitive enhancement
⏳ **NEXT** - Phase 2: Risk Manager integration and testing

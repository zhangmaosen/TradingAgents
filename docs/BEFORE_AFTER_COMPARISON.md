# 📊 Before & After: How Prompts Changed

## The Problem We Solved

**Before:** Prompts had explicit frameworks but **no self-awareness**
- Rules applied rigidly
- No flexibility for edge cases
- Hidden assumptions
- Agents didn't know why they were scoring what they scored

**After:** Prompts have **frameworks + meta-cognitive layer**
- Rules are guidelines, not laws
- Encourages questioning assumptions
- Assumptions made explicit
- Agents explain their reasoning and acknowledge uncertainty

---

## Example 1: Market Analyst

### BEFORE (Old Approach)
```
"Select up to 8 indicators that provide complementary insights..."
→ Agent analyzes indicators
→ Outputs technical conclusion

Problem: What if the signal is real but at 52-week high?
         What if whole industry is crashing?
         The framework has no answer.
```

### AFTER (New Approach with Context Verification)
```
Step 1: Analyze indicators (same as before)
Step 2: CHECK CONTEXT
        - Is company in growth or decline stage?
        - How far from 200-day average?
        - Is competition collapsing or strengthening?
        - Are fundamentals improving or deteriorating?
        
Step 3: ADJUST SCORE
        Signal + Positive context = Trust it more
        Signal + Negative context = Trust it less
        
Step 4: META-COGNITIVE CHECK
        "What's my biggest assumption?"
        "If I'm wrong, where would I fail?"
        "Am I 30% or 90% certain?"
        
Output: Signal Reliability Score: 6/10
        Certainty: 60%
        Biggest risk: Competitor price war
```

**Result:** Signals are now contextualized and the agent explains its thinking.

---

## Example 2: News Analyst

### BEFORE (Old Approach)
```
Analyze news → Calculate sentiment → Output sentiment score

Problem: Didn't distinguish between:
- FOMO peak (short-term reversal likely)
- Genuine narrative emergence (long-term opportunity)
- New normal (sentiment won't reverse)
```

### AFTER (New Approach with Peak Detection)
```
Step 1: Analyze news (same)
Step 2: IDENTIFY LIFECYCLE STAGE
        Early-stage narrative? Growth? Peak? Decay? Bottom?
        
Step 3: PEAK DETECTION (6 conditions)
        ✓ News volume at historical high?
        ✓ Social media 85%+ bullish?
        ✓ Extreme language ("game-changing")?
        ✓ Price new high + 20% gains?
        ✓ Price targets 100%+ upside?
        ✓ Retail participation exploding?
        
        3+ met = Peak warning ⚠️
        
Step 4: META-COGNITIVE CHECK
        "Is this peak permanent or temporary?"
        "Historical precedent: how long did similar peaks last?"
        "Am I confusing correlation with causation?"
        "Certainty: 60%"
        
Output: 
  Stage: Peak
  Peak Detection: 4/6 conditions met ⚠️
  Risk Level: High
  Sentiment Score: 7/10 (base) - 2 (peak penalty) = 5/10
  Certainty: 60%
```

**Result:** Distinguishes between different types of peaks.

---

## Example 3: Fundamentals Analyst

### BEFORE (Old Approach)
```
"Analyze financial statements and earnings calls"
→ Agent produces financial analysis
→ Single summary score

Problem: Couldn't separate:
- Is the company healthy (cost structure)?
- Does the company have competitive advantages (market share)?
- These require different analyses!
```

### AFTER (New Approach with Dual Models)
```
MODEL 2: Cost Structure Analysis
  - Gross margin: 45% (high)
  - Trend: improving (+2%)
  - Cash flow quality: strong
  - Unit economics: LTV/CAC = 5.2 (excellent)
  → Cost Structure Score: 7/10
  → Meta question: "Is this sustainable or one-time optimization?"
  → Answer: Sustainable because market expanding
  → Certainty: 75%

MODEL 3: Competitive Landscape
  - Our market share: 22% (+2% YoY)
  - Competitor A: -1%
  - Competitor B: -1%
  - Competitive signal: L2 (our strength recognized)
  → Competition Score: 6/10
  → Meta question: "Are we gaining share or market expanding?"
  → Answer: We're actually gaining relative share
  → Certainty: 80%

Output:
  Cost Structure Score: 7/10 (certain 75%)
  Competitive Score: 6/10 (certain 80%)
  (Separate!) Not averaged.
```

**Result:** Two independent assessments for two independent questions.

---

## Example 4: Bull Researcher

### BEFORE (Old Approach)
```
"Build a strong case emphasizing growth potential..."
→ Agent writes bullish narrative
→ Outputs argument

Problem: Hidden assumption dependencies
- "Revenue will grow 50%" — based on what?
- "Market will recognize value" — when? how certain?
- Are these assumptions independent or all fail together?
```

### AFTER (New Approach with Assumption Chain)
```
Step 1: EXPLICIT ASSUMPTIONS
  A1: Business model works → 60% confidence
      (Historical precedent: 60% of SaaS startups reach PMF)
      
  A2: Market will grow as projected → 70% confidence
      (TAM is $50B, currently $5B, realistic?)
      
  A3: Company achieves profitability → 50% confidence
      (Path: reduce CAC 20%, margins improve 15%)
      
  A4: Market recognizes story → 40% confidence
      (Need: analyst coverage, customer wins, PR)

Step 2: SYNTHETIC PROBABILITY
  Combined = 0.60 × 0.70 × 0.50 × 0.40 = 8.4%
  
  ⚠️ This is MUCH lower than general bullish sentiment!
  
Step 3: META-COGNITIVE CHECK
  "Am I being realistic or overly optimistic?"
  "Which assumption is most uncertain? A4 (40%)"
  "If A4 fails, does whole case collapse?"
  "Certainty on my assessment: 65%"

Output:
  Assumption 1: 60%
  Assumption 2: 70%
  Assumption 3: 50%
  Assumption 4: 40%
  ──────────────────
  Combined Probability: 8.4%
  Assumption Chain Strength: 5/10
  Weakest Link: Market Recognition (40%)
  Certainty: 65%
```

**Result:** Bullish case now has explicit, quantified assumptions.

---

## Example 5: Bear Researcher

### BEFORE (Old Approach)
```
"Present arguments against investing..."
→ Agent lists risks
→ Outputs bearish narrative

Problem: No systematic way to question bull assumptions
- Seems like disagreement, but where exactly?
- What probability does bear assign?
- Are they fundamentally opposed or just pessimistic?
```

### AFTER (New Approach with Fragility Analysis)
```
Step 1: EXTRACT BULL'S ASSUMPTIONS
  Bull's A1: 60% → Bear assessment: 30%
    Why: Similar startups averaged 30% success, management unproven
    
  Bull's A2: 70% → Bear assessment: 40%
    Why: Market may not grow as fast, competitor entries emerging
    
  Bull's A3: 50% → Bear assessment: 25%
    Why: Unit economics don't improve as planned in competitive market
    
  Bull's A4: 40% → Bear assessment: 15%
    Why: No analyst support yet, not household name, PR is limited

Step 2: BEAR'S SYNTHETIC PROBABILITY
  Combined = 0.30 × 0.40 × 0.25 × 0.15 = 0.45%
  
  vs. Bull's 8.4%
  
Step 3: FRAGILITY ANALYSIS
  Weakest link: A4 (15%)
  "This company needs to be recognized by market, but has no analyst support"
  "This is the breaking point of the entire thesis"
  
Step 4: META-COGNITIVE CHECK
  "Am I too pessimistic? What would change my mind?"
  "If company gets analyst upgrade, I'd reassess A4 to 30%"
  "But currently, fragility is real"
  "Certainty: 70%"

Output:
  Bull's Probability: 8.4%
  Bear's Probability: 0.45%
  ──────────────
  Fragility Score: 8/10 (Very fragile)
  Weakest Link: Market Recognition (15%)
  Certainty: 70%
```

**Result:** Bear case now quantified and specific, not just doom-saying.

---

## The Key Insight

### Old Framework
```
Rule-based → One answer
    ↓
"If 6+ indicators agree → BUY signal"
    ↓
But ignores: valuation, fundamentals, sentiment, competition
```

### New Framework
```
Principle-based + Context → Nuanced answer
    ├─ Signal says BULLISH
    ├─ Context says CAUTIOUS (high valuation)
    ├─ Sentiment says EXTREME (peak detected)
    ├─ Fundamentals say MODERATE (margin pressure)
    ├─ Competition says WEAK (new entrant)
    │
    └─ → CONFLICTING SIGNALS
        → Need meta-thinking to reconcile
        → Agent explains tradeoffs
        → Humans can evaluate for themselves
```

---

## The Meta-Cognitive Layer

**Core idea:** Every agent now asks itself:

```
1. What am I assuming?
2. Am I seeing all angles?
3. How certain am I really?
4. What's my biggest blind spot?
5. Under what conditions would I be wrong?
```

This prevents:
- ❌ Overconfidence ("I'm always right because my framework is right")
- ❌ Hidden biases ("I didn't notice I was ignoring this")
- ❌ Brittle analysis ("This breaks if X changes")
- ❌ Dogmatism ("Rules must be followed")

And enables:
- ✅ Principled skepticism ("I doubt this, and here's why")
- ✅ Humble confidence ("I'm 75% sure, not 100%")
- ✅ Adaptability ("If this changes, my whole case changes")
- ✅ Transparency ("Here's my reasoning")

---

## Comparing Certainty Levels

### Old System
```
Agent: "Market signal is strong → Score 8/10"
Human: "But how sure are you?"
Agent: "Uh... I don't know? I just applied the rule?"
```

### New System
```
Agent: "Market signal is strong (7/10 base)"
       "Context support adds value (context +1)"
       "But valuation is extreme (risk -1)"
       "Final score: 7/10"
       "My certainty: 65%"
       "If competition surprises, score drops to 4/10"
Human: "OK, now I understand your confidence level"
```

---

## Summary Table

| Aspect | Before | After |
|--------|--------|-------|
| **Framework Type** | Rules | Principles + Rules |
| **Assumption Visibility** | Hidden | Explicit |
| **Probability Quantification** | No | Yes (MODEL 5) |
| **Context Awareness** | No | Yes (MODEL 1) |
| **Peak Recognition** | No | Yes (MODEL 4) |
| **Self-Awareness** | No | Yes (Meta questions) |
| **Certainty Levels** | Not stated | Explicit (30-90%) |
| **Flexibility** | Low | High |
| **Transparency** | Medium | High |
| **Robustness** | To rules | To reasoning |

---

## Result

Instead of 5 rigid agents following formulas, we now have:

**5 thinking partners** who:
- Acknowledge their assumptions
- Question themselves
- State their certainty level
- Explain their reasoning
- Admit where they could be wrong
- Work with humans, not instead of them

This is **meta-cognition in prompting** — not just analyzing the market, but analyzing how we analyze the market.

# 🚀 NEXT STEPS - How to Use Updated Agents

## Quick Start Guide

All 7 agents have been updated with the FIVE_MENTAL_MODELS framework and meta-cognitive layers. Here's how to proceed:

---

## 1. Test Individual Agents (Immediately)

### Test Market Analyst
```python
from tradingagents.agents.analysts.market_analyst import MarketAnalyst

analyst = MarketAnalyst()
result = analyst.analyze_signal(ticker="AAPL")
print(result)

# Should see:
# - Signal Reliability Score: X/10
# - Certainty Level: [30/60/75/90%]
# - Context verification results
```

### Test News Analyst
```python
from tradingagents.agents.analysts.news_analyst import NewsAnalyst

analyst = NewsAnalyst()
result = analyst.analyze_news(ticker="AAPL")
print(result)

# Should see:
# - ⚠️ Emotion Peak Detection: YES/NO
# - Risk Level: Low/Medium/High/Critical
# - Sentiment Score: 0-10
# - Narrative Lifecycle Stage: 1-5
```

### Test Fundamentals Analyst
```python
from tradingagents.agents.analysts.fundamentals_analyst import FundamentalsAnalyst

analyst = FundamentalsAnalyst()
result = analyst.analyze_fundamentals(ticker="AAPL")
print(result)

# Should see:
# - Cost Structure Score: X/10
# - Competitive Signal: L[0-4]
# - Market Share Trajectory: Stable/Growing/Declining
# - Unit Economics Trend: Improving/Stable/Deteriorating
```

### Test Bull & Bear Researchers
```python
from tradingagents.agents.researchers.bull_researcher import BullResearcher
from tradingagents.agents.researchers.bear_researcher import BearResearcher

bull = BullResearcher()
bear = BearResearcher()

bull_result = bull.prepare_argument(ticker="AAPL", data=...)
bear_result = bear.prepare_argument(ticker="AAPL", data=...)

# Should see in Bull:
# - Assumption 1-4 Probabilities
# - Combined Probability: X.X%
# - Assumption Chain Strength: X/10

# Should see in Bear:
# - Bull's Estimated Prob: X%
# - Bear's Recalibrated Prob: Y%
# - Fragility Index: Z%
# - Weakest Link identified
```

### Test PhilosophicalResearcher
```python
from tradingagents.agents.researchers.philosophical_researcher import PhilosophicalResearcher

researcher = PhilosophicalResearcher()
bull_result = researcher._build_bull_messages_with_assessment(...)
bear_result = researcher._build_bear_messages_with_assessment(...)

# Bull output (JSON):
# {
#   "assumption_1_probability": 0.75,
#   "assumption_2_probability": 0.65,
#   "combined_probability_percent": 27.3,
#   "certainty_level": 0.75,
#   ...
# }

# Bear output (JSON):
# {
#   "bull_combined_probability": 0.45,
#   "recalibrated_probability": 0.25,
#   "fragility_index": 0.75,
#   "weakest_link": "...",
#   ...
# }
```

---

## 2. Update Risk Manager (Important!)

The Risk Manager will need to be updated to:

1. **Parse different output formats**
   - Basic agents: Text-based
   - PhilosophicalResearcher: JSON-based

2. **Handle new fields**
   ```python
   # New Bull fields to consider
   bull_output = {
       "assumption_1_probability": 0.75,
       "assumption_2_probability": 0.65,
       "assumption_3_probability": 0.80,
       "assumption_4_probability": 0.70,
       "combined_probability_percent": 27.3,
       "certainty_level": 0.75,
       "biggest_risk": "Market share erosion"
   }
   
   # New Bear fields to consider
   bear_output = {
       "bull_combined_probability": 0.45,
       "recalibrated_probability": 0.25,
       "fragility_index": 0.75,
       "weakest_link": "Assumption 1 breaks the thesis",
       "certainty_level": 0.65
   }
   ```

3. **Update scoring logic**
   ```python
   def calculate_investment_score(bull_output, bear_output):
       """
       Consider:
       - Spread between Bull and Bear probabilities
       - Fragility index (higher = more risky)
       - Certainty levels (higher = more confident)
       - Weakest links in Bull's argument
       """
       
       bull_prob = bull_output['combined_probability_percent'] / 100
       bear_prob = bear_output['recalibrated_probability']
       fragility = bear_output['fragility_index']
       bull_certainty = bull_output['certainty_level']
       bear_certainty = bear_output['certainty_level']
       
       # High fragility means thesis is risky
       if fragility > 0.70:
           risk_multiplier = 1.5
       else:
           risk_multiplier = 1.0
       
       # Calculate adjusted probability
       adjusted_prob = (bull_prob - bear_prob) * risk_multiplier
       
       # Factor in certainty levels
       confidence = min(bull_certainty, bear_certainty)
       
       return adjusted_prob * confidence
   ```

---

## 3. Integration Tests (Required)

Run full pipeline with sample tickers:

```bash
# Test with AAPL
python main.py --ticker AAPL --mode test

# Check outputs from all 7 agents
# Verify Risk Manager can parse all formats
# Validate final trading decision
```

**What to check:**
- [ ] All agents produce output
- [ ] No parsing errors in Risk Manager
- [ ] Decision quality seems reasonable
- [ ] Meta-cognitive questions are relevant
- [ ] Assumption probabilities are realistic

---

## 4. Comparison: Old vs New

### OLD Prompt Example (Market Analyst)
```
"Analyze the price trend. Is it up or down? What's the strength?"
```

### NEW Prompt Example (Market Analyst)
```
STEP 1: Analyze the technical signal
[Your analysis...]

STEP 2: Consider the macro context
[Your analysis...]

STEP 3: Context Verification
- Interest rate environment: [Y/N]
- Earnings calendar: [Y/N]
- Sector momentum: [Y/N]
- Market breadth: [Y/N]
- Volatility regime: [Y/N]

STEP 4: Score Signal Reliability (0-10)
- [Your reasoning]
- Score: 7/10

STEP 5: Meta-Cognitive Check
- Q1: Am I being objective? [Answer]
- Q2: Biggest blind spot: [Answer]
- Q3: Would skeptics disagree? [Answer]
- Q4: What would change my mind? [Answer]
- Q5: Certainty Level: 75%
```

---

## 5. Key Outputs to Monitor

### Market Analyst
```
Signal Reliability Score: 7/10
Certainty: 75%
✅ Most reliable when signal matches all 5 context factors
⚠️ Least reliable when signal contradicts multiple factors
```

### News Analyst
```
⚠️ Emotion Peak Detection: YES
Risk Level: MEDIUM (Peak emotion + Declining narrative)
Sentiment Score: 7/10
Narrative Stage: 4 (Declining from peak)
✅ Good time to check contrary positions
```

### Fundamentals Analyst
```
Cost Structure Score: 6/10 (Margins compressing)
Competitive Signal: L2 (Competitive pressure evident)
Market Share: DECLINING
Unit Economics: DETERIORATING
⚠️ Fundamental deterioration = Risk factor
```

### Bull Researcher
```
Assumption 1: 75% (Business foundation solid)
Assumption 2: 65% (Growth potential realistic)
Assumption 3: 80% (Financial pathway achievable)
Assumption 4: 70% (Market will recognize story)

Combined Probability: 27.3%
⚠️ Much lower than initial sentiment of 60%+
Biggest Risk: Competitor market share grab
```

### Bear Researcher
```
Bull's Estimated Probability: 45%
Bear's Recalibrated: 25%
Fragility Index: 75%
Weakest Link: "Assumption 1 - market growth rate"

If market growth = half what bull expects...
Entire thesis collapses
```

---

## 6. Metrics to Track

Create a monitoring dashboard:

```python
# Track these over time:
metrics = {
    "Bull_vs_Bear_Spread": bull_prob - bear_prob,
    "Fragility_Index": fragility_index,
    "Certainty_Alignment": min(bull_certainty, bear_certainty),
    "Meta_Cognitive_Signals": num_blind_spots_identified,
    "Model_Application_Accuracy": % correct model identification,
    "Weakest_Link_Calls": % of weakest links that actually broke
}

# Track decision outcomes:
outcomes = {
    "Win_Rate": % winning trades,
    "Fragile_Thesis_Win_Rate": % winning when fragility > 70%,
    "Strong_Thesis_Win_Rate": % winning when fragility < 30%,
    "Average_Holding_Period": days,
    "Profit_Factor": profit / loss
}
```

---

## 7. Debugging Issues

### If Agent Output Looks Wrong

**Market Analyst Output is Generic:**
- Check: Are you providing price history data?
- Check: Context factors (interest rates, earnings dates, etc.) available?
- Fix: Ensure all 5 context factors can be evaluated

**News Analyst Says No Emotion Peak But Data Shows High Sentiment:**
- Check: Is narrative in declining stage (Stage 4-5)?
- Check: Are there multiple conflicting narratives?
- Fix: Provide clearer news feed data with dates

**Bull Gives 90% Probability But Logic Seems Weak:**
- Check: Are assumptions realistic?
- Check: Is management history strong?
- Check: Has bull considered counterarguments?
- Fix: May need better/more data inputs

**Bear Fragility > 90% But Seems Too Negative:**
- Check: How certain is bear about recalibrations? (certainty_level)
- Check: Is weakest link actually critical?
- Fix: Compare with historical similar cases

---

## 8. Next Phase Checklist

- [ ] Run individual agent tests (all 7 agents)
- [ ] Verify output formats and quality
- [ ] Update Risk Manager parsing logic
- [ ] Update Risk Manager scoring logic
- [ ] Run integration tests with 5 sample tickers
- [ ] Compare decision quality vs baseline
- [ ] Create monitoring dashboard
- [ ] Document any API changes needed
- [ ] Plan staged rollout (% of portfolio)
- [ ] Set up A/B testing framework

---

## 9. Questions for Team

1. **Is PhilosophicalResearcher the primary implementation?**
   - If YES: Focus on ensuring JSON parsing works
   - If NO: Focus on basic agents

2. **Should we run both implementations simultaneously?**
   - A/B test: Compare basic vs advanced outputs
   - Useful for measuring improvement

3. **How should Assumption Chain probabilities influence Risk Manager?**
   - Should fragility index override other signals?
   - How much weight on weakest link?

4. **Do we need human review before deploying?**
   - Recommend: Yes, for first 10-20 trades
   - Review argument quality and reasonableness

---

## 10. Documentation References

- **For implementation details**: `AGENTS_PROMPT_IMPLEMENTATION.md`
- **For meta-cognitive framework**: `AGENTS_METACOGNITION_LAYER.md`
- **For specific code changes**: `BEFORE_AFTER_COMPARISON.md`
- **For PhilosophicalResearcher**: `PHILOSOPHICAL_RESEARCHER_UPDATES.md`
- **For complete overview**: `COMPLETE_AGENT_PROMPT_OPTIMIZATION.md`
- **For checklist**: `FINAL_COMPLETION_CHECKLIST.md`

---

## 11. Success Indicators

You'll know the update is successful when:

✅ All 7 agents produce output without errors
✅ Output format is valid (JSON or text as expected)
✅ Meta-cognitive questions appear in arguments
✅ Assumption probabilities are realistic (20-90%)
✅ Fragility indices make intuitive sense
✅ Bull vs Bear spreads identify genuine risks
✅ Decision quality metrics improve vs baseline
✅ Team agrees reasoning is clearer and more transparent

---

## 12. Support/Debugging

If you encounter issues:

1. **Check syntax**: `mcp_pylance_mcp_s_pylanceFileSyntaxErrors`
2. **Check imports**: Try importing each agent individually
3. **Check output parsing**: Add print statements to see raw output
4. **Review prompts**: Compare with markdown documentation
5. **Run simplified test**: Use hardcoded data instead of real APIs

---

## Final Notes

- All changes maintain backward compatibility
- No breaking changes to core APIs
- All agents still work as before (just better prompts)
- Ready for testing phase immediately

**Good luck! 🚀**


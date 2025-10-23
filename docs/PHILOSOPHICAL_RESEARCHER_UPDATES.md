# PhilosophicalResearcher.py - MODEL 5 Integration Updates

## Overview

Updated `philosophical_researcher.py` to include **MODEL 5 (Assumption Chain Strength/Fragility)** with meta-cognitive layers. This is a critical update because this file contains the advanced, class-based researcher implementation that may be actively used in production.

## Files Modified

- **File**: `/tradingagents/agents/researchers/philosophical_researcher.py`
- **Total Lines**: 1198 lines
- **Status**: ✅ Syntax checked - No errors

## Changes Made

### 1. Bull Analyst - `_build_bull_messages_with_assessment()` (Lines 363-560)

**What Changed:**
- Replaced old verbose prompt with streamlined MODEL 5 framework
- Added explicit assumption chain identification (5 core assumptions)
- Integrated synthetic probability calculation
- Added meta-cognitive checking layer
- Preserved worldview integration

**New Workflow:**
```
Step 1: Build Your Assumption Chain (CRITICAL)
  - Assumption 1-4: Business Foundation, Growth, Financial, Market Recognition
  - Each with explicit probability estimate
  
Step 2: Calculate Synthetic Probability  
  - Combined Prob = Prob_A1 × Prob_A2 × Prob_A3 × Prob_A4
  - Reveals real probability vs sentiment
  
Step 3: Meta-Cognitive Check
  - Q1: How objective am I really being?
  - Q2: What's my biggest blind spot?
  - Q3: Management execution credibility?
  - Q4: Time horizon still works if doubled?
  - Q5: Certainty level assessment
```

**New JSON Output Format:**
```json
{
  "assumption_1_probability": 0.XX,
  "assumption_2_probability": 0.XX,
  "assumption_3_probability": 0.XX,
  "assumption_4_probability": 0.XX,
  "combined_probability_percent": X.X,
  "argument": "200-400 words, data-backed",
  "evidence_strength": 0.85,
  "logic_clarity": 0.90,
  "certainty_level": 0.75,
  "biggest_risk": "What's most likely to break?"
}
```

**Key Difference from Basic bull_researcher.py:**
- Keeps JSON output format (not text-based like basic version)
- Maintains worldview integration
- More sophisticated probability tracking (4 assumptions explicitly)
- Preserves class-based architecture

---

### 2. Bear Analyst - `_build_bear_messages_with_assessment()` (Lines 644-850)

**What Changed:**
- Replaced old verbose risk-focused prompt with MODEL 5 fragility analysis
- Added explicit assumption extraction from bull case
- Integrated recalibrated probability with evidence
- Added fragility index calculation  
- Added meta-cognitive skepticism check
- Preserved worldview integration

**New Workflow:**
```
Step 1: Extract Bull's Assumption Chain
  - Pull out their 4 core assumptions from their argument
  - Extract their claimed probabilities
  - Note: Do they seem overconfident or realistic?
  
Step 2: Challenge Probabilities with Evidence
  - For EACH assumption, provide competing evidence
  - Recalibrate probability downward (usually -20-40%)
  - Show: Historical patterns, execution risk, market headwinds, etc.
  
Step 3: Calculate Fragility Score
  - Fragility Index = 1 - (Recalibrated Combined Probability)
  - Example: Bull 45% → Bear 25% = 75% fragility index
  - This shows how fragile the bull thesis really is
  
Step 4: Meta-Cognitive Check
  - Q1: Am I being fairly skeptical or just negative?
  - Q2: What specific evidence would change my mind?
  - Q3: Timing issue vs fundamental problem?
  - Q4: Where's my own bias showing?
  - Q5: Certainty level - adjust if < 60%
```

**New JSON Output Format:**
```json
{
  "bull_combined_probability": 0.45,
  "recalibrated_probability": 0.28,
  "fragility_index": 0.72,
  "weakest_link": "Assumption 1: Market growing fast enough",
  "argument": "200-400 words, data-backed",
  "evidence_strength": 0.80,
  "logic_clarity": 0.85,
  "certainty_level": 0.65
}
```

**Key Difference from Basic bear_researcher.py:**
- Keeps JSON output format (maintains compatibility)
- Maintains worldview integration
- Shows comparative probability analysis (bull vs bear)
- Preserves class-based architecture

---

## Five Mental Models Integration

Both Bull and Bear now explicitly implement **MODEL 5**:

### MODEL 5: Assumption Chain Strength/Fragility

**Core Concept:**
- All investment theses rest on assumption chains
- Strength = individual assumptions × their interdependencies  
- Fragility = how easily the chain breaks if one link fails
- Real probability = product of assumption probabilities (not sum)

**Bull's Role (Assumption Chain Strength):**
- Identify 4 core assumptions needed for thesis to work
- Estimate probability for each
- Calculate synthetic probability (product)
- Show meta-cognitive awareness of blind spots

**Bear's Role (Assumption Chain Fragility):**
- Extract bull's assumptions explicitly
- Challenge each with evidence
- Recalibrate to more realistic probabilities
- Show which link is weakest (breaks = thesis fails)

---

## Compatibility Considerations

### With Basic Researchers
- **Bull Researcher** (`bull_researcher.py`): Text-based output
- **PhilosophicalResearcher Bull**: JSON-based output
- Different formats but same underlying MODEL 5 logic

- **Bear Researcher** (`bear_researcher.py`): Text-based output  
- **PhilosophicalResearcher Bear**: JSON-based output
- Different formats but same underlying MODEL 5 logic

### With Worldview System
- Both prompts preserve worldview integration
- Worldview philosophy, beliefs, quality thresholds still respected
- Meta-cognitive checks now work WITH worldview philosophy

### With Risk Manager
- Risk Manager will need to parse both text and JSON formats
- May need updated scoring logic to handle new fields:
  - `assumption_*_probability` (Bull)
  - `fragility_index`, `weakest_link` (Bear)
  - `certainty_level` (both)

---

## Integration Status

### ✅ COMPLETED
- Market Analyst (English + meta-cognitive layer)
- News Analyst (English + peak detection)
- Fundamentals Analyst (English + dual-model scoring)
- Bull Researcher (English + assumption chain)
- Bear Researcher (English + fragility analysis)
- PhilosophicalResearcher Bull (MODEL 5 + assumption chain)
- PhilosophicalResearcher Bear (MODEL 5 + fragility analysis)

### ⏳ NEXT STEPS
1. Test both implementations with actual trading data
2. Update Risk Manager to handle new output formats
3. Measure effectiveness improvement in trading signals
4. Compare basic vs advanced researcher outputs

---

## Testing Recommendations

### For PhilosophicalResearcher:
1. Run with sample ticker (e.g., AAPL)
2. Check JSON output format is valid
3. Verify worldview integration still working
4. Ensure meta-cognitive layers produce realistic scores
5. Validate assumption chain calculations are correct

### Expected Output Example:
```json
{
  "assumption_1_probability": 0.75,
  "assumption_2_probability": 0.65,
  "assumption_3_probability": 0.80,
  "assumption_4_probability": 0.70,
  "combined_probability_percent": 27.3,
  "argument": "[200-400 word detailed argument...]",
  "evidence_strength": 0.82,
  "logic_clarity": 0.88,
  "certainty_level": 0.72,
  "biggest_risk": "Market share erosion from Chinese competitors"
}
```

---

## Version History

**Version 1.0** (This Update)
- Integrated MODEL 5 into both Bull and Bear methods
- Added meta-cognitive checking frameworks
- Preserved worldview integration
- Updated from verbose prompts to concise, explicit frameworks
- Syntax validated - No errors


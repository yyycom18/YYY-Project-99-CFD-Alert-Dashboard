# Complete Trading Strategy Specification

---

# 1. Strategy Philosophy

This is a discretionary trading system supported by a scoring-based Dashboard.

The Dashboard:
- Does NOT execute trades.
- Does NOT determine exact entry trigger.
- Acts as a structured alert and filtering tool.
- Highlights high-probability opportunities based on condition scoring.

Deployment Condition:
- Total 7 conditions.
- If ≥ 4 conditions satisfied.
- AND Risk:Reward ≥ 1:1.3.
→ Trade opportunity qualifies for manual evaluation.

---

# 2. Market Structure Framework

## 2.1 Market Stage Model

Market is divided into 3 stages:

[+1] Upside
[0] No Clear Side
[-1] Downside

Purpose:
- Avoid binary thinking (Up → Down immediately).
- Allow transition into neutral phase instead of forced reversal.

Example:
- 4H uptrend remains intact.
- 1H drops sharply to 4H 0.618 support.
→ 4H remains trend.
→ 1H may shift to neutral, not full downtrend.

---

## 2.2 Trend vs Range Definition

Trend:
- Can be upward or downward.
- Normal retracement ≤ 0.618.
- Slight tolerance up to 0.7 acceptable.
- If retracement > 0.618–0.7 → considered loss of trend structure.

Range:
- Retracement deeper than 0.618–0.7.
- Two tops / two bottoms formation.
- Can be horizontal, slightly rising, falling, expanding or contracting triangle.
- Key principle: retracement depth defines structure shift.

---

# 3. Multi-Timeframe Structure

Three-layer hierarchy:

Higher TF → Defines structure and key zones
Middle TF → Observes momentum & Fibonacci
Lower TF → Entry execution observation

Examples:
1W → 1D → 4H
4H → 1H → 15M

Entries only meaningful when aligned with higher timeframe structure.

---

# 4. The 7 Trading Conditions

## 1. Trade With Trend
Must align with higher timeframe bias.

## 2. Original Impulse Break of Structure

Definition:
- Breaks previous structural behavior.
- Can be:
  - 3 consecutive long-bodied candles
  - OR 1 extremely strong reversal candle
- Candle body significantly larger than recent candles.
- Small wicks preferred.
- Close break preferred (higher reliability).
- Represents concentrated momentum within short time.

Purpose:
- Detect trend shift or transition to neutral.

---

## 3. Stop Hunt (打止蝕)

Occurs when:
- Mid TF trend intact.
- Lower TF forms double bottom in Asia session.
- EU session breaks below double bottom.
- Liquidity sweep of long stops.

Used as scoring enhancement, not mandatory.

---

## 4. Stop Hunt (打錢)

Mirror logic of 打止蝕.
- Double top liquidity sweep.
- Short stop orders cleared.

Also scoring enhancement.

---

## 5. Supply / Demand Zone (禁區)

Definition:
- Origin of strong impulsive move.
- Triggered by large directional candles.
- Long bodies, small wicks.

Types:
- Down impulse → Down zone
- Up impulse → Up zone

Logic:
- Price returning to zone often reacts.
- 0.618 + Down Zone → Higher probability short.
- Zone weakens after two distant retests.

---

## 6. Fibonacci 0.618 / 0.5

Dual Role:
- Technical retracement location.
- Risk:Reward validation filter.

Minimum R:R = 1:1.3

0.618:
- Naturally satisfies R:R.
- Higher weight.

0.5:
- Only valid if stop at 0.88 maintains R:R ≥ 1:1.3.

Shallower retracement (e.g., 0.18) acceptable if R:R strong.

Not mandatory condition.
Used in scoring system.

---

## 7. EU / US Session Continuation

If higher TF trend is up:
- Asia forms range.
- EU breaks upward.
→ Considered trend continuation.

Continuation signs:
- Momentum expansion.
- New highs.

HK50 Exception:
- EU/US less representative.

---

# 5. Price Role Reversal (價格互換區)

- Former support becomes resistance after structure break.
- Before break: lower wicks & bounce.
- After break: upper wicks & rejection.

---

# 6. Momentum Density Principle

Impulse strength judged by:
- Candle body size relative to recent candles.
- Concentration of movement in short time.

3 large candles > 10 small candles.
Focus on momentum density.

---

# 7. Scoring System

7 total conditions.

If ≥ 4 conditions satisfied
AND R:R ≥ 1:1.3
→ Deployment opportunity.

Dashboard Role:
- Alert only.
- Highlight candidates.
- No automatic execution.

---

# 8. Execution Philosophy

Trader Thinking Flow:

1. Define (Market State)
2. Assume (Location & Structure)
3. Deploy (Wait for favorable condition)

Time segmentation used for training and practical application.

---

END OF STRATEGY SPECIFICATION


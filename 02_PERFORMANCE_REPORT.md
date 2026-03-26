# VAM Performance Report Generator
*Use with 02_MASTER_SYSTEM_PROMPT.md loaded as context. Run this BEFORE generating a batch.*

---

## Instructions

Analyze the latest VAM performance data and generate a performance report with batch recommendations. The copywriter (Nate) will review the report and choose which direction to take for the next batch.

## Data Input

Paste or reference the latest data from these sources:
- **Static ad performance:** `[VAM] - Creative & Copy Tracking Sheet - Static Ad Performance` CSV
- **Video ad performance:** `[VAM] - Creative & Copy Tracking Sheet - Video Ad Performance` CSV
- **Copy performance:** `[VAM] - Creative & Copy Tracking Sheet - Copy Performance` CSV
- **Dashboard metrics:** `VAM Meta Marketing Dashboard - Dashboard` CSV (if available)

*If CSV data is not pasted, analyze the reference files: `04_WINNING_HOOKS_LIBRARY.md`, `04_WINNING_VISUALS_LIBRARY.md`, `04_LOSING_PATTERNS.md`, and `04_PERFORMANCE_SNAPSHOT.md`*

---

## Output Format

Generate the report in this exact structure:

```
========================================
VAM PERFORMANCE REPORT — [Date]
========================================

━━━ SECTION 1: KPI SNAPSHOT ━━━

| Metric                    | Current  | Target  | Gap     | Trend  |
|---------------------------|----------|---------|---------|--------|
| ROAS                      | [X.XXx]  | 2.0x    | [±XX%]  | [↑↓→]  |
| Cost per Connected Call   | [$XXX]   | $250    | [±XX%]  | [↑↓→]  |
| CAC                       | [$X,XXX] | $750    | [±XX%]  | [↑↓→]  |
| CPL                       | [$XX]    | —       | —       | [↑↓→]  |
| Close Rate (Connected)    | [XX%]    | —       | —       | [↑↓→]  |

Key Takeaway: [1 sentence on overall account health]


━━━ SECTION 2: TOP PERFORMERS ━━━

STATIC — Top 5 by ROAS (min $500 spend):
1. [SC#_Name | SV#_Visual] — ROAS [X.XXx], $[spend] spend, CPL $[XX]
2. [...]
3. [...]
4. [...]
5. [...]

VIDEO — Top 5 by CTR:
1. [VHK#_Name | VV#_Visual] — CTR [XX%], ROAS [X.XXx], $[spend] spend
2. [...]
3. [...]
4. [...]
5. [...]

COPY — Top 3 Hook + Body Combos:
1. [CHK#_Name + CB#_Name] — ROAS [X.XXx], $[spend] spend
2. [...]
3. [...]


━━━ SECTION 3: WHAT'S WORKING ━━━

Winning Copy Angles (trending up):
• [Angle name] — [Why it's working, performance data]
• [Angle name] — [Why it's working, performance data]

Winning Visual Styles (trending up):
• [SV#_Name] — [Performance context]
• [SV#_Name] — [Performance context]

Emerging Winners (early data, worth expanding):
• [Name] — [Early metrics, why it's promising]

Awareness Level Coverage:
| Level          | Current % of Active Ads | Target % | Gap    |
|----------------|------------------------|----------|--------|
| Most Aware     | [XX%]                  | 30%      | [±XX%] |
| Product Aware  | [XX%]                  | 25%      | [±XX%] |
| Solution Aware | [XX%]                  | 20%      | [±XX%] |
| Problem Aware  | [XX%]                  | 15%      | [±XX%] |
| Unaware        | [XX%]                  | 10%      | [±XX%] |


━━━ SECTION 4: WHAT'S FAILING ━━━

Ads to Kill (ROAS <0.8x with $500+ spend):
• [Name] — ROAS [X.XXx], $[spend] spent — KILL
• [Name] — ROAS [X.XXx], $[spend] spent — KILL

New Losing Patterns Identified:
• [Pattern] — [Why it failed, data]

Reminder — Confirmed Losing Patterns (DO NOT USE):
• [Brief summary of top losing patterns from 04_LOSING_PATTERNS.md]


━━━ SECTION 5: BATCH RECOMMENDATIONS ━━━

Based on the data above, here are 3 recommended batch directions:

OPTION A: [Batch Name]
• Focus: [What the batch focuses on]
• Rationale: [Why this is recommended based on the data — 2-3 sentences]
• Batch Type: [Static / Video / Copy]
• Awareness Distribution: [e.g., 2 Most Aware, 1 Product Aware, 1 Problem Aware, 1 Unaware]
• Visual Styles: [Which SV/VV styles to use]
• Net New/Iteration: [Net New or Iteration]

OPTION B: [Batch Name]
• Focus: [What the batch focuses on]
• Rationale: [Why this is recommended — 2-3 sentences]
• Batch Type: [Static / Video / Copy]
• Awareness Distribution: [e.g., ...]
• Visual Styles: [...]
• Net New/Iteration: [...]

OPTION C: [Batch Name]
• Focus: [What the batch focuses on]
• Rationale: [Why this is recommended — 2-3 sentences]
• Batch Type: [Static / Video / Copy]
• Awareness Distribution: [e.g., ...]
• Visual Styles: [...]
• Net New/Iteration: [...]

========================================
Pick an option (A, B, C) or describe your own direction.
Then run the appropriate batch generator to create the briefs.
========================================
```

---

## Analysis Framework

When analyzing the data, follow this decision logic:

### Categorize Every Active Ad
| Bucket | Criteria | Recommendation |
|--------|----------|---------------|
| **Scale** | ROAS >1.5x OR cost per connected <$350 | Increase budget. Create variations for the batch. |
| **Optimize** | ROAS 1.0-1.5x OR cost per connected $350-$500 | Create variations (new hook same visual, or same hook new visual) |
| **Test** | <$500 spend | Let run to $500+ before judging |
| **Kill** | ROAS <0.8x with $500+ spend, OR CPL >$80 with 20+ leads | Turn off. Add to losing patterns. |

### Recommendation Logic
1. **If top performers are static:** Recommend Option A as a static batch with variations of the top winners
2. **If top performers are video:** Recommend Option A as a UGC batch expanding on winning hooks
3. **If awareness levels are skewed:** Recommend one option that pushes into underrepresented levels
4. **If there are emerging winners:** Recommend one option that expands on early signals
5. **Always include one "expansion" option** that tests new hooks or angles
6. **Never recommend anything from the Confirmed Losing Patterns**

### Update Reference Files
After running the report, update these files if new data warrants it:
- `04_WINNING_HOOKS_LIBRARY.md` — Add any new winners
- `04_LOSING_PATTERNS.md` — Add any new confirmed losers
- `04_PERFORMANCE_SNAPSHOT.md` — Update current KPIs

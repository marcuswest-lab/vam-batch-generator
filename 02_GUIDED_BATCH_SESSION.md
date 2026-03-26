# VAM Guided Batch Session
*All-in-one prompt: Load this + 02_MASTER_SYSTEM_PROMPT.md to go from data analysis → batch recommendation → Nate's input → finished briefs in a single session.*

---

## How This Works

This prompt creates a conversational session where Claude:
1. Analyzes current performance data
2. Presents a performance report with recommendations
3. Asks Nate a few quick questions
4. Generates a complete batch of 5 briefs based on his answers

**Nate just needs to answer 4-5 questions. Everything else is automated.**

---

## Session Instructions for Claude

You are running a guided creative batch session for VAM. Follow these phases in order. **Wait for Nate's response after each question before proceeding.**

### Auto-Fill Values (do NOT ask about these)
- Copywriter: **Nate**
- AI Allowed: **Yes, AI Is Allowed**
- Status: **Ready For Internal**
- Conversion Objective: **Lead Generation**
- Avatar: **Individuals and families planning a cross-country move, primarily 2-4+ bedroom households**
- Ad Platform: **All**
- Ratio Format(s): **1x1, 4x5, 9x16** (static) / **9x16, 1x1, 4x5** (video)

---

### PHASE 1: DATA INTAKE

Start the session by saying:

> **Hey Nate! Let's build your next batch. First, I need the latest performance data.**
>
> You can either:
> 1. **Paste the CSV data** from the Creative & Copy Tracking Sheet (static, video, or copy tabs)
> 2. **Point me to the file paths** if the CSVs are in the project folder
> 3. **Skip this step** and I'll use the existing reference files (04_WINNING_HOOKS_LIBRARY.md, 04_PERFORMANCE_SNAPSHOT.md)
>
> Which would you prefer?

Wait for Nate's response. Then proceed to Phase 2.

---

### PHASE 2: PERFORMANCE REPORT

Analyze the data and present a concise report. Use the format from `02_PERFORMANCE_REPORT.md` but keep it shorter for the conversational flow:

**Show:**
- KPI snapshot (ROAS, cost per connected, CAC vs targets)
- Top 3-5 performers right now
- What's working and what's failing (bullet points)
- 3 recommended batch directions (Options A, B, C)

Then ask:

> **Based on this data, which direction do you want to go?**
>
> - **Option A:** [name — 1 sentence description]
> - **Option B:** [name — 1 sentence description]
> - **Option C:** [name — 1 sentence description]
> - **Custom:** Tell me what you have in mind
>
> *(Pick one or mix and match)*

Wait for Nate's answer.

---

### PHASE 3: NATE'S INPUT

Ask these questions one at a time (or group 2-3 if the flow is natural). **Only ask what's needed — skip questions where the answer is obvious from context.**

**Question 1** (if not already answered):
> **Static, Video, or Copy batch?**

**Question 2** (required — critical for proper A/B testing):
> **What variable are you testing in this batch?**
>
> *Each batch should test ONE variable while holding everything else constant.*
>
> - **Static:** Copy (different hooks/headlines, same visual) or Visual (different visual styles, same copy)
> - **Video:** Lead (different hooks) / Body (different talking points) / CTA (different CTAs) / Pattern Interrupt
> - **Copy:** Lead (different hooks) / Body (different body text) / CTA (different CTAs) / Full (all new)

**Question 3** (required — follows from Question 2):
> **What stays constant?**
> *(e.g., "Use Gmail for all 5" or "Keep the same body script from VB3_SavingsStory" or "Same CTA: Get your free quote")*

**Question 4** (if not already answered):
> **Net New or Iteration?**
> *(Net New = testing brand new concepts. Iteration = variations on existing winners.)*

**Question 5** (optional — only ask if relevant):
> **Any other specific hooks, angles, or constraints?**
> *(e.g., "I want to try a Secret lead type" or "Test a fear-of-loss angle" or "No Apple Notes")*

After getting answers, confirm the plan:

> **Got it. Here's what I'm generating:**
>
> - **Batch Type:** [Static / Video / Copy]
> - **Testing:** [the ONE variable being tested]
> - **Held Constant:** [everything that stays the same]
> - **Focus:** [what they chose]
> - **Net New/Iteration:** [choice]
> - **Awareness Distribution:** [based on recommendation]
>
> **Look good? I'll generate the batch now.**

Wait for confirmation, then proceed.

---

### PHASE 4: BATCH GENERATION

Generate 5 creatives using the appropriate format:
- **Static:** Use the format from `02_BATCH_GENERATOR_STATIC.md`
- **Video:** Use the format from `02_BATCH_GENERATOR_VIDEO.md`
- **Copy:** Use the format from `02_BATCH_GENERATOR_COPY.md`

**CRITICAL — Variable Isolation:**
- ALL 5 creatives must have the SAME Variation Type.
- Only the tested variable changes between creatives. Everything else is held constant.
- Example: If testing Copy on Static → all 5 use Gmail (or whatever visual was chosen). Only the hook/copy differs.
- Example: If testing Lead on Video → all 5 use the same body script and CTA. Only the hook changes.

**CRITICAL — Enforce these dropdown constraints:**

| Field | Static Values | Video Values | Copy Values |
|-------|--------------|-------------|------------|
| Variation Type | Copy · Visual | Lead · Pattern Interrupt · Graphic Overlay · Body · CTA | Lead · Body · CTA · Full |
| Lead Type | Offer · Promise · Problem-Solution · Secret · Proclamation · Story | *(same)* | *(same)* |
| Awareness Level | Most Aware · Product Aware · Solution Aware · Problem Aware · Unaware | *(same)* | *(same)* |
| Status | Ready For Internal | *(same)* | *(same)* |
| Video Type | — | Ad Video | — |
| Copy Type | — | — | Primary Text · Headline · Asset Set |

Follow all generation rules from the batch generator (70-20-10 applied ONLY to the tested variable, different hook types, no losing patterns, etc.). The held-constant variable must be literally identical across all 5 creatives — same visual code, same copy, same everything that isn't being tested.

---

### PHASE 5: REVIEW & ADJUST

After outputting the batch, say:

> **Here's your batch! Review and let me know:**
>
> - ✅ **Good to go** — I'll format the ClickUp submission note
> - ✏️ **Change Creative #X** — Tell me what to adjust (hook, copy, visual, awareness level, etc.)
> - 🔄 **Regenerate** — I'll create a fresh batch with the same parameters
> - ➕ **Add another batch** — We can run a second batch in the same session

Wait for Nate's response and make adjustments as needed.

When he confirms the batch is final, output the ClickUp submission summary:

> **ClickUp Submission Note:**
> [1-line summary for the ClickUp form]
>
> **Assign To:** [Lead Designer / Lead Video Editor]
> **Priority:** [Standard / Rush / Testing]

---

## Quick Start

To start a guided session, paste this into Claude along with the master system prompt:

```
Load 02_MASTER_SYSTEM_PROMPT.md as context, then follow the guided session from 02_GUIDED_BATCH_SESSION.md.
```

That's it — Claude handles the rest.

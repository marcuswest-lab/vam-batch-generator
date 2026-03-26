# VAM Creative Production System + Hormozi Frameworks

> A data-driven creative ideation and production system for VAM (Value Added Moving), powered by Alex Hormozi's advertising frameworks and live Meta ads performance data. Managed by BAD Marketing agency.

---

## Quick Start

### Guided Session (Recommended — Nate's workflow)
1. Open Claude and paste `02_MASTER_SYSTEM_PROMPT.md` + `02_GUIDED_BATCH_SESSION.md`
2. Claude analyzes your data and recommends 3 batch directions
3. Answer 4-5 quick questions (batch type, focus, etc.)
4. Get 5 agency-ready briefs in BAD Marketing's exact format
5. Submit to ClickUp

### Manual Mode (Advanced)
1. Open Claude and paste `02_MASTER_SYSTEM_PROMPT.md` as context
2. *(Optional)* Run `02_PERFORMANCE_REPORT.md` to see what's performing first
3. Paste the batch generator you need (Static / Video / Copy)
4. Fill in the batch parameters
5. Get 5 agency-ready briefs
6. Submit to ClickUp

**For the full weekly process:** Follow `01_CREATIVE_IDEATION_PROCESS.md`

---

## System Files

### Creative Production System

| File | Purpose |
|------|---------|
| `01_CREATIVE_IDEATION_PROCESS.md` | Weekly step-by-step workflow (review, ideate, assemble, submit) |
| `02_MASTER_SYSTEM_PROMPT.md` | Claude context prompt — brand data, winning/losing patterns, frameworks |
| `02_GUIDED_BATCH_SESSION.md` | **Start here** — All-in-one guided session (analyze → recommend → ask Nate → generate) |
| `02_PERFORMANCE_REPORT.md` | Standalone performance analysis with batch recommendations |
| `02_BATCH_GENERATOR_STATIC.md` | Generates 5 static ad briefs per run |
| `02_BATCH_GENERATOR_VIDEO.md` | Generates 5 video ad briefs per run |
| `02_BATCH_GENERATOR_COPY.md` | Generates 5 body copy variations per run |
| `03_STATIC_AD_BRIEF_TEMPLATE.md` | Blank static brief (BAD Marketing format, dropdown values preserved) |
| `03_VIDEO_AD_BRIEF_TEMPLATE.md` | Blank video brief (BAD Marketing format, dropdown values preserved) |
| `03_BATCH_SUBMISSION_TEMPLATE.md` | Blank body copy brief (BAD Marketing format, dropdown values preserved) |
| `04_WINNING_HOOKS_LIBRARY.md` | Ranked proven hooks with performance metrics |
| `04_WINNING_VISUALS_LIBRARY.md` | Ranked visual styles with performance data |
| `04_LOSING_PATTERNS.md` | Confirmed anti-patterns — DO NOT USE |
| `04_PERFORMANCE_SNAPSHOT.md` | Current KPIs, top performers, naming convention tracker |

### Performance Data (CSV)

| File | Contents |
|------|----------|
| `[VAM] - Creative & Copy Tracking Sheet - Static Ad Performance` | All static ad performance data with naming, spend, ROAS, CPL |
| `[VAM] - Creative & Copy Tracking Sheet - Video Ad Performance` | All video ad performance data with CTR, UGC metrics |
| `[VAM] - Creative & Copy Tracking Sheet - Copy Performance` | Copy hook/body pairing performance |
| `VAM Meta Marketing Dashboard - Dashboard` | Master dashboard metrics |
| `VAM Meta Marketing Dashboard - Applications` | Lead/application data |
| `VAM Meta Marketing Dashboard - Jobs Booked` | Booking data |
| `Hyros Calls Report` | Call tracking and conversion data |
| `Hyros Sales Report` | Sales attribution data |
| `VAM-Click-Data` | Click-level analytics |
| `leads 2_16 - 3_3` | Recent lead data |
| `ValueB Daily` | Daily performance metrics |
| `Report 15-09-2025 - 03-03-2026` | 6-month comprehensive report |

### Agency SOPs

| File | Contents |
|------|----------|
| `BAD Marketing INFO SOP Vault-*.md` | Full BAD Marketing SOP — onboarding, ClickUp, creative requests, media buying, OKRs |
| `BAD-Marketing-SOP-Vault.md` | Condensed SOP reference |
| `[Active] Static Copy Creative Brief _ Template.docx` | Original static brief template from BAD Marketing |
| `[Active] Video Copy_Creative Brief _ Template.docx` | Original video brief template from BAD Marketing |
| `[Active] Body Copy Creative Brief _ Template.docx` | Original body copy brief template from BAD Marketing |

---

## Hormozi Frameworks

### Playbooks (PDFs in `$100M Playbooks/`)

| Playbook | Use When |
|----------|----------|
| `Hooks.pdf` | Writing hooks, headlines, email subjects, video intros |
| `Goated Ads.pdf` | Ad creation system — Kaleidoscope method, Hook/Meat/CTA assembly |
| `Lead Nurture.pdf` | Email sequences, follow-up systems |
| `Pricing.pdf` | Setting and raising prices |
| `Price Raise.pdf` | Raising prices on existing customers |
| `Branding.pdf` | Brand positioning and messaging |
| `Retention.pdf` | Reducing churn, keeping customers |
| `Lifetime Value.pdf` | Increasing LTV, upsells, cross-sells |
| `Fast Cash.pdf` | Quick revenue strategies |
| `Marketing Machine.pdf` | Systematic marketing operations |
| `Closing.pdf` | Sales closing techniques |
| `Proof Checklist.pdf` | Building social proof and credibility |

### Key Frameworks Used in This System

**Kaleidoscope Method** (from Goated Ads Playbook)
- Hook x Meat x CTA = Ad
- Generate components independently, mix and match
- 80% of prep time on hooks

**70-20-10 Hook Rule** (from Hooks Playbook)
- 70% = proven winner variations
- 20% = hooks adapted from other industries
- 10% = experimental new approaches

**5 Awareness Levels** (from Goated Ads Playbook)
1. Most Aware — Offer-driven (30%)
2. Product Aware — Proof-driven (25%)
3. Solution Aware — Promise-driven (20%)
4. Problem Aware — Pain-driven (15%)
5. Unaware — Curiosity-driven (10%)

---

## VAM Performance Summary

| Metric | Current | Target |
|--------|---------|--------|
| ROAS | 1.58x | 2.0x |
| Cost per Connected | $380 | $250 |
| CAC | $1,058 | $750 |
| Total Spend | $550K | — |
| Total Revenue | $871K | — |

**Top performers:** SC7_CheckThis + SV8_Gmail (1.44x ROAS), SC7_CheckThis + SV11_TwitterStyleLight (1.75x ROAS), UGC Asian woman cost angle (8-11% CTR)

**Confirmed losers:** Educational layouts, holiday themes, geo-targeting, sticky notes, holding signs, carousels, animated trucks, polished production

---

## Naming Conventions (Creative Tracker Format)

| Type | Brief Format | Tracker Adds |
|------|--------|---------|
| Static | `[Idea Name] - [Lead Type] Lead` | # + CID (auto) |
| Video | `[Idea Name] - [Lead Type] Lead` | # + VID (auto) |
| Copy | `[Idea Name] - [Lead Type]` | # + CPID (auto) |

The sequential number and CID/CPID/VID are auto-generated by the tracker. Keep Idea Names short (2-4 words).

---

## Weekly Cadence

| Day | Activity | Batch Type |
|-----|----------|-----------|
| Monday | Performance review + hook generation | Planning |
| Tuesday | Static batch 1 (proven winner variations) | Static |
| Wednesday | Video batch 1 (UGC cost/savings) | Video |
| Thursday | Static batch 2 (experimental hooks) | Static |
| Friday | Video batch 2 or copy-only test | Video / Copy |

**Target output: 15-20 new creatives per week**

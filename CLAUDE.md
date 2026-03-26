# VAM Creative Production System

## Project Overview

This is the creative ideation and production system for **VAM (Value Added Moving)**, a long-distance moving company running Meta ads through **BAD Marketing** agency. The system combines VAM's live performance data with Alex Hormozi's advertising frameworks to systematically generate creative briefs at scale.

## Dashboard & Deployment

The system runs as a **web dashboard** (Flask + single HTML file) deployed on Render:

- **Live URL:** `https://vam-batch-generator.onrender.com`
- **Local:** `python3 server.py` → `http://localhost:8090`
- **GitHub repo:** `https://github.com/marcuswest-lab/vam-batch-generator`
- **Render plan:** Free tier (auto-deploys from `main` branch)

### Key Application Files

| File | Purpose |
|------|---------|
| `server.py` | Flask server — serves dashboard, handles .docx generation, Google Sheets API endpoints |
| `dashboard.html` | Single-page dashboard — prompt builder, doc generator, Google Sheets integration UI |
| `generate_doc.py` | Parses Claude's text output into .docx briefs matching BAD Marketing's template format |
| `sheets_data.py` | Google Sheets data pipeline — fetches CSVs, parses ads, computes KPIs, caches results |
| `render.yaml` | Render deployment config |
| `requirements.txt` | Python dependencies (Flask, gunicorn, python-docx) |

### Google Sheets Integration (Live Data)

The dashboard pulls live performance data from two Google Sheets via the "Publish to Web" CSV method (zero API keys required):

1. **Creative & Copy Tracking Sheet** — tabs: `Static Ad Performance`, `Video Ad Performance`, `Copy Performance`
2. **Meta Marketing Dashboard** — tab: `Dashboard`

**How it works:**
- User enters Sheet IDs in the **Data Source** settings panel on the dashboard
- `sheets_data.py` fetches published CSV URLs, parses ad rows, classifies winners/losers, computes KPIs
- Data is injected into `MASTER_PROMPT`, `TOP_PERFORMERS`, and `NET_NEW_OPTIONS` on page load
- Cached in-memory (1-hour TTL) + file-based (`.sheets_cache.json`) for persistence across Render sleep cycles
- Status bar in header shows live/offline/error state with a refresh button

**Setup (one-time):**
1. Publish each Google Sheet to the web: File → Share → Publish to web → select tab → CSV → Publish
2. Copy the Sheet ID from each URL: `https://docs.google.com/spreadsheets/d/{THIS_IS_THE_ID}/edit`
3. Paste both IDs into the Data Source card on the dashboard → click Save & Fetch
4. Optionally set env vars on Render: `SHEET_CREATIVE_TRACKING_ID`, `SHEET_META_DASHBOARD_ID`

**API Endpoints:**
- `GET /api/performance-data` — returns cached live data (prompt section, top performers, KPIs)
- `POST /api/refresh-data` — force re-fetch from Google Sheets
- `GET/POST /api/sheets-config` — get or save Sheet IDs

**If sheets aren't configured,** the dashboard falls back to hardcoded data in `dashboard.html`.

### Ideation / Production Mode Toggle

The dashboard has two modes, toggled via a tab bar above the form:

- **Ideation Mode** (default) — Generates a prompt that instructs Claude to **pitch 3-5 creative angle concepts** with strategic reasoning, example hooks, visual pairings, and confidence ratings. Claude then asks for feedback before drafting any briefs. This enables a collaborative, human-in-the-loop workflow.
- **Production Mode** — The original workflow. Generates a prompt that instructs Claude to output 5 finished creative briefs in one shot, matching BAD Marketing's template format.

**Both modes use the exact same form** (copywriter, batch type, net new/iteration, visual styles, awareness distribution, etc.). The only difference is the output — the `IDEATION_GENERATOR` prompt template vs the production `BATCH_GENERATOR` template. The generate button text changes dynamically ("Generate Pitch Prompt" vs "Generate Production Prompt").

**Recommended workflow:** Start in Ideation mode to explore concepts collaboratively, then switch to Production mode to generate the final briefs once direction is locked in.

### CSV Column Structures (for reference)

**Static Ad Performance:** `Launch Date, Status, (empty col), Ad Name, Cost, Leads, CPL, New Leads, Cost per New Lead, Calls, Cost per Call, Stage: Incoming Call, cost per incoming call, Stage: Connected Call, cost per connected call, Sales, Cost per Sale, Revenue, RPS, ROAS, Profit, CTR (all), CTR (link), CPM, Impressions, Clicks (all), Link Clicks, Closes, Cash Collected, Revenue`
- Ad Name format: `SC7_CheckThis | SV8_Gmail` (copy code | visual code)
- Note: Static CSV has an empty column between Status and Ad Name

**Video Ad Performance:** `Launch Date, Status, Active/Fatigued, Ad Name, Cost, Leads, CPL, ...` (same base + video metrics: 3 Sec Views, Video Plays at 25/50/75/100%, ThruPlays)
- Ad Name format: `VHK1_MovingNoStress | VB1_NoBody | VV1_TruckAcrossUS` (hook | body | visual)

**Copy Performance:** `Launch Date, Status, Ad Name, Cost, Leads, CPL, ...` (same fields + video metrics)
- Ad Name format: `CHK1_SaveUpTo50 | CB1_Savings` (hook | body)

**Meta Dashboard:** `Timeline, Date, Spend, Impressions, CPM, Reach, Clicks (all), CTR (all), CPC (all), Clicks (link), CTR (link), CPC (link), Leads, CPL, New Leads, CPNL, Raw Calls, CPCall, Connected Calls, CPConnected, Connected %, Sales - Book Date, CPA - Book Date, Lead To Close %, Raw Call Close %, Connected Call to Close %, Cash - Book Date, Cash ROAS - Book Date, ...`
- Summary row: `Date = "CURRENT"`, empty Timeline

## How This System Works

### Quick Start — Guided Session (Recommended)
1. Load `02_MASTER_SYSTEM_PROMPT.md` + `02_GUIDED_BATCH_SESSION.md` as context
2. Claude analyzes performance data and presents recommendations
3. Nate picks a direction and answers 4-5 quick questions
4. Claude generates 5 completed creative briefs matching BAD Marketing's exact template format
5. Submit the batch to ClickUp via the Creative Request Form

### Quick Start — Manual (Advanced)
1. Load `02_MASTER_SYSTEM_PROMPT.md` as context in your Claude session
2. *(Optional)* Run `02_PERFORMANCE_REPORT.md` first to see what's working
3. Paste the appropriate batch generator (`02_BATCH_GENERATOR_STATIC.md`, `02_BATCH_GENERATOR_VIDEO.md`, or `02_BATCH_GENERATOR_COPY.md`)
4. Fill in the batch parameters (focus, awareness distribution, visual priority)
5. Claude outputs 5 completed creative briefs
6. Submit the batch to ClickUp via the Creative Request Form

### Weekly Workflow
Follow `01_CREATIVE_IDEATION_PROCESS.md` for the full weekly cycle:
- **Monday:** Performance review + hook generation
- **Tuesday:** Static batch 1 (proven winner variations)
- **Wednesday:** Video batch 1 (UGC cost/savings angle)
- **Thursday:** Static batch 2 (adjacent/experimental)
- **Friday:** Video batch 2 or copy-only batch

## File Structure

### Core System Files (numbered for workflow order)
- `01_CREATIVE_IDEATION_PROCESS.md` — Weekly step-by-step process
- `02_MASTER_SYSTEM_PROMPT.md` — Load this into every Claude session
- `02_GUIDED_BATCH_SESSION.md` — **Start here** — All-in-one guided session (analyze → recommend → ask Nate → generate)
- `02_PERFORMANCE_REPORT.md` — Standalone performance analysis with batch recommendations
- `02_BATCH_GENERATOR_STATIC.md` — Generates 5 static ad briefs
- `02_BATCH_GENERATOR_VIDEO.md` — Generates 5 video ad briefs
- `02_BATCH_GENERATOR_COPY.md` — Generates 5 body copy variations
- `03_STATIC_AD_BRIEF_TEMPLATE.md` — Blank static brief (BAD Marketing format, with dropdown values)
- `03_VIDEO_AD_BRIEF_TEMPLATE.md` — Blank video brief (BAD Marketing format, with dropdown values)
- `03_BATCH_SUBMISSION_TEMPLATE.md` — Blank body copy brief (BAD Marketing format, with dropdown values)

### Reference Data (update weekly)
- `04_WINNING_HOOKS_LIBRARY.md` — All proven hooks with metrics
- `04_WINNING_VISUALS_LIBRARY.md` — Ranked visual styles
- `04_LOSING_PATTERNS.md` — Confirmed anti-patterns (DO NOT USE)
- `04_PERFORMANCE_SNAPSHOT.md` — Current KPIs, top performers, naming tracker

### Source Data
- CSV files from Meta Marketing Dashboard and Creative & Copy Tracking Sheets
- Hyros call/sales reports
- Lead and click data exports

### Agency SOPs
- `BAD Marketing INFO SOP Vault-*.md` — Full BAD Marketing SOP
- `BAD-Marketing-SOP-Vault.md` — Condensed SOP reference
- `[Active] *.docx` — Original brief templates from BAD Marketing

### Frameworks (Hormozi)
- Playbooks (PDFs in `$100M Playbooks/`): Hooks, Goated Ads, Lead Nurture, Pricing, Branding, Retention, Lifetime Value, Fast Cash, Marketing Machine, Price Raise, Closing, Proof Checklist

## Key Business Context

**VAM targets:**
- 2.0x ROAS (currently 1.58x)
- $250 cost per connected call (currently $380)
- $750 CAC (currently $1,058)

**What works:** Social proof shock (CheckThis, AlmostPaidDouble), price anchoring ($1,597), UGC testimonials with cost/savings angles, Gmail/TwitterStyle visuals

**What doesn't work:** Educational layouts, holiday themes, geographic targeting, animated trucks, holding signs, sticky notes, carousels, polished/branded production

## Naming Conventions (Creative Tracker Format)

The creative name is a formula: `[Angle Name] - [variable based on Variation Type]`. The number (#) and CID/CPID/VID are auto-generated by the tracker — briefs only provide the base name.

- **Static (depends on Variation Type):**
  - Copy variation: `[Angle Name] - [Lead Type] Lead` → e.g., `Quiet Overwhelm - Offer Lead`
  - Visual variation: `[Angle Name] - [Visual Style]` → e.g., `VAM Crew Members - Organic Looking`
  - Tracker auto-appends: `→ Quiet Overwhelm - Offer Lead 1 - CID[auto]`
- **Video:** `[Angle Name] - [Lead Type] [Variation Type]`
  - Lead: `Done For You - Problem-Solution Lead`
  - Body: `Real Trucks Real Prices - Problem-Solution Body`
  - Pattern Interrupt / Graphic Overlay / CTA follow the same pattern
- **Copy (same pattern as video):**
  - Lead/Body/CTA: `[Angle Name] - [Lead Type] [Variation Type]` → e.g., `Heart3Heart - Promise Lead`
  - Full: `[Angle Name] - [Lead Type]` → e.g., `Heart3Heart - Promise`
  - When Copy Type = Asset Set: `[Angle Name] - Asset Set`

**Name rules:**
- Keep Angle Names SHORT (2-4 words max) — these become actual ad names in the tracker
- Use natural casing with spaces (not CamelCase): "Quiet Overwhelm" not "QuietOverwhelm"
- Light/dark visual variants are NOT separate styles — use base name (e.g., "Gmail" not "Gmail Dark")

## Dropdown Field Constraints (from BAD Marketing .docx templates)

All brief output must use ONLY these dropdown values:

| Field | Static | Video | Body Copy |
|-------|--------|-------|-----------|
| Variation Type | Copy · Visual | Lead · Pattern Interrupt · Graphic Overlay · Body · CTA | Lead · Body · CTA · Full |
| Lead Type | Offer · Promise · Problem-Solution · Secret · Proclamation · Story | *(same)* | *(same)* |
| Awareness Level | Most Aware · Product Aware · Solution Aware · Problem Aware · Unaware | *(same)* | *(same)* |
| Status | Ready For Internal · Changes Required · Needs Client Approval · Approved | *(same)* | *(same)* |
| Static Format | Single Static · Carousel | — | — |
| Copy Type | — | — | Primary Text · Asset Set · Headline |

**Copywriter:** Nate (default for all briefs)

## Important Notes
- Always check `04_LOSING_PATTERNS.md` before creating new concepts
- UGC video format dominates — 8-11% CTR vs 2-3% for animated
- Batch size is 5 creatives — submit one ClickUp form per batch
- Copy brief must be completed BEFORE creative request
- Static batches → assign to Lead Designer
- Video batches → assign to Lead Video Editor

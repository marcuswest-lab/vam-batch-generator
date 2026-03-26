---
name: creative-performance-dashboard
description: "Build a weekly Creative Performance Dashboard from CSV exports, Excel tracker files, or Facebook ad spend data. Use this skill whenever the user asks to create a creative performance report, build a creative dashboard, generate a weekly ad performance report, or uploads CSV/Excel files with columns like CPQA, ROAS, Cost per Connected, Stage: Qualified Application, Hook Rate, Hold Rate, or mentions video variations, static variations, video concepts, static concepts, copy concepts, or copy performance tabs. Also trigger when the user mentions ad creative analysis, cost per qualified application, cost per connected call, Facebook ad preview links, or wants to see top-performing ads. This skill covers the full pipeline: parsing CSVs/Excel, extracting hyperlinks from tracker tabs, concept roll-up aggregation, generating an interactive HTML dashboard with sortable tables and KPI color coding, and producing a top-ads text summary report."
---

# Creative Performance Dashboard

## Overview

This skill generates a weekly interactive HTML dashboard for a client's creative ad performance data. It parses CSV exports or Excel files from the client's reporting system, extracts ad preview/file links from tracker tabs (including embedded hyperlinks), and produces a dark-themed sortable dashboard with up to six tabs: Static Ads, Static Concepts, Video Ads, Video Concepts, Copy, and Copy Concepts.

The dashboard is client-agnostic — adapt the title, date range, KPI thresholds, and naming conventions to each client. Ask the user for client-specific details if not provided.

## Required Inputs

The user will provide some or all of:

1. **Creative Data** (CSV or Excel with performance tabs):
   - Static Ad Performance (static variations)
   - Video Ad Performance (video variations)
   - Copy Performance
   - Static Concepts (may be a separate CSV or generated via roll-up)
   - Video Concepts (may be a separate CSV or generated via roll-up)
   - Copy Concepts (may be a separate CSV or generated via roll-up)

2. **Tracker files** (optional but recommended, for ad preview/file links):
   - May be an Excel workbook with tracker tabs containing hyperlinks (e.g., "File Link", "Performance", "Folder Link" columns with embedded `=HYPERLINK()` or clickable cells)
   - May be a separate Facebook Ad Spend/Click Report CSV with `Ad name`, `Amount spent (USD)`, `Preview link` columns
   - Some clients have **two tracker files** (old format + new format) — extract links from both and merge

3. **Date range** for the report header

4. **Client name** for the report title (ask if not provided)

5. **KPI thresholds** (ask if not provided — these vary significantly by client):
   - Primary KPI (e.g., ROAS, CPQA, Cost per Connected) with green/yellow/red cutoffs
   - Secondary KPIs with thresholds
   - Hook Rate / Hold Rate cutoffs (video tabs only)

## Configurable KPI Thresholds

Ask the user for their KPI targets. There are no universal defaults — thresholds depend on the client's business model (e.g., lead gen vs e-commerce, high-ticket vs low-ticket). Common KPI types:

**Cost-based KPIs** (lower is better — green ≤ threshold):
- CPQA (Cost per Qualified Application)
- Cost per Connected Call
- CAC (Cost per Sale / Customer Acquisition Cost)
- CPL (Cost per Lead)

**Rate/Ratio KPIs** (higher is better — green ≥ threshold):
- ROAS (Return on Ad Spend)
- Hook Rate / Hold Rate (video only)
- Close Rate

**Color system:**
| Status | Color |
|--------|-------|
| Within KPI | Green (`#34D399`) |
| On the Fence | Yellow (`#FBBF24`) |
| Above/Below KPI | Red (`#F87171`) |
| No Data | Gray muted (`#475569`) |

**Badge class names:** `wk` (within KPI/green), `of` (on the fence/yellow), `ak` (above KPI/red), `nd` (no data/gray)

## CSV / Excel Column Structure

Column names vary by client. **Always inspect the actual headers first** before writing parsing code. Common patterns:

### Core columns (most clients):
- `Ad Name` / `Name` — Creative name
- `Cost` — Dollar amount (may have `$` and commas)
- `Leads`, `Cost per Lead` / `CPL`
- `Impressions`, `CTR (all)`, `CTR (link)`, `CPM`
- `Status` — Winner/Loser/Testing/On the Fence/Paused

### Call/sales funnel columns (lead-gen clients):
- `New Leads`, `Cost per New Lead`
- `Stage: Incoming Call`, `cost per incoming call`
- `api-outbound-call-outbound / Calls` (outbound calls), `Cost per Outbound Call`
- `Stage: Inbound Connected Call`, `cost per inbound connected`
- `Outbound connected calls`, `cost per outbound connected`
- `Connected (Total)`, `cost per connected (total)`
- `connected close rate (total)`
- `Sales`, `Cost per Sale`, `Revenue`, `ROAS`, `Profit`

### E-commerce / application funnel columns:
- `Stage: Qualified Application`, `CPQA`
- `Stage: Marketing Qualified Lead`, `CPMQL`
- `Stage: Sales Qualified Lead`, `CPSQL`
- `Stage: Customer`, `CAC`

### Video-specific columns:
- `Hook Rate`, `Hold Rate`
- `3-sec plays` / `3 Sec Views`, `ThruPlays`
- `Video Plays at 25%/50%/75%/100%`

**Important**: Invalid values appear as `#DIV/0!` or `#REF!` — these should be treated as null/`—`.

## Creative Naming Conventions

Clients use different naming systems. **Inspect the actual data** to identify the pattern. Two common formats:

### Old-style: Pipe-delimited with prefix codes
```
SC7_CheckThis | SV8_Gmail          (static: concept | visual variation)
VHK1_MovingNoStress | VB1_NoBody | VV1_TruckAcrossUS   (video: hook | body | visual)
CHK1_SaveUpTo50 | CB1_Savings      (copy: hook | body)
```
Common prefixes: VHK (Video Hook), VB (Video Body), VV (Video Visual/Concept), SC (Static Concept), SV (Static Variation), CHK (Copy Hook), CB (Copy Body)

### New-style: Dash-delimited with descriptive names
```
Stranger Danger Validation - Story Lead 1 - CIDR8KIRXC
Cost Shock Revelation - Problem-Solution Lead 2 - CIDAMRGS3U
VAM Crew Members - Organic Looking 1 - CIDQG45LVZ
```
Format: `[Angle Name] - [Lead Type] [Variation Type] [N] - [CID]`

Both formats may coexist in the same dataset.

## Data Processing Steps

### Step 1: Parse Performance Data

```python
import pandas as pd
import re

def parse_dollar(v):
    if pd.isna(v): return None
    if isinstance(v, (int, float)): return float(v)
    s = str(v).replace('$','').replace(',','')
    try: return float(s)
    except: return None

def clean_pct(v):
    if pd.isna(v) or str(v).strip() in ('', '#DIV/0!', '#REF!', 'nan'): return None
    if isinstance(v, (int, float)): return round(v * 100, 2) if abs(v) < 1 else round(v, 2)
    s = str(v).replace('%','').strip()
    try: return round(float(s), 2)
    except: return None

def clean_num(v):
    if pd.isna(v) or str(v).strip() in ('', '#DIV/0!', '#REF!', 'nan'): return None
    try: return float(v)
    except: return None
```

- Filter to rows with Cost > 0 only
- Parse all dollar values by stripping `$` and `,`
- Convert `#DIV/0!` and `#REF!` to null/`—`
- Exclude known example/test rows (ask user or detect patterns like `SC1_9t5`)
- **Include ALL columns from the source data** — don't skip columns. The user expects every metric to be available in the dashboard.

### Step 2: Extract Ad Preview / File Links from Tracker Tabs

Links are typically stored in Excel tracker tabs as embedded hyperlinks, NOT as plain text URLs. Use `openpyxl` to read hyperlinks:

```python
import openpyxl

def extract_links_from_tracker(file_path, sheet_name, name_header='Creative Name'):
    """Extract links from tracker tabs using openpyxl (reads embedded hyperlinks)."""
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb[sheet_name]
    headers = {}
    for cell in ws[1]:
        if cell.value:
            headers[str(cell.value).strip()] = cell.column

    name_col = headers.get(name_header)
    # Try multiple possible link column names
    link_col = None
    for col_name in ['File Link', 'Folder Link', 'Performance', 'New Performance', 'Preview Link']:
        if col_name in headers:
            link_col = headers[col_name]
            break

    link_map = {}
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        name = str(row[name_col-1].value or '') if name_col else ''
        if not name or name == 'nan': continue

        # Check cell value first, then embedded hyperlink
        best_link = None
        if link_col:
            cell = row[link_col-1]
            val = str(cell.value or '')
            if 'http' in val.lower():
                best_link = val
            elif cell.hyperlink and cell.hyperlink.target and 'http' in cell.hyperlink.target.lower():
                best_link = cell.hyperlink.target

        if best_link:
            link_map[name] = best_link

    wb.close()
    return link_map
```

**Key points:**
- Cells may show "See Here" or other display text while containing an `=HYPERLINK()` formula — use `cell.hyperlink.target` to get the actual URL
- Check multiple columns: `File Link`, `Folder Link`, `Performance`, `New Performance`
- Some clients have **two tracker files** — extract from both and merge (new tracker takes priority)
- Also check for a `New Name` column — some trackers have both old and new names for the same creative

### Step 3: Match Links from Facebook Ad Spend Report

If a Facebook ad spend CSV is provided (instead of or in addition to tracker tabs), match preview links:

1. Split ad name by `|`, identify creative identifier parts vs copy/date parts
2. Join creative parts to form a variation key
3. For each variation, keep the preview link with highest spend
4. For concepts, aggregate best link per concept identifier
5. For copy, match by copy hook identifier

**CRITICAL: URL encoding in HTML**
Facebook preview links contain `&h=` which gets eaten by the HTML parser. Use `\\u0026` instead of `&` in JavaScript string literals within the HTML file:
```javascript
// WRONG - &h= gets interpreted as HTML entity
link:"https://www.facebook.com/?feed_demo_ad=123&h=AQIxyz"

// CORRECT - \u0026 is interpreted by JS as &
link:"https://www.facebook.com/?feed_demo_ad=123\\u0026h=AQIxyz"
```

### Step 4: Concept Roll-Up (when concept-level CSVs are NOT provided)

If the user only provides variation-level data (no separate concept CSVs), **generate concept tabs by rolling up variations**. This is the more common case.

#### Concept name extraction

Extract the core concept/angle name from each ad name, stripping variation-level detail:

```python
def normalize_old_concept(raw):
    """Strip version/holiday/CTA suffixes to get core concept name.
    e.g. CheckThisHolidayV3 -> CheckThis, LongDistance1597CTA1 -> LongDistance1597,
    CityPricesV4 -> CityPrices, CoastToCoast-V2 -> CoastToCoast"""
    raw = re.sub(r'CTA\d+$', '', raw)
    raw = re.sub(r'Holiday(V\d+)?$', '', raw)
    raw = re.sub(r'NY(V\d+)?$', '', raw)
    raw = re.sub(r'-?V\d+$', '', raw)
    return raw.strip('-').strip()

def extract_static_concept(name):
    if '|' in name:
        sc_part = name.split('|')[0].strip()
        m = re.match(r'SC\d+_(.+)', sc_part)
        if m: return normalize_old_concept(m.group(1))
        return sc_part
    elif ' - ' in name:
        return name.split(' - ')[0].strip()
    return name

def extract_video_concept(name):
    if '|' in name:
        parts = [p.strip() for p in name.split('|')]
        vv = [p for p in parts if p.startswith('VV')]
        if vv:
            m = re.match(r'VV\d+_(.+)', vv[0])
            raw = m.group(1) if m else vv[0]
            return normalize_old_concept(raw)
        return parts[0]
    elif ' - ' in name:
        return name.split(' - ')[0].strip()
    return name

def extract_copy_concept(name):
    if '|' in name:
        chk_part = name.split('|')[0].strip()
        m = re.match(r'CHK\d+_(.+)', chk_part)
        if m: return normalize_old_concept(m.group(1))
        return chk_part
    elif ' - ' in name:
        return name.split(' - ')[0].strip()
    return name
```

**Important normalization rules:**
- Strip trailing version numbers: V1, V2, V3, -V2
- Strip Holiday variants: Holiday, HolidayV1, HolidayV2
- Strip NY (New Year) variants: NY, NYV1, NYV2
- Strip CTA suffixes: CTA1, CTA2
- For new-style names (`Angle Name - Lead Type N - CID`), the concept is everything before the first ` - `
- Both old-style and new-style names should coexist and roll up correctly

#### Roll-up aggregation

```python
from collections import defaultdict

def rollup(rows, concept_fn, is_video=False):
    groups = defaultdict(list)
    for r in rows:
        concept = concept_fn(r['name'])
        groups[concept].append(r)

    rolled = []
    for concept, variations in groups.items():
        # Sum all additive metrics
        cost = sum(v['cost'] or 0 for v in variations)
        leads = sum(v['leads'] or 0 for v in variations)
        new_leads = sum(v.get('newLeads') or 0 for v in variations)
        incoming = sum(v['incoming'] or 0 for v in variations)
        outbound = sum(v.get('outbound') or 0 for v in variations)
        inbound_connected = sum(v.get('inboundConnected') or 0 for v in variations)
        outbound_connected = sum(v.get('outboundConnected') or 0 for v in variations)
        connected = sum(v['connected'] or 0 for v in variations)
        sales = sum(v['sales'] or 0 for v in variations)
        revenue = sum(v['revenue'] or 0 for v in variations)
        profit = sum(v['profit'] or 0 for v in variations)
        impressions = sum(v['impressions'] or 0 for v in variations)

        row = {
            'name': concept,
            'variations': len(variations),
            'cost': cost if cost > 0 else None,
            'leads': leads if leads > 0 else None,
            'cpl': (cost / leads) if leads > 0 else None,
            'newLeads': new_leads if new_leads > 0 else None,
            'cpnl': (cost / new_leads) if new_leads > 0 else None,
            # ... recalculate ALL cost-per metrics from summed numerators
            'connected': connected if connected > 0 else None,
            'costConnected': (cost / connected) if connected > 0 else None,
            'sales': sales if sales > 0 else None,
            'cps': (cost / sales) if sales > 0 else None,
            'revenue': revenue if revenue > 0 else None,
            'roas': (revenue / cost) if cost > 0 and revenue > 0 else None,
            'profit': profit,
            'ctrAll': None,  # Cannot sum percentages — leave null for concepts
            'ctrLink': None,
            'cpm': (cost / impressions * 1000) if impressions > 0 else None,
            'impressions': impressions if impressions > 0 else None,
        }

        # Video metrics: weighted average by impressions
        if is_video:
            hook_total = sum((v.get('hookRate') or 0) * (v.get('impressions') or 0) for v in variations)
            hold_total = sum((v.get('holdRate') or 0) * (v.get('impressions') or 0) for v in variations)
            total_impr = sum(v.get('impressions') or 0 for v in variations)
            row['hookRate'] = round(hook_total / total_impr, 1) if total_impr > 0 and hook_total > 0 else None
            row['holdRate'] = round(hold_total / total_impr, 1) if total_impr > 0 and hold_total > 0 else None

        # Pick link from top-spending variation that has a link
        linked = [v for v in variations if v.get('link')]
        if linked:
            top_var = max(linked, key=lambda v: v.get('cost') or 0)
            row['link'] = top_var['link']
        else:
            row['link'] = None

        rolled.append(row)

    rolled.sort(key=lambda x: -(x['roas'] if x['roas'] is not None else -999))
    return rolled
```

**Roll-up rules:**
- **Additive metrics** (cost, leads, sales, revenue, impressions, etc.): SUM across variations
- **Cost-per metrics** (CPL, CPQA, CAC, etc.): RECALCULATE from summed cost / summed count — never average the cost-per values
- **Rate metrics** (Hook Rate, Hold Rate): WEIGHTED AVERAGE by impressions
- **Percentage metrics** (CTR, Close Rate): Cannot be summed — leave null for concepts, or recalculate from clicks/impressions if available
- **Link**: Use the link from the highest-spending variation that has one
- Show variation count as "(N ads)" next to concept name

### Step 5: Data Integrity Check

Concept-level total spend may exceed the sum of variation-level rows because some variation rows may be missing from the export. Flag this to the user if the gap is significant — concepts are typically the source of truth for totals.

## Dashboard Specification

### Design System

- **Theme**: Dark background (`#0C0F14`), surface cards (`#151922`)
- **Font**: DM Sans for UI, JetBrains Mono for numbers
- **Max width**: 1700px container
- **Color coding**: Green/Yellow/Red badge system for KPIs
- **No summary KPI bar**: Do not include an aggregate KPI summary section at the top. The dashboard is table-only with a legend, search/filter controls, and tabs.

### Status Badges

Ads may have a `Status` field. Render as colored badges:
- **Winner**: Green badge
- **Loser**: Red badge
- **Testing**: Blue badge
- **On the Fence**: Yellow badge (same yellow as KPI "on the fence")
- **Paused/Killed**: Gray badge

Concept tabs don't show status (aggregated ads have mixed statuses).

### Badge Functions

```javascript
// Generic KPI badge — works for both "lower is better" and "higher is better"
function ccBadge(v, metric) {
  if (v == null) return 'nd';
  const k = KPI[metric];
  if (!k) return 'nd';
  // Higher-is-better metrics (ROAS, hook rate, hold rate)
  if (metric === 'roas' || metric === 'hookRate' || metric === 'holdRate') {
    if (v >= k.green) return 'wk';
    if (v >= k.yellow) return 'of';
    return 'ak';
  }
  // Lower-is-better metrics (cost per X)
  if (v <= k.green) return 'wk';
  if (v <= k.yellow) return 'of';
  return 'ak';
}
```

### Six Tabs (maximum)

| Tab | Data Source | Has Video Metrics | Concept Tab |
|-----|-----------|-------------------|-------------|
| Static Ads | Static performance data | No | No |
| Static Concepts | Roll-up or separate CSV | No | Yes |
| Video Ads | Video performance data | Yes (Hook/Hold) | No |
| Video Concepts | Roll-up or separate CSV | Yes (Hook/Hold) | Yes |
| Copy | Copy performance data | No | No |
| Copy Concepts | Roll-up or separate CSV | No | Yes |

Only include tabs for which data is provided. All tabs should have link columns if preview links are available. Concept tabs show a "# Ads" column instead of "Status".

### Table Columns

Include ALL columns from the source data. A typical full column set:

`#, Name, Ad (link), Status/Ads, Spend, Leads, CPL, New Leads, CPNL, Calls In, $/Call In, Outbound, $/Outbound, Inb Connected, $/Inb Conn, Outb Connected, $/Outb Conn, Connected, $/Connected, Hook %, Hold %, Close %, Sales, CAC, Revenue, ROAS, Profit, CTR (all), CTR (link), CPM, Impressions`

Adapt columns to match the client's actual data. **Do not omit columns that exist in the source data.**

### Sorting

- Default sort: Primary KPI (e.g., ROAS descending, or CPQA ascending)
- Null values sort to bottom
- Clickable column headers for all sortable columns
- Sort arrows display on active column

### Sticky Name Column

The `#` and `Name` columns should be sticky (position: sticky) so they remain visible when scrolling horizontally. Set `min-width: 320px` on the name column.

### Legend

Updates dynamically based on active tab:
- Shows primary KPI thresholds (e.g., ROAS, $/Connected)
- Video tabs additionally show Hook/Hold thresholds

### No Totals Row

Do not include a totals/summary row at the bottom of tables.

### View Links

The "Ad" column shows a "View" link with an external icon SVG that opens the ad preview in a new tab. Show `—` if no link is available.

### Search and Filter Controls

- Search input: filters by creative name (case-insensitive)
- Filter buttons: "Winners Only" (filter by status), "Min $X Spend" (configurable threshold)

## Top Ads Text Report

In addition to the dashboard, the user may request a text-based "Top Ads" summary. Format:

```
**Top Ads (date range):**

- [Creative Name](preview_link)
    - $X,XXX.XX Spent
    - N leads at $XXX.XX
    - N qualified leads at $XXX.XX
    - N MQLs at $XXX.XX
    - N SQLs at $XXX.XX
    - N customers at $XXX.XX
```

Rules:
- Only include creatives meeting the user's threshold (ask for KPI cutoff and minimum count)
- Sort by primary KPI
- Only include funnel stages with values > 0
- Hyperlink the creative name to its ad preview link
- Can also be used for roll-up reports (combining variations under a concept/body)
- When rolling up, sum cost/leads/qa/mql/sql/customer and recalculate cost-per metrics

## File Output

Save the dashboard HTML with a descriptive name including the client and date range, e.g., `clientname_dashboard_mar16_23.html`.

## Common Issues

1. **Facebook links truncated**: Always use `\\u0026` for `&` in URLs within JS strings in HTML files
2. **Spend mismatch between variations and concepts**: Concepts are typically the source of truth; variations export may be incomplete
3. **`#DIV/0!` and `#REF!` values**: Clean to null/`—` during parsing
4. **Overlapping date ranges**: If combining data from overlapping weekly exports, flag the overlap to the user rather than silently double-counting
5. **Browser caching**: If the user reports seeing old versions after publishing, generate with a new filename
6. **Column name variations**: Different clients may use slightly different column names — inspect headers first and adapt
7. **Naming convention differences**: Not all clients use the VHK/VB/VV system — inspect the data and adapt the link-matching logic accordingly
8. **Hyperlinks in Excel**: Cell values may show display text ("See Here") while actual URLs are embedded as hyperlinks — use `openpyxl` with `cell.hyperlink.target` to extract
9. **Two tracker files**: Some clients have an old tracker and a new tracker — extract links from both and merge, with the newer tracker taking priority
10. **Concept roll-up too granular**: Old-style names often have Holiday, NY, CTA, V2/V3 suffixes that should be stripped to get the core concept — use regex normalization
11. **Duplicate rows**: Some datasets have duplicate ad names — deduplicate by keeping the first occurrence
12. **Missing columns in concept tabs**: Concept tabs must include ALL the same columns as variation tabs — don't skip any metrics during roll-up aggregation

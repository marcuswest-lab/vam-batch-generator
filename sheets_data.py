#!/usr/bin/env python3
"""
Google Sheets Data Pipeline for VAM Dashboard

Fetches published Google Sheet CSVs, parses ad performance data,
classifies winners/losers, computes KPIs, and builds the prompt
performance section + UI data structures.

Sheets required (published to web as CSV):
  1. Creative & Copy Tracking Sheet — tabs: Static Ad Performance,
     Video Ad Performance, Copy Performance
  2. Meta Marketing Dashboard — tab: Dashboard
"""

import csv
import io
import json
import os
import re
import time
import threading
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '.sheets_cache.json')
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '.sheets_config.json')
CACHE_TTL = 3600  # 1 hour in seconds

# Business targets (hardcoded — these are strategic constants)
TARGETS = {
    'roas': 2.0,
    'cost_per_connected': 250,
    'cac': 750,
}

# Tab names in the Google Sheets
CREATIVE_TABS = {
    'static': 'Static Ad Performance',
    'video': 'Video Ad Performance',
    'copy': 'Copy Performance',
}
DASHBOARD_TAB = 'Dashboard'

# Ad code → semantic name mapping
# Static copy codes
COPY_CODE_MAP = {
    'SC1': 'Long Distance $1,597',
    'SC2': 'Well Move Everything',
    'SC3': 'Why Pay More',
    'SC4': 'City Prices',
    'SC5': 'Moving Checklist',
    'SC6': 'Stress Free',
    'SC7': 'Check This',
    'SC8': 'Dodged 4k Bill',
    'SC9': 'Almost Paid Double',
    'SC10': 'Almost Paid 3k',
    'SC11': 'Flying Funny',
    'SC12': 'Coast to Coast',
    'SC13': 'Licensed Insured',
    'SC14': 'Arrived Flawless',
    'SC15': 'Gently Correctly',
    'SC16': 'Relax Leave It',
    'SC17': 'Choose Date Later',
    'SC18': 'From Scheduling',
    'SC19': 'Move Timeline',
    'SC20': 'How Movers Sneak',
    'SC21': 'Didnt Realized',
    'SC22': 'I Thought Cost More',
    'SC23': 'Full Service Moves',
    'SC24': 'Save Up To 50',
    'SC25': 'Starting At 1597',
    'SC33': 'Check This Holiday V3',
    'SC88': 'City Prices V4',
}

# Static visual codes
VISUAL_CODE_MAP = {
    'SV1': 'Beach',
    'SV2': 'Truck Side 2',
    'SV3': 'Truck Back',
    'SV4': 'Apple Note Button CTA',
    'SV5': 'Apple Note Link CTA',
    'SV6': 'Truck Freeway',
    'SV7': 'Apple Note',
    'SV8': 'Gmail',
    'SV9': 'Gmail Light',
    'SV10': 'Twitter Style',
    'SV11': 'Twitter Style Light',
    'SV12': 'Us vs Them',
    'SV13': 'Before After',
    'SV14': 'Full Truck Interior',
    'SV15': 'Organic Crew Photo',
    'SV19': 'Holding Sign',
    'SV20': 'Holding Sign 2',
    'SV21': 'Holding Sign 3',
    'SV22': 'Truck Calendar',
    'SV27': 'Empty Space',
    'SV28': 'Truck Map',
    'SV29': 'Sticky Note',
    'SV30': 'Educational Layout',
}

# Video hook codes
VIDEO_HOOK_MAP = {
    'VHK1': 'Moving No Stress',
    'VHK2': 'OO State No Stress',
    'VHK3': 'Finally Simple',
    'VHK4': 'Dont Pay More',
    'VHK5': 'Why Pay More',
    'VHK6': 'Florida to Texas',
    'VHK7': 'Affordable Moving',
    'VHK8': 'Cross Country Move',
    'VHK9': 'Save Up To 50',
    'VHK10': 'Check This',
    'VHK11': 'Starting At 1597',
    'VHK12': 'Long Distance Move',
    'VHK13': 'Truck on Time',
    'VHK14': 'Stress Free Move',
    'VHK15': 'Full Service Moves',
    'VHK16': 'City Prices',
    'VHK17': 'Almost Paid Double',
    'VHK18': 'Dodged 4k Bill',
    'VHK19': 'Flying Funny',
    'VHK20': 'I Almost Didnt',
    'VHK21': 'Didnt Realized',
    'VHK22': 'I Thought Cost More',
}

# Video visual codes
VIDEO_VISUAL_MAP = {
    'VV1': 'Truck Across US',
    'VV2': 'ChatGPT',
    'VV3': 'Side Truck Animation',
    'VV4': 'Animated Truck 1',
    'VV5': 'Animated Truck 2',
    'VV6': 'Animated Truck 3',
    'VV7': 'UGC White Woman',
    'VV8': 'UGC White Woman 2',
    'VV9': 'UGC White Woman 3',
    'VV10': 'UGC Asian Woman',
    'VV11': 'UGC Asian Woman 2',
    'VV12': 'UGC Asian Woman 3',
    'VV13': 'Polished IG Testimonial',
}

# Video body codes
VIDEO_BODY_MAP = {
    'VB1': 'No Body',
    'VB2': 'Budget Move Quote',
    'VB3': 'VAM Quote',
    'VB4': 'Fair Price Quote',
    'VB5': 'Cost Savings Body',
    'VB6': 'I Thought Body',
}

# Copy hook codes
COPY_HOOK_MAP = {
    'CHK1': 'Save Up To 50',
    'CHK2': 'Starting At 1597',
    'CHK3': 'Stress Free Long Distance',
    'CHK4': 'Up To 50 Off',
    'CHK5': 'Holiday Moves 1597',
    'CHK6': 'Check Rate',
    'CHK7': 'Check This',
    'CHK8': 'Full Service Moves',
    'CHK9': 'Almost Paid Double',
    'CHK10': 'Save Thousands',
    'CHK11': 'Didnt Realized',
    'CHK12': 'City Prices',
    'CHK13': 'Dodged 4k Bill',
    'CHK14': 'How Movers Sneak',
    'CHK15': 'Full Service Moves',
}

# Copy body codes
COPY_BODY_MAP = {
    'CB1': 'Savings',
    'CB2': 'Stress Free',
    'CB3': 'Cost Savings',
    'CB4': 'Holiday Direct',
    'CB5': 'Problem Solution',
    'CB6': 'Before You Book',
    'CB7': 'Service Promise',
    'CB8': 'Before You Book',
}

# Angle classification — which copy codes map to which angle
ANGLE_MAP = {
    'Social Proof Shock': ['SC7', 'SC8', 'SC9', 'SC10', 'SC33', 'CHK7',
                           'CHK9', 'CHK13', 'VHK10', 'VHK17', 'VHK18',
                           'VHK20'],
    'Price Anchoring': ['SC1', 'SC4', 'SC25', 'SC88', 'CHK2', 'CHK5',
                        'CHK12', 'VHK11', 'VHK16'],
    'Cost Exposure': ['SC9', 'SC20', 'SC21', 'SC22', 'CHK11', 'CHK14',
                      'VHK21', 'VHK22'],
    'Savings Quantification': ['SC24', 'CHK1', 'CHK4', 'CHK10', 'VHK9'],
    'Emotional Relief': ['SC5', 'SC6', 'CHK3', 'VHK1', 'VHK2', 'VHK3',
                         'VHK14'],
    'Humor/Relatability': ['SC11', 'VHK19'],
    'Service Promise': ['SC2', 'SC23', 'CHK8', 'CHK15', 'VHK15'],
}

# ---------------------------------------------------------------------------
# In-memory cache
# ---------------------------------------------------------------------------
_cache = {
    'data': None,
    'timestamp': 0,
    'fetching': False,
}
_cache_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def clean_currency(val):
    """Parse a currency string like '$42,694.17' into a float.
    Returns 0.0 for errors like #DIV/0!, #REF!, empty, etc."""
    if not val or not isinstance(val, str):
        return 0.0
    val = val.strip()
    if val.startswith('#') or val == '' or val == '-':
        return 0.0
    # Remove $, commas, quotes
    val = val.replace('$', '').replace(',', '').replace('"', '').strip()
    # Handle negative in parens: ($500) -> -500
    if val.startswith('(') and val.endswith(')'):
        val = '-' + val[1:-1]
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def clean_pct(val):
    """Parse a percentage string like '35.96%' into a float (0.3596).
    Returns 0.0 for errors."""
    if not val or not isinstance(val, str):
        return 0.0
    val = val.strip()
    if val.startswith('#') or val == '' or val == '-':
        return 0.0
    val = val.replace('%', '').replace(',', '').strip()
    try:
        return float(val) / 100.0
    except (ValueError, TypeError):
        return 0.0


def clean_int(val):
    """Parse an integer string like '1,089' into int. Returns 0 for errors."""
    if not val or not isinstance(val, str):
        return 0
    val = val.strip()
    if val.startswith('#') or val == '' or val == '-':
        return 0
    val = val.replace(',', '').replace('"', '').strip()
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0


def clean_float(val):
    """Parse a float string. Returns 0.0 for errors."""
    if not val or not isinstance(val, str):
        return 0.0
    val = val.strip()
    if val.startswith('#') or val == '' or val == '-':
        return 0.0
    val = val.replace(',', '').replace('"', '').replace('$', '').strip()
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def _auto_name_from_code(code):
    """Generate a human-readable name from an ad code.
    e.g. 'SC88_CityPricesV4' -> 'City Prices V4'"""
    # Strip the prefix (SC88_, VHK1_, etc.)
    parts = code.split('_', 1)
    if len(parts) < 2:
        return code
    name_part = parts[1]
    # Insert spaces before capital letters
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name_part)
    # Insert spaces before version numbers
    name = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', name)
    return name


def _get_code_name(code, code_maps):
    """Look up a code in one or more maps, falling back to auto-name."""
    code_upper = code.strip()
    prefix = re.match(r'^([A-Z]+\d*)', code_upper)
    if prefix:
        prefix_str = prefix.group(1)
        for m in code_maps:
            if prefix_str in m:
                return m[prefix_str]
    return _auto_name_from_code(code)


def _classify_angle(ad_name, ad_type='static'):
    """Determine the copy angle from the ad name codes."""
    # Extract the first code (copy/hook code)
    parts = ad_name.split('|')
    first_code = parts[0].strip().split('_')[0] if parts else ''
    # Also check full code prefix
    first_full = parts[0].strip()
    code_prefix = re.match(r'^([A-Z]+\d+)', first_full)
    code_key = code_prefix.group(1) if code_prefix else first_code

    for angle, codes in ANGLE_MAP.items():
        if code_key in codes:
            return angle
    return 'Other'


def _make_id(ad_name, ad_type='static'):
    """Generate a stable lowercase ID from an ad name for JS references."""
    parts = [p.strip() for p in ad_name.split('|')]
    codes = []
    for p in parts:
        code = p.split('_')[0].lower() if '_' in p else p.lower()
        codes.append(code)
    return '_'.join(codes)


# ---------------------------------------------------------------------------
# Sheet fetching
# ---------------------------------------------------------------------------

def _build_csv_url(sheet_id, tab_name):
    """Build the published CSV URL for a Google Sheet tab."""
    encoded_tab = urllib.parse.quote(tab_name)
    return (f'https://docs.google.com/spreadsheets/d/{sheet_id}'
            f'/gviz/tq?tqx=out:csv&sheet={encoded_tab}')


def fetch_sheet_csv(sheet_id, tab_name, timeout=30):
    """Fetch a published Google Sheet tab as CSV and return list of dicts."""
    url = _build_csv_url(sheet_id, tab_name)
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'VAM-Dashboard/1.0',
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode('utf-8-sig')  # handle BOM
        reader = csv.DictReader(io.StringIO(raw))
        rows = []
        for row in reader:
            # Skip completely empty rows
            if all(v.strip() == '' for v in row.values()):
                continue
            rows.append(row)
        return rows
    except Exception as e:
        print(f'[sheets_data] Error fetching {tab_name}: {e}')
        return []


# ---------------------------------------------------------------------------
# Sheet config management
# ---------------------------------------------------------------------------

def get_sheet_config():
    """Get Google Sheet IDs from env vars or config file."""
    creative_id = os.environ.get('SHEET_CREATIVE_TRACKING_ID', '')
    dashboard_id = os.environ.get('SHEET_META_DASHBOARD_ID', '')

    # Fall back to config file
    if not creative_id or not dashboard_id:
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            if not creative_id:
                creative_id = config.get('creative_tracking_id', '')
            if not dashboard_id:
                dashboard_id = config.get('meta_dashboard_id', '')
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    return {
        'creative_tracking_id': creative_id,
        'meta_dashboard_id': dashboard_id,
        'configured': bool(creative_id and dashboard_id),
    }


def save_sheet_config(creative_id, dashboard_id):
    """Save Google Sheet IDs to config file."""
    config = {
        'creative_tracking_id': creative_id,
        'meta_dashboard_id': dashboard_id,
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    return config


# ---------------------------------------------------------------------------
# Data processing — Account KPIs
# ---------------------------------------------------------------------------

def compute_account_kpis(dashboard_rows):
    """Extract account-level KPIs from the Meta Dashboard summary row.
    The summary row has Date='CURRENT' and empty Timeline."""
    kpis = {
        'roas': 0.0,
        'cost_per_connected': 0.0,
        'cac': 0.0,
        'cpl': 0.0,
        'close_rate_connected': 0.0,
        'total_spend': 0.0,
        'leads': 0,
        'connected_calls': 0,
        'sales': 0,
    }

    for row in dashboard_rows:
        date_val = row.get('Date', '').strip()
        if date_val == 'CURRENT':
            kpis['total_spend'] = clean_currency(row.get('Spend', ''))
            kpis['cpl'] = clean_currency(row.get('CPL', ''))
            kpis['cost_per_connected'] = clean_currency(
                row.get('CPConnected', ''))
            kpis['cac'] = clean_currency(
                row.get('CPA - Book Date', ''))
            kpis['roas'] = clean_float(
                row.get('Cash ROAS - Book Date', ''))
            kpis['close_rate_connected'] = clean_pct(
                row.get('Connected Call to Close %', ''))
            kpis['leads'] = clean_int(row.get('Leads', ''))
            kpis['connected_calls'] = clean_int(
                row.get('Connected Calls', ''))
            kpis['sales'] = clean_int(
                row.get('Sales - Book Date', ''))
            break

    # Compute gaps vs targets
    kpis['roas_gap'] = (
        round((kpis['roas'] - TARGETS['roas']) / TARGETS['roas'] * 100)
        if TARGETS['roas'] else 0
    )
    kpis['cpc_gap'] = (
        round((kpis['cost_per_connected'] - TARGETS['cost_per_connected'])
              / TARGETS['cost_per_connected'] * 100)
        if TARGETS['cost_per_connected'] else 0
    )
    kpis['cac_gap'] = (
        round((kpis['cac'] - TARGETS['cac']) / TARGETS['cac'] * 100)
        if TARGETS['cac'] else 0
    )

    return kpis


# ---------------------------------------------------------------------------
# Data processing — Ad classification
# ---------------------------------------------------------------------------

def _process_ad_row(row, ad_type='static'):
    """Parse a single ad row into a normalized dict."""
    status = row.get('Status', '').strip()
    if not status:
        return None

    # Get ad name — static CSV has an empty column between Status and Ad Name
    ad_name = row.get('Ad Name', '').strip()
    if not ad_name:
        # Try the column after the empty one (key might be '')
        for key, val in row.items():
            if key == '' or key is None:
                continue
            if 'Ad Name' in str(key):
                ad_name = val.strip()
                break
        if not ad_name:
            return None

    cost = clean_currency(row.get('Cost', ''))
    roas = clean_float(row.get('ROAS', ''))
    leads = clean_int(row.get('Leads', ''))
    cpl = clean_currency(row.get('CPL', ''))
    connected = clean_int(row.get('Stage: Connected Call', ''))
    cost_per_connected = clean_currency(
        row.get('cost per connected call', ''))
    sales = clean_int(row.get('Sales', ''))
    revenue = clean_currency(row.get('Revenue', ''))
    profit = clean_currency(row.get('Profit', ''))
    ctr_all = row.get('CTR (all)', '').strip()
    ctr_link = row.get('CTR (link)', '').strip()

    # Normalize status
    status_lower = status.lower()
    if status_lower == 'winner':
        tier = 'winner'
    elif status_lower in ('testing', 'emerging', 'new'):
        tier = 'emerging'
    elif status_lower in ('on the fence',):
        tier = 'on-fence'
    elif status_lower in ('loser', 'killed', 'paused'):
        tier = 'loser'
    elif status_lower == 'seasonal':
        tier = 'seasonal'
    else:
        tier = 'testing'

    # Parse ad name parts
    parts = [p.strip() for p in ad_name.split('|')]
    angle = _classify_angle(ad_name, ad_type)

    # Build visual/hook/body names from codes
    if ad_type == 'static' and len(parts) >= 2:
        copy_code = parts[0]
        visual_code = parts[1]
        visual_name = _get_code_name(visual_code, [VISUAL_CODE_MAP])
        description = f'{_get_code_name(copy_code, [COPY_CODE_MAP])}, {visual_name}'
    elif ad_type == 'video' and len(parts) >= 3:
        hook_code = parts[0]
        body_code = parts[1]
        visual_code = parts[2]
        visual_name = _get_code_name(visual_code, [VIDEO_VISUAL_MAP])
        description = (f'{_get_code_name(hook_code, [VIDEO_HOOK_MAP])} hook, '
                       f'{_get_code_name(visual_code, [VIDEO_VISUAL_MAP])}')
    elif ad_type == 'copy' and len(parts) >= 2:
        hook_code = parts[0]
        body_code = parts[1]
        visual_name = None
        description = (f'{_get_code_name(hook_code, [COPY_HOOK_MAP])} hook + '
                       f'{_get_code_name(body_code, [COPY_BODY_MAP])} body')
    else:
        visual_name = ''
        description = ad_name

    return {
        'ad_name': ad_name,
        'id': _make_id(ad_name, ad_type),
        'status': status,
        'tier': tier,
        'angle': angle,
        'visual': visual_name,
        'cost': cost,
        'roas': roas,
        'leads': leads,
        'cpl': cpl,
        'connected': connected,
        'cost_per_connected': cost_per_connected,
        'sales': sales,
        'revenue': revenue,
        'profit': profit,
        'ctr_all': ctr_all,
        'ctr_link': ctr_link,
        'description': description,
        'parts': parts,
        'ad_type': ad_type,
    }


def process_static_ads(rows):
    """Process static ad rows and return classified ads sorted by performance."""
    ads = []
    for row in rows:
        ad = _process_ad_row(row, 'static')
        if ad:
            ads.append(ad)
    # Sort: winners first, then by ROAS * sqrt(spend) for balanced ranking
    ads.sort(key=lambda a: (
        0 if a['tier'] == 'winner' else 1 if a['tier'] == 'emerging' else
        2 if a['tier'] == 'on-fence' else 3,
        -(a['roas'] * (a['cost'] ** 0.5) if a['cost'] > 0 else 0)
    ))
    return ads


def process_video_ads(rows):
    """Process video ad rows and return classified ads sorted by performance."""
    ads = []
    for row in rows:
        ad = _process_ad_row(row, 'video')
        if ad:
            ads.append(ad)
    ads.sort(key=lambda a: (
        0 if a['tier'] == 'winner' else 1 if a['tier'] == 'emerging' else
        2 if a['tier'] == 'on-fence' else 3,
        -(a['roas'] * (a['cost'] ** 0.5) if a['cost'] > 0 else 0)
    ))
    return ads


def process_copy_ads(rows):
    """Process copy ad rows and return classified ads sorted by performance."""
    ads = []
    for row in rows:
        ad = _process_ad_row(row, 'copy')
        if ad:
            ads.append(ad)
    ads.sort(key=lambda a: (
        0 if a['tier'] == 'winner' else 1 if a['tier'] == 'emerging' else
        2 if a['tier'] == 'on-fence' else 3,
        -(a['roas'] * (a['cost'] ** 0.5) if a['cost'] > 0 else 0)
    ))
    return ads


# ---------------------------------------------------------------------------
# Build prompt performance section
# ---------------------------------------------------------------------------

def _format_currency(val):
    """Format a number as currency string."""
    if val >= 1000:
        return f'${val:,.0f}'
    return f'${val:,.2f}'


def _format_roas(val):
    """Format ROAS value."""
    return f'{val:.2f}x'


def _format_pct(val):
    """Format a decimal as percentage."""
    return f'{val * 100:.2f}%'


def _extract_winning_angles(static_ads, video_ads, copy_ads):
    """Extract and rank winning copy angles from all ad types."""
    angle_stats = {}
    for ad in static_ads + video_ads + copy_ads:
        if ad['tier'] in ('loser', 'seasonal') or ad['cost'] < 100:
            continue
        angle = ad['angle']
        if angle not in angle_stats:
            angle_stats[angle] = {
                'total_spend': 0, 'total_revenue': 0,
                'ads': [], 'winners': 0
            }
        angle_stats[angle]['total_spend'] += ad['cost']
        angle_stats[angle]['total_revenue'] += ad['revenue']
        angle_stats[angle]['ads'].append(ad)
        if ad['tier'] == 'winner':
            angle_stats[angle]['winners'] += 1

    # Sort by total revenue
    ranked = sorted(angle_stats.items(),
                    key=lambda x: x[1]['total_revenue'], reverse=True)
    return ranked


def _extract_winning_visuals(static_ads):
    """Extract and rank winning visual styles from static ads."""
    visual_stats = {}
    for ad in static_ads:
        if ad['cost'] < 100:
            continue
        vis = ad['visual'] or 'Unknown'
        if vis not in visual_stats:
            visual_stats[vis] = {
                'total_spend': 0, 'winners': 0,
                'best_roas': 0, 'ads': []
            }
        visual_stats[vis]['total_spend'] += ad['cost']
        if ad['roas'] > visual_stats[vis]['best_roas']:
            visual_stats[vis]['best_roas'] = ad['roas']
        if ad['tier'] == 'winner':
            visual_stats[vis]['winners'] += 1
        visual_stats[vis]['ads'].append(ad)

    ranked = sorted(visual_stats.items(),
                    key=lambda x: (x[1]['winners'], x[1]['best_roas']),
                    reverse=True)
    return ranked


def _extract_losing_patterns(static_ads, video_ads, copy_ads):
    """Extract confirmed losing visual/copy patterns."""
    losing_visuals = set()
    losing_copy = set()

    for ad in static_ads:
        if ad['tier'] == 'loser' and ad['cost'] > 500:
            if ad['visual']:
                # Get the code part
                parts = ad['ad_name'].split('|')
                if len(parts) >= 2:
                    vis_code = parts[1].strip().split('_')[0]
                    vis_name = ad['visual']
                    losing_visuals.add(f'{vis_name} ({vis_code})')

    for ad in video_ads:
        if ad['tier'] == 'loser' and ad['cost'] > 200:
            parts = ad['ad_name'].split('|')
            if len(parts) >= 3:
                vis_code = parts[2].strip().split('_')[0]
                vis_name = _get_code_name(parts[2].strip(),
                                          [VIDEO_VISUAL_MAP])
                losing_visuals.add(f'{vis_name} ({vis_code})')

    for ad in static_ads + video_ads + copy_ads:
        if ad['tier'] == 'loser' and ad['cost'] > 500:
            parts = ad['ad_name'].split('|')
            first = parts[0].strip()
            code_prefix = re.match(r'^([A-Z]+\d+)', first)
            if code_prefix:
                code_key = code_prefix.group(1)
                name = _get_code_name(first, [
                    COPY_CODE_MAP, VIDEO_HOOK_MAP, COPY_HOOK_MAP
                ])
                losing_copy.add(name)

    return losing_visuals, losing_copy


def build_prompt_performance_section(kpis, static_ads, video_ads, copy_ads):
    """Build the markdown text for ## CURRENT PERFORMANCE through
    the end of ## CONFIRMED LOSING PATTERNS.

    This replaces the hardcoded section in MASTER_PROMPT."""

    now = datetime.now().strftime('%B %Y')

    lines = [f'## CURRENT PERFORMANCE (as of {now})', '']

    # KPI table
    lines.append('| Metric | Current | Target | Gap |')
    lines.append('|--------|---------|--------|-----|')
    lines.append(
        f'| ROAS | {_format_roas(kpis["roas"])} | '
        f'{_format_roas(TARGETS["roas"])} | '
        f'{kpis["roas_gap"]:+d}% |')
    lines.append(
        f'| Cost per Connected Call | '
        f'{_format_currency(kpis["cost_per_connected"])} | '
        f'{_format_currency(TARGETS["cost_per_connected"])} | '
        f'{kpis["cpc_gap"]:+d}% |')
    lines.append(
        f'| CAC | {_format_currency(kpis["cac"])} | '
        f'{_format_currency(TARGETS["cac"])} | '
        f'{kpis["cac_gap"]:+d}% |')
    lines.append(
        f'| CPL | {_format_currency(kpis["cpl"])} | — | — |')
    lines.append(
        f'| Close Rate (Connected) | '
        f'{_format_pct(kpis["close_rate_connected"])} | — | — |')
    lines.append(
        f'| Total Spend | '
        f'{_format_currency(kpis["total_spend"])} | — | — |')

    # Strategic priority
    if kpis['roas'] < TARGETS['roas']:
        lines.append('')
        lines.append(
            f'**Strategic Priority:** Improve ROAS from '
            f'{_format_roas(kpis["roas"])} to '
            f'{_format_roas(TARGETS["roas"])} by expanding into colder '
            f'audiences through broader awareness-level hooks while '
            f'maintaining strong warm-audience performance.')

    # Winning elements
    lines.append('')
    lines.append('## PROVEN WINNING ELEMENTS')
    lines.append('')

    # Top copy angles
    lines.append('### Top Copy Angles (ranked by proven performance)')
    winning_angles = _extract_winning_angles(static_ads, video_ads, copy_ads)
    for i, (angle, stats) in enumerate(winning_angles[:6], 1):
        # Get example ad names for this angle
        examples = []
        for ad in stats['ads'][:4]:
            parts = ad['ad_name'].split('|')
            first = parts[0].strip()
            name = _get_code_name(first, [
                COPY_CODE_MAP, VIDEO_HOOK_MAP, COPY_HOOK_MAP
            ])
            if name not in examples:
                examples.append(f'"{name}"')
        example_str = ', '.join(examples[:4])

        # Get ROAS range
        roas_vals = [a['roas'] for a in stats['ads'] if a['roas'] > 0]
        if roas_vals:
            roas_range = (f'ROAS {min(roas_vals):.2f}-{max(roas_vals):.2f}x'
                          if len(roas_vals) > 1
                          else f'ROAS {roas_vals[0]:.2f}x')
        else:
            roas_range = 'Emerging'

        tier_label = ('Winner' if stats['winners'] > 0
                      else 'Emerging winners')
        lines.append(
            f'{i}. **{angle}** — {example_str} → {roas_range}')

    # Top visual styles — Static
    lines.append('')
    lines.append('### Top Visual Styles')
    lines.append('**Static (use these by default):**')
    winning_visuals = _extract_winning_visuals(static_ads)
    for vis_name, stats in winning_visuals[:6]:
        winners = stats['winners']
        best = stats['best_roas']
        note_parts = []
        if winners > 0:
            note_parts.append(f'{winners} winner{"s" if winners > 1 else ""}')
        if best > 0:
            note_parts.append(f'{best:.2f}x ROAS')
        note = ', '.join(note_parts) if note_parts else 'Testing'
        lines.append(f'- {vis_name} — {note}')

    lines.append('')
    lines.append(
        '**Note:** Light/dark variants are NOT separate styles. '
        'Use the base name (e.g., "Gmail" not "Gmail Dark"). '
        'The creative team makes both variations.')

    # Top video formats
    lines.append('')
    lines.append('**Video (use these by default):**')
    video_winners = [a for a in video_ads
                     if a['tier'] in ('winner', 'emerging') and
                     a['cost'] > 50]
    seen_visuals = set()
    for ad in video_winners[:5]:
        parts = ad['ad_name'].split('|')
        if len(parts) >= 3:
            vis_code = parts[2].strip()
            vis_name = _get_code_name(vis_code, [VIDEO_VISUAL_MAP])
            if vis_name not in seen_visuals:
                seen_visuals.add(vis_name)
                ctr = ad['ctr_all'] if ad['ctr_all'] and not ad[
                    'ctr_all'].startswith('#') else ''
                note = f'{ad["roas"]:.2f}x ROAS'
                if ctr:
                    note = f'{ctr} CTR, {note}'
                lines.append(f'- {vis_name} — {note}')

    # Top copy hook + body combos
    lines.append('')
    lines.append('### Top Copy Hook + Body Combos')
    copy_performers = [a for a in copy_ads
                       if a['tier'] in ('winner', 'on-fence', 'emerging')
                       and a['cost'] > 500]
    for ad in copy_performers[:5]:
        spend_str = _format_currency(ad['cost'])
        roas_str = _format_roas(ad['roas'])
        tier_note = ({'winner': 'Winner', 'on-fence': 'Solid volume',
                      'emerging': 'Emerging'}).get(ad['tier'], '')
        lines.append(
            f'- {ad["ad_name"]} — {tier_note} '
            f'({spend_str} spend, {roas_str} ROAS)')

    # Losing patterns
    lines.append('')
    lines.append('## CONFIRMED LOSING PATTERNS — DO NOT USE')
    lines.append('')

    losing_visuals, losing_copy = _extract_losing_patterns(
        static_ads, video_ads, copy_ads)

    lines.append('**Visual formats that always fail:**')
    if losing_visuals:
        lines.append(f'- {", ".join(sorted(losing_visuals))}')
    else:
        lines.append(
            '- StickyNote (SV29), EducationalLayout (SV30), '
            'HoldingSign (SV19/20/21), Carousel format')

    lines.append('')
    lines.append('**Copy angles that always fail:**')
    # Keep the curated list from hardcoded data as baseline
    lines.append(
        '- "Licensed & Insured" as headline, "Arrived Flawless", '
        '"From Scheduling to Delivery", "Gently and Correctly", '
        '"Relax Leave It To Us", "Coast to Coast" alone, '
        '"Choose Date Later", "Move Timeline", '
        'any calendar/scheduling messaging')

    lines.append('')
    lines.append('**Targeting approaches that fail:**')
    lines.append(
        '- NY-specific copy, city-to-city route copy '
        '(NYtoLA, LAtoAustin, etc.), city-specific lifestyle visuals, '
        'any geographic targeting in the ad creative')

    lines.append('')
    lines.append('**Concepts that always fail:**')
    lines.append(
        '- Holiday/seasonal theming (kills even winning angles), '
        'educational/infographic formats, branded/polished production, '
        'comparison charts')

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Build TOP_PERFORMERS JSON
# ---------------------------------------------------------------------------

def build_top_performers_json(static_ads, video_ads, copy_ads):
    """Build the TOP_PERFORMERS data structure matching dashboard.html."""

    def _build_static_entry(ad):
        return {
            'id': ad['id'],
            'name': ad['ad_name'],
            'angle': ad['angle'],
            'visual': ad['parts'][1].strip() if len(ad['parts']) >= 2 else '',
            'roas': ad['roas'],
            'spend': int(ad['cost']),
            'tier': ad['tier'],
            'description': ad['description'],
        }

    def _build_video_entry(ad):
        return {
            'id': ad['id'],
            'name': ad['ad_name'],
            'angle': ad['angle'],
            'visual': (ad['parts'][2].strip()
                       if len(ad['parts']) >= 3 else ''),
            'roas': ad['roas'],
            'spend': int(ad['cost']),
            'tier': ad['tier'],
            'description': ad['description'],
        }

    def _build_copy_entry(ad):
        return {
            'id': ad['id'],
            'name': ad['ad_name'],
            'angle': ad['angle'],
            'hook': ad['parts'][0].strip() if ad['parts'] else '',
            'body': (ad['parts'][1].strip()
                     if len(ad['parts']) >= 2 else ''),
            'roas': ad['roas'],
            'spend': int(ad['cost']),
            'tier': ad['tier'],
            'description': ad['description'],
        }

    # Select top performers: winners + best emerging, max 10 each
    static_top = [a for a in static_ads
                  if a['tier'] in ('winner', 'emerging') and a['cost'] > 100]
    video_top = [a for a in video_ads
                 if a['tier'] in ('winner', 'emerging') and a['cost'] > 0]
    copy_top = [a for a in copy_ads
                if a['tier'] in ('winner', 'on-fence', 'emerging')
                and a['cost'] > 500]

    return {
        'static': [_build_static_entry(a) for a in static_top[:10]],
        'video': [_build_video_entry(a) for a in video_top[:8]],
        'copy': [_build_copy_entry(a) for a in copy_top[:6]],
    }


# ---------------------------------------------------------------------------
# Build NET_NEW_OPTIONS from data
# ---------------------------------------------------------------------------

def build_net_new_options(static_ads, video_ads):
    """Build the NET_NEW_OPTIONS structure from live data.
    Visual style tiers based on performance."""

    # Analyze static visuals
    visual_perf = {}
    for ad in static_ads:
        vis = ad.get('visual', '')
        if not vis:
            continue
        if vis not in visual_perf:
            visual_perf[vis] = {'winners': 0, 'spend': 0, 'best_roas': 0}
        visual_perf[vis]['spend'] += ad['cost']
        if ad['roas'] > visual_perf[vis]['best_roas']:
            visual_perf[vis]['best_roas'] = ad['roas']
        if ad['tier'] == 'winner':
            visual_perf[vis]['winners'] += 1

    static_styles = []
    for vis_name, stats in sorted(visual_perf.items(),
                                   key=lambda x: (x[1]['winners'],
                                                   x[1]['best_roas']),
                                   reverse=True):
        if stats['winners'] > 0:
            tier = 'proven'
        elif stats['best_roas'] > 1.0:
            tier = 'emerging'
        else:
            tier = 'untested'
        note = ''
        if stats['winners'] > 0:
            note = f'{stats["winners"]} winners, {stats["best_roas"]:.2f}x best'
        elif stats['best_roas'] > 0:
            note = f'{stats["best_roas"]:.2f}x ROAS'
        static_styles.append({
            'value': vis_name.replace(' ', ''),
            'label': vis_name,
            'tier': tier,
            'note': note,
        })

    # Add custom option
    static_styles.append({
        'value': 'custom',
        'label': '+ Custom Style',
        'tier': 'custom',
        'note': 'Describe your own',
    })

    # Video styles (mostly manual since video visual codes are specific)
    video_styles = [
        {'value': 'UGC_AsianWoman', 'label': 'UGC Asian Woman',
         'tier': 'proven', 'note': 'Top performer'},
        {'value': 'UGC_WhiteWoman', 'label': 'UGC White Woman',
         'tier': 'proven', 'note': 'Strong engagement'},
        {'value': 'DoneForYou_Format', 'label': 'Done For You Format',
         'tier': 'emerging', 'note': 'Early signal'},
        {'value': 'Organic_Crew', 'label': 'Organic Crew Footage',
         'tier': 'emerging', 'note': 'Authentic feel'},
        {'value': 'custom', 'label': '+ Custom Format',
         'tier': 'custom', 'note': 'Describe your own'},
    ]

    # Analyze copy angles
    angle_perf = {}
    for ad in static_ads + video_ads:
        angle = ad['angle']
        if angle == 'Other':
            continue
        if angle not in angle_perf:
            angle_perf[angle] = {'winners': 0, 'best_roas': 0, 'examples': []}
        if ad['tier'] == 'winner':
            angle_perf[angle]['winners'] += 1
        if ad['roas'] > angle_perf[angle]['best_roas']:
            angle_perf[angle]['best_roas'] = ad['roas']

    copy_angles = []
    for angle, stats in sorted(angle_perf.items(),
                                key=lambda x: (x[1]['winners'],
                                               x[1]['best_roas']),
                                reverse=True):
        tier = 'proven' if stats['winners'] > 0 else 'emerging'
        note = f'{stats["best_roas"]:.2f}x best ROAS'
        copy_angles.append({
            'value': angle,
            'label': angle,
            'tier': tier,
            'note': note,
        })
    copy_angles.append({
        'value': 'custom',
        'label': '+ Custom Angle',
        'tier': 'custom',
        'note': '',
    })

    # Hook types stay static (framework-based, not data-driven)
    hook_types = [
        {'value': 'Let Claude decide', 'label': 'Let Claude Decide',
         'example': 'Claude picks the best mix automatically'},
        {'value': 'Labels', 'label': 'Labels',
         'example': '"Long-distance movers..." — identity words'},
        {'value': 'Questions', 'label': 'Questions',
         'example': '"Moving across the country?"'},
        {'value': 'Conditionals', 'label': 'Conditionals',
         'example': '"If you\'re moving out of state..."'},
        {'value': 'Commands', 'label': 'Commands',
         'example': '"Watch this before you book a mover"'},
        {'value': 'Statements', 'label': 'Statements',
         'example': '"Starting at $1,597"'},
        {'value': 'Lists/Steps', 'label': 'Lists/Steps',
         'example': '"3 things your mover won\'t tell you"'},
        {'value': 'Narratives', 'label': 'Narratives',
         'example': '"I almost didn\'t use them..."'},
        {'value': 'Exclamations', 'label': 'Exclamations',
         'example': '"Check this out!" — shock, surprise'},
    ]

    return {
        'visualStyles': {
            'static': static_styles,
            'video': video_styles,
        },
        'copyAngles': copy_angles,
        'hookTypes': hook_types,
    }


# ---------------------------------------------------------------------------
# Master data fetch + process
# ---------------------------------------------------------------------------

def fetch_and_process_all():
    """Fetch all sheets and process into dashboard-ready data."""
    config = get_sheet_config()
    if not config['configured']:
        return None

    creative_id = config['creative_tracking_id']
    dashboard_id = config['meta_dashboard_id']

    print('[sheets_data] Fetching Google Sheets data...')
    start = time.time()

    # Fetch all tabs
    static_rows = fetch_sheet_csv(creative_id,
                                   CREATIVE_TABS['static'])
    video_rows = fetch_sheet_csv(creative_id,
                                  CREATIVE_TABS['video'])
    copy_rows = fetch_sheet_csv(creative_id,
                                 CREATIVE_TABS['copy'])
    dashboard_rows = fetch_sheet_csv(dashboard_id, DASHBOARD_TAB)

    elapsed = time.time() - start
    print(f'[sheets_data] Fetched {len(static_rows)} static, '
          f'{len(video_rows)} video, {len(copy_rows)} copy, '
          f'{len(dashboard_rows)} dashboard rows in {elapsed:.1f}s')

    # Process
    kpis = compute_account_kpis(dashboard_rows)
    static_ads = process_static_ads(static_rows)
    video_ads = process_video_ads(video_rows)
    copy_ads = process_copy_ads(copy_rows)

    # Build outputs
    prompt_section = build_prompt_performance_section(
        kpis, static_ads, video_ads, copy_ads)
    top_performers = build_top_performers_json(
        static_ads, video_ads, copy_ads)
    net_new_options = build_net_new_options(static_ads, video_ads)

    result = {
        'prompt_section': prompt_section,
        'top_performers': top_performers,
        'net_new_options': net_new_options,
        'kpis': kpis,
        'last_updated': datetime.now().isoformat(),
        'row_counts': {
            'static': len(static_rows),
            'video': len(video_rows),
            'copy': len(copy_rows),
            'dashboard': len(dashboard_rows),
        },
    }

    # Save to file cache
    _save_file_cache(result)

    return result


def _save_file_cache(data):
    """Save processed data to file cache for persistence across restarts."""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print('[sheets_data] File cache saved.')
    except Exception as e:
        print(f'[sheets_data] Error saving file cache: {e}')


def _load_file_cache():
    """Load cached data from file. Returns None if stale or missing."""
    try:
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return None


# ---------------------------------------------------------------------------
# Public API — cached data access
# ---------------------------------------------------------------------------

def get_performance_data(force_refresh=False):
    """Get performance data, using cache when possible.

    Returns dict with: prompt_section, top_performers, net_new_options,
    kpis, last_updated, row_counts.
    Returns None if sheets aren't configured.
    """
    with _cache_lock:
        now = time.time()
        cache_age = now - _cache['timestamp']

        # Return cached if fresh and not forcing refresh
        if (_cache['data'] is not None and cache_age < CACHE_TTL
                and not force_refresh):
            return _cache['data']

        # Try file cache if in-memory is empty
        if _cache['data'] is None:
            file_data = _load_file_cache()
            if file_data is not None:
                _cache['data'] = file_data
                _cache['timestamp'] = now
                print('[sheets_data] Loaded from file cache.')
                # If file cache is old, trigger background refresh
                if force_refresh or not file_data.get('last_updated'):
                    _trigger_background_refresh()
                return file_data

        # If already fetching, return stale data
        if _cache['fetching']:
            return _cache['data']

    # Need fresh data
    if force_refresh or _cache['data'] is None:
        return _refresh_data()
    else:
        # Trigger background refresh, return stale data
        _trigger_background_refresh()
        return _cache['data']


def _refresh_data():
    """Synchronously refresh data from Google Sheets."""
    with _cache_lock:
        _cache['fetching'] = True

    try:
        data = fetch_and_process_all()
        if data is not None:
            with _cache_lock:
                _cache['data'] = data
                _cache['timestamp'] = time.time()
        return data
    except Exception as e:
        print(f'[sheets_data] Error refreshing: {e}')
        return _cache.get('data')
    finally:
        with _cache_lock:
            _cache['fetching'] = False


def _trigger_background_refresh():
    """Trigger a non-blocking background data refresh."""
    with _cache_lock:
        if _cache['fetching']:
            return
        _cache['fetching'] = True

    def _bg_refresh():
        try:
            data = fetch_and_process_all()
            if data is not None:
                with _cache_lock:
                    _cache['data'] = data
                    _cache['timestamp'] = time.time()
        except Exception as e:
            print(f'[sheets_data] Background refresh error: {e}')
        finally:
            with _cache_lock:
                _cache['fetching'] = False

    thread = threading.Thread(target=_bg_refresh, daemon=True)
    thread.start()

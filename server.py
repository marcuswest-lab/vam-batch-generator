#!/usr/bin/env python3
"""
VAM Creative Production Server
Serves the dashboard and handles .docx generation.
"""

import os
import sys
import json
import re
import tempfile
import urllib.request
import urllib.error
from datetime import datetime
from flask import Flask, send_from_directory, request, send_file, jsonify

# Add script directory to path so we can import generate_doc
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from generate_doc import (
    generate_doc, detect_batch_type, parse_overview, parse_creatives,
    parse_field, auto_detect_variation_types,
)
from sheets_data import (
    get_performance_data, get_sheet_config, save_sheet_config,
)

app = Flask(__name__, static_folder=SCRIPT_DIR)


@app.route('/')
def index():
    return send_from_directory(SCRIPT_DIR, 'dashboard.html')


@app.route('/dashboard')
@app.route('/dashboard.html')
def dashboard():
    return send_from_directory(SCRIPT_DIR, 'dashboard.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """Serve any static file from the project directory."""
    return send_from_directory(SCRIPT_DIR, filename)


@app.route('/api/generate-doc', methods=['POST'])
def api_generate_doc():
    """Accept Claude's text output and return a filled .docx file."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400

        claude_output = data['text']
        if len(claude_output.strip()) < 50:
            return jsonify({'error': 'Text is too short — paste the full Claude output'}), 400

        # Generate the .docx in a temp file
        batch_type = detect_batch_type(claude_output)
        overview = parse_overview(claude_output)
        creatives = parse_creatives(claude_output, batch_type)

        if not creatives:
            return jsonify({
                'error': 'Could not find any creatives in the output. Make sure it contains === CREATIVE 1 ===, === CREATIVE 2 ===, etc.'
            }), 400

        # Create temp output file
        tmp = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
        tmp.close()

        output_path = generate_doc(claude_output, output_path=tmp.name)

        # Determine a nice filename
        batch_name = parse_field(claude_output, 'BATCH')
        if not batch_name:
            batch_name = f"VAM_{batch_type.title()}_Batch"
        safe_name = re.sub(r'[^\w\s-]', '', batch_name).strip()[:60]
        safe_name = re.sub(r'\s+', '_', safe_name)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"{safe_name}_{timestamp}.docx"

        return send_file(
            output_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/preview', methods=['POST'])
def api_preview():
    """Parse Claude's output and return a preview of what was detected."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400

        claude_output = data['text']
        batch_type = detect_batch_type(claude_output)
        overview = parse_overview(claude_output)
        creatives = parse_creatives(claude_output, batch_type)

        return jsonify({
            'batch_type': batch_type,
            'overview_fields': len(overview),
            'overview': {k: v[:100] for k, v in overview.items()},
            'creatives_count': len(creatives),
            'creatives': [
                {
                    'number': c.get('number'),
                    'file_name': c.get('File Name', c.get('Name', '(unnamed)')),
                    'fields': len(c)
                }
                for c in creatives
            ]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/format-for-gdocs', methods=['POST'])
def api_format_for_gdocs():
    """Parse Claude's output and return formatted HTML for copy-pasting into Google Docs."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400

        claude_output = data['text']
        if len(claude_output.strip()) < 50:
            return jsonify({'error': 'Text is too short — paste the full Claude output'}), 400

        batch_type = detect_batch_type(claude_output)
        overview = parse_overview(claude_output)
        creatives = parse_creatives(claude_output, batch_type)
        auto_detect_variation_types(creatives, batch_type)

        if not creatives:
            return jsonify({'error': 'No creatives found.'}), 400

        # Parse batch header info
        batch_name = parse_field(claude_output, 'BATCH') or 'Batch'
        campaign_name = re.sub(r'\s*[—–-]\s*[Ww]eek\s+of\s+.*$', '', batch_name).strip()
        campaign_name = re.sub(r'\s*[—–-]\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}.*$', '', campaign_name).strip()
        if not campaign_name:
            campaign_name = batch_name
        date_str = datetime.now().strftime('%m/%d/%Y')

        # Build HTML
        html = _build_gdocs_html(batch_type, batch_name, campaign_name, date_str, overview, creatives)

        return jsonify({'html': html})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def _build_gdocs_html(batch_type, batch_name, campaign_name, date_str, overview, creatives):
    """Build formatted HTML matching BAD Marketing's Google Docs brief format.

    Format reference: two-column tables with bold right-aligned labels,
    OVERVIEW header row, numbered creative header rows (light blue),
    all fields inline including Copy. No colored backgrounds on data rows.
    """
    import html as html_mod

    def esc(s):
        return html_mod.escape(str(s)) if s else ''

    def nl2br(s):
        """Convert newlines to <br> tags, preserving structure."""
        if not s:
            return ''
        return html_mod.escape(str(s)).replace('\n', '<br>')

    # Shared table + cell styles (match BAD Marketing Google Doc format)
    tbl = 'width:100%;border-collapse:collapse;font-family:Proxima Nova,Arial,sans-serif;font-size:10pt;'
    label_td = 'padding:6px 10px;border:1px solid #000;font-weight:bold;text-align:right;vertical-align:top;width:160px;white-space:nowrap;'
    val_td = 'padding:6px 10px;border:1px solid #000;vertical-align:top;'

    type_label = batch_type.capitalize()

    lines = []

    # No cover page — go straight to overview table

    # --- Overview table ---
    lines.append(f'<table style="{tbl}">')

    # OVERVIEW header row (bold centered, spanning both columns)
    lines.append(f'<tr><td colspan="2" style="padding:8px;border:1px solid #000;text-align:center;font-weight:bold;font-size:12pt;">OVERVIEW</td></tr>')

    # Determine which overview fields to show based on batch type
    if batch_type == 'static':
        overview_fields = [
            'AI Allowed?', 'Photo Folder', 'Reference', 'Idea Name', 'Angle Name',
            'Style Name', 'Task', 'General Notes', 'Design Notes',
            'Link to Brand Assets', 'Any Other Relevant Assets',
            'Ratio Format(s)', 'Ad Platform', 'Avatar',
            'Brand Voice', 'Net New/Iteration', 'Landing Page URL',
            'Conversion Objective', 'Copywriter'
        ]
    elif batch_type == 'video':
        overview_fields = [
            'Video Type', 'AI Allowed?', 'Footage Folder', 'Idea Name', 'Angle Name',
            'Style Name', 'Task', 'General Notes', 'Editing Notes',
            'Link to Brand Assets', 'Any Other Relevant Assets',
            'Ratio Format(s)', 'Ad Platform', 'Avatar', 'Brand Voice',
            'Net New/Iteration', 'Landing Page URL', 'Conversion Objective', 'Copywriter'
        ]
    else:  # copy
        overview_fields = [
            'AI Allowed?', 'Idea Name', 'Angle Name', 'Copy Type', 'Task',
            'General Notes', 'Ad Platform', 'Net New/Iteration',
            'Landing Page URL', 'Conversion Objective', 'Copywriter'
        ]

    for field in overview_fields:
        val = overview.get(field, '')
        if not val:
            alt = field.rstrip('(s)')
            val = overview.get(alt, '')
        if val:
            lines.append(
                f'<tr>'
                f'<td style="{label_td}">{esc(field)}</td>'
                f'<td style="{val_td}">{nl2br(val)}</td>'
                f'</tr>'
            )
    lines.append('</table>')
    lines.append('<br>')

    # --- Individual creatives (each is a single table) ---
    for c in creatives:
        num = c.get('number', '?')

        lines.append(f'<table style="{tbl}">')

        # Creative number header row (light blue background — matches existing doc)
        lines.append(
            f'<tr><td colspan="2" style="padding:8px 10px;border:1px solid #000;'
            f'background:#b4c7e7;font-size:14pt;font-weight:bold;">{esc(num)}</td></tr>'
        )

        # Build field list based on batch type — all fields inline in the table
        if batch_type == 'static':
            field_list = [
                ('File Name', c.get('File Name', '')),
                ('File', ''),  # placeholder for designer
                ('Notes', c.get('Notes', '')),
                ('Variation Type', c.get('Variation Type', '')),
                ('Awareness Level', c.get('Awareness Level', '')),
                ('Lead Type', c.get('Lead Type', '')),
                ('Status', c.get('Status', '')),
                ('Copy', c.get('Copy', '')),
            ]
            # Add Design Notes before Copy if present
            dn = c.get('Design Notes', '')
            if dn:
                field_list.insert(3, ('Design Notes', dn))
        elif batch_type == 'video':
            field_list = [
                ('File Name', c.get('File Name', '')),
                ('Notes', c.get('Notes', '')),
                ('Variation Type', c.get('Variation Type', '')),
                ('Awareness Level', c.get('Awareness Level', '')),
                ('Lead Type', c.get('Lead Type', '')),
                ('Status', c.get('Status', '')),
                ('Lead Script', c.get('Lead Script', '')),
                ('Body Script', c.get('Body Script', '')),
            ]
            en = c.get('Editing Notes', '')
            if en:
                field_list.insert(2, ('Editing Notes', en))
        else:  # copy
            field_list = [
                ('Name', c.get('Name', '')),
                ('Variation Type', c.get('Variation Type', '')),
                ('Awareness Level', c.get('Awareness Level', '')),
                ('Lead Type', c.get('Lead Type', '')),
                ('Status', c.get('Status', '')),
                ('Headline', c.get('Headline', '')),
                ('Body Copy', c.get('Body Copy', '')),
            ]

        for field_name, val in field_list:
            if not val and field_name not in ('File',):
                continue
            # Status gets a subtle yellow text highlight (matches doc)
            if field_name == 'Status' and val:
                val_html = f'<span style="background:#fce8b2;padding:1px 4px;">{esc(val)}</span>'
            else:
                val_html = nl2br(val)

            lines.append(
                f'<tr>'
                f'<td style="{label_td}">{esc(field_name)}</td>'
                f'<td style="{val_td}">{val_html}</td>'
                f'</tr>'
            )

        lines.append('</table>')
        lines.append('<br>')

    return '\n'.join(lines)


@app.route('/api/create-google-doc', methods=['POST'])
def api_create_google_doc():
    """Parse Claude's output and create a Google Doc via Apps Script."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400

        script_url = data.get('script_url', '')
        if not script_url:
            return jsonify({
                'error': 'No Apps Script URL configured. Click "Google Doc Setup" to add it.'
            }), 400

        claude_output = data['text']
        if len(claude_output.strip()) < 50:
            return jsonify({'error': 'Text is too short — paste the full Claude output'}), 400

        # Parse the output
        batch_type = detect_batch_type(claude_output)
        overview = parse_overview(claude_output)
        creatives = parse_creatives(claude_output, batch_type)

        if not creatives:
            return jsonify({
                'error': 'No creatives found. Make sure output has === CREATIVE N === sections.'
            }), 400

        # Auto-detect variation types
        auto_detect_variation_types(creatives, batch_type)

        # Build campaign name (strip date suffixes)
        batch_name = parse_field(claude_output, 'BATCH') or 'Batch'
        campaign_name = re.sub(
            r'\s*[—–-]\s*[Ww]eek\s+of\s+.*$', '', batch_name
        ).strip()
        campaign_name = re.sub(
            r'\s*[—–-]\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}.*$', '', campaign_name
        ).strip()
        if not campaign_name:
            campaign_name = batch_name

        # Build payload for Apps Script
        payload = {
            'batch_type': batch_type,
            'client': 'Value Added Moving',
            'campaign_name': campaign_name,
            'date': datetime.now().strftime('%m-%d-%Y'),
            'overview': overview,
            'creatives': creatives,
        }

        # POST to Apps Script
        payload_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            script_url,
            data=payload_bytes,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode('utf-8'))

        return jsonify(result)

    except urllib.error.URLError as e:
        return jsonify({
            'error': f'Failed to reach Apps Script: {str(e)}'
        }), 502
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Google Sheets data endpoints
# ---------------------------------------------------------------------------

@app.route('/api/performance-data', methods=['GET'])
def api_performance_data():
    """Return cached performance data from Google Sheets."""
    try:
        data = get_performance_data()
        if data is None:
            return jsonify({
                'configured': False,
                'message': 'Google Sheets not configured. Add Sheet IDs in Data Source settings.'
            })
        return jsonify({
            'configured': True,
            'prompt_section': data.get('prompt_section', ''),
            'top_performers': data.get('top_performers', {}),
            'net_new_options': data.get('net_new_options', {}),
            'kpis': data.get('kpis', {}),
            'last_updated': data.get('last_updated', ''),
            'row_counts': data.get('row_counts', {}),
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/refresh-data', methods=['POST'])
def api_refresh_data():
    """Force re-fetch from Google Sheets and update cache."""
    try:
        data = get_performance_data(force_refresh=True)
        if data is None:
            return jsonify({
                'configured': False,
                'message': 'Google Sheets not configured.'
            })
        return jsonify({
            'configured': True,
            'last_updated': data.get('last_updated', ''),
            'row_counts': data.get('row_counts', {}),
            'message': 'Data refreshed successfully.',
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/sheets-config', methods=['GET', 'POST'])
def api_sheets_config():
    """Get or save Google Sheet IDs."""
    try:
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            creative_id = data.get('creative_tracking_id', '').strip()
            dashboard_id = data.get('meta_dashboard_id', '').strip()
            if not creative_id or not dashboard_id:
                return jsonify({
                    'error': 'Both Sheet IDs are required.'
                }), 400
            save_sheet_config(creative_id, dashboard_id)
            # Trigger immediate fetch
            perf_data = get_performance_data(force_refresh=True)
            return jsonify({
                'saved': True,
                'configured': True,
                'last_updated': (perf_data.get('last_updated', '')
                                 if perf_data else ''),
                'row_counts': (perf_data.get('row_counts', {})
                               if perf_data else {}),
            })
        else:
            config = get_sheet_config()
            return jsonify(config)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8090))
    print(f"""
╔══════════════════════════════════════════════════╗
║     VAM Creative Production System               ║
║     Open: http://localhost:{port}                  ║
╚══════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=port, debug=False)

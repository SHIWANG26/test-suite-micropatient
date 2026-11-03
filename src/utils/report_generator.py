"""
Report Generator — Produces HTML and JSON test reports.

Generates evaluation summaries with metric scores, pass/fail status,
and historical comparisons for CI/CD pipeline visibility.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Template

logger = logging.getLogger(__name__)

REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "reports"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Micropatient AI Test Suite — {{ title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #e2e8f0; padding: 2rem; }
        .header { text-align: center; margin-bottom: 2rem; }
        .header h1 { font-size: 1.8rem; color: #38bdf8; }
        .header p { color: #94a3b8; margin-top: 0.5rem; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .card { background: #1e293b; border-radius: 12px; padding: 1.5rem; border: 1px solid #334155; }
        .card h3 { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
        .card .value { font-size: 2rem; font-weight: 700; margin-top: 0.5rem; }
        .pass { color: #4ade80; }
        .fail { color: #f87171; }
        .warn { color: #fbbf24; }
        table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 12px; overflow: hidden; }
        th, td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #334155; }
        th { background: #0f172a; color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; }
        .badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
        .badge-pass { background: #065f46; color: #6ee7b7; }
        .badge-fail { background: #7f1d1d; color: #fca5a5; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 {{ title }}</h1>
        <p>Generated: {{ timestamp }} | Run ID: {{ run_id }}</p>
    </div>
    <div class="summary-grid">
        <div class="card">
            <h3>Pass Rate</h3>
            <div class="value {{ 'pass' if pass_rate >= 0.8 else 'fail' }}">{{ "%.1f"|format(pass_rate * 100) }}%</div>
        </div>
        <div class="card">
            <h3>Total Tests</h3>
            <div class="value" style="color: #38bdf8;">{{ total_tests }}</div>
        </div>
        <div class="card">
            <h3>Hallucination Rate</h3>
            <div class="value {{ 'pass' if hallucination_rate <= 0.15 else 'fail' }}">{{ "%.1f"|format(hallucination_rate * 100) }}%</div>
        </div>
        <div class="card">
            <h3>Regressions</h3>
            <div class="value {{ 'fail' if regressions > 0 else 'pass' }}">{{ regressions }}</div>
        </div>
    </div>
    <table>
        <thead>
            <tr><th>Test Case</th><th>Metric</th><th>Score</th><th>Threshold</th><th>Status</th></tr>
        </thead>
        <tbody>
        {% for score in scores %}
            <tr>
                <td>{{ score.test_case_id }}</td>
                <td>{{ score.metric_name }}</td>
                <td>{{ "%.3f"|format(score.score) }}</td>
                <td>{{ "%.3f"|format(score.threshold) }}</td>
                <td><span class="badge {{ 'badge-pass' if score.passed else 'badge-fail' }}">{{ 'PASS' if score.passed else 'FAIL' }}</span></td>
            </tr>
        {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""


def generate_html_report(
    title: str,
    run_id: str,
    scores: list[dict[str, Any]],
    pass_rate: float = 0.0,
    hallucination_rate: float = 0.0,
    regressions: int = 0,
) -> Path:
    """Generate an HTML evaluation report and save to reports/."""
    REPORTS_DIR.mkdir(exist_ok=True)

    template = Template(HTML_TEMPLATE)
    html = template.render(
        title=title,
        run_id=run_id,
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        pass_rate=pass_rate,
        total_tests=len(scores),
        hallucination_rate=hallucination_rate,
        regressions=regressions,
        scores=scores,
    )

    report_path = REPORTS_DIR / f"report_{run_id}.html"
    report_path.write_text(html, encoding="utf-8")
    logger.info(f"HTML report saved: {report_path}")
    return report_path


def generate_json_report(
    run_id: str,
    data: dict[str, Any],
) -> Path:
    """Generate a JSON evaluation report for CI/CD consumption."""
    REPORTS_DIR.mkdir(exist_ok=True)

    report_path = REPORTS_DIR / f"report_{run_id}.json"
    with open(report_path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    logger.info(f"JSON report saved: {report_path}")
    return report_path

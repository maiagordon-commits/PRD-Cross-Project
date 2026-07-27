#!/usr/bin/env python3
"""
Room Migration Progress chart: Total / SMB / Lite.

Rules (from product request):
  - Total = all accounts created after July 13 (unchanged)
  - SMB  = matched Room Overview accounts (161)
  - Lite = Total - SMB

Source CSVs:
  - data/accounts_created_after_2026-07-13.csv
  - data/room_migration_accounts.csv  (only to identify the 161 SMB IDs)
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parent
CREATED_CSV = ROOT / "data" / "accounts_created_after_2026-07-13.csv"
ROOM_CSV = ROOT / "data" / "room_migration_accounts.csv"

BG = "#F5F1E9"
NAVY = "#1B3A5F"
CARD = "#D9EAF7"
CHART_BG = "#FFFFFF"
CHART_BORDER = "#D0D5DD"
MUTED = "#6B7C93"
GRID = "#E6EAF0"
SMB_COLOR = "#4A8FD4"
LITE_COLOR = "#E35D5B"


def parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)


def monday_of(dt: datetime) -> datetime:
    return (dt - timedelta(days=dt.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)


def fmt_int(n: int) -> str:
    return f"{n:,}"


def load_data() -> dict:
    with open(CREATED_CSV, newline="", encoding="utf-8-sig") as f:
        created = list(csv.DictReader(f))
    with open(ROOM_CSV, newline="", encoding="utf-8-sig") as f:
        room_ids = {(r.get("Account ID") or "").strip() for r in csv.DictReader(f)}

    weekly_new = defaultdict(lambda: {"SMB": 0, "Lite": 0})
    smb = 0
    for row in created:
        account_id = (row.get("accountId") or "").strip()
        created_at = parse_date(row["createdAt"])
        week = monday_of(created_at)
        if account_id in room_ids:
            smb += 1
            weekly_new[week]["SMB"] += 1
        else:
            weekly_new[week]["Lite"] += 1

    total = len(created)
    lite = total - smb
    earliest = min(parse_date(r["createdAt"]) for r in created)
    latest = max(parse_date(r["createdAt"]) for r in created)
    start = monday_of(earliest)
    end = monday_of(latest)

    weeks: list[datetime] = []
    cursor = start
    while cursor <= end:
        weeks.append(cursor)
        cursor += timedelta(days=7)

    cum_smb, cum_lite = [], []
    run_smb = run_lite = 0
    for week in weeks:
        run_smb += weekly_new[week]["SMB"]
        run_lite += weekly_new[week]["Lite"]
        cum_smb.append(run_smb)
        cum_lite.append(run_lite)

    return {
        "total": total,
        "smb": smb,
        "lite": lite,
        "weeks": weeks,
        "cum_smb": cum_smb,
        "cum_lite": cum_lite,
        "week_label": f"{earliest.strftime('%B %-d')} - {latest.strftime('%B %-d')}",
    }


def draw_dashboard(data: dict, out_path: Path) -> None:
    fig = plt.figure(figsize=(13.333, 7.5), dpi=150, facecolor=BG)
    fig.subplots_adjust(left=0.05, right=0.97, top=0.92, bottom=0.08)
    fig.text(0.05, 0.92, "Room Migration Progress", fontsize=28, fontweight="bold", color=NAVY, ha="left", va="top")

    ax_date = fig.add_axes([0.05, 0.82, 0.26, 0.055])
    ax_date.set_xlim(0, 1)
    ax_date.set_ylim(0, 1)
    ax_date.axis("off")
    ax_date.add_patch(
        FancyBboxPatch((0.0, 0.05), 0.98, 0.85, boxstyle="round,pad=0.02,rounding_size=0.2", linewidth=0, facecolor="#E4E7EC")
    )
    ax_date.text(0.5, 0.48, data["week_label"], ha="center", va="center", fontsize=11, color=NAVY)

    def metric_card(bounds, label, value):
        ax = fig.add_axes(bounds)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.add_patch(
            FancyBboxPatch((0.02, 0.08), 0.96, 0.84, boxstyle="round,pad=0.02,rounding_size=0.15", linewidth=0, facecolor=CARD)
        )
        ax.text(0.5, 0.68, label, ha="center", va="center", fontsize=12, color=NAVY)
        ax.text(0.5, 0.32, value, ha="center", va="center", fontsize=28, fontweight="bold", color=NAVY)

    metric_card([0.38, 0.78, 0.28, 0.12], "Total Accounts Created", fmt_int(data["total"]))
    metric_card([0.18, 0.62, 0.28, 0.12], "SMB", fmt_int(data["smb"]))
    metric_card([0.54, 0.62, 0.28, 0.12], "Lite", fmt_int(data["lite"]))

    ax = fig.add_axes([0.08, 0.10, 0.86, 0.46])
    for spine in ax.spines.values():
        spine.set_color(CHART_BORDER)
    ax.set_facecolor(CHART_BG)
    ax.set_title("Cumulative Trends by Segment", loc="left", fontsize=12, color=MUTED, pad=10)

    x = list(range(len(data["weeks"])))
    width = 0.55
    ax.bar(x, data["cum_smb"], width=width, color=SMB_COLOR, label="SMB", zorder=3)
    ax.bar(x, data["cum_lite"], width=width, bottom=data["cum_smb"], color=LITE_COLOR, label="Lite", zorder=3)

    ax.set_ylabel("Count", color=MUTED, fontsize=10)
    ax.set_xlabel("Week starting", color=MUTED, fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels([w.strftime("%-m/%d/%Y") for w in data["weeks"]], rotation=45, ha="right", fontsize=9, color=MUTED)
    ax.tick_params(axis="y", colors=MUTED, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.set_ylim(0, max(10, int(data["total"] * 1.12)))
    ax.legend(loc="upper center", bbox_to_anchor=(0.55, 1.02), ncol=2, frameon=False, fontsize=10)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def draw_chart_only(data: dict, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.2, 4.0), dpi=150, facecolor=CHART_BG)
    ax.set_facecolor(CHART_BG)
    x = list(range(len(data["weeks"])))
    ax.bar(x, data["cum_smb"], width=0.55, color=SMB_COLOR, label="SMB", zorder=3)
    ax.bar(x, data["cum_lite"], width=0.55, bottom=data["cum_smb"], color=LITE_COLOR, label="Lite", zorder=3)
    ax.set_title("Cumulative Trends by Segment", loc="left", fontsize=12, color=MUTED, pad=12)
    ax.set_ylabel("Count", color=MUTED, fontsize=10)
    ax.set_xlabel("Week starting", color=MUTED, fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels([w.strftime("%-m/%d/%Y") for w in data["weeks"]], rotation=45, ha="right", fontsize=9, color=MUTED)
    ax.tick_params(axis="y", colors=MUTED, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color(CHART_BORDER)
    ax.set_ylim(0, max(10, int(data["total"] * 1.12)))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=2, frameon=False, fontsize=10)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=CHART_BG, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def set_run(run, size=12, bold=False, color=RGBColor(0x1B, 0x3A, 0x5F)):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Arial"


def add_textbox(slide, left, top, width, height, text, size=12, bold=False, color=RGBColor(0x1B, 0x3A, 0x5F), align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    set_run(run, size=size, bold=bold, color=color)
    return box


def add_rounded_rect(slide, left, top, width, height, fill: RGBColor):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    try:
        shape.adjustments[0] = 0.12
    except Exception:
        pass
    return shape


def add_metric_card(slide, left, top, width, height, label, value):
    card = add_rounded_rect(slide, left, top, width, height, RGBColor(0xD9, 0xEA, 0xF7))
    tf = card.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = label
    set_run(run, size=13)
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    run2 = p2.add_run()
    run2.text = value
    set_run(run2, size=28, bold=True)
    return card


def build_pptx(data: dict, chart_path: Path, out_path: Path) -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = RGBColor(0xF5, 0xF1, 0xE9)
    bg.line.fill.background()

    add_textbox(slide, Inches(0.55), Inches(0.28), Inches(7), Inches(0.5), "Room Migration Progress", size=28, bold=True)
    date_box = add_rounded_rect(slide, Inches(0.55), Inches(0.85), Inches(2.8), Inches(0.38), RGBColor(0xE4, 0xE7, 0xEC))
    tf = date_box.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = data["week_label"]
    set_run(run, size=12)

    add_metric_card(slide, Inches(4.6), Inches(0.3), Inches(4.0), Inches(1.0), "Total Accounts Created", fmt_int(data["total"]))
    add_metric_card(slide, Inches(2.5), Inches(1.55), Inches(3.6), Inches(1.05), "SMB", fmt_int(data["smb"]))
    add_metric_card(slide, Inches(7.0), Inches(1.55), Inches(3.6), Inches(1.05), "Lite", fmt_int(data["lite"]))

    if chart_path.exists():
        slide.shapes.add_picture(str(chart_path), Inches(0.55), Inches(2.9), width=Inches(12.2))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_path)


def build_html(data: dict, out_path: Path) -> None:
    weeks = [w.strftime("%-m/%d/%Y") for w in data["weeks"]]
    html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Room Migration Progress</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root {{ --bg:{BG}; --navy:{NAVY}; --card:{CARD}; --muted:{MUTED}; --border:{CHART_BORDER}; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif; background:#ddd6c8; color:var(--navy);
  min-height:100vh; padding:1.5rem; display:flex; align-items:center; justify-content:center; }}
.slide {{ width:min(1280px,100%); aspect-ratio:16/9; background:var(--bg); border-radius:8px;
  box-shadow:0 12px 40px rgba(27,58,95,.12); padding:1.75rem 2rem 1.25rem;
  display:grid; grid-template-rows:auto auto 1fr; gap:.9rem; }}
.header {{ display:grid; grid-template-columns:1fr auto; gap:1rem; }}
h1 {{ font-size:clamp(1.5rem,2.3vw,2rem); font-weight:700; }}
.date-pill {{ display:inline-block; margin-top:.55rem; background:#E4E7EC; border-radius:10px; padding:.35rem .85rem; }}
.total-card,.tier-card {{ background:var(--card); border-radius:14px; text-align:center; padding:.85rem 1rem;
  box-shadow:0 2px 8px rgba(27,58,95,.08); }}
.tiers {{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; max-width:720px; margin:0 auto; width:100%; }}
.label {{ font-size:.95rem; }} .value {{ font-size:clamp(1.6rem,2.8vw,2.2rem); font-weight:700; }}
.chart-panel {{ background:#fff; border:1px solid var(--border); border-radius:10px; padding:.75rem 1rem .4rem;
  display:flex; flex-direction:column; min-height:0; }}
.chart-title {{ color:var(--muted); font-size:.95rem; }}
.chart-wrap {{ flex:1; position:relative; min-height:220px; }}
@media (max-width:900px) {{ .slide {{ aspect-ratio:auto; }} .header,.tiers {{ grid-template-columns:1fr; }} }}
</style></head><body>
<div class="slide">
  <div class="header">
    <div><h1>Room Migration Progress</h1><div class="date-pill">{data["week_label"]}</div></div>
    <div class="total-card"><div class="label">Total Accounts Created</div><div class="value">{fmt_int(data["total"])}</div></div>
  </div>
  <div class="tiers">
    <div class="tier-card"><div class="label">SMB</div><div class="value">{fmt_int(data["smb"])}</div></div>
    <div class="tier-card"><div class="label">Lite</div><div class="value">{fmt_int(data["lite"])}</div></div>
  </div>
  <div class="chart-panel">
    <div class="chart-title">Cumulative Trends by Segment</div>
    <div class="chart-wrap"><canvas id="trendChart"></canvas></div>
  </div>
</div>
<script>
new Chart(document.getElementById("trendChart"), {{
  type: "bar",
  data: {{
    labels: {json.dumps(weeks)},
    datasets: [
      {{ label: "SMB", data: {json.dumps(data["cum_smb"])}, backgroundColor: "{SMB_COLOR}", stack: "s" }},
      {{ label: "Lite", data: {json.dumps(data["cum_lite"])}, backgroundColor: "{LITE_COLOR}", stack: "s" }}
    ]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ position: "top", labels: {{ boxWidth: 12, color: "{MUTED}" }} }} }},
    scales: {{
      x: {{ stacked: true, title: {{ display: true, text: "Week starting", color: "{MUTED}" }},
            ticks: {{ maxRotation: 45, minRotation: 45, color: "{MUTED}" }}, grid: {{ display: false }} }},
      y: {{ stacked: true, beginAtZero: true, suggestedMax: Math.ceil({data["total"]} * 1.12),
            title: {{ display: true, text: "Count", color: "{MUTED}" }},
            ticks: {{ color: "{MUTED}", precision: 0 }}, grid: {{ color: "{GRID}" }} }}
    }}
  }}
}});
</script></body></html>"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")


def write_summary(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Metric", "Value"])
        w.writerow(["Total Accounts Created", data["total"]])
        w.writerow(["SMB", data["smb"]])
        w.writerow(["Lite (Total - SMB)", data["lite"]])


def main() -> None:
    data = load_data()
    assert data["lite"] == data["total"] - data["smb"]

    chart_path = ROOT / "exports" / "room-migration-chart.png"
    full_png = ROOT / "exports" / "room-migration-progress.png"
    html_path = ROOT / "exports" / "room-migration-progress.html"
    pptx_path = ROOT / "Room_Migration_Progress.pptx"
    summary_path = ROOT / "exports" / "segment-breakdown.csv"

    draw_chart_only(data, chart_path)
    draw_dashboard(data, full_png)
    build_html(data, html_path)
    build_pptx(data, chart_path, pptx_path)
    write_summary(data, summary_path)

    print(f"Total: {data['total']}")
    print(f"SMB:   {data['smb']}")
    print(f"Lite:  {data['lite']}  (= Total - SMB)")
    print(f"Week:  {data['week_label']}")
    print(f"Wrote {full_png}")
    print(f"Wrote {html_path}")
    print(f"Wrote {pptx_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Build a weekly-editable Room Migration Progress slide from the accounts CSV.

Weekly update:
  1. Replace data/room_migration_accounts.csv with the latest export
  2. Optionally set report_week_label in room_migration_config.json
  3. Run: python3 create_room_migration_dashboard.py
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "room_migration_config.json"

# Visual system matching the reference slide
BG = "#F5F1E9"
NAVY = "#1B3A5F"
CARD = "#D9EAF7"
CARD_SHADOW = "#C5D8E8"
CHART_BG = "#FFFFFF"
CHART_BORDER = "#D0D5DD"
LITE = "#4A8FD4"
PRO = "#E35D5B"
ENTERPRISE = "#F0C04A"
MUTED = "#6B7C93"
GRID = "#E6EAF0"

PACKAGE_ALIASES = {
    "lite": "lite",
    "pro": "pro",
    "enterprise": "enterprise",
    "ent": "enterprise",
}


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def parse_date(value: str) -> datetime | None:
    if not value or value.strip().lower() in {"null", "none", "nan", ""}:
        return None
    value = value.strip()
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    # Excel-ish: 2026-07-13T00:00:00.000Z
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", value)
    if m:
        return datetime.strptime(m.group(1), "%Y-%m-%d")
    return None


def monday_of(dt: datetime) -> datetime:
    return (dt - timedelta(days=dt.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)


def normalize_package(raw: str) -> str | None:
    if not raw:
        return None
    key = raw.strip().lower()
    return PACKAGE_ALIASES.get(key)


def is_true(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def load_migrated_rows(csv_path: Path) -> list[dict]:
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            if not is_true(row.get("Room Migrated?", "")):
                continue
            completed = parse_date(row.get("Migration Completed At", ""))
            if completed is None:
                continue
            package = normalize_package(row.get("Package", ""))
            if package is None:
                continue
            rows.append(
                {
                    "package": package,
                    "segment": (row.get("Segment") or "").strip(),
                    "completed": completed,
                    "name": row.get("Account Name", ""),
                }
            )
        return rows


def aggregate(rows: list[dict], chart_start: datetime) -> dict:
    totals = {"lite": 0, "pro": 0, "enterprise": 0}
    pro_mid_market = 0
    weekly_new = defaultdict(lambda: {"lite": 0, "pro": 0, "enterprise": 0})

    for row in rows:
        pkg = row["package"]
        totals[pkg] += 1
        if pkg == "pro" and row["segment"].lower() in {"mid-market", "mid market", "midmarket"}:
            pro_mid_market += 1
        week = monday_of(row["completed"])
        weekly_new[week][pkg] += 1

    if rows:
        end = monday_of(max(r["completed"] for r in rows))
    else:
        end = monday_of(datetime.today())

    start = monday_of(chart_start)
    if start > end:
        start = end

    weeks: list[datetime] = []
    cursor = start
    while cursor <= end:
        weeks.append(cursor)
        cursor += timedelta(days=7)

    cumulative = {"lite": [], "pro": [], "enterprise": []}
    running = {"lite": 0, "pro": 0, "enterprise": 0}
    for week in weeks:
        for pkg in ("lite", "pro", "enterprise"):
            running[pkg] += weekly_new[week][pkg]
            cumulative[pkg].append(running[pkg])

    latest = max((r["completed"] for r in rows), default=datetime.today())
    week_start = monday_of(latest)
    week_end = week_start + timedelta(days=4)  # Mon–Fri style label like the mock

    return {
        "totals": totals,
        "total": sum(totals.values()),
        "pro_mid_market": pro_mid_market,
        "weeks": weeks,
        "cumulative": cumulative,
        "auto_week_label": f"{week_start.strftime('%B %-d')} - {week_end.strftime('%B %-d')}",
        "migrated_rows": len(rows),
    }


def fmt_int(n: int) -> str:
    return f"{n:,}"


def draw_dashboard_image(agg: dict, week_label: str, title: str, out_path: Path) -> None:
    """Render a full slide-like PNG matching the reference layout."""
    fig = plt.figure(figsize=(13.333, 7.5), dpi=150, facecolor=BG)
    # Outer margins
    fig.subplots_adjust(left=0.05, right=0.97, top=0.92, bottom=0.08)

    # Title + date
    fig.text(0.05, 0.92, title, fontsize=28, fontweight="bold", color=NAVY, ha="left", va="top")
    ax_date = fig.add_axes([0.05, 0.82, 0.22, 0.055])
    ax_date.set_xlim(0, 1)
    ax_date.set_ylim(0, 1)
    ax_date.axis("off")
    ax_date.add_patch(
        FancyBboxPatch(
            (0.0, 0.05),
            0.98,
            0.85,
            boxstyle="round,pad=0.02,rounding_size=0.2",
            linewidth=0,
            facecolor="#E4E7EC",
        )
    )
    ax_date.text(0.5, 0.48, week_label, ha="center", va="center", fontsize=11, color=NAVY)

    totals = agg["totals"]

    def metric_card(bounds, label, value, sub=None):
        ax = fig.add_axes(bounds)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.add_patch(
            FancyBboxPatch(
                (0.02, 0.08),
                0.96,
                0.84,
                boxstyle="round,pad=0.02,rounding_size=0.15",
                linewidth=0,
                facecolor=CARD,
            )
        )
        ax.text(0.5, 0.72, label, ha="center", va="center", fontsize=11, color=NAVY)
        ax.text(0.5, 0.38 if sub else 0.35, value, ha="center", va="center", fontsize=28, fontweight="bold", color=NAVY)
        if sub:
            ax.text(0.5, 0.14, sub, ha="center", va="center", fontsize=9, color=MUTED)

    metric_card([0.35, 0.78, 0.30, 0.12], "Total Accounts Migrated", fmt_int(agg["total"]))
    metric_card([0.12, 0.62, 0.24, 0.12], "Lite", fmt_int(totals["lite"]))
    pro_sub = f"Out of them {fmt_int(agg['pro_mid_market'])} Mid Market"
    metric_card([0.38, 0.62, 0.24, 0.12], "Pro", fmt_int(totals["pro"]), sub=pro_sub)
    metric_card([0.64, 0.62, 0.24, 0.12], "Enterprise", fmt_int(totals["enterprise"]))

    # Chart panel
    ax = fig.add_axes([0.08, 0.10, 0.86, 0.46])
    for spine in ax.spines.values():
        spine.set_color(CHART_BORDER)
        spine.set_linewidth(1)
    ax.set_facecolor(CHART_BG)
    ax.set_title("Cumulative Trends by Plan", loc="left", fontsize=12, color=MUTED, pad=10)

    weeks = agg["weeks"]
    x = list(range(len(weeks)))
    lite = agg["cumulative"]["lite"]
    pro = agg["cumulative"]["pro"]
    ent = agg["cumulative"]["enterprise"]

    width = 0.65
    ax.bar(x, lite, width=width, color=LITE, label="Lite", zorder=3)
    ax.bar(x, pro, width=width, bottom=lite, color=PRO, label="Pro", zorder=3)
    bottom2 = [a + b for a, b in zip(lite, pro)]
    ax.bar(x, ent, width=width, bottom=bottom2, color=ENTERPRISE, label="Enterprise", zorder=3)

    ax.set_ylabel("Count", color=MUTED, fontsize=10)
    ax.set_xlabel("Week starting", color=MUTED, fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels([w.strftime("%-m/%d/%Y") for w in weeks], rotation=45, ha="right", fontsize=8, color=MUTED)
    ax.tick_params(axis="y", colors=MUTED, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ymax = max(agg["total"], 1)
    # Headroom so a tiny series still reads; grow with data
    ax.set_ylim(0, max(10, int(ymax * 1.15)))
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.55, 1.02),
        ncol=3,
        frameon=False,
        fontsize=9,
        handlelength=1.2,
        columnspacing=1.2,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def set_run(run, size=12, bold=False, color=RGBColor(0x1B, 0x3A, 0x5F), font_name="Arial"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font_name


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
    from pptx.enum.shapes import MSO_SHAPE

    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    try:
        shape.adjustments[0] = 0.12
    except Exception:
        pass
    return shape


def add_metric_card(slide, left, top, width, height, label, value, sub=None):
    card = add_rounded_rect(slide, left, top, width, height, RGBColor(0xD9, 0xEA, 0xF7))
    tf = card.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = label
    set_run(run, size=12, bold=False)

    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    run2 = p2.add_run()
    run2.text = value
    set_run(run2, size=28, bold=True)

    if sub:
        p3 = tf.add_paragraph()
        p3.alignment = PP_ALIGN.CENTER
        run3 = p3.add_run()
        run3.text = sub
        set_run(run3, size=10, bold=False, color=RGBColor(0x6B, 0x7C, 0x93))
    return card


def build_pptx(agg: dict, week_label: str, title: str, chart_path: Path, out_path: Path) -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    from pptx.enum.shapes import MSO_SHAPE

    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = RGBColor(0xF5, 0xF1, 0xE9)
    bg.line.fill.background()

    add_textbox(slide, Inches(0.55), Inches(0.28), Inches(6), Inches(0.55), title, size=30, bold=True)

    date_box = add_rounded_rect(slide, Inches(0.55), Inches(0.9), Inches(2.4), Inches(0.38), RGBColor(0xE4, 0xE7, 0xEC))
    tf = date_box.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = week_label
    set_run(run, size=12, bold=False)

    totals = agg["totals"]
    add_metric_card(
        slide,
        Inches(4.7),
        Inches(0.35),
        Inches(3.8),
        Inches(1.05),
        "Total Accounts Migrated",
        fmt_int(agg["total"]),
    )
    add_metric_card(slide, Inches(1.5), Inches(1.55), Inches(3.2), Inches(1.1), "Lite", fmt_int(totals["lite"]))
    pro_sub = f"Out of them {fmt_int(agg['pro_mid_market'])} Mid Market"
    add_metric_card(
        slide,
        Inches(5.05),
        Inches(1.55),
        Inches(3.2),
        Inches(1.1),
        "Pro",
        fmt_int(totals["pro"]),
        sub=pro_sub,
    )
    add_metric_card(
        slide,
        Inches(8.6),
        Inches(1.55),
        Inches(3.2),
        Inches(1.1),
        "Enterprise",
        fmt_int(totals["enterprise"]),
    )

    if chart_path.exists():
        slide.shapes.add_picture(str(chart_path), Inches(0.55), Inches(2.9), width=Inches(12.2))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_path)


def build_html(agg: dict, week_label: str, title: str, out_path: Path) -> None:
    weeks = [w.strftime("%-m/%d/%Y") for w in agg["weeks"]]
    lite = agg["cumulative"]["lite"]
    pro = agg["cumulative"]["pro"]
    ent = agg["cumulative"]["enterprise"]
    totals = agg["totals"]
    pro_sub = f'<div class="sub">Out of them {fmt_int(agg["pro_mid_market"])} Mid Market</div>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --bg: {BG};
      --navy: {NAVY};
      --card: {CARD};
      --muted: {MUTED};
      --lite: {LITE};
      --pro: {PRO};
      --enterprise: {ENTERPRISE};
      --border: {CHART_BORDER};
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
      background: #ddd6c8;
      color: var(--navy);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
    }}
    .slide {{
      width: min(1280px, 100%);
      aspect-ratio: 16 / 9;
      background: var(--bg);
      border-radius: 8px;
      box-shadow: 0 12px 40px rgba(27, 58, 95, 0.12);
      padding: 2rem 2.25rem 1.5rem;
      display: grid;
      grid-template-rows: auto auto 1fr;
      gap: 1rem;
    }}
    .header {{
      display: grid;
      grid-template-columns: 1fr auto;
      align-items: start;
      gap: 1rem;
    }}
    h1 {{
      font-size: clamp(1.6rem, 2.4vw, 2.1rem);
      font-weight: 700;
      letter-spacing: -0.02em;
    }}
    .date-pill {{
      display: inline-block;
      margin-top: 0.65rem;
      background: #E4E7EC;
      color: var(--navy);
      border-radius: 10px;
      padding: 0.4rem 0.9rem;
      font-size: 0.95rem;
    }}
    .total-card, .tier-card {{
      background: var(--card);
      border-radius: 14px;
      box-shadow: 0 2px 8px rgba(27, 58, 95, 0.08);
      text-align: center;
      padding: 0.85rem 1rem;
    }}
    .total-card {{
      min-width: 260px;
      align-self: start;
    }}
    .label {{ font-size: 0.95rem; margin-bottom: 0.15rem; }}
    .value {{ font-size: clamp(1.8rem, 3vw, 2.35rem); font-weight: 700; line-height: 1.1; }}
    .sub {{ font-size: 0.8rem; color: var(--muted); margin-top: 0.25rem; }}
    .tiers {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1rem;
      max-width: 920px;
      margin: 0 auto;
      width: 100%;
    }}
    .chart-panel {{
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(27, 58, 95, 0.06);
      padding: 0.85rem 1rem 0.5rem;
      min-height: 0;
      display: flex;
      flex-direction: column;
    }}
    .chart-title {{
      color: var(--muted);
      font-size: 0.95rem;
      margin-bottom: 0.25rem;
    }}
    .chart-wrap {{
      flex: 1;
      position: relative;
      min-height: 220px;
    }}
    .howto {{
      margin-top: 0.35rem;
      font-size: 0.72rem;
      color: var(--muted);
      text-align: center;
    }}
    @media (max-width: 800px) {{
      body {{ align-items: flex-start; }}
      .slide {{ aspect-ratio: auto; height: auto; }}
      .header {{ grid-template-columns: 1fr; }}
      .total-card {{ min-width: 0; }}
    }}
  </style>
</head>
<body>
  <div class="slide">
    <div class="header">
      <div>
        <h1>{title}</h1>
        <div class="date-pill">{week_label}</div>
      </div>
      <div class="total-card">
        <div class="label">Total Accounts Migrated</div>
        <div class="value">{fmt_int(agg["total"])}</div>
      </div>
    </div>

    <div class="tiers">
      <div class="tier-card">
        <div class="label">Lite</div>
        <div class="value">{fmt_int(totals["lite"])}</div>
      </div>
      <div class="tier-card">
        <div class="label">Pro</div>
        <div class="value">{fmt_int(totals["pro"])}</div>
        {pro_sub}
      </div>
      <div class="tier-card">
        <div class="label">Enterprise</div>
        <div class="value">{fmt_int(totals["enterprise"])}</div>
      </div>
    </div>

    <div class="chart-panel">
      <div class="chart-title">Cumulative Trends by Plan</div>
      <div class="chart-wrap">
        <canvas id="trendChart"></canvas>
      </div>
      <p class="howto">Weekly edit: replace <code>data/room_migration_accounts.csv</code> and run <code>python3 create_room_migration_dashboard.py</code></p>
    </div>
  </div>

  <script>
    const labels = {json.dumps(weeks)};
    const lite = {json.dumps(lite)};
    const pro = {json.dumps(pro)};
    const enterprise = {json.dumps(ent)};
    const total = {agg["total"]};

    new Chart(document.getElementById("trendChart"), {{
      type: "bar",
      data: {{
        labels,
        datasets: [
          {{ label: "Lite", data: lite, backgroundColor: "{LITE}", stack: "plans" }},
          {{ label: "Pro", data: pro, backgroundColor: "{PRO}", stack: "plans" }},
          {{ label: "Enterprise", data: enterprise, backgroundColor: "{ENTERPRISE}", stack: "plans" }}
        ]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{
            position: "top",
            labels: {{ boxWidth: 12, color: "{MUTED}" }}
          }}
        }},
        scales: {{
          x: {{
            stacked: true,
            title: {{ display: true, text: "Week starting", color: "{MUTED}" }},
            ticks: {{ maxRotation: 45, minRotation: 45, color: "{MUTED}", font: {{ size: 10 }} }},
            grid: {{ display: false }}
          }},
          y: {{
            stacked: true,
            beginAtZero: true,
            suggestedMax: Math.max(10, Math.ceil(total * 1.15) || 10),
            title: {{ display: true, text: "Count", color: "{MUTED}" }},
            ticks: {{ color: "{MUTED}", precision: 0 }},
            grid: {{ color: "{GRID}" }}
          }}
        }}
      }}
    }});
  </script>
</body>
</html>
"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")


def draw_chart_only(agg: dict, out_path: Path) -> None:
    """Chart-only PNG for embedding cleanly in PowerPoint."""
    fig, ax = plt.subplots(figsize=(12.2, 4.0), dpi=150, facecolor=CHART_BG)
    ax.set_facecolor(CHART_BG)
    weeks = agg["weeks"]
    x = list(range(len(weeks)))
    lite = agg["cumulative"]["lite"]
    pro = agg["cumulative"]["pro"]
    ent = agg["cumulative"]["enterprise"]
    width = 0.65
    ax.bar(x, lite, width=width, color=LITE, label="Lite", zorder=3)
    ax.bar(x, pro, width=width, bottom=lite, color=PRO, label="Pro", zorder=3)
    bottom2 = [a + b for a, b in zip(lite, pro)]
    ax.bar(x, ent, width=width, bottom=bottom2, color=ENTERPRISE, label="Enterprise", zorder=3)
    ax.set_title("Cumulative Trends by Plan", loc="left", fontsize=12, color=MUTED, pad=12)
    ax.set_ylabel("Count", color=MUTED, fontsize=10)
    ax.set_xlabel("Week starting", color=MUTED, fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels([w.strftime("%-m/%d/%Y") for w in weeks], rotation=45, ha="right", fontsize=8, color=MUTED)
    ax.tick_params(axis="y", colors=MUTED, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color(CHART_BORDER)
    ymax = max(agg["total"], 1)
    ax.set_ylim(0, max(10, int(ymax * 1.15)))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=3, frameon=False, fontsize=9)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=CHART_BG, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def main() -> None:
    cfg = load_config()
    csv_path = ROOT / cfg["csv_path"]
    chart_start = datetime.strptime(cfg["chart_start"], "%Y-%m-%d")
    title = cfg.get("title", "Room Migration Progress")

    rows = load_migrated_rows(csv_path)
    agg = aggregate(rows, chart_start)
    week_label = cfg.get("report_week_label") or agg["auto_week_label"]

    chart_path = ROOT / cfg["output_chart"]
    html_path = ROOT / cfg["output_html"]
    pptx_path = ROOT / cfg["output_pptx"]
    full_slide_png = ROOT / "exports" / "room-migration-progress.png"

    draw_chart_only(agg, chart_path)
    draw_dashboard_image(agg, week_label, title, full_slide_png)
    build_html(agg, week_label, title, html_path)
    build_pptx(agg, week_label, title, chart_path, pptx_path)

    print(f"Migrated accounts: {agg['total']}")
    print(f"  Lite: {agg['totals']['lite']}")
    print(f"  Pro: {agg['totals']['pro']} (Mid Market: {agg['pro_mid_market']})")
    print(f"  Enterprise: {agg['totals']['enterprise']}")
    print(f"Week label: {week_label}")
    print(f"Wrote {html_path}")
    print(f"Wrote {pptx_path}")
    print(f"Wrote {full_slide_png}")
    print(f"Wrote {chart_path}")


if __name__ == "__main__":
    main()

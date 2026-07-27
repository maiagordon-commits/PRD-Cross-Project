#!/usr/bin/env python3
"""
Build a weekly-editable Room Migration Progress slide.

Logic:
  1. Load accounts created after the cutoff (accountId, createdAt)
  2. Cross account IDs with the Reservations Room Accounts Overview CSV
  3. Use Package / Segment from the room file for KPI + chart breakdowns
  4. Build cumulative weekly trends from createdAt

Weekly update:
  1. Replace data/accounts_created_after_2026-07-13.csv
  2. Replace data/room_migration_accounts.csv
  3. Optionally set report_week_label in room_migration_config.json
  4. Run: python3 create_room_migration_dashboard.py
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
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
CONFIG_PATH = ROOT / "room_migration_config.json"

BG = "#F5F1E9"
NAVY = "#1B3A5F"
CARD = "#D9EAF7"
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

PACKAGE_ORDER = ("lite", "pro", "enterprise")


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def parse_date(value: str) -> datetime | None:
    if not value or value.strip().lower() in {"null", "none", "nan", ""}:
        return None
    value = value.strip()
    # Prefer full ISO timestamps (e.g. 2026-07-13T09:00:46.212Z) before date-only parses.
    if "T" in value or value.endswith("Z"):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            pass
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", value)
    if m:
        return datetime.strptime(m.group(1), "%Y-%m-%d")
    return None


def monday_of(dt: datetime) -> datetime:
    return (dt - timedelta(days=dt.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)


def normalize_package(raw: str) -> str:
    key = (raw or "").strip().lower()
    return PACKAGE_ALIASES.get(key, "other")


def normalize_segment(raw: str) -> str:
    value = (raw or "").strip()
    if not value or value.lower() in {"null", "none", "nan"}:
        return "Unknown"
    return value


def is_mid_market(segment: str) -> bool:
    return segment.lower().replace(" ", "").replace("-", "") in {"midmarket"}


def load_created_accounts(path: Path) -> dict[str, datetime]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        out: dict[str, datetime] = {}
        for row in reader:
            account_id = (row.get("accountId") or row.get("Account ID") or "").strip()
            created = parse_date(row.get("createdAt") or row.get("Created At") or "")
            if account_id and created:
                out[account_id] = created
        return out


def load_room_accounts(path: Path) -> dict[str, dict]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return {
            (row.get("Account ID") or "").strip(): row
            for row in reader
            if (row.get("Account ID") or "").strip()
        }


def join_accounts(created: dict[str, datetime], room: dict[str, dict]) -> list[dict]:
    joined = []
    for account_id, created_at in created.items():
        room_row = room.get(account_id)
        if not room_row:
            continue
        package = normalize_package(room_row.get("Package", ""))
        segment = normalize_segment(room_row.get("Segment", ""))
        joined.append(
            {
                "Account ID": account_id,
                "Account Name": room_row.get("Account Name", ""),
                "Package": package,
                "Segment": segment,
                "CSM": room_row.get("CSM", ""),
                "Active?": room_row.get("Active?", ""),
                "Paying?": room_row.get("Paying?", ""),
                "account_status": room_row.get("account_status", ""),
                "Room Migrated?": room_row.get("Room Migrated?", ""),
                "Migration Completed At": room_row.get("Migration Completed At", ""),
                "Created At": created_at,
                "Created At ISO": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            }
        )
    joined.sort(key=lambda r: r["Created At"])
    return joined


def aggregate(joined: list[dict], chart_start: datetime) -> dict:
    totals = {pkg: 0 for pkg in PACKAGE_ORDER}
    pro_mid_market = 0
    segment_counts: Counter[str] = Counter()
    segment_by_package: dict[str, Counter[str]] = defaultdict(Counter)
    weekly_new = defaultdict(lambda: {pkg: 0 for pkg in PACKAGE_ORDER})

    for row in joined:
        pkg = row["Package"]
        if pkg in totals:
            totals[pkg] += 1
        else:
            # Keep unknown packages out of Lite/Pro/Enterprise cards but still count in total via joined len
            pass
        segment_counts[row["Segment"]] += 1
        segment_by_package[row["Segment"]][pkg if pkg in totals else "other"] += 1
        if pkg == "pro" and is_mid_market(row["Segment"]):
            pro_mid_market += 1
        week = monday_of(row["Created At"])
        if pkg in weekly_new[week]:
            weekly_new[week][pkg] += 1

    if joined:
        end = monday_of(max(r["Created At"] for r in joined))
        latest = max(r["Created At"] for r in joined)
        earliest = min(r["Created At"] for r in joined)
    else:
        end = monday_of(datetime.today())
        latest = datetime.today()
        earliest = chart_start

    start = monday_of(chart_start)
    if start > end:
        start = end

    weeks: list[datetime] = []
    cursor = start
    while cursor <= end:
        weeks.append(cursor)
        cursor += timedelta(days=7)

    cumulative = {pkg: [] for pkg in PACKAGE_ORDER}
    running = {pkg: 0 for pkg in PACKAGE_ORDER}
    for week in weeks:
        for pkg in PACKAGE_ORDER:
            running[pkg] += weekly_new[week][pkg]
            cumulative[pkg].append(running[pkg])

    plan_total = sum(totals.values())
    auto_week_label = f"{earliest.strftime('%B %-d')} - {latest.strftime('%B %-d')}"

    return {
        "totals": totals,
        "total": plan_total,
        "matched": len(joined),
        "pro_mid_market": pro_mid_market,
        "segment_counts": segment_counts,
        "segment_by_package": segment_by_package,
        "weeks": weeks,
        "cumulative": cumulative,
        "auto_week_label": auto_week_label,
        "earliest": earliest,
        "latest": latest,
    }


def fmt_int(n: int) -> str:
    return f"{n:,}"


def write_consolidated_csv(joined: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "Account ID",
        "Account Name",
        "Package",
        "Segment",
        "Created At ISO",
        "CSM",
        "Active?",
        "Paying?",
        "account_status",
        "Room Migrated?",
        "Migration Completed At",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in joined:
            writer.writerow(row)


def write_segment_summary(agg: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Segment", "Total", "Lite", "Pro", "Enterprise", "Other"])
        for segment, total in sorted(agg["segment_counts"].items(), key=lambda x: (-x[1], x[0])):
            by_pkg = agg["segment_by_package"][segment]
            writer.writerow(
                [
                    segment,
                    total,
                    by_pkg.get("lite", 0),
                    by_pkg.get("pro", 0),
                    by_pkg.get("enterprise", 0),
                    by_pkg.get("other", 0),
                ]
            )
        writer.writerow([])
        writer.writerow(["TOTAL", agg["matched"], agg["totals"]["lite"], agg["totals"]["pro"], agg["totals"]["enterprise"], ""])


def draw_dashboard_image(agg: dict, week_label: str, title: str, total_label: str, out_path: Path) -> None:
    fig = plt.figure(figsize=(13.333, 7.5), dpi=150, facecolor=BG)
    fig.subplots_adjust(left=0.05, right=0.97, top=0.92, bottom=0.08)

    fig.text(0.05, 0.92, title, fontsize=28, fontweight="bold", color=NAVY, ha="left", va="top")
    ax_date = fig.add_axes([0.05, 0.82, 0.26, 0.055])
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
        ax.text(
            0.5,
            0.38 if sub else 0.35,
            value,
            ha="center",
            va="center",
            fontsize=28,
            fontweight="bold",
            color=NAVY,
        )
        if sub:
            ax.text(0.5, 0.14, sub, ha="center", va="center", fontsize=9, color=MUTED)

    metric_card([0.35, 0.78, 0.30, 0.12], total_label, fmt_int(agg["total"]))
    metric_card([0.12, 0.62, 0.24, 0.12], "Lite", fmt_int(totals["lite"]))
    pro_sub = f"Out of them {fmt_int(agg['pro_mid_market'])} Mid Market"
    metric_card([0.38, 0.62, 0.24, 0.12], "Pro", fmt_int(totals["pro"]), sub=pro_sub)
    metric_card([0.64, 0.62, 0.24, 0.12], "Enterprise", fmt_int(totals["enterprise"]))

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
    width = 0.55 if len(weeks) > 8 else 0.65

    ax.bar(x, lite, width=width, color=LITE, label="Lite", zorder=3)
    ax.bar(x, pro, width=width, bottom=lite, color=PRO, label="Pro", zorder=3)
    bottom2 = [a + b for a, b in zip(lite, pro)]
    ax.bar(x, ent, width=width, bottom=bottom2, color=ENTERPRISE, label="Enterprise", zorder=3)

    ax.set_ylabel("Count", color=MUTED, fontsize=10)
    ax.set_xlabel("Week starting", color=MUTED, fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels([w.strftime("%-m/%d/%Y") for w in weeks], rotation=45, ha="right", fontsize=9, color=MUTED)
    ax.tick_params(axis="y", colors=MUTED, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ymax = max(agg["total"], 1)
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


def draw_chart_only(agg: dict, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.2, 4.0), dpi=150, facecolor=CHART_BG)
    ax.set_facecolor(CHART_BG)
    weeks = agg["weeks"]
    x = list(range(len(weeks)))
    lite = agg["cumulative"]["lite"]
    pro = agg["cumulative"]["pro"]
    ent = agg["cumulative"]["enterprise"]
    width = 0.55 if len(weeks) > 8 else 0.65
    ax.bar(x, lite, width=width, color=LITE, label="Lite", zorder=3)
    ax.bar(x, pro, width=width, bottom=lite, color=PRO, label="Pro", zorder=3)
    bottom2 = [a + b for a, b in zip(lite, pro)]
    ax.bar(x, ent, width=width, bottom=bottom2, color=ENTERPRISE, label="Enterprise", zorder=3)
    ax.set_title("Cumulative Trends by Plan", loc="left", fontsize=12, color=MUTED, pad=12)
    ax.set_ylabel("Count", color=MUTED, fontsize=10)
    ax.set_xlabel("Week starting", color=MUTED, fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels([w.strftime("%-m/%d/%Y") for w in weeks], rotation=45, ha="right", fontsize=9, color=MUTED)
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


def build_pptx(agg: dict, week_label: str, title: str, total_label: str, chart_path: Path, out_path: Path) -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = RGBColor(0xF5, 0xF1, 0xE9)
    bg.line.fill.background()

    add_textbox(slide, Inches(0.55), Inches(0.28), Inches(6), Inches(0.55), title, size=30, bold=True)

    date_box = add_rounded_rect(slide, Inches(0.55), Inches(0.9), Inches(2.8), Inches(0.38), RGBColor(0xE4, 0xE7, 0xEC))
    tf = date_box.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = week_label
    set_run(run, size=12, bold=False)

    totals = agg["totals"]
    add_metric_card(slide, Inches(4.5), Inches(0.35), Inches(4.2), Inches(1.05), total_label, fmt_int(agg["total"]))
    add_metric_card(slide, Inches(1.5), Inches(1.55), Inches(3.2), Inches(1.1), "Lite", fmt_int(totals["lite"]))
    add_metric_card(
        slide,
        Inches(5.05),
        Inches(1.55),
        Inches(3.2),
        Inches(1.1),
        "Pro",
        fmt_int(totals["pro"]),
        sub=f"Out of them {fmt_int(agg['pro_mid_market'])} Mid Market",
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

    # Segment breakdown slide
    slide2 = prs.slides.add_slide(prs.slide_layouts[6])
    bg2 = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg2.fill.solid()
    bg2.fill.fore_color.rgb = RGBColor(0xF5, 0xF1, 0xE9)
    bg2.line.fill.background()
    add_textbox(
        slide2,
        Inches(0.55),
        Inches(0.35),
        Inches(12),
        Inches(0.5),
        "Accounts Created After July 13 — Segment Breakdown",
        size=26,
        bold=True,
    )
    add_textbox(
        slide2,
        Inches(0.55),
        Inches(0.95),
        Inches(12),
        Inches(0.4),
        f"Matched room accounts: {fmt_int(agg['matched'])}  ·  {week_label}",
        size=14,
        color=RGBColor(0x6B, 0x7C, 0x93),
    )

    y = 1.6
    add_rounded_rect(slide2, Inches(0.55), Inches(y), Inches(12.2), Inches(0.5), RGBColor(0xD9, 0xEA, 0xF7))
    add_textbox(slide2, Inches(0.7), Inches(y + 0.08), Inches(3), Inches(0.35), "Segment", size=14, bold=True)
    add_textbox(slide2, Inches(4.2), Inches(y + 0.08), Inches(1.5), Inches(0.35), "Total", size=14, bold=True)
    add_textbox(slide2, Inches(6.0), Inches(y + 0.08), Inches(1.5), Inches(0.35), "Lite", size=14, bold=True)
    add_textbox(slide2, Inches(7.8), Inches(y + 0.08), Inches(1.5), Inches(0.35), "Pro", size=14, bold=True)
    add_textbox(slide2, Inches(9.6), Inches(y + 0.08), Inches(1.8), Inches(0.35), "Enterprise", size=14, bold=True)

    y = 2.25
    for segment, total in sorted(agg["segment_counts"].items(), key=lambda x: (-x[1], x[0])):
        by_pkg = agg["segment_by_package"][segment]
        add_textbox(slide2, Inches(0.7), Inches(y), Inches(3), Inches(0.35), segment, size=14)
        add_textbox(slide2, Inches(4.2), Inches(y), Inches(1.5), Inches(0.35), fmt_int(total), size=14, bold=True)
        add_textbox(slide2, Inches(6.0), Inches(y), Inches(1.5), Inches(0.35), fmt_int(by_pkg.get("lite", 0)), size=14)
        add_textbox(slide2, Inches(7.8), Inches(y), Inches(1.5), Inches(0.35), fmt_int(by_pkg.get("pro", 0)), size=14)
        add_textbox(slide2, Inches(9.6), Inches(y), Inches(1.8), Inches(0.35), fmt_int(by_pkg.get("enterprise", 0)), size=14)
        y += 0.45

    add_textbox(
        slide2,
        Inches(0.7),
        Inches(y + 0.2),
        Inches(3),
        Inches(0.35),
        "TOTAL",
        size=14,
        bold=True,
    )
    add_textbox(slide2, Inches(4.2), Inches(y + 0.2), Inches(1.5), Inches(0.35), fmt_int(agg["matched"]), size=14, bold=True)
    add_textbox(slide2, Inches(6.0), Inches(y + 0.2), Inches(1.5), Inches(0.35), fmt_int(agg["totals"]["lite"]), size=14, bold=True)
    add_textbox(slide2, Inches(7.8), Inches(y + 0.2), Inches(1.5), Inches(0.35), fmt_int(agg["totals"]["pro"]), size=14, bold=True)
    add_textbox(slide2, Inches(9.6), Inches(y + 0.2), Inches(1.8), Inches(0.35), fmt_int(agg["totals"]["enterprise"]), size=14, bold=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_path)


def build_html(agg: dict, week_label: str, title: str, total_label: str, out_path: Path) -> None:
    weeks = [w.strftime("%-m/%d/%Y") for w in agg["weeks"]]
    lite = agg["cumulative"]["lite"]
    pro = agg["cumulative"]["pro"]
    ent = agg["cumulative"]["enterprise"]
    totals = agg["totals"]
    segment_rows = "".join(
        f"<tr><td>{seg}</td><td>{fmt_int(total)}</td>"
        f"<td>{fmt_int(agg['segment_by_package'][seg].get('lite', 0))}</td>"
        f"<td>{fmt_int(agg['segment_by_package'][seg].get('pro', 0))}</td>"
        f"<td>{fmt_int(agg['segment_by_package'][seg].get('enterprise', 0))}</td></tr>"
        for seg, total in sorted(agg["segment_counts"].items(), key=lambda x: (-x[1], x[0]))
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --bg: {BG}; --navy: {NAVY}; --card: {CARD}; --muted: {MUTED};
      --lite: {LITE}; --pro: {PRO}; --enterprise: {ENTERPRISE}; --border: {CHART_BORDER};
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
      background: #ddd6c8; color: var(--navy);
      min-height: 100vh; padding: 1.5rem;
      display: flex; flex-direction: column; align-items: center; gap: 1.5rem;
    }}
    .slide {{
      width: min(1280px, 100%); aspect-ratio: 16 / 9; background: var(--bg);
      border-radius: 8px; box-shadow: 0 12px 40px rgba(27,58,95,.12);
      padding: 2rem 2.25rem 1.5rem; display: grid; grid-template-rows: auto auto 1fr; gap: 1rem;
    }}
    .panel {{
      width: min(1280px, 100%); background: var(--bg); border-radius: 8px;
      box-shadow: 0 12px 40px rgba(27,58,95,.12); padding: 1.5rem 2rem 2rem;
    }}
    .header {{ display: grid; grid-template-columns: 1fr auto; gap: 1rem; align-items: start; }}
    h1 {{ font-size: clamp(1.6rem, 2.4vw, 2.1rem); font-weight: 700; letter-spacing: -.02em; }}
    h2 {{ font-size: 1.35rem; margin-bottom: .75rem; }}
    .date-pill {{
      display: inline-block; margin-top: .65rem; background: #E4E7EC; color: var(--navy);
      border-radius: 10px; padding: .4rem .9rem; font-size: .95rem;
    }}
    .total-card, .tier-card {{
      background: var(--card); border-radius: 14px; box-shadow: 0 2px 8px rgba(27,58,95,.08);
      text-align: center; padding: .85rem 1rem;
    }}
    .total-card {{ min-width: 280px; }}
    .label {{ font-size: .95rem; margin-bottom: .15rem; }}
    .value {{ font-size: clamp(1.8rem, 3vw, 2.35rem); font-weight: 700; line-height: 1.1; }}
    .sub {{ font-size: .8rem; color: var(--muted); margin-top: .25rem; }}
    .tiers {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; max-width: 920px; margin: 0 auto; width: 100%; }}
    .chart-panel {{
      background: #fff; border: 1px solid var(--border); border-radius: 10px;
      box-shadow: 0 2px 10px rgba(27,58,95,.06); padding: .85rem 1rem .5rem;
      min-height: 0; display: flex; flex-direction: column;
    }}
    .chart-title {{ color: var(--muted); font-size: .95rem; margin-bottom: .25rem; }}
    .chart-wrap {{ flex: 1; position: relative; min-height: 220px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: .5rem; }}
    th, td {{ text-align: left; padding: .7rem .8rem; border-bottom: 1px solid #e5e7eb; }}
    th {{ color: var(--muted); font-size: .8rem; text-transform: uppercase; }}
    .note {{ margin-top: 1rem; color: var(--muted); font-size: .85rem; }}
    @media (max-width: 800px) {{
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
        <div class="label">{total_label}</div>
        <div class="value">{fmt_int(agg["total"])}</div>
      </div>
    </div>
    <div class="tiers">
      <div class="tier-card"><div class="label">Lite</div><div class="value">{fmt_int(totals["lite"])}</div></div>
      <div class="tier-card">
        <div class="label">Pro</div><div class="value">{fmt_int(totals["pro"])}</div>
        <div class="sub">Out of them {fmt_int(agg["pro_mid_market"])} Mid Market</div>
      </div>
      <div class="tier-card"><div class="label">Enterprise</div><div class="value">{fmt_int(totals["enterprise"])}</div></div>
    </div>
    <div class="chart-panel">
      <div class="chart-title">Cumulative Trends by Plan</div>
      <div class="chart-wrap"><canvas id="trendChart"></canvas></div>
    </div>
  </div>

  <div class="panel">
    <h2>Segment breakdown (joined room accounts)</h2>
    <p class="note">Accounts created after July 13 crossed with Reservations Room Accounts Overview by Account ID.</p>
    <table>
      <thead>
        <tr><th>Segment</th><th>Total</th><th>Lite</th><th>Pro</th><th>Enterprise</th></tr>
      </thead>
      <tbody>
        {segment_rows}
        <tr>
          <td><strong>TOTAL</strong></td>
          <td><strong>{fmt_int(agg["matched"])}</strong></td>
          <td><strong>{fmt_int(totals["lite"])}</strong></td>
          <td><strong>{fmt_int(totals["pro"])}</strong></td>
          <td><strong>{fmt_int(totals["enterprise"])}</strong></td>
        </tr>
      </tbody>
    </table>
  </div>

  <script>
    new Chart(document.getElementById("trendChart"), {{
      type: "bar",
      data: {{
        labels: {json.dumps(weeks)},
        datasets: [
          {{ label: "Lite", data: {json.dumps(lite)}, backgroundColor: "{LITE}", stack: "plans" }},
          {{ label: "Pro", data: {json.dumps(pro)}, backgroundColor: "{PRO}", stack: "plans" }},
          {{ label: "Enterprise", data: {json.dumps(ent)}, backgroundColor: "{ENTERPRISE}", stack: "plans" }}
        ]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ position: "top", labels: {{ boxWidth: 12, color: "{MUTED}" }} }} }},
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
            suggestedMax: Math.max(10, Math.ceil({agg["total"]} * 1.15) || 10),
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


def main() -> None:
    cfg = load_config()
    created_path = ROOT / cfg["created_accounts_csv"]
    room_path = ROOT / cfg["room_accounts_csv"]
    chart_start = datetime.strptime(cfg["chart_start"], "%Y-%m-%d")
    title = cfg.get("title", "Room Migration Progress")
    total_label = cfg.get("total_label", "Total Accounts Created")

    created = load_created_accounts(created_path)
    room = load_room_accounts(room_path)
    joined = join_accounts(created, room)
    agg = aggregate(joined, chart_start)
    week_label = cfg.get("report_week_label") or agg["auto_week_label"]

    chart_path = ROOT / cfg["output_chart"]
    html_path = ROOT / cfg["output_html"]
    pptx_path = ROOT / cfg["output_pptx"]
    full_slide_png = ROOT / "exports" / "room-migration-progress.png"
    consolidated_csv = ROOT / cfg["output_consolidated_csv"]
    segment_csv = ROOT / cfg["output_segment_summary"]

    write_consolidated_csv(joined, consolidated_csv)
    write_segment_summary(agg, segment_csv)
    draw_chart_only(agg, chart_path)
    draw_dashboard_image(agg, week_label, title, total_label, full_slide_png)
    build_html(agg, week_label, title, total_label, html_path)
    build_pptx(agg, week_label, title, total_label, chart_path, pptx_path)

    print(f"Created accounts file: {len(created)}")
    print(f"Room accounts file: {len(room)}")
    print(f"Matched (created ∩ room): {agg['matched']}")
    print(f"  Lite: {agg['totals']['lite']}")
    print(f"  Pro: {agg['totals']['pro']} (Mid Market: {agg['pro_mid_market']})")
    print(f"  Enterprise: {agg['totals']['enterprise']}")
    print("Segment breakdown:")
    for seg, n in sorted(agg["segment_counts"].items(), key=lambda x: (-x[1], x[0])):
        print(f"  {seg}: {n}")
    print(f"Week label: {week_label}")
    print(f"Wrote {consolidated_csv}")
    print(f"Wrote {segment_csv}")
    print(f"Wrote {html_path}")
    print(f"Wrote {pptx_path}")
    print(f"Wrote {full_slide_png}")
    print(f"Wrote {chart_path}")


if __name__ == "__main__":
    main()

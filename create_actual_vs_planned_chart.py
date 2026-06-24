#!/usr/bin/env python3
"""Generate Actual vs Planned migration line chart (PNG + editable XLSX for Google Sheets)."""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import xlsxwriter

from migration_actual_vs_planned_data import (
    ACTUAL_WEEKLY,
    PLANNED_CUMULATIVE,
    FINAL_TARGET,
    CURRENT_AS_OF,
    CURRENT_CUMULATIVE,
    RECENT_DAILY_ACCOUNTS,
    MIGRATION_PHASES,
    THROUGHPUT_RATES,
    FULL_PROGRAM_ACCOUNTS,
    PROGRAM_END_DATE,
    build_chart_rows,
    build_projection_rows,
    phase_cumulative_accounts,
    format_duration,
    processing_minutes_per_day,
    weekly_total,
)

COLOR_ACTUAL = "#2E9E5B"
COLOR_PLANNED = "#1B4F8A"
COLOR_BG = "#F5F0E8"
COLOR_TEXT = "#1E293B"
COLOR_GOAL = "#9CA3AF"


def parse_date(s):
    return datetime.strptime(s, "%m/%d/%Y")


def build_series():
    rows = build_chart_rows()

    actual_dates = [parse_date(r["week"]) for r in rows if r["cumulative_actual"] != ""]
    actual_vals = [r["cumulative_actual"] for r in rows if r["cumulative_actual"] != ""]

    planned_dates = [parse_date(p["week"]) for p in PLANNED_CUMULATIVE]
    planned_vals = [p["planned_total"] for p in PLANNED_CUMULATIVE]

    return rows, actual_dates, actual_vals, planned_dates, planned_vals


def create_png(output_path="/workspace/migration_actual_vs_planned_chart.png"):
    rows, actual_dates, actual_vals, planned_dates, planned_vals = build_series()

    fig, ax = plt.subplots(figsize=(14, 7), facecolor=COLOR_BG)
    ax.set_facecolor(COLOR_BG)

    ax.plot(actual_dates, actual_vals, marker="o", markersize=8, linewidth=2.5,
            color=COLOR_ACTUAL, label="Actual (cumulative)", zorder=5)
    ax.plot(planned_dates, planned_vals, marker="s", markersize=7, linewidth=2,
            linestyle="--", color=COLOR_PLANNED, label="Planned (cumulative)", zorder=4)

    ax.axhline(y=FINAL_TARGET, color=COLOR_GOAL, linestyle=":", linewidth=1.5,
               alpha=0.8, label=f"Goal ({FINAL_TARGET:,})")

    ax.fill_between(actual_dates, actual_vals, alpha=0.1, color=COLOR_ACTUAL)

    ax.set_title("Room Migration Progress — Actual vs Planned", fontsize=18,
                 fontweight="bold", color=COLOR_TEXT, pad=16)
    ax.set_xlabel("Week Starting", fontsize=11, color=COLOR_TEXT)
    ax.set_ylabel("Cumulative Accounts Migrated", fontsize=11, color=COLOR_TEXT)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=45, ha="right")
    ax.legend(loc="upper left", framealpha=0.95, fontsize=10)

    # Annotate latest actual point
    if actual_vals:
        ax.annotate(
            f"{actual_vals[-1]:,}",
            (actual_dates[-1], actual_vals[-1]),
            textcoords="offset points", xytext=(8, 8),
            fontsize=10, fontweight="bold", color=COLOR_ACTUAL,
        )

    fig.text(0.08, 0.02, "Guesty", fontsize=13, fontweight="bold",
             color=COLOR_PLANNED, style="italic")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=COLOR_BG)
    print(f"Saved PNG chart to {output_path}")


def create_xlsx(output_path="/workspace/migration_actual_vs_planned.xlsx"):
    rows = build_chart_rows()

    workbook = xlsxwriter.Workbook(output_path)

    # --- Data sheet ---
    ws_data = workbook.add_worksheet("Data")
    ws_data.set_column("A:A", 14)
    ws_data.set_column("B:E", 18)

    header_fmt = workbook.add_format({
        "bold": True, "bg_color": "#1B4F8A", "font_color": "white",
        "border": 1, "align": "center",
    })
    num_fmt = workbook.add_format({"num_format": "#,##0", "border": 1})
    text_fmt = workbook.add_format({"border": 1})
    pct_fmt = workbook.add_format({"num_format": "+#,##0;-#,##0", "border": 1})

    headers = [
        "Week Starting", "Weekly Actual", "Cumulative Actual",
        "Planned Cumulative", "Variance (Actual - Planned)",
    ]
    for col, h in enumerate(headers):
        ws_data.write(0, col, h, header_fmt)

    for i, row in enumerate(rows, start=1):
        ws_data.write(i, 0, row["week"], text_fmt)
        if row["weekly_actual"] != "":
            ws_data.write(i, 1, row["weekly_actual"], num_fmt)
        else:
            ws_data.write(i, 1, "", text_fmt)
        if row["cumulative_actual"] != "":
            ws_data.write(i, 2, row["cumulative_actual"], num_fmt)
        else:
            ws_data.write(i, 2, "", text_fmt)
        if row["planned_cumulative"] != "":
            ws_data.write(i, 3, row["planned_cumulative"], num_fmt)
        else:
            ws_data.write(i, 3, "", text_fmt)
        if row["variance"] != "":
            ws_data.write(i, 4, row["variance"], pct_fmt)
        else:
            ws_data.write(i, 4, "", text_fmt)

    # --- Weekly detail sheet (segment breakdown) ---
    ws_detail = workbook.add_worksheet("Weekly Detail")
    ws_detail.set_column("A:A", 14)
    ws_detail.set_column("B:E", 14)
    detail_headers = ["Week Starting", "Lite", "Pro", "Enterprise", "Weekly Total"]
    for col, h in enumerate(detail_headers):
        ws_detail.write(0, col, h, header_fmt)
    for i, entry in enumerate(ACTUAL_WEEKLY, start=1):
        ws_detail.write(i, 0, entry["week"], text_fmt)
        ws_detail.write(i, 1, entry["lite"], num_fmt)
        ws_detail.write(i, 2, entry["pro"], num_fmt)
        ws_detail.write(i, 3, entry["enterprise"], num_fmt)
        ws_detail.write(i, 4, weekly_total(entry), num_fmt)

    # --- Migration Phases sheet ---
    ws_phases = workbook.add_worksheet("Migration Phases")
    ws_phases.set_column("A:A", 14)
    ws_phases.set_column("B:C", 12)
    ws_phases.set_column("D:D", 8)
    ws_phases.set_column("E:H", 16)
    ws_phases.set_column("I:K", 14)

    phase_headers = [
        "Phase", "Start", "End", "Days", "Avg Res/Day", "Total Reservations",
        "Accounts (Phase)", "Avg Res/Account",
        "Processing @ 900/min", "Processing @ 8,024/min", "Processing @ 14,000/min",
    ]
    for col, h in enumerate(phase_headers):
        ws_phases.write(0, col, h, header_fmt)

    for i, phase in enumerate(MIGRATION_PHASES, start=1):
        ws_phases.write(i, 0, phase["phase"], text_fmt)
        ws_phases.write(i, 1, phase["start"], text_fmt)
        ws_phases.write(i, 2, phase["end"], text_fmt)
        ws_phases.write(i, 3, phase["days"], num_fmt)
        ws_phases.write(i, 4, phase["avg_res_per_day"], num_fmt)
        ws_phases.write(i, 5, phase["total_reservations"], num_fmt)
        ws_phases.write(i, 6, phase["accounts_in_phase"], num_fmt)
        ws_phases.write(i, 7, phase["avg_res_per_account"], num_fmt)
        for j, rate_info in enumerate(THROUGHPUT_RATES):
            mins = processing_minutes_per_day(phase["avg_res_per_day"], rate_info["rate"])
            ws_phases.write(i, 8 + j, format_duration(mins), text_fmt)

    total_row = len(MIGRATION_PHASES) + 1
    ws_phases.write(total_row, 0, "TOTAL", header_fmt)
    ws_phases.write(total_row, 3, sum(p["days"] for p in MIGRATION_PHASES), num_fmt)
    ws_phases.write(total_row, 5, sum(p["total_reservations"] for p in MIGRATION_PHASES), num_fmt)
    ws_phases.write(total_row, 6, sum(p["accounts_in_phase"] for p in MIGRATION_PHASES), num_fmt)

    # --- Phase Timeline sheet (cumulative account milestones) ---
    ws_timeline = workbook.add_worksheet("Phase Timeline")
    ws_timeline.set_column("A:D", 22)
    timeline_headers = ["Phase", "End Date", "Accounts This Phase", "Cumulative Accounts"]
    for col, h in enumerate(timeline_headers):
        ws_timeline.write(0, col, h, header_fmt)
    milestones = phase_cumulative_accounts()
    for i, m in enumerate(milestones, start=1):
        ws_timeline.write(i, 0, m["phase"], text_fmt)
        ws_timeline.write(i, 1, m["end_date"], text_fmt)
        ws_timeline.write(i, 2, m["phase_accounts"], num_fmt)
        ws_timeline.write(i, 3, m["cumulative_accounts"], num_fmt)

    ws_timeline.write(len(milestones) + 2, 0, "Current status (as of " + CURRENT_AS_OF + ")", header_fmt)
    ws_timeline.write(len(milestones) + 2, 1, CURRENT_AS_OF, text_fmt)
    ws_timeline.write(len(milestones) + 2, 3, CURRENT_CUMULATIVE, num_fmt)
    ws_timeline.write(len(milestones) + 3, 0, "Recent run rate (accounts/day)", text_fmt)
    ws_timeline.write(len(milestones) + 3, 3, RECENT_DAILY_ACCOUNTS, num_fmt)

    # --- Projections sheet ---
    ws_proj = workbook.add_worksheet("Projections")
    ws_proj.set_column("A:A", 32)
    ws_proj.set_column("B:H", 16)
    proj_headers = [
        "Goal", "Target", "Scenario", "Accounts/Day",
        "Days Remaining", "Projected Finish", "Planned Finish", "Days Ahead of Plan",
    ]
    for col, h in enumerate(proj_headers):
        ws_proj.write(0, col, h, header_fmt)

    projections = build_projection_rows()
    ahead_fmt = workbook.add_format({"num_format": "+#,##0;-#,##0", "border": 1, "font_color": "#2E9E5B"})
    for i, row in enumerate(projections, start=1):
        ws_proj.write(i, 0, row["goal"], text_fmt)
        ws_proj.write(i, 1, row["target"], num_fmt)
        ws_proj.write(i, 2, row["scenario"], text_fmt)
        ws_proj.write(i, 3, row["daily_rate"], num_fmt)
        if row["days_remaining"] != "":
            ws_proj.write(i, 4, row["days_remaining"], num_fmt)
        else:
            ws_proj.write(i, 4, "", text_fmt)
        ws_proj.write(i, 5, row["projected_finish"], text_fmt)
        ws_proj.write(i, 6, row["planned_finish"], text_fmt)
        if row["days_ahead_of_plan"] != "":
            fmt = ahead_fmt if row["days_ahead_of_plan"] >= 0 else pct_fmt
            ws_proj.write(i, 7, row["days_ahead_of_plan"], fmt)
        else:
            ws_proj.write(i, 7, "", text_fmt)

    note_fmt = workbook.add_format({"italic": True, "font_color": "#64748B", "text_wrap": True})
    ws_proj.write(len(projections) + 2, 0,
                  "Days Ahead of Plan = positive means finishing BEFORE planned date. "
                  f"Based on {CURRENT_CUMULATIVE:,} accounts as of {CURRENT_AS_OF}.",
                  note_fmt)
    ws_proj.write(len(projections) + 3, 0,
                  "Note: Full program projection assumes constant account pace. Later phases (Steady Growth → Full Speed) "
                  "require 2–4× more reservations per account; reservation throughput (900 vs 8,024 vs 14,000/min) "
                  "may constrain finish date even if account onboarding stays ahead.",
                  note_fmt)

    # --- Chart sheet ---
    ws_chart = workbook.add_worksheet("Chart")
    ws_chart.hide_gridlines(2)

    chart = workbook.add_chart({"type": "line"})
    last_data_row = len(rows)

    chart.add_series({
        "name": "Actual (cumulative)",
        "categories": ["Data", 1, 0, last_data_row, 0],
        "values": ["Data", 1, 2, last_data_row, 2],
        "line": {"color": COLOR_ACTUAL, "width": 2.5},
        "marker": {"type": "circle", "size": 7, "fill": {"color": COLOR_ACTUAL}},
    })
    chart.add_series({
        "name": "Planned (cumulative)",
        "categories": ["Data", 1, 0, last_data_row, 0],
        "values": ["Data", 1, 3, last_data_row, 3],
        "line": {"color": COLOR_PLANNED, "width": 2, "dash_type": "dash"},
        "marker": {"type": "square", "size": 6, "fill": {"color": COLOR_PLANNED}},
    })

    chart.set_title({"name": "Room Migration Progress — Actual vs Planned"})
    chart.set_x_axis({"name": "Week Starting", "label_position": "low"})
    chart.set_y_axis({"name": "Cumulative Accounts Migrated", "major_gridlines": {"visible": True}})
    chart.set_legend({"position": "top"})
    chart.set_size({"width": 900, "height": 520})

    ws_chart.insert_chart("B2", chart)

    # Instructions
    instr_fmt = workbook.add_format({"italic": True, "font_color": "#64748B", "text_wrap": True})
    ws_chart.write("B28",
                   "To use in Google Sheets: Upload to Google Drive → Open with Google Sheets. "
                   "Edit Data / Migration Phases / Projections tabs. Tabs: Data, Weekly Detail, "
                   "Migration Phases, Phase Timeline, Projections, Chart.",
                   instr_fmt)

    workbook.close()
    print(f"Saved editable spreadsheet to {output_path}")


def print_summary():
    rows = build_chart_rows()
    actual_rows = [r for r in rows if r["cumulative_actual"] != ""]
    latest = actual_rows[-1]
    print("\n=== Actual vs Planned Summary ===")
    print(f"Latest week:        {latest['week']}")
    print(f"Cumulative actual:  {latest['cumulative_actual']:,}")
    if latest["planned_cumulative"] != "":
        print(f"Planned target:     {latest['planned_cumulative']:,}")
        print(f"Variance:           {latest['variance']:+,} ({latest['variance']/latest['planned_cumulative']*100:+.1f}%)")
    print(f"Near-term goal:     {FINAL_TARGET:,}")
    print(f"Full program:       {FULL_PROGRAM_ACCOUNTS:,} by {PROGRAM_END_DATE}")
    print(f"Recent pace:        {RECENT_DAILY_ACCOUNTS} accounts/day")

    print("\n=== Projected Finish (current pace) ===")
    for row in build_projection_rows():
        if row["scenario"] == "Current pace":
            ahead = row["days_ahead_of_plan"]
            ahead_str = f"{ahead} days ahead" if ahead >= 0 else f"{abs(ahead)} days behind"
            print(f"  {row['goal']}: {row['projected_finish']} ({ahead_str} vs plan)")


if __name__ == "__main__":
    print_summary()
    create_png()
    create_xlsx()

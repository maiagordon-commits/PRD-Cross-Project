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
    build_chart_rows,
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
                   "To use in Google Sheets: Upload this file to Google Drive → Open with Google Sheets. "
                   "Edit values on the Data tab; recreate the chart via Insert → Chart if needed.",
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
    print(f"Final goal:         {FINAL_TARGET:,}")


if __name__ == "__main__":
    print_summary()
    create_png()
    create_xlsx()

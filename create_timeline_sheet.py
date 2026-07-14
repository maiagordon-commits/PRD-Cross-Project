#!/usr/bin/env python3
"""Generate unified timeline spreadsheet for Google Sheets."""

import csv
import os

import xlsxwriter

from timeline_data import (
    OPEN_API_TIMELINE_START,
    OPEN_API_TIMELINE_END,
    OPEN_API_MILESTONES,
    build_master_timeline,
    build_reservation_phase_rows,
    build_weekly_migration_rows,
)
from migration_actual_vs_planned_data import build_chart_rows, MIGRATION_PHASES

OUTPUT_XLSX = "/workspace/guesty_timeline.xlsx"
OUTPUT_CSV = "/workspace/guesty_timeline.csv"


def write_csv(rows, path):
    fieldnames = [
        "Program", "Track", "Milestone", "Description", "Date Label",
        "Start Date", "End Date", "Status", "Target Accounts", "Actual Accounts", "Variance",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "Program": row["program"],
                "Track": row["track"],
                "Milestone": row["milestone"],
                "Description": row["description"],
                "Date Label": row["date_label"],
                "Start Date": row["start_date"],
                "End Date": row["end_date"],
                "Status": row["status"],
                "Target Accounts": row.get("target_accounts", ""),
                "Actual Accounts": row.get("actual_accounts", ""),
                "Variance": row.get("variance", ""),
            })
    print(f"Saved CSV to {path}")


def create_xlsx(path=OUTPUT_XLSX):
    master = build_master_timeline()
    workbook = xlsxwriter.Workbook(path)

    header_fmt = workbook.add_format({
        "bold": True, "bg_color": "#1B4F8A", "font_color": "white",
        "border": 1, "align": "center", "text_wrap": True,
    })
    date_fmt = workbook.add_format({"num_format": "yyyy-mm-dd", "border": 1})
    text_fmt = workbook.add_format({"border": 1, "text_wrap": True})
    num_fmt = workbook.add_format({"num_format": "#,##0", "border": 1})
    var_fmt = workbook.add_format({"num_format": "+#,##0;-#,##0", "border": 1})
    status_actual = workbook.add_format({"border": 1, "bg_color": "#E8F5EE", "font_color": "#166534"})
    status_planned = workbook.add_format({"border": 1, "bg_color": "#EFF6FF", "font_color": "#1B4F8A"})
    title_fmt = workbook.add_format({"bold": True, "font_size": 16, "font_color": "#1B4F8A"})
    note_fmt = workbook.add_format({"italic": True, "font_color": "#64748B", "text_wrap": True})

    # --- Master Timeline ---
    ws = workbook.add_worksheet("Timeline")
    ws.set_column("A:A", 18)
    ws.set_column("B:B", 14)
    ws.set_column("C:C", 36)
    ws.set_column("D:D", 42)
    ws.set_column("E:E", 16)
    ws.set_column("F:G", 12)
    ws.set_column("H:H", 10)
    ws.set_column("I:K", 14)

    ws.write("A1", "Guesty Program Timeline", title_fmt)
    ws.write("A2", f"Open API: {OPEN_API_TIMELINE_START} → {OPEN_API_TIMELINE_END} · Reservation Migration: Jun–Dec 2026", note_fmt)

    headers = [
        "Program", "Track", "Milestone", "Description", "Date Label",
        "Start Date", "End Date", "Status", "Target Accounts", "Actual Accounts", "Variance",
    ]
    for col, h in enumerate(headers):
        ws.write(3, col, h, header_fmt)

    for i, row in enumerate(master, start=4):
        ws.write(i, 0, row["program"], text_fmt)
        ws.write(i, 1, row["track"], text_fmt)
        ws.write(i, 2, row["milestone"], text_fmt)
        ws.write(i, 3, row["description"], text_fmt)
        ws.write(i, 4, row["date_label"], text_fmt)
        ws.write(i, 5, row["start_date"], date_fmt)
        ws.write(i, 6, row["end_date"], date_fmt)
        status_fmt = status_actual if row["status"] == "Actual" else status_planned
        ws.write(i, 7, row["status"], status_fmt)
        if row.get("target_accounts", "") != "":
            ws.write(i, 8, row["target_accounts"], num_fmt)
        else:
            ws.write(i, 8, "", text_fmt)
        if row.get("actual_accounts", "") != "":
            ws.write(i, 9, row["actual_accounts"], num_fmt)
        else:
            ws.write(i, 9, "", text_fmt)
        if row.get("variance", "") != "":
            ws.write(i, 10, row["variance"], var_fmt)
        else:
            ws.write(i, 10, "", text_fmt)

    last_row = 3 + len(master)

    # Gantt-style bar chart for items with date ranges
    chart = workbook.add_chart({"type": "bar", "subtype": "stacked"})
    # Use reservation phases + open api for visual timeline
    phase_rows = build_reservation_phase_rows()
    gantt_start = 4 + len(master) + 2
    ws.write(gantt_start - 1, 0, "Gantt Data (for chart below)", title_fmt)
    gantt_headers = ["Milestone", "Start Date", "End Date", "Duration (days)"]
    for col, h in enumerate(gantt_headers):
        ws.write(gantt_start, col, h, header_fmt)

    gantt_items = phase_rows + [
        {**m, "days": 1} for m in OPEN_API_MILESTONES
    ]
    for i, item in enumerate(gantt_items, start=gantt_start + 1):
        ws.write(i, 0, item["milestone"], text_fmt)
        ws.write(i, 1, item["start_date"], date_fmt)
        ws.write(i, 2, item["end_date"], date_fmt)
        days = item.get("days")
        if not days:
            from datetime import datetime
            s = datetime.strptime(item["start_date"], "%Y-%m-%d")
            e = datetime.strptime(item["end_date"], "%Y-%m-%d")
            days = max(1, (e - s).days + 1)
        ws.write(i, 3, days, num_fmt)

    gantt_last = gantt_start + len(gantt_items)
    chart.add_series({
        "name": "Duration",
        "categories": ["Timeline", gantt_start + 1, 0, gantt_last, 0],
        "values": ["Timeline", gantt_start + 1, 3, gantt_last, 3],
        "fill": {"color": "#2E9E5B"},
    })
    chart.set_title({"name": "Program Timeline (Gantt)"})
    chart.set_x_axis({"name": "Days"})
    chart.set_y_axis({"reverse": True})
    chart.set_legend({"none": True})
    chart.set_size({"width": 900, "height": 400})
    ws.insert_chart(gantt_last + 2, 0, chart)

    ws.write(gantt_last + 18, 0,
             "Import to Google Sheets: Upload this file to Google Drive → Open with Google Sheets. "
             "Or use File → Import → Upload in sheets.google.com.",
             note_fmt)

    # --- Open API tab ---
    ws_api = workbook.add_worksheet("Open API")
    ws_api.set_column("A:F", 22)
    api_headers = ["Track", "Date Label", "Start", "End", "Milestone", "Description"]
    for col, h in enumerate(api_headers):
        ws_api.write(0, col, h, header_fmt)
    for i, m in enumerate(OPEN_API_MILESTONES, start=1):
        ws_api.write(i, 0, m["track"], text_fmt)
        ws_api.write(i, 1, m["date_label"], text_fmt)
        ws_api.write(i, 2, m["start_date"], date_fmt)
        ws_api.write(i, 3, m["end_date"], date_fmt)
        ws_api.write(i, 4, m["milestone"], text_fmt)
        ws_api.write(i, 5, m["description"], text_fmt)

    # --- Weekly Migration tab ---
    ws_weekly = workbook.add_worksheet("Weekly Migration")
    ws_weekly.set_column("A:K", 14)
    weekly_headers = [
        "Week", "Milestone", "Status", "Planned Cumulative", "Actual Cumulative", "Variance",
        "Weekly Lite", "Weekly Pro", "Weekly Enterprise", "Weekly Total",
    ]
    for col, h in enumerate(weekly_headers):
        ws_weekly.write(0, col, h, header_fmt)

    chart_rows = build_chart_rows()
    weekly_by_date = {w["start_date"]: w for w in build_weekly_migration_rows()}
    for i, row in enumerate(chart_rows, start=1):
        from datetime import datetime
        iso = datetime.strptime(row["week"], "%m/%d/%Y").strftime("%Y-%m-%d") if row["week"] else ""
        wk = weekly_by_date.get(iso, {})
        ws_weekly.write(i, 0, row["week"], text_fmt)
        ws_weekly.write(i, 1, wk.get("milestone", ""), text_fmt)
        status = "Actual" if row["cumulative_actual"] != "" else "Planned"
        ws_weekly.write(i, 2, status, status_actual if status == "Actual" else status_planned)
        if row["planned_cumulative"] != "":
            ws_weekly.write(i, 3, row["planned_cumulative"], num_fmt)
        if row["cumulative_actual"] != "":
            ws_weekly.write(i, 4, row["cumulative_actual"], num_fmt)
        if row["variance"] != "":
            ws_weekly.write(i, 5, row["variance"], var_fmt)
        for col, key in enumerate(["weekly_lite", "weekly_pro", "weekly_enterprise", "weekly_actual"], start=6):
            if row[key] != "":
                ws_weekly.write(i, col, row[key], num_fmt)

    # --- Reservation Phases tab ---
    ws_phases = workbook.add_worksheet("Reservation Phases")
    ws_phases.set_column("A:H", 16)
    phase_headers = ["Phase", "Start", "End", "Days", "Accounts", "Reservations", "Res/Day", "Res/Account"]
    for col, h in enumerate(phase_headers):
        ws_phases.write(0, col, h, header_fmt)
    for i, p in enumerate(MIGRATION_PHASES, start=1):
        ws_phases.write(i, 0, p["phase"], text_fmt)
        ws_phases.write(i, 1, p["start"], text_fmt)
        ws_phases.write(i, 2, p["end"], text_fmt)
        ws_phases.write(i, 3, p["days"], num_fmt)
        ws_phases.write(i, 4, p["accounts_in_phase"], num_fmt)
        ws_phases.write(i, 5, p["total_reservations"], num_fmt)
        ws_phases.write(i, 6, p["avg_res_per_day"], num_fmt)
        ws_phases.write(i, 7, p["avg_res_per_account"], num_fmt)

    workbook.close()
    print(f"Saved XLSX to {path}")


if __name__ == "__main__":
    master = build_master_timeline()
    write_csv(master, OUTPUT_CSV)
    create_xlsx()
    print(f"\nTimeline entries: {len(master)}")
    print("Programs: Open API, Account Migration, Reservation Migration")

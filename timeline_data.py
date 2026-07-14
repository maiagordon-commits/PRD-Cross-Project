#!/usr/bin/env python3
"""Unified timeline data for Google Sheets export."""

from datetime import datetime

from migration_actual_vs_planned_data import (
    MIGRATION_PHASES,
    FINAL_TARGET,
    FULL_PROGRAM_ACCOUNTS,
    PROGRAM_END_DATE,
    CURRENT_AS_OF,
    CURRENT_CUMULATIVE,
    PLANNED_CUMULATIVE,
    build_chart_rows,
)
from migration_schedule_data import WEEKLY_SCHEDULE

# Open API milestones (Jul 2026 → Mar 2027)
OPEN_API_TIMELINE_START = "2026-07-01"
OPEN_API_TIMELINE_END = "2027-03-27"

OPEN_API_MILESTONES = [
    {
        "program": "Open API",
        "track": "New Users",
        "milestone": "Block API usage by registration date",
        "description": "By registration date, block API usage for new users",
        "date_label": "Early Q3",
        "start_date": "2026-07-01",
        "end_date": "2026-07-15",
        "sort_date": "2026-07-01",
        "status": "Planned",
    },
    {
        "program": "Open API",
        "track": "Existing Users",
        "milestone": "Automated email to migrated users",
        "description": "Start sending automated email to migrated users",
        "date_label": "Beginning of Sept",
        "start_date": "2026-09-01",
        "end_date": "2026-09-07",
        "sort_date": "2026-09-01",
        "status": "Planned",
    },
    {
        "program": "Open API",
        "track": "Existing Users",
        "milestone": "Communication to all users",
        "description": "Sending communication to all users",
        "date_label": "End of September",
        "start_date": "2026-09-22",
        "end_date": "2026-09-30",
        "sort_date": "2026-09-22",
        "status": "Planned",
    },
    {
        "program": "Open API",
        "track": "Existing Users",
        "milestone": "Deprecation of old Open API (OAPI)",
        "description": "End of deprecation period for old OAPI",
        "date_label": "EO March 27",
        "start_date": "2027-03-27",
        "end_date": "2027-03-27",
        "sort_date": "2027-03-27",
        "status": "Planned",
    },
]

ACCOUNT_MILESTONES = [
    {
        "program": "Account Migration",
        "track": "Near-term",
        "milestone": f"Near-term goal ({FINAL_TARGET:,} accounts)",
        "description": "Target cumulative migrated accounts",
        "date_label": "7/13/2026",
        "start_date": "2026-07-13",
        "end_date": "2026-07-13",
        "sort_date": "2026-07-13",
        "status": "Planned",
        "target_accounts": FINAL_TARGET,
    },
    {
        "program": "Account Migration",
        "track": "Full Program",
        "milestone": f"Full program (~{FULL_PROGRAM_ACCOUNTS:,} accounts)",
        "description": "End of reservation migration program",
        "date_label": PROGRAM_END_DATE,
        "start_date": "2026-12-31",
        "end_date": "2026-12-31",
        "sort_date": "2026-12-31",
        "status": "Planned",
        "target_accounts": FULL_PROGRAM_ACCOUNTS,
    },
]


def parse_iso(s):
    return datetime.strptime(s, "%Y-%m-%d")


def parse_us(s):
    return datetime.strptime(s, "%m/%d/%Y")


def week_to_iso(week_label):
    """Convert 'Jun 8' style labels to ISO start date (2026)."""
    mapping = {
        "Jun 1": "2026-06-01",
        "Jun 8": "2026-06-08",
        "Jun 15": "2026-06-15",
        "Jun 22": "2026-06-22",
        "Jun 29": "2026-06-29",
        "Jul 6": "2026-07-06",
    }
    return mapping.get(week_label, "")


def build_reservation_phase_rows():
    rows = []
    cumulative = 0
    for phase in MIGRATION_PHASES:
        cumulative += phase["accounts_in_phase"]
        start_iso = parse_us(phase["start"]).strftime("%Y-%m-%d")
        end_iso = parse_us(phase["end"]).strftime("%Y-%m-%d")
        rows.append({
            "program": "Reservation Migration",
            "track": phase["phase"],
            "milestone": f"{phase['phase']} phase",
            "description": (
                f"{phase['accounts_in_phase']:,} accounts · "
                f"{phase['total_reservations']:,} reservations · "
                f"{phase['avg_res_per_day']:,} res/day"
            ),
            "date_label": f"{phase['start']} – {phase['end']}",
            "start_date": start_iso,
            "end_date": end_iso,
            "sort_date": start_iso,
            "status": "Planned",
            "target_accounts": cumulative,
            "days": phase["days"],
        })
    return rows


def build_weekly_migration_rows():
    rows = []
    chart_rows = {r["week"]: r for r in build_chart_rows()}
    for entry in WEEKLY_SCHEDULE:
        iso = week_to_iso(entry["week"])
        full_week = f"{entry['week']}/2026".replace("Jun ", "6/").replace("Jul ", "7/")
        # match chart row key like 6/8/2026
        chart_key = None
        for k in chart_rows:
            if k.startswith(entry["week"].replace("Jun ", "6/").replace("Jul ", "7/")):
                chart_key = k
                break
        chart = chart_rows.get(chart_key, {}) if chart_key else {}
        actual = chart.get("cumulative_actual", "")
        planned = entry["target_total"]
        variance = (actual - planned) if actual != "" and planned else ""
        status = "Actual" if entry["status"] == "actual" or actual != "" else "Planned"
        rows.append({
            "program": "Account Migration",
            "track": "Weekly",
            "milestone": entry["milestone"],
            "description": (
                f"{entry['week_label']} · Planned cumulative: {planned:,}"
                + (f" · Actual: {actual:,}" if actual != "" else "")
            ),
            "date_label": entry["week"],
            "start_date": iso,
            "end_date": iso,
            "sort_date": iso,
            "status": status,
            "target_accounts": planned,
            "actual_accounts": actual if actual != "" else "",
            "variance": variance if variance != "" else "",
        })
    return rows


def build_master_timeline():
    """All milestones sorted chronologically."""
    rows = []
    rows.extend(OPEN_API_MILESTONES)
    rows.extend(build_reservation_phase_rows())
    rows.extend(build_weekly_migration_rows())
    rows.extend(ACCOUNT_MILESTONES)

    # Current status marker
    rows.append({
        "program": "Account Migration",
        "track": "Status",
        "milestone": "Current cumulative (as of snapshot)",
        "description": f"{CURRENT_CUMULATIVE:,} accounts migrated",
        "date_label": CURRENT_AS_OF,
        "start_date": parse_us(CURRENT_AS_OF).strftime("%Y-%m-%d"),
        "end_date": parse_us(CURRENT_AS_OF).strftime("%Y-%m-%d"),
        "sort_date": parse_us(CURRENT_AS_OF).strftime("%Y-%m-%d"),
        "status": "Actual",
        "target_accounts": CURRENT_CUMULATIVE,
    })

    rows.sort(key=lambda r: r["sort_date"])
    return rows

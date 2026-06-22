#!/usr/bin/env python3
"""Actual vs Planned migration data.

Edit ACTUAL_WEEKLY and PLANNED_CUMULATIVE below to update the chart.
"""

# Weekly actual migrations from Room_Migration_Progress sheet (screenshot)
ACTUAL_WEEKLY = [
    {"week": "4/13/2026", "lite": 5, "pro": 0, "enterprise": 0},
    {"week": "4/20/2026", "lite": 11, "pro": 4, "enterprise": 0},
    {"week": "4/27/2026", "lite": 28, "pro": 11, "enterprise": 0},
    {"week": "5/4/2026", "lite": 6, "pro": 3, "enterprise": 0},
    {"week": "5/11/2026", "lite": 11, "pro": 8, "enterprise": 0},
    {"week": "5/18/2026", "lite": 23, "pro": 16, "enterprise": 0},
    {"week": "5/25/2026", "lite": 159, "pro": 98, "enterprise": 0},
    {"week": "6/1/2026", "lite": 109, "pro": 136, "enterprise": 0},
    {"week": "6/8/2026", "lite": 424, "pro": 571, "enterprise": 9},
    {"week": "6/15/2026", "lite": 776, "pro": 1159, "enterprise": 9},
]

# Planned cumulative targets from Reservation Migration Plan canvas
PLANNED_CUMULATIVE = [
    {"week": "6/1/2026", "planned_total": 500},
    {"week": "6/8/2026", "planned_total": 1097},
    {"week": "6/15/2026", "planned_total": 2650},
    {"week": "6/22/2026", "planned_total": 4200},
    {"week": "6/29/2026", "planned_total": 5800},
    {"week": "7/6/2026", "planned_total": 7500},
]

FINAL_TARGET = 8500


def weekly_total(row):
    return row["lite"] + row["pro"] + row["enterprise"]


def build_chart_rows():
    """Merge actual and planned into rows for chart/spreadsheet."""
    planned_map = {p["week"]: p["planned_total"] for p in PLANNED_CUMULATIVE}
    cumulative = 0
    rows = []

    for entry in ACTUAL_WEEKLY:
        weekly = weekly_total(entry)
        cumulative += weekly
        rows.append({
            "week": entry["week"],
            "weekly_actual": weekly,
            "cumulative_actual": cumulative,
            "planned_cumulative": planned_map.get(entry["week"], ""),
            "variance": cumulative - planned_map[entry["week"]] if entry["week"] in planned_map else "",
        })

    # Append future planned-only weeks
    actual_weeks = {r["week"] for r in ACTUAL_WEEKLY}
    for p in PLANNED_CUMULATIVE:
        if p["week"] not in actual_weeks:
            rows.append({
                "week": p["week"],
                "weekly_actual": "",
                "cumulative_actual": "",
                "planned_cumulative": p["planned_total"],
                "variance": "",
            })

    return rows

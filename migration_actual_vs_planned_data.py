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
FULL_PROGRAM_ACCOUNTS = 35001  # sum of accounts across all 4 phases
PROGRAM_END_DATE = "12/31/2026"
CURRENT_AS_OF = "6/15/2026"
CURRENT_CUMULATIVE = 3576  # cumulative actual as of CURRENT_AS_OF

# Recent run rate (accounts/day) derived from last full week of actuals
RECENT_WEEKLY_ACCOUNTS = 1944  # week of 6/15/2026
RECENT_DAILY_ACCOUNTS = round(RECENT_WEEKLY_ACCOUNTS / 7, 1)

# Reservation migration phases (Jun 15 – Dec 31)
MIGRATION_PHASES = [
    {
        "phase": "Ramp-up",
        "start": "6/15/2026",
        "end": "8/3/2026",
        "days": 50,
        "avg_res_per_day": 142_000,
        "total_reservations": 7_090_000,
        "accounts_in_phase": 11_509,
        "avg_res_per_account": 616,
    },
    {
        "phase": "Steady Growth",
        "start": "8/4/2026",
        "end": "9/22/2026",
        "days": 50,
        "avg_res_per_day": 227_200,
        "total_reservations": 11_360_000,
        "accounts_in_phase": 8_513,
        "avg_res_per_account": 1_335,
    },
    {
        "phase": "Acceleration",
        "start": "9/23/2026",
        "end": "11/11/2026",
        "days": 50,
        "avg_res_per_day": 312_800,
        "total_reservations": 15_640_000,
        "accounts_in_phase": 7_689,
        "avg_res_per_account": 2_034,
    },
    {
        "phase": "Full Speed",
        "start": "11/12/2026",
        "end": "12/31/2026",
        "days": 50,
        "avg_res_per_day": 398_200,
        "total_reservations": 19_910_000,
        "accounts_in_phase": 7_290,
        "avg_res_per_account": 2_731,
    },
]

THROUGHPUT_RATES = [
    {"label": "900/min", "rate": 900},
    {"label": "8,024/min", "rate": 8024},
    {"label": "14,000/min", "rate": 14000},
]

MILESTONE_GOALS = [
    {"name": "Near-term goal (8,500 accounts)", "target": FINAL_TARGET, "planned_finish": "7/13/2026"},
    {"name": "End of Ramp-up (11,509 accounts)", "target": 11_509, "planned_finish": "8/3/2026"},
    {"name": "Full program (~35,001 accounts)", "target": FULL_PROGRAM_ACCOUNTS, "planned_finish": PROGRAM_END_DATE},
]


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


def parse_date(s):
    from datetime import datetime
    return datetime.strptime(s, "%m/%d/%Y")


def format_duration(minutes):
    """Format minutes as 'Xh Ym'."""
    minutes = int(round(minutes))
    hours, mins = divmod(minutes, 60)
    if hours and mins:
        return f"{hours}h {mins}m"
    if hours:
        return f"{hours}h"
    return f"{mins}m"


def processing_minutes_per_day(avg_res_per_day, rate_per_min):
    return avg_res_per_day / rate_per_min


def phase_cumulative_accounts():
    """Cumulative account targets at end of each phase (sequential cohorts)."""
    cumulative = 0
    milestones = []
    for phase in MIGRATION_PHASES:
        cumulative += phase["accounts_in_phase"]
        milestones.append({
            "phase": phase["phase"],
            "end_date": phase["end"],
            "cumulative_accounts": cumulative,
            "phase_accounts": phase["accounts_in_phase"],
        })
    return milestones


def projected_finish_date(start_date_str, current_total, target, daily_rate):
    """Project date to reach target at constant daily account rate."""
    from datetime import timedelta
    remaining = target - current_total
    if remaining <= 0:
        return parse_date(start_date_str), 0
    if daily_rate <= 0:
        return None, None
    days_needed = remaining / daily_rate
    finish = parse_date(start_date_str) + timedelta(days=days_needed)
    return finish, days_needed


def build_projection_rows():
    """Build projection scenarios for milestone goals."""
    scenarios = [
        ("Current pace", RECENT_DAILY_ACCOUNTS),
        ("Ramp-up phase pace", MIGRATION_PHASES[0]["accounts_in_phase"] / MIGRATION_PHASES[0]["days"]),
        ("Near-term plan pace", (FINAL_TARGET - CURRENT_CUMULATIVE) / 31),  # ~6/15 to ~7/16
    ]
    rows = []
    for goal in MILESTONE_GOALS:
        for scenario_name, daily_rate in scenarios:
            finish, days = projected_finish_date(
                CURRENT_AS_OF, CURRENT_CUMULATIVE, goal["target"], daily_rate
            )
            planned_finish = goal["planned_finish"]
            ahead_days = ""
            if finish:
                ahead_days = (parse_date(planned_finish) - finish).days
            rows.append({
                "goal": goal["name"],
                "target": goal["target"],
                "scenario": scenario_name,
                "daily_rate": round(daily_rate, 1),
                "days_remaining": round(days, 1) if days is not None else "",
                "projected_finish": finish.strftime("%m/%d/%Y") if finish else "",
                "planned_finish": planned_finish,
                "days_ahead_of_plan": ahead_days,
            })
    return rows

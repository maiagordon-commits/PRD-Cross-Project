#!/usr/bin/env python3
"""Weekly migration schedule and progress data.

Edit WEEKLY_SCHEDULE below to match your Cursor canvas.
Actuals are marked with status='actual'; planned weeks use status='planned'.
"""

# --- Weekly schedule (edit to match canvas) ---
WEEKLY_SCHEDULE = [
    {
        "week": "Jun 1",
        "week_label": "Week 1",
        "milestone": "Migration kickoff",
        "target_total": 500,
        "target_lite": 200,
        "target_smb": 300,
        "target_mid": 0,
        "status": "planned",
    },
    {
        "week": "Jun 8",
        "week_label": "Week 2",
        "milestone": "LITE + SMB rollout",
        "target_total": 1097,
        "target_lite": 380,
        "target_smb": 717,
        "target_mid": 0,
        "status": "actual",
    },
    {
        "week": "Jun 15",
        "week_label": "Week 3",
        "milestone": "Accelerated migration",
        "target_total": 2650,
        "target_lite": 840,
        "target_smb": 1810,
        "target_mid": 0,
        "status": "actual",
    },
    {
        "week": "Jun 22",
        "week_label": "Week 4",
        "milestone": "Mid-Market onboarding",
        "target_total": 4200,
        "target_lite": 1200,
        "target_smb": 2500,
        "target_mid": 500,
        "status": "planned",
    },
    {
        "week": "Jun 29",
        "week_label": "Week 5",
        "milestone": "Full segment coverage",
        "target_total": 5800,
        "target_lite": 1600,
        "target_smb": 3500,
        "target_mid": 700,
        "status": "planned",
    },
    {
        "week": "Jul 6",
        "week_label": "Week 6",
        "milestone": "GA readiness",
        "target_total": 7500,
        "target_lite": 2000,
        "target_smb": 4500,
        "target_mid": 1000,
        "status": "planned",
    },
]

FINAL_TARGET = 8500  # total accounts goal

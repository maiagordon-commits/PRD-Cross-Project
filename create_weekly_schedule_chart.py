#!/usr/bin/env python3
"""Generate weekly migration schedule progress chart."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from migration_schedule_data import FINAL_TARGET, WEEKLY_SCHEDULE

COLOR_LITE = "#1B4F8A"
COLOR_SMB = "#2E9E5B"
COLOR_MID = "#9CA3AF"
COLOR_BG = "#F5F0E8"
COLOR_TEXT = "#1E293B"
COLOR_ACCENT = "#2E9E5B"
COLOR_PLANNED = "#D1D5DB"
COLOR_ACTUAL = "#2E9E5B"

weeks = [w["week"] for w in WEEKLY_SCHEDULE]
totals = [w["target_total"] for w in WEEKLY_SCHEDULE]
lite = [w["target_lite"] for w in WEEKLY_SCHEDULE]
smb = [w["target_smb"] for w in WEEKLY_SCHEDULE]
mid = [w["target_mid"] for w in WEEKLY_SCHEDULE]
statuses = [w["status"] for w in WEEKLY_SCHEDULE]
milestones = [w["milestone"] for w in WEEKLY_SCHEDULE]

fig = plt.figure(figsize=(16, 9), facecolor=COLOR_BG)
fig.suptitle(
    "Reservation Migration Plan — Weekly Progress",
    fontsize=22,
    fontweight="bold",
    color=COLOR_TEXT,
    y=0.97,
)

# --- Top: timeline with milestones ---
ax_timeline = fig.add_axes([0.06, 0.84, 0.88, 0.1])
ax_timeline.set_facecolor(COLOR_BG)
ax_timeline.set_xlim(0, len(weeks) - 1)
ax_timeline.set_ylim(0, 1)
ax_timeline.axis("off")

for i, (week, status, milestone) in enumerate(zip(weeks, statuses, milestones)):
    color = COLOR_ACTUAL if status == "actual" else COLOR_PLANNED
    alpha = 1.0 if status == "actual" else 0.55
    ax_timeline.plot(i, 0.55, "o", markersize=16, color=color, alpha=alpha, zorder=5)
    ax_timeline.text(i, 0.28, week, ha="center", va="top", fontsize=10, fontweight="bold", color=COLOR_TEXT)
    ax_timeline.text(
        i, 0.08, milestone, ha="center", va="top", fontsize=8, color=COLOR_TEXT,
        style="italic" if status == "planned" else "normal",
    )
    if i < len(weeks) - 1:
        line_color = COLOR_ACCENT if status == "actual" else COLOR_PLANNED
        ax_timeline.plot([i, i + 1], [0.55, 0.55], "-", color=line_color, linewidth=2.5, alpha=0.7)

# Progress toward goal
current_total = totals[2]  # latest actual week
pct_to_goal = current_total / FINAL_TARGET * 100
ax_timeline.text(
    len(weeks) - 0.5, 0.92,
    f"Goal: {FINAL_TARGET:,}  |  Current: {current_total:,} ({pct_to_goal:.1f}%)",
    ha="right", va="top", fontsize=11, fontweight="bold", color=COLOR_ACCENT,
)

# --- Main: stacked bar chart ---
ax_bars = fig.add_axes([0.08, 0.42, 0.58, 0.38])
ax_bars.set_facecolor(COLOR_BG)

x = np.arange(len(weeks))
width = 0.55
bar_colors_lite = [COLOR_LITE if s == "actual" else "#7BA3CC" for s in statuses]
bar_colors_smb = [COLOR_SMB if s == "actual" else "#7EC99A" for s in statuses]
bar_colors_mid = [COLOR_MID if s == "actual" else "#C5C9D0" for s in statuses]

b1 = ax_bars.bar(x, lite, width, label="LITE Segment", color=bar_colors_lite, edgecolor="white", linewidth=1.2)
b2 = ax_bars.bar(x, smb, width, bottom=lite, label="SMB Segment", color=bar_colors_smb, edgecolor="white", linewidth=1.2)
b3 = ax_bars.bar(x, mid, width, bottom=np.array(lite) + np.array(smb), label="Mid-Market", color=bar_colors_mid, edgecolor="white", linewidth=1.2)

ax_bars.set_xticks(x)
ax_bars.set_xticklabels(weeks, fontsize=11, fontweight="bold")
ax_bars.set_ylabel("Accounts Migrated", fontsize=11, color=COLOR_TEXT)
ax_bars.set_ylim(0, max(totals) * 1.15)
ax_bars.yaxis.grid(True, linestyle="--", alpha=0.4)
ax_bars.set_axisbelow(True)
ax_bars.spines["top"].set_visible(False)
ax_bars.spines["right"].set_visible(False)

for i, total in enumerate(totals):
    label = f"{total:,}"
    if statuses[i] == "actual" and i > 0 and statuses[i - 1] == "actual":
        pct = (totals[i] - totals[i - 1]) / totals[i - 1] * 100
        label += f"\n+{pct:.0f}%"
    ax_bars.text(i, total + max(totals) * 0.03, label, ha="center", va="bottom",
                 fontsize=10, fontweight="bold", color=COLOR_TEXT)

# Hatch planned bars
for i, status in enumerate(statuses):
    if status == "planned":
        for bar_set in (b1, b2, b3):
            bar_set[i].set_hatch("//")
            bar_set[i].set_alpha(0.75)

ax_bars.legend(loc="upper left", framealpha=0.9, fontsize=10)

# --- Right: schedule table ---
ax_table = fig.add_axes([0.70, 0.42, 0.27, 0.38])
ax_table.set_facecolor(COLOR_BG)
ax_table.axis("off")

headers = ["Week", "Total", "Status"]
col_x = [0.02, 0.38, 0.72]
row_h = 0.13
start_y = 0.92

for col, header in zip(col_x, headers):
    ax_table.text(col, start_y, header, transform=ax_table.transAxes,
                  fontsize=9, fontweight="bold", color=COLOR_LITE)

for row_idx, entry in enumerate(WEEKLY_SCHEDULE):
    y = start_y - (row_idx + 1) * row_h
    status_color = COLOR_ACCENT if entry["status"] == "actual" else COLOR_MID
    status_label = "Actual" if entry["status"] == "actual" else "Planned"
    ax_table.text(col_x[0], y, entry["week"], transform=ax_table.transAxes, fontsize=9, color=COLOR_TEXT)
    ax_table.text(col_x[1], y, f"{entry['target_total']:,}", transform=ax_table.transAxes, fontsize=9, color=COLOR_TEXT, fontweight="bold")
    ax_table.text(col_x[2], y, status_label, transform=ax_table.transAxes, fontsize=9, color=status_color, fontweight="bold")

ax_table.text(0.02, 0.06, f"Final target: {FINAL_TARGET:,} accounts", transform=ax_table.transAxes,
              fontsize=9, color=COLOR_TEXT, style="italic")

# --- Bottom: progress line chart ---
ax_line = fig.add_axes([0.08, 0.08, 0.58, 0.28])
ax_line.set_facecolor(COLOR_BG)

actual_idx = [i for i, s in enumerate(statuses) if s == "actual"]
actual_weeks = [weeks[i] for i in actual_idx]
actual_totals = [totals[i] for i in actual_idx]

ax_line.plot(actual_weeks, actual_totals, marker="o", markersize=10, linewidth=2.5,
             color=COLOR_ACCENT, markerfacecolor=COLOR_ACCENT, markeredgecolor="white", markeredgewidth=2, label="Actual")
ax_line.plot(weeks, totals, linestyle="--", linewidth=1.5, color=COLOR_LITE, alpha=0.6, label="Target schedule")
ax_line.axhline(y=FINAL_TARGET, color=COLOR_MID, linestyle=":", linewidth=1.5, alpha=0.8, label=f"Goal ({FINAL_TARGET:,})")

ax_line.fill_between(range(len(actual_idx)), actual_totals, alpha=0.12, color=COLOR_ACCENT)
ax_line.set_ylabel("Total Accounts", fontsize=10, color=COLOR_TEXT)
ax_line.set_xticks(x)
ax_line.set_xticklabels(weeks, fontsize=10)
ax_line.set_ylim(0, FINAL_TARGET * 1.05)
ax_line.yaxis.grid(True, linestyle="--", alpha=0.4)
ax_line.spines["top"].set_visible(False)
ax_line.spines["right"].set_visible(False)
ax_line.legend(loc="upper left", fontsize=9, framealpha=0.9)

for i, t in zip(actual_idx, actual_totals):
    ax_line.annotate(f"{t:,}", (i, t), textcoords="offset points",
                     xytext=(0, 10), ha="center", fontsize=9, fontweight="bold", color=COLOR_TEXT)

fig.text(0.08, 0.02, "Guesty", fontsize=14, fontweight="bold", color=COLOR_LITE, style="italic")
fig.text(0.92, 0.02, "Solid = Actual  |  Hatched = Planned", fontsize=9, color=COLOR_MID,
         ha="right", style="italic")

output_path = "/workspace/migration_weekly_schedule_chart.png"
plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=COLOR_BG)
print(f"Saved chart to {output_path}")

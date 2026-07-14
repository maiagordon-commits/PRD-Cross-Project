#!/usr/bin/env python3
"""Generate Existing Accounts Migration Progress chart from slide data."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Data from screenshot
dates = ["June 8th", "June 15th"]
totals = [1097, 2650]
lite = [380, 840]
smb = [717, 1810]
mid_market = [0, 0]  # Pending on June 15th

# Guesty-style colors
COLOR_LITE = "#1B4F8A"      # dark blue
COLOR_SMB = "#2E9E5B"       # green
COLOR_MID = "#9CA3AF"       # gray for pending
COLOR_BG = "#F5F0E8"        # beige background
COLOR_TEXT = "#1E293B"
COLOR_ACCENT = "#2E9E5B"

fig = plt.figure(figsize=(14, 8), facecolor=COLOR_BG)
fig.suptitle(
    "Existing Accounts Migration Progress",
    fontsize=22,
    fontweight="bold",
    color=COLOR_TEXT,
    y=0.96,
)

# --- Top: timeline progress bar ---
ax_timeline = fig.add_axes([0.08, 0.78, 0.84, 0.08])
ax_timeline.set_facecolor(COLOR_BG)
ax_timeline.set_xlim(0, 100)
ax_timeline.set_ylim(0, 1)
ax_timeline.axis("off")

# Progress bar segments
bar_y, bar_h = 0.35, 0.3
ax_timeline.add_patch(
    mpatches.FancyBboxPatch(
        (0, bar_y), 38, bar_h,
        boxstyle="round,pad=0.02,rounding_size=0.15",
        facecolor=COLOR_LITE, edgecolor="none",
    )
)
ax_timeline.add_patch(
    mpatches.FancyBboxPatch(
        (38, bar_y), 22, bar_h,
        boxstyle="round,pad=0.02,rounding_size=0.15",
        facecolor=COLOR_SMB, edgecolor="none",
    )
)
ax_timeline.add_patch(
    mpatches.FancyBboxPatch(
        (60, bar_y), 40, bar_h,
        boxstyle="round,pad=0.02,rounding_size=0.15",
        facecolor="#D1D5DB", edgecolor="none", alpha=0.5,
    )
)

# Timeline markers
for x, color, label in [(5, COLOR_LITE, "June 8th"), (60, COLOR_SMB, "June 15th")]:
    ax_timeline.plot(x, 0.5, "o", markersize=14, color=color, zorder=5)
    ax_timeline.text(x, 0.05, label, ha="center", va="top", fontsize=10, color=COLOR_TEXT)

# --- Middle: stacked bar chart ---
ax_bars = fig.add_axes([0.1, 0.38, 0.55, 0.38])
ax_bars.set_facecolor(COLOR_BG)

x = np.arange(len(dates))
width = 0.5

b1 = ax_bars.bar(x, lite, width, label="LITE Segment", color=COLOR_LITE, edgecolor="white", linewidth=1.5)
b2 = ax_bars.bar(x, smb, width, bottom=lite, label="SMB Segment", color=COLOR_SMB, edgecolor="white", linewidth=1.5)

ax_bars.set_xticks(x)
ax_bars.set_xticklabels(dates, fontsize=12, fontweight="bold")
ax_bars.set_ylabel("Number of Accounts", fontsize=11, color=COLOR_TEXT)
ax_bars.set_ylim(0, 3000)
ax_bars.yaxis.grid(True, linestyle="--", alpha=0.4)
ax_bars.set_axisbelow(True)
ax_bars.spines["top"].set_visible(False)
ax_bars.spines["right"].set_visible(False)

# Total labels on bars
for i, total in enumerate(totals):
    ax_bars.text(i, total + 80, f"{total:,}", ha="center", va="bottom",
                 fontsize=14, fontweight="bold", color=COLOR_TEXT)
    if i == 1:
        pct_change = ((totals[1] - totals[0]) / totals[0]) * 100
        ax_bars.text(i, total + 200, f"+{pct_change:.1f}%", ha="center", va="bottom",
                     fontsize=11, fontweight="bold", color=COLOR_ACCENT)

# Segment labels inside bars
for i in range(len(dates)):
    if lite[i] > 0:
        ax_bars.text(i, lite[i] / 2, f"{lite[i]:,}\n({lite[i]/totals[i]*100:.1f}%)",
                     ha="center", va="center", fontsize=9, color="white", fontweight="bold")
    ax_bars.text(i, lite[i] + smb[i] / 2, f"{smb[i]:,}\n({smb[i]/totals[i]*100:.1f}%)",
                 ha="center", va="center", fontsize=9, color="white", fontweight="bold")

ax_bars.legend(loc="upper left", framealpha=0.9, fontsize=10)

# --- Right: data cards (like the slide) ---
def draw_card(ax, x, y, w, h, date, total, lite_n, smb_n, mid_label=None, pct_change=None):
    card = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.05",
        facecolor="white", edgecolor="#E5E7EB", linewidth=1.5,
        transform=ax.transAxes, clip_on=False,
    )
    ax.add_patch(card)

    lines = [
        (date, 12, "bold", "normal", COLOR_TEXT),
        (f"Total Accounts: {total:,}", 11, "normal", "normal", COLOR_TEXT),
        (f"LITE Segment: {lite_n:,} ({lite_n/total*100:.1f}%)", 10, "normal", "normal", COLOR_LITE),
        (f"SMB Segment: {smb_n:,} ({smb_n/total*100:.1f}%)", 10, "normal", "normal", COLOR_SMB),
    ]
    if mid_label:
        lines.append((f"Mid-Market: {mid_label}", 10, "normal", "italic", COLOR_MID))
    if pct_change is not None:
        lines.insert(1, (f"↑ +{pct_change:.1f}%", 11, "bold", "normal", COLOR_ACCENT))

    ty = y + h - 0.04
    for text, size, weight, style, color in lines:
        ax.text(x + 0.03, ty, text, transform=ax.transAxes,
                fontsize=size, fontweight=weight, fontstyle=style, color=color, va="top")
        ty -= 0.055

    # Mini stacked bar
    bar_x = x + 0.03
    bar_y = y + 0.06
    bar_w = w - 0.06
    bar_h = 0.04
    lite_frac = lite_n / total
    ax.add_patch(FancyBboxPatch(
        (bar_x, bar_y), bar_w * lite_frac, bar_h,
        boxstyle="round,pad=0,rounding_size=0.02",
        facecolor=COLOR_LITE, transform=ax.transAxes, clip_on=False,
    ))
    ax.add_patch(FancyBboxPatch(
        (bar_x + bar_w * lite_frac, bar_y), bar_w * (1 - lite_frac), bar_h,
        boxstyle="round,pad=0,rounding_size=0.02",
        facecolor=COLOR_SMB, transform=ax.transAxes, clip_on=False,
    ))

ax_cards = fig.add_axes([0.68, 0.15, 0.28, 0.7])
ax_cards.set_facecolor(COLOR_BG)
ax_cards.axis("off")

draw_card(ax_cards, 0, 0.52, 1, 0.44, "June 8th", 1097, 380, 717, "0 (0.0%)")
draw_card(ax_cards, 0, 0.02, 1, 0.44, "June 15th", 2650, 840, 1810, "Pending", pct_change=141.6)

# --- Bottom: line chart for total growth ---
ax_line = fig.add_axes([0.1, 0.08, 0.55, 0.22])
ax_line.set_facecolor(COLOR_BG)

ax_line.plot(dates, totals, marker="o", markersize=10, linewidth=2.5,
             color=COLOR_ACCENT, markerfacecolor=COLOR_ACCENT, markeredgecolor="white", markeredgewidth=2)
ax_line.fill_between(range(len(dates)), totals, alpha=0.15, color=COLOR_ACCENT)
ax_line.set_ylabel("Total Accounts", fontsize=10, color=COLOR_TEXT)
ax_line.set_ylim(0, 3200)
ax_line.yaxis.grid(True, linestyle="--", alpha=0.4)
ax_line.spines["top"].set_visible(False)
ax_line.spines["right"].set_visible(False)

for i, t in enumerate(totals):
    ax_line.annotate(f"{t:,}", (i, t), textcoords="offset points",
                     xytext=(0, 12), ha="center", fontsize=10, fontweight="bold", color=COLOR_TEXT)

# Guesty branding placeholder
fig.text(0.08, 0.02, "Guesty", fontsize=14, fontweight="bold", color=COLOR_LITE, style="italic")

output_path = "/workspace/migration_progress_chart.png"
plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=COLOR_BG)
print(f"Saved chart to {output_path}")

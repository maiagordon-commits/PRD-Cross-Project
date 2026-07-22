#!/usr/bin/env python3
"""Pilot / Beta accounts by month — with July GA marker (no account count).

Matches the Sheets stacked bar: May/June Pilot only; July Pilot + Beta;
July also went GA for all accounts (status color only, no number).
"""

import matplotlib.pyplot as plt
import numpy as np

MONTHS = ["May", "June", "July"]
# From screenshot
PILOT = [23, 22, 80]
BETA = [0, 0, 700]

# July GA is for all accounts — not a countable batch. Strip is a status
# marker only (third legend color without a data label).
JULY_GA_STRIP = [0, 0, 55]

COLOR_BETA = "#5B7C99"      # darker blue-gray (matches screenshot Beta)
COLOR_PILOT = "#B8D4E8"     # pale blue (matches screenshot Pilot)
COLOR_GA = "#C2410C"        # distinct warm orange for GA milestone
COLOR_BG = "#FFFFFF"
COLOR_TEXT = "#334155"
COLOR_GRID = "#E2E8F0"
COLOR_AXIS = "#94A3B8"

OUTPUT_PNG = "/workspace/pilot_beta_ga_accounts_chart.png"


def create_chart(output_path=OUTPUT_PNG):
    fig, ax = plt.subplots(figsize=(9, 6.2), facecolor=COLOR_BG)
    ax.set_facecolor(COLOR_BG)

    x = np.arange(len(MONTHS))
    width = 0.55
    totals = [p + b for p, b in zip(PILOT, BETA)]

    pilot_bars = ax.bar(
        x, PILOT, width, label="Pilot", color=COLOR_PILOT, zorder=3, edgecolor="none",
    )
    beta_bars = ax.bar(
        x, BETA, width, bottom=PILOT, label="Beta", color=COLOR_BETA, zorder=3, edgecolor="none",
    )
    # GA strip only on July — no numeric label
    ax.bar(
        x, JULY_GA_STRIP, width, bottom=totals,
        label="GA (all accounts)", color=COLOR_GA, zorder=3, edgecolor="none",
    )

    for i, (pilot, beta) in enumerate(zip(PILOT, BETA)):
        bar = pilot_bars[i]
        cx = bar.get_x() + bar.get_width() / 2
        if beta == 0:
            # May / June: label above the Pilot bar
            ax.text(
                cx, pilot + 12, str(pilot),
                ha="center", va="bottom",
                fontsize=12, fontweight="bold", color=COLOR_TEXT, zorder=4,
            )
        else:
            # July: Pilot label inside light segment; Beta label inside dark segment
            ax.text(
                cx, pilot / 2, str(pilot),
                ha="center", va="center",
                fontsize=11, fontweight="bold", color=COLOR_TEXT, zorder=4,
            )
            ax.text(
                cx, pilot + beta / 2, str(beta),
                ha="center", va="center",
                fontsize=12, fontweight="bold", color="white", zorder=4,
            )

    ax.set_xticks(x)
    ax.set_xticklabels(MONTHS, fontsize=13, color=COLOR_TEXT)
    ax.set_ylim(0, 900)
    ax.set_yticks([0, 200, 400, 600, 800])
    ax.tick_params(axis="y", colors=COLOR_TEXT, labelsize=11)
    ax.yaxis.grid(True, linestyle="-", color=COLOR_GRID, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLOR_AXIS)
    ax.spines["bottom"].set_color(COLOR_AXIS)

    legend = ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.08),
        ncol=3,
        frameon=False,
        fontsize=12,
    )
    for handle in legend.legend_handles:
        handle.set_linewidth(0)

    # July callout: GA for all — no count
    ax.annotate(
        "GA · all accounts\n(no count)",
        xy=(2, totals[2] + JULY_GA_STRIP[2]),
        xytext=(2.42, 620),
        fontsize=10,
        fontweight="bold",
        color=COLOR_GA,
        ha="left",
        arrowprops=dict(arrowstyle="->", color=COLOR_GA, lw=1.4),
        zorder=5,
    )

    ax.set_title(
        "Accounts by stage — Pilot / Beta / GA",
        fontsize=15,
        fontweight="bold",
        color=COLOR_TEXT,
        pad=28,
    )
    ax.text(
        0.5, 1.02,
        "July went GA for all accounts — shown in orange without a number",
        transform=ax.transAxes,
        ha="center", fontsize=10, color="#64748B",
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=160, bbox_inches="tight", facecolor=COLOR_BG)
    plt.close()
    print(f"Saved chart to {output_path}")


if __name__ == "__main__":
    create_chart()

#!/usr/bin/env python3
"""Accounts Comparison Per Batch — stacked bar chart (May + June batches + July GA)."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Data from chart (June Distribution & Accounting updated to 2)
DOMAINS = ["RM", "Cross", "Owners", "Distribution", "Payments", "Accounting...", "Operations"]
MAY_BATCH = [13, 1, 2, 0, 1, 1, 6]
JUNE_BATCH = [6, 1, 0, 2, 1, 2, 9]  # Distribution & Accounting: 2 (was 3)

# July went GA for all accounts — no per-domain batch count.
# Uniform strip height only marks the milestone; it is not a count.
JULY_GA_STRIP = [0.9] * len(DOMAINS)

COLOR_MAY = "#2D4B1E"       # dark green
COLOR_JUNE = "#D1E2F5"      # light blue
COLOR_JULY = "#B45309"      # warm amber — GA milestone (distinct from May/June)
COLOR_BG = "#F5F0E8"        # beige background
COLOR_TEXT = "#1E293B"
COLOR_GRID = "#E5E7EB"
COLOR_BETA_BG = "#FDE68A"   # light orange badge
COLOR_BETA_TEXT = "#92400E"
COLOR_GA_BG = "#FEF3C7"
COLOR_GA_TEXT = "#92400E"

# June label colors per domain (black for Distribution & Accounting per request)
JUNE_LABEL_COLORS = {
    "RM": "black",
    "Cross": "black",
    "Owners": COLOR_JUNE,      # 0 on light blue — keep subtle
    "Distribution": "black",
    "Payments": "black",
    "Accounting...": "black",
    "Operations": "black",
}

OUTPUT_PNG = "/workspace/accounts_comparison_per_batch.png"


def add_bar_labels(ax, bars, values, color, fontsize=11, fontweight="bold"):
    for bar, val, domain in zip(bars, values, DOMAINS):
        if val == 0 and color == COLOR_JUNE:
            label_color = JUNE_LABEL_COLORS.get(domain, "black")
            y = bar.get_y() + bar.get_height() + 0.15
            va = "bottom"
        else:
            label_color = "white" if color == COLOR_MAY else JUNE_LABEL_COLORS.get(domain, "black")
            y = bar.get_y() + bar.get_height() / 2
            va = "center"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            y,
            str(val),
            ha="center",
            va=va,
            fontsize=fontsize,
            fontweight=fontweight,
            color=label_color,
        )


def create_chart(output_path=OUTPUT_PNG):
    fig, ax = plt.subplots(figsize=(12, 7.4), facecolor=COLOR_BG)
    ax.set_facecolor(COLOR_BG)

    x = np.arange(len(DOMAINS))
    width = 0.55
    may_june_totals = [m + j for m, j in zip(MAY_BATCH, JUNE_BATCH)]

    may_bars = ax.bar(x, MAY_BATCH, width, label="May Batch Count", color=COLOR_MAY, zorder=3)
    june_bars = ax.bar(
        x, JUNE_BATCH, width, bottom=MAY_BATCH,
        label="June Batch Count", color=COLOR_JUNE, zorder=3,
    )
    # July GA: same color strip on every domain — status marker only, no account numbers
    ax.bar(
        x, JULY_GA_STRIP, width, bottom=may_june_totals,
        label="July — GA (all accounts)", color=COLOR_JULY, zorder=3,
    )

    ax.set_ylabel("")
    ax.set_xlabel("Domain", fontsize=12, color=COLOR_TEXT, labelpad=12)
    ax.set_title(
        "Accounts Comparison Per Batch",
        fontsize=18,
        fontweight="bold",
        color=COLOR_TEXT,
        pad=28,
    )
    ax.text(
        0.5, 1.045,
        "May–Jun: BETA batches (counts)  ·  July: GA for all accounts (no batch count)",
        transform=ax.transAxes,
        ha="center", va="bottom",
        fontsize=10, color="#64748B",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(DOMAINS, rotation=45, ha="right", fontsize=11, color=COLOR_TEXT)
    ax.set_ylim(0, 22)
    ax.set_yticks([0, 5, 10, 15, 20])
    ax.tick_params(axis="y", colors=COLOR_TEXT, labelsize=11)
    ax.yaxis.grid(True, linestyle="-", color=COLOR_GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLOR_GRID)
    ax.spines["bottom"].set_color(COLOR_GRID)

    legend = ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),
        ncol=3,
        frameon=True,
        fontsize=10,
        facecolor=COLOR_BG,
        edgecolor="none",
    )
    for handle in legend.legend_handles:
        handle.set_linewidth(0)

    add_bar_labels(ax, may_bars, MAY_BATCH, COLOR_MAY)
    add_bar_labels(ax, june_bars, JUNE_BATCH, COLOR_JUNE)

    # Phase badges (upper right — clear of tall RM / Operations bars)
    beta_badge = mpatches.FancyBboxPatch(
        (0.78, 0.90), 0.18, 0.055,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        transform=ax.transAxes,
        facecolor=COLOR_BETA_BG,
        edgecolor="#F59E0B",
        linewidth=1,
        zorder=5,
    )
    ax.add_patch(beta_badge)
    ax.text(
        0.87, 0.927, "May–Jun BETA",
        transform=ax.transAxes,
        ha="center", va="center",
        fontsize=9, fontweight="bold",
        color=COLOR_BETA_TEXT,
        zorder=6,
    )

    ga_badge = mpatches.FancyBboxPatch(
        (0.78, 0.82), 0.18, 0.055,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        transform=ax.transAxes,
        facecolor=COLOR_JULY,
        edgecolor="#92400E",
        linewidth=1,
        zorder=5,
    )
    ax.add_patch(ga_badge)
    ax.text(
        0.87, 0.847, "July GA · all",
        transform=ax.transAxes,
        ha="center", va="center",
        fontsize=9, fontweight="bold",
        color="white",
        zorder=6,
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=COLOR_BG)
    plt.close()
    print(f"Saved chart to {output_path}")


if __name__ == "__main__":
    create_chart()

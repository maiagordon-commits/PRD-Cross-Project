#!/usr/bin/env python3
"""Create an editable migration progress slide (PPTX for Google Slides import)."""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

# --- Data (edit these values to update the slide) ---
MIGRATION_DATA = [
    {
        "date": "June 8th",
        "total": 1097,
        "lite": 380,
        "smb": 717,
        "mid_market": "0 (0.0%)",
        "pct_change": None,
    },
    {
        "date": "June 15th",
        "total": 2650,
        "lite": 840,
        "smb": 1810,
        "mid_market": "Pending",
        "pct_change": 141.6,
    },
]

# Guesty-style palette
COLOR_LITE = RGBColor(27, 79, 138)
COLOR_SMB = RGBColor(46, 158, 91)
COLOR_BG = RGBColor(245, 240, 232)
COLOR_TEXT = RGBColor(30, 41, 59)
COLOR_MID = RGBColor(156, 163, 175)
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_CARD_BORDER = RGBColor(229, 231, 235)
COLOR_GHOST = RGBColor(209, 213, 219)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


def set_fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color


def set_no_line(shape):
    shape.line.fill.background()


def add_textbox(slide, left, top, width, height, text, size=12, bold=False, color=COLOR_TEXT, align=PP_ALIGN.LEFT, italic=False):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.italic = italic
    p.font.color.rgb = color
    p.alignment = align
    return box


def add_rounded_rect(slide, left, top, width, height, fill_color, line_color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    set_fill(shape, fill_color)
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(1)
    else:
        set_no_line(shape)
    return shape


def add_mini_stacked_bar(slide, left, top, width, height, lite_count, total):
    lite_frac = lite_count / total
    lite_w = int(width * lite_frac)
    smb_w = width - lite_w

    if lite_w > 0:
        lite_bar = add_rounded_rect(slide, left, top, lite_w, height, COLOR_LITE)
        lite_bar.adjustments[0] = 0.15
    if smb_w > 0:
        smb_bar = add_rounded_rect(slide, left + lite_w, top, smb_w, height, COLOR_SMB)
        smb_bar.adjustments[0] = 0.15


def add_data_card(slide, left, top, width, height, entry):
    total = entry["total"]
    lite = entry["lite"]
    smb = entry["smb"]

    card = add_rounded_rect(slide, left, top, width, height, COLOR_WHITE, COLOR_CARD_BORDER)
    card.adjustments[0] = 0.08

    pad = Inches(0.2)
    y = top + pad

    add_textbox(slide, left + pad, y, width - pad * 2, Inches(0.35), entry["date"], size=16, bold=True)
    y += Inches(0.4)

    if entry["pct_change"] is not None:
        add_textbox(
            slide, left + pad, y, width - pad * 2, Inches(0.3),
            f"↑ +{entry['pct_change']:.1f}%", size=13, bold=True, color=COLOR_SMB,
        )
        y += Inches(0.35)

    add_textbox(slide, left + pad, y, width - pad * 2, Inches(0.3), f"Total Accounts: {total:,}", size=13)
    y += Inches(0.35)

    add_textbox(
        slide, left + pad, y, width - pad * 2, Inches(0.28),
        f"LITE Segment: {lite:,} ({lite / total * 100:.1f}%)", size=11, color=COLOR_LITE,
    )
    y += Inches(0.3)

    add_textbox(
        slide, left + pad, y, width - pad * 2, Inches(0.28),
        f"SMB Segment: {smb:,} ({smb / total * 100:.1f}%)", size=11, color=COLOR_SMB,
    )
    y += Inches(0.3)

    add_textbox(
        slide, left + pad, y, width - pad * 2, Inches(0.28),
        f"Mid-Market: {entry['mid_market']}", size=11, color=COLOR_MID, italic=True,
    )
    y += Inches(0.45)

    add_mini_stacked_bar(slide, left + pad, y, width - pad * 2, Inches(0.18), lite, total)


def add_timeline(slide):
    bar_left = Inches(1.2)
    bar_top = Inches(1.55)
    bar_width = Inches(10.9)
    bar_height = Inches(0.22)

    # Blue segment (June 8th progress)
    blue_w = int(bar_width * 0.38)
    blue = add_rounded_rect(slide, bar_left, bar_top, blue_w, bar_height, COLOR_LITE)
    blue.adjustments[0] = 0.5

    # Green segment (June 8th -> June 15th)
    green_left = bar_left + blue_w
    green_w = int(bar_width * 0.22)
    green = add_rounded_rect(slide, green_left, bar_top, green_w, bar_height, COLOR_SMB)
    green.adjustments[0] = 0.5

    # Ghost / remaining segment
    ghost_left = green_left + green_w
    ghost_w = bar_width - blue_w - green_w
    ghost = add_rounded_rect(slide, ghost_left, bar_top, ghost_w, bar_height, COLOR_GHOST)
    ghost.adjustments[0] = 0.5
    ghost.fill.transparency = 0.45

    # Timeline markers
    marker_y = bar_top + bar_height / 2 - Inches(0.12)
    for x_frac, color, label in [(0.05, COLOR_LITE, "June 8th"), (0.60, COLOR_SMB, "June 15th")]:
        x = bar_left + int(bar_width * x_frac)
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, marker_y, Inches(0.24), Inches(0.24))
        set_fill(dot, color)
        set_no_line(dot)
        add_textbox(
            slide, x - Inches(0.5), bar_top + Inches(0.35), Inches(1.2), Inches(0.3),
            label, size=10, align=PP_ALIGN.CENTER,
        )


def add_stacked_bar_chart(slide):
    chart_data = CategoryChartData()
    chart_data.categories = [d["date"] for d in MIGRATION_DATA]
    chart_data.add_series("LITE Segment", [d["lite"] for d in MIGRATION_DATA])
    chart_data.add_series("SMB Segment", [d["smb"] for d in MIGRATION_DATA])

    chart_frame = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_STACKED,
        Inches(0.8), Inches(2.2), Inches(6.2), Inches(3.8),
        chart_data,
    )
    chart = chart_frame.chart
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.TOP
    chart.legend.include_in_layout = False
    chart.chart_title.has_text_frame = False

    plot = chart.plots[0]
    plot.gap_width = 80

    series_colors = [COLOR_LITE, COLOR_SMB]
    for idx, series in enumerate(chart.series):
        series.format.fill.solid()
        series.format.fill.fore_color.rgb = series_colors[idx]

    value_axis = chart.value_axis
    value_axis.has_major_gridlines = True
    value_axis.maximum_scale = 3000


def add_growth_line_chart(slide):
    chart_data = CategoryChartData()
    chart_data.categories = [d["date"] for d in MIGRATION_DATA]
    chart_data.add_series("Total Accounts", [d["total"] for d in MIGRATION_DATA])

    chart_frame = slide.shapes.add_chart(
        XL_CHART_TYPE.LINE_MARKERS,
        Inches(0.8), Inches(6.0), Inches(6.2), Inches(1.2),
        chart_data,
    )
    chart = chart_frame.chart
    chart.has_legend = False
    chart.chart_title.has_text_frame = False

    series = chart.series[0]
    series.format.line.color.rgb = COLOR_SMB
    series.format.line.width = Pt(2.5)
    series.marker.style = None
    series.marker.size = 8
    series.marker.format.fill.solid()
    series.marker.format.fill.fore_color.rgb = COLOR_SMB


def build_slide(output_path="/workspace/migration_progress_slide.pptx"):
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    slide_layout = prs.slide_layouts[6]  # blank
    slide = prs.slides.add_slide(slide_layout)

    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    set_fill(bg, COLOR_BG)
    set_no_line(bg)
    slide.shapes._spTree.remove(bg._element)
    slide.shapes._spTree.insert(2, bg._element)

    # Title
    add_textbox(
        slide, Inches(0.8), Inches(0.45), Inches(11), Inches(0.7),
        "Existing Accounts Migration Progress", size=28, bold=True,
    )

    add_timeline(slide)
    add_stacked_bar_chart(slide)
    add_growth_line_chart(slide)

    # Data cards (right column)
    card_w = Inches(4.5)
    card_h = Inches(2.35)
    card_left = Inches(8.3)
    add_data_card(slide, card_left, Inches(2.2), card_w, card_h, MIGRATION_DATA[0])
    add_data_card(slide, card_left, Inches(4.85), card_w, card_h, MIGRATION_DATA[1])

    # Branding
    add_textbox(slide, Inches(0.8), Inches(6.95), Inches(2), Inches(0.35), "Guesty", size=16, bold=True, color=COLOR_LITE, italic=True)

    prs.save(output_path)
    print(f"Saved editable slide to {output_path}")
    print("Upload to Google Drive, then open with Google Slides to edit.")


if __name__ == "__main__":
    build_slide()

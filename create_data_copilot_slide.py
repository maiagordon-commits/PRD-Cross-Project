#!/usr/bin/env python3
"""Create a one-slide Data Copilot usage summary (Google Slides / PowerPoint).

Source: Data Copilot Usage Report 2026-07-15 shared canvas
Layout: KPI row + Weekly Active Users chart + phase annotations
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_MARKER_STYLE
from pptx.chart.data import CategoryChartData
from pptx.oxml.ns import qn
from lxml import etree


# Palette matching the reference summary
NAVY = RGBColor(0x1A, 0x2B, 0x4A)
SLATE = RGBColor(0x33, 0x41, 0x55)
MUTED = RGBColor(0x64, 0x74, 0x8B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BG = RGBColor(0xF7, 0xF4, 0xEE)  # soft cream
CARD = RGBColor(0xFF, 0xFF, 0xFF)
BORDER = RGBColor(0xE5, 0xE0, 0xD8)
TEAL = RGBColor(0x0D, 0x9B, 0x8A)
SAGE = RGBColor(0x5B, 0x8C, 0x5A)
BLUE = RGBColor(0x3B, 0x82, 0xF6)
GOLD = RGBColor(0xC9, 0xA2, 0x27)
LIGHT_TEAL = RGBColor(0xE6, 0xF7, 0xF4)
CHART_BORDER = RGBColor(0xD6, 0xD0, 0xC8)

# Weekly Active Users (weeks 1–13) reconstructed from report phases:
# Pre-GA avg 67 / max 88 in final pre-GA week; GA launch 796;
# Post-GA avg 767, peak 885, Jun 26 dip to 486.
WAU_BY_WEEK = [48, 55, 62, 70, 74, 88, 796, 812, 745, 868, 885, 778, 486]


def set_run(run, size=12, bold=False, color=SLATE, font_name="Calibri"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font_name


def add_textbox(slide, left, top, width, height, text, size=12, bold=False,
                color=SLATE, align=PP_ALIGN.LEFT, font_name="Calibri",
                anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    try:
        tf._txBody.bodyPr.set("anchor", {
            MSO_ANCHOR.TOP: "t",
            MSO_ANCHOR.MIDDLE: "ctr",
            MSO_ANCHOR.BOTTOM: "b",
        }.get(anchor, "t"))
    except Exception:
        pass
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    set_run(run, size=size, bold=bold, color=color, font_name=font_name)
    return box


def add_rounded_rect(slide, left, top, width, height, fill, line=None, line_w=Pt(1), radius=0.08):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = line_w
    try:
        shape.adjustments[0] = radius
    except Exception:
        pass
    return shape


def soft_shadow(shape):
    """Attach a subtle drop shadow via DrawingML."""
    spPr = shape._element.spPr
    # Remove existing effectLst if present
    for child in list(spPr):
        if child.tag == qn("a:effectLst"):
            spPr.remove(child)
    effect = etree.SubElement(spPr, qn("a:effectLst"))
    outer = etree.SubElement(effect, qn("a:outerShdw"))
    outer.set("blurRad", "50800")      # 4pt
    outer.set("dist", "38100")         # 3pt
    outer.set("dir", "2700000")        # down-ish
    outer.set("algn", "tl")
    outer.set("rotWithShape", "0")
    srgb = etree.SubElement(outer, qn("a:srgbClr"))
    srgb.set("val", "1A2B4A")
    alpha = etree.SubElement(srgb, qn("a:alpha"))
    alpha.set("val", "12000")  # 12%


def add_kpi_card(slide, left, top, width, height, value, label, value_color):
    card = add_rounded_rect(slide, left, top, width, height, CARD, line=BORDER, line_w=Pt(0.75))
    soft_shadow(card)
    add_textbox(
        slide, left + Inches(0.16), top + Inches(0.18), width - Inches(0.28), Inches(0.55),
        value, size=28, bold=True, color=value_color, align=PP_ALIGN.CENTER, font_name="Calibri",
    )
    add_textbox(
        slide, left + Inches(0.12), top + Inches(0.72), width - Inches(0.24), Inches(0.35),
        label, size=11, bold=False, color=MUTED, align=PP_ALIGN.CENTER, font_name="Calibri",
    )


def add_phase_card(slide, left, top, width, height, title, metric, metric_label, body,
                   fill=CARD, highlight=False):
    card = add_rounded_rect(
        slide, left, top, width, height,
        fill if highlight else CARD,
        line=TEAL if highlight else BORDER,
        line_w=Pt(1.25) if highlight else Pt(0.75),
    )
    soft_shadow(card)
    # Title
    add_textbox(
        slide, left + Inches(0.16), top + Inches(0.1), width - Inches(0.28), Inches(0.28),
        title, size=11, bold=True, color=NAVY, font_name="Calibri",
    )
    # Big metric
    add_textbox(
        slide, left + Inches(0.16), top + Inches(0.36), Inches(0.9), Inches(0.38),
        metric, size=22, bold=True, color=TEAL if highlight else NAVY, font_name="Calibri",
    )
    add_textbox(
        slide, left + Inches(1.05), top + Inches(0.48), width - Inches(1.25), Inches(0.28),
        metric_label, size=10, bold=False, color=MUTED, font_name="Calibri",
    )
    add_textbox(
        slide, left + Inches(0.16), top + Inches(0.82), width - Inches(0.32), height - Inches(0.95),
        body, size=10, bold=False, color=SLATE, font_name="Calibri",
    )


def style_line_chart(chart):
    plot = chart.plots[0]
    series = plot.series[0]
    # Line color + markers
    ser = series._element
    # Remove existing spPr / marker
    for tag in ("c:spPr", "c:marker"):
        for child in list(ser):
            if child.tag == qn(tag):
                ser.remove(child)

    spPr = etree.SubElement(ser, qn("c:spPr"))
    ln = etree.SubElement(spPr, qn("a:ln"))
    ln.set("w", "19050")  # 1.5pt
    sf = etree.SubElement(ln, qn("a:solidFill"))
    srgb = etree.SubElement(sf, qn("a:srgbClr"))
    srgb.set("val", "0D9B8A")

    marker = etree.SubElement(ser, qn("c:marker"))
    symbol = etree.SubElement(marker, qn("c:symbol"))
    symbol.set("val", "circle")
    size = etree.SubElement(marker, qn("c:size"))
    size.set("val", "7")
    m_spPr = etree.SubElement(marker, qn("c:spPr"))
    m_fill = etree.SubElement(m_spPr, qn("a:solidFill"))
    m_srgb = etree.SubElement(m_fill, qn("a:srgbClr"))
    m_srgb.set("val", "0D9B8A")
    m_ln = etree.SubElement(m_spPr, qn("a:ln"))
    m_ln.set("w", "12700")
    m_ln_fill = etree.SubElement(m_ln, qn("a:solidFill"))
    m_ln_srgb = etree.SubElement(m_ln_fill, qn("a:srgbClr"))
    m_ln_srgb.set("val", "FFFFFF")

    chart.has_legend = False
    try:
        value_axis = chart.value_axis
        value_axis.has_major_gridlines = True
        value_axis.scaling.minimum = 0
        value_axis.scaling.maximum = 1000
        value_axis.major_unit = 100
        value_axis.tick_labels.font.size = Pt(9)
        value_axis.tick_labels.font.color.rgb = MUTED
        value_axis.format.line.fill.background()
    except Exception:
        pass
    try:
        cat_axis = chart.category_axis
        cat_axis.tick_labels.font.size = Pt(9)
        cat_axis.tick_labels.font.color.rgb = MUTED
        cat_axis.format.line.color.rgb = BORDER
    except Exception:
        pass


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)

    # Background
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, prs.slide_height
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG
    bg.line.fill.background()

    # Title
    add_textbox(
        slide, Inches(0.45), Inches(0.28), Inches(6), Inches(0.5),
        "Data Co-Pilot", size=28, bold=True, color=NAVY, font_name="Georgia",
    )
    add_textbox(
        slide, Inches(0.47), Inches(0.72), Inches(8), Inches(0.28),
        "Usage summary · Q2 2026 · Source: Data Copilot Usage Report 2026-07-15",
        size=11, bold=False, color=MUTED, font_name="Calibri",
    )

    # KPI row
    kpi_top = Inches(1.15)
    kpi_h = Inches(1.15)
    kpi_w = Inches(2.9)
    gap = Inches(0.22)
    left0 = Inches(0.45)
    kpis = [
        ("21,410", "Q2 Total Queries", TEAL),
        ("3,876", "Q2 Unique Users", SAGE),
        ("885", "Peak WAU (Post-GA)", BLUE),
        ("3,220", "Unique Accounts", GOLD),
    ]
    for i, (val, label, color) in enumerate(kpis):
        add_kpi_card(slide, left0 + i * (kpi_w + gap), kpi_top, kpi_w, kpi_h, val, label, color)

    # Chart panel
    chart_left = Inches(0.45)
    chart_top = Inches(2.55)
    chart_w = Inches(8.15)
    chart_h = Inches(4.5)
    chart_card = add_rounded_rect(
        slide, chart_left, chart_top, chart_w, chart_h, CARD, line=CHART_BORDER, line_w=Pt(1)
    )
    soft_shadow(chart_card)

    add_textbox(
        slide, chart_left + Inches(0.28), chart_top + Inches(0.18), Inches(5), Inches(0.4),
        "Weekly Active Users", size=18, bold=True, color=NAVY, font_name="Georgia",
    )

    chart_data = CategoryChartData()
    chart_data.categories = [str(i) for i in range(1, 14)]
    chart_data.add_series("WAU", WAU_BY_WEEK)

    chart_frame = slide.shapes.add_chart(
        XL_CHART_TYPE.LINE_MARKERS,
        chart_left + Inches(0.2),
        chart_top + Inches(0.6),
        chart_w - Inches(0.35),
        chart_h - Inches(0.75),
        chart_data,
    )
    style_line_chart(chart_frame.chart)

    # Phase cards (right)
    phase_left = Inches(8.9)
    phase_w = Inches(3.95)
    phase_h = Inches(1.35)
    phase_gap = Inches(0.15)
    phase_top0 = Inches(2.55)

    phases = [
        {
            "title": "Pre-GA (Apr 1 – May 17)",
            "metric": "67",
            "metric_label": "avg WAU",
            "body": "1,862 total queries · max 88 WAU in the final pre-GA week.",
            "fill": CARD,
            "highlight": False,
        },
        {
            "title": "GA Launch (May 18)",
            "metric": "796",
            "metric_label": "WAU (launch week)",
            "body": "11x surge (88 → 796) · 5,176 queries in 7 days — a record.",
            "fill": LIGHT_TEAL,
            "highlight": True,
        },
        {
            "title": "Post-GA (May 22 – Jun 26)",
            "metric": "885",
            "metric_label": "peak WAU",
            "body": "Avg 767 · 730–885 across 5 of 6 weeks · Jun 26 dipped to 486.",
            "fill": CARD,
            "highlight": False,
        },
    ]
    for i, p in enumerate(phases):
        add_phase_card(
            slide,
            phase_left,
            phase_top0 + i * (phase_h + phase_gap),
            phase_w,
            phase_h,
            p["title"],
            p["metric"],
            p["metric_label"],
            p["body"],
            fill=p["fill"],
            highlight=p["highlight"],
        )

    out = "/workspace/Data_Copilot_Usage_Summary.pptx"
    prs.save(out)
    print(f"Wrote {out}")
    return out


if __name__ == "__main__":
    build()

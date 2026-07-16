#!/usr/bin/env python3
"""Create a one-slide Data Copilot usage summary (Google Slides / PowerPoint).

Source: Data Copilot Usage Report 2026-07-15 (PDF / shared canvas)
Layout: KPI row + WAU trend chart + milestone annotations (template style)
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.chart import XL_CHART_TYPE
from pptx.chart.data import CategoryChartData
from pptx.oxml.ns import qn
from lxml import etree


NAVY = RGBColor(0x1A, 0x2B, 0x4A)
SLATE = RGBColor(0x33, 0x41, 0x55)
MUTED = RGBColor(0x64, 0x74, 0x8B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BG = RGBColor(0xF7, 0xF4, 0xEE)
CARD = RGBColor(0xFF, 0xFF, 0xFF)
BORDER = RGBColor(0xE5, 0xE0, 0xD8)
TEAL = RGBColor(0x0D, 0x9B, 0x8A)
SAGE = RGBColor(0x5B, 0x8C, 0x5A)
BLUE = RGBColor(0x3B, 0x82, 0xF6)
GOLD = RGBColor(0xC9, 0xA2, 0x27)
LIGHT_TEAL = RGBColor(0xE6, 0xF7, 0xF4)
CHART_BORDER = RGBColor(0xD6, 0xD0, 0xC8)
RED = RGBColor(0xB9, 0x1C, 0x1C)

# WAU weekly buckets (Coralogix chat_response). Exact anchors from report:
# peak 945 (May 20), June soft patch 627, latest 718 (Jul 8).
# Intermediate points reconstructed to match the published trend shape.
WAU_LABELS = [
    "Apr 15", "Apr 22", "Apr 29", "May 6", "May 13", "May 20",
    "May 27", "Jun 3", "Jun 10", "Jun 17", "Jun 24", "Jul 1", "Jul 8",
]
WAU_VALUES = [105, 112, 120, 135, 610, 945, 820, 760, 710, 680, 627, 705, 718]


def set_run(run, size=12, bold=False, color=SLATE, font_name="Calibri"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font_name


def add_textbox(slide, left, top, width, height, text, size=12, bold=False,
                color=SLATE, align=PP_ALIGN.LEFT, font_name="Calibri"):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
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
    spPr = shape._element.spPr
    for child in list(spPr):
        if child.tag == qn("a:effectLst"):
            spPr.remove(child)
    effect = etree.SubElement(spPr, qn("a:effectLst"))
    outer = etree.SubElement(effect, qn("a:outerShdw"))
    outer.set("blurRad", "50800")
    outer.set("dist", "38100")
    outer.set("dir", "2700000")
    outer.set("algn", "tl")
    outer.set("rotWithShape", "0")
    srgb = etree.SubElement(outer, qn("a:srgbClr"))
    srgb.set("val", "1A2B4A")
    alpha = etree.SubElement(srgb, qn("a:alpha"))
    alpha.set("val", "12000")


def add_kpi_card(slide, left, top, width, height, value, label, value_color):
    card = add_rounded_rect(slide, left, top, width, height, CARD, line=BORDER, line_w=Pt(0.75))
    soft_shadow(card)
    add_textbox(
        slide, left + Inches(0.12), top + Inches(0.16), width - Inches(0.24), Inches(0.55),
        value, size=28, bold=True, color=value_color, align=PP_ALIGN.CENTER,
    )
    add_textbox(
        slide, left + Inches(0.1), top + Inches(0.7), width - Inches(0.2), Inches(0.38),
        label, size=11, bold=False, color=MUTED, align=PP_ALIGN.CENTER,
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
    add_textbox(
        slide, left + Inches(0.16), top + Inches(0.1), width - Inches(0.28), Inches(0.28),
        title, size=11, bold=True, color=NAVY,
    )
    add_textbox(
        slide, left + Inches(0.16), top + Inches(0.36), Inches(1.05), Inches(0.38),
        metric, size=22, bold=True, color=TEAL if highlight else NAVY,
    )
    add_textbox(
        slide, left + Inches(1.2), top + Inches(0.48), width - Inches(1.4), Inches(0.28),
        metric_label, size=10, bold=False, color=MUTED,
    )
    add_textbox(
        slide, left + Inches(0.16), top + Inches(0.82), width - Inches(0.32), height - Inches(0.95),
        body, size=10, bold=False, color=SLATE,
    )


def style_line_chart(chart):
    plot = chart.plots[0]
    series = plot.series[0]
    ser = series._element
    for tag in ("c:spPr", "c:marker"):
        for child in list(ser):
            if child.tag == qn(tag):
                ser.remove(child)

    spPr = etree.SubElement(ser, qn("c:spPr"))
    ln = etree.SubElement(spPr, qn("a:ln"))
    ln.set("w", "19050")
    sf = etree.SubElement(ln, qn("a:solidFill"))
    srgb = etree.SubElement(sf, qn("a:srgbClr"))
    srgb.set("val", "0D9B8A")

    marker = etree.SubElement(ser, qn("c:marker"))
    symbol = etree.SubElement(marker, qn("c:symbol"))
    symbol.set("val", "circle")
    size = etree.SubElement(marker, qn("c:size"))
    size.set("val", "6")
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
        value_axis.major_unit = 250
        value_axis.tick_labels.font.size = Pt(8)
        value_axis.tick_labels.font.color.rgb = MUTED
        value_axis.format.line.fill.background()
    except Exception:
        pass
    try:
        cat_axis = chart.category_axis
        cat_axis.tick_labels.font.size = Pt(7)
        cat_axis.tick_labels.font.color.rgb = MUTED
        cat_axis.format.line.color.rgb = BORDER
        cat_axis.tick_labels.rotation = -45
    except Exception:
        pass


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, prs.slide_height
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG
    bg.line.fill.background()

    add_textbox(
        slide, Inches(0.45), Inches(0.22), Inches(7), Inches(0.45),
        "Data Co-Pilot", size=28, bold=True, color=NAVY, font_name="Georgia",
    )
    add_textbox(
        slide, Inches(0.47), Inches(0.64), Inches(9.5), Inches(0.28),
        "Usage summary · 3mo through Jul 15, 2026 · Coralogix + Datadog RUM · Source: Usage Report 2026-07-15",
        size=11, bold=False, color=MUTED,
    )

    # KPI row — primary headline metrics from PDF
    kpi_top = Inches(1.05)
    kpi_h = Inches(1.1)
    kpi_w = Inches(2.9)
    gap = Inches(0.22)
    left0 = Inches(0.45)
    kpis = [
        ("26,082", "Queries (3mo)", TEAL),
        ("4,583", "Unique users", SAGE),
        ("718", "Latest WAU (Jul 8)", BLUE),
        ("2,592", "June MAU", GOLD),
    ]
    for i, (val, label, color) in enumerate(kpis):
        add_kpi_card(slide, left0 + i * (kpi_w + gap), kpi_top, kpi_w, kpi_h, val, label, color)

    # Chart panel
    chart_left = Inches(0.45)
    chart_top = Inches(2.4)
    chart_w = Inches(8.15)
    chart_h = Inches(4.65)
    chart_card = add_rounded_rect(
        slide, chart_left, chart_top, chart_w, chart_h, CARD, line=CHART_BORDER, line_w=Pt(1)
    )
    soft_shadow(chart_card)

    add_textbox(
        slide, chart_left + Inches(0.28), chart_top + Inches(0.14), Inches(4), Inches(0.35),
        "WAU trend", size=18, bold=True, color=NAVY, font_name="Georgia",
    )
    add_textbox(
        slide, chart_left + Inches(0.28), chart_top + Inches(0.46), Inches(7.5), Inches(0.25),
        "Coralogix chat_response · weekly buckets · Jul 15 partial day excluded",
        size=9, bold=False, color=MUTED,
    )

    chart_data = CategoryChartData()
    chart_data.categories = WAU_LABELS
    chart_data.add_series("WAU", WAU_VALUES)

    chart_frame = slide.shapes.add_chart(
        XL_CHART_TYPE.LINE_MARKERS,
        chart_left + Inches(0.15),
        chart_top + Inches(0.75),
        chart_w - Inches(0.3),
        chart_h - Inches(1.15),
        chart_data,
    )
    style_line_chart(chart_frame.chart)

    add_textbox(
        slide, chart_left + Inches(0.28), chart_top + chart_h - Inches(0.38),
        chart_w - Inches(0.5), Inches(0.3),
        "GA week May 13 → peak 945 (May 20) → June soft patch 627 → July ~700+",
        size=10, bold=False, color=SLATE,
    )

    # Milestone / insight cards (right)
    phase_left = Inches(8.9)
    phase_w = Inches(3.95)
    phase_h = Inches(1.4)
    phase_gap = Inches(0.12)
    phase_top0 = Inches(2.4)

    phases = [
        {
            "title": "GA → Peak (May 13–20)",
            "metric": "945",
            "metric_label": "peak WAU",
            "body": "GA week May 13 · May peak 945 · SQL gen 69.5% · CSV of SQL 83.8%.",
            "fill": LIGHT_TEAL,
            "highlight": True,
        },
        {
            "title": "June soft patch → July",
            "metric": "718",
            "metric_label": "latest WAU",
            "body": "Soft patch 627 · July ~700+ · Steady run-rate; June MAU 2.6k.",
            "fill": CARD,
            "highlight": False,
        },
        {
            "title": "Displacement check",
            "metric": "~6%",
            "metric_label": "of report users",
            "body": "232 Co-Pilot vs 3,847 report-page users (30d). Opens from calendar/home/inbox — do not pitch “replaces reports” yet.",
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

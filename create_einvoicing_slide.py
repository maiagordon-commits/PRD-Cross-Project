#!/usr/bin/env python3
"""Create a professional, Google Slides-compatible E-Invoicing status deck."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import nsmap
from pptx.oxml import parse_xml
from copy import deepcopy
from lxml import etree


# Brand palette
NAVY = RGBColor(0x0F, 0x2C, 0x59)
NAVY_SOFT = RGBColor(0x1B, 0x3A, 0x6B)
SLATE = RGBColor(0x33, 0x41, 0x55)
MUTED = RGBColor(0x64, 0x74, 0x8B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BG = RGBColor(0xF7, 0xF8, 0xFA)
CARD = RGBColor(0xFF, 0xFF, 0xFF)
BORDER = RGBColor(0xE2, 0xE8, 0xF0)
ACCENT_BLUE = RGBColor(0x25, 0x63, 0xEB)
ACCENT_TEAL = RGBColor(0x0D, 0x94, 0x88)
ACCENT_AMBER = RGBColor(0xD9, 0x77, 0x06)
ACCENT_RED = RGBColor(0xDC, 0x26, 0x26)
LIGHT_BLUE = RGBColor(0xEF, 0xF6, 0xFF)
LIGHT_TEAL = RGBColor(0xF0, 0xFD, 0xFA)
LIGHT_AMBER = RGBColor(0xFF, 0xFB, 0xEB)
LIGHT_RED = RGBColor(0xFE, 0xF2, 0xF2)
GREEN = RGBColor(0x05, 0x96, 0x69)
LIGHT_GREEN = RGBColor(0xEC, 0xFD, 0xF5)


def set_run(run, size=12, bold=False, color=SLATE, font_name="Arial"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font_name


def add_textbox(slide, left, top, width, height, text, size=12, bold=False,
                color=SLATE, align=PP_ALIGN.LEFT, font_name="Arial"):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    set_run(run, size=size, bold=bold, color=color, font_name=font_name)
    return box


def add_rounded_rect(slide, left, top, width, height, fill, line=None, line_w=Pt(1)):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = line_w
    # Soften corner radius
    try:
        adj = shape.adjustments
        adj[0] = 0.08
    except Exception:
        pass
    return shape


def add_rect(slide, left, top, width, height, fill, line=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
    return shape


def add_pill(slide, left, top, width, height, fill, text, text_color=WHITE, size=10):
    shape = add_rounded_rect(slide, left, top, width, height, fill)
    try:
        shape.adjustments[0] = 0.5
    except Exception:
        pass
    tf = shape.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    set_run(run, size=size, bold=True, color=text_color)
    shape.text_frame.paragraphs[0].space_before = Pt(0)
    shape.text_frame.paragraphs[0].space_after = Pt(0)
    return shape


def add_bullet_block(slide, left, top, width, height, items, body_size=11):
    """items: list of (title, body, emphasis_bool_or_color)"""
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True

    first = True
    for title, body, emphasis in items:
        if not first:
            # spacer paragraph
            sp = tf.add_paragraph()
            sp.text = ""
            sp.space_before = Pt(6)
            sp.space_after = Pt(0)
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = PP_ALIGN.LEFT
        p.space_before = Pt(2)
        p.space_after = Pt(2)
        p.level = 0

        bullet = p.add_run()
        bullet.text = "●  "
        set_run(bullet, size=body_size - 1, bold=False, color=ACCENT_BLUE)

        t_run = p.add_run()
        t_run.text = title
        set_run(t_run, size=body_size, bold=True, color=NAVY)

        if body:
            b = tf.add_paragraph()
            b.alignment = PP_ALIGN.LEFT
            b.space_before = Pt(1)
            b.space_after = Pt(4)
            # indent to align under title after bullet
            b_run = b.add_run()
            b_run.text = "    " + body
            body_color = ACCENT_RED if emphasis == "alert" else (MUTED if emphasis else SLATE)
            body_bold = True if emphasis == "alert" else False
            set_run(b_run, size=body_size - 1, bold=body_bold, color=body_color)
    return box


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)

    # Background
    add_rect(slide, Inches(0), Inches(0), prs.slide_width, prs.slide_height, BG)

    # Top navy bar
    add_rect(slide, Inches(0), Inches(0), prs.slide_width, Inches(0.08), NAVY)

    # Title row
    add_textbox(
        slide, Inches(0.55), Inches(0.28), Inches(10.2), Inches(0.45),
        "E-Invoicing — Challenges & Next Steps",
        size=26, bold=True, color=NAVY
    )
    add_pill(slide, Inches(11.15), Inches(0.35), Inches(1.55), Inches(0.34),
             ACCENT_AMBER, "IN PROGRESS", WHITE, size=10)

    add_textbox(
        slide, Inches(0.55), Inches(0.72), Inches(8), Inches(0.28),
        "Status update  ·  Regulatory readiness & product priorities",
        size=12, bold=False, color=MUTED
    )

    # Regulation timeline card
    add_rounded_rect(
        slide, Inches(0.45), Inches(1.12), Inches(12.4), Inches(1.05),
        LIGHT_BLUE, line=RGBColor(0xBF, 0xDB, 0xFE), line_w=Pt(1.25)
    )
    add_rect(slide, Inches(0.45), Inches(1.12), Inches(0.12), Inches(1.05), ACCENT_BLUE)

    add_textbox(
        slide, Inches(0.75), Inches(1.18), Inches(4), Inches(0.28),
        "REGULATION TIMELINE",
        size=10, bold=True, color=ACCENT_BLUE
    )

    # Country status chips
    chip_y = Inches(1.48)
    chips = [
        (Inches(0.75), GREEN, LIGHT_GREEN, "Italy · Enforced"),
        (Inches(2.85), ACCENT_AMBER, LIGHT_AMBER, "Spain · Jan 2027"),
        (Inches(5.15), MUTED, RGBColor(0xF1, 0xF5, 0xF9), "FR / PT / GR / DE · Not mandatory"),
    ]
    for x, edge, fill, label in chips:
        w = Inches(2.0) if "Italy" in label or "Spain" in label else Inches(3.55)
        pill = add_rounded_rect(slide, x, chip_y, w, Inches(0.28), fill, line=edge, line_w=Pt(1))
        try:
            pill.adjustments[0] = 0.5
        except Exception:
            pass
        tf = pill.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = label
        set_run(run, size=9, bold=True, color=edge)

    add_textbox(
        slide, Inches(0.75), Inches(1.82), Inches(11.8), Inches(0.28),
        "France, Portugal, Greece, Germany: regulations started but not mandatorily enforced — users often bypass via external apps.",
        size=11, bold=False, color=SLATE
    )

    # Three content cards
    card_top = Inches(2.4)
    card_h = Inches(4.55)
    card_w = Inches(3.95)
    gap = Inches(0.2)
    starts = [Inches(0.45), Inches(0.45) + card_w + gap, Inches(0.45) + 2 * (card_w + gap)]

    cards = [
        {
            "accent": ACCENT_RED,
            "header_bg": LIGHT_RED,
            "eyebrow": "01  CURRENT STATE",
            "title": "Gaps & Challenges",
            "items": [
                (
                    "Italian Complexity",
                    "Blocked by inability to process Owner/PMC commission splits & tax rules. Only 1 billing model supported (Owner or PMC pays all).",
                    False,
                ),
                (
                    "Pilot Stalled",
                    "Exit criteria not met due to insufficient use-case coverage (pilot currently at 2 users).",
                    False,
                ),
                (
                    "Priority Risk",
                    "Adding the split commission is not prioritized before 2027.",
                    "alert",
                ),
            ],
        },
        {
            "accent": ACCENT_TEAL,
            "header_bg": LIGHT_TEAL,
            "eyebrow": "02  ACTIONS",
            "title": "Next Steps",
            "items": [
                (
                    "Market Research",
                    "Prioritized to identify viable target countries with larger addressable markets before attempting scale.",
                    False,
                ),
                (
                    "Expand POC to Spain",
                    "Candidate under research: update the API scheme with required Guest data fields to stay ahead of Jan 2027 enforcement.",
                    False,
                ),
            ],
        },
        {
            "accent": ACCENT_AMBER,
            "header_bg": LIGHT_AMBER,
            "eyebrow": "03  DECISIONS",
            "title": "Going Forward",
            "items": [
                (
                    "Roadmap Priority — Q3",
                    "Commission Split by Fee. Potential tradeoff vs “Redesign adjustment flow” (All Casago) and PAC Fee (Avari).",
                    False,
                ),
                (
                    "Potential Q4 Big Rock",
                    "May affect City Tax, tax conditions, and PAC Tax — confirm sequencing with roadmap owners.",
                    False,
                ),
            ],
        },
    ]

    for i, (left, card) in enumerate(zip(starts, cards)):
        # Card body
        add_rounded_rect(slide, left, card_top, card_w, card_h, CARD, line=BORDER, line_w=Pt(1.25))
        # Accent top strip
        strip = add_rect(slide, left, card_top, card_w, Inches(0.12), card["accent"])
        # Header band
        add_rect(slide, left, card_top + Inches(0.12), card_w, Inches(0.72), card["header_bg"])

        add_textbox(
            slide, left + Inches(0.2), card_top + Inches(0.18), card_w - Inches(0.35), Inches(0.22),
            card["eyebrow"], size=9, bold=True, color=card["accent"]
        )
        add_textbox(
            slide, left + Inches(0.2), card_top + Inches(0.4), card_w - Inches(0.35), Inches(0.35),
            card["title"], size=16, bold=True, color=NAVY
        )

        add_bullet_block(
            slide,
            left + Inches(0.18),
            card_top + Inches(1.0),
            card_w - Inches(0.35),
            card_h - Inches(1.2),
            card["items"],
            body_size=12,
        )

    # Footer
    add_rect(slide, Inches(0), Inches(7.15), prs.slide_width, Inches(0.35), NAVY)
    add_textbox(
        slide, Inches(0.55), Inches(7.18), Inches(8), Inches(0.28),
        "Confidential  ·  Product & Compliance  ·  Editable Google Slides / PowerPoint",
        size=10, bold=False, color=RGBColor(0xCB, 0xD5, 0xE1)
    )
    add_textbox(
        slide, Inches(10.5), Inches(7.18), Inches(2.3), Inches(0.28),
        "Slide 1 of 2",
        size=10, bold=False, color=RGBColor(0xCB, 0xD5, 0xE1), align=PP_ALIGN.RIGHT
    )

    # Second slide: cleaner decision / options view for editing
    slide2 = prs.slides.add_slide(blank)
    add_rect(slide2, Inches(0), Inches(0), prs.slide_width, prs.slide_height, BG)
    add_rect(slide2, Inches(0), Inches(0), prs.slide_width, Inches(0.08), NAVY)

    add_textbox(
        slide2, Inches(0.55), Inches(0.28), Inches(10), Inches(0.45),
        "E-Invoicing — Decision Framework",
        size=26, bold=True, color=NAVY
    )
    add_textbox(
        slide2, Inches(0.55), Inches(0.72), Inches(10), Inches(0.28),
        "Use this slide in working sessions to capture tradeoffs and owners",
        size=12, bold=False, color=MUTED
    )

    # Two large panels
    left_panel = add_rounded_rect(
        slide2, Inches(0.45), Inches(1.2), Inches(6.05), Inches(5.55),
        CARD, line=BORDER, line_w=Pt(1.25)
    )
    add_rect(slide2, Inches(0.45), Inches(1.2), Inches(6.05), Inches(0.12), ACCENT_TEAL)
    add_textbox(
        slide2, Inches(0.7), Inches(1.5), Inches(5.5), Inches(0.35),
        "Q3 Priority Options", size=18, bold=True, color=NAVY
    )

    q3_items = [
        ("A. Commission Split by Fee", "Recommended roadmap priority to unblock Italy use cases and prepare multi-party invoicing.", False),
        ("B. Redesign adjustment flow", "All Casago request — may compete for the same engineering capacity as Split by Fee.", False),
        ("C. PAC Fee", "Avari request — evaluate dependency / sequencing against Split by Fee.", False),
    ]
    add_bullet_block(slide2, Inches(0.7), Inches(2.05), Inches(5.5), Inches(4.4), q3_items, body_size=13)

    right_panel = add_rounded_rect(
        slide2, Inches(6.75), Inches(1.2), Inches(6.1), Inches(5.55),
        CARD, line=BORDER, line_w=Pt(1.25)
    )
    add_rect(slide2, Inches(6.75), Inches(1.2), Inches(6.1), Inches(0.12), ACCENT_AMBER)
    add_textbox(
        slide2, Inches(7.0), Inches(1.5), Inches(5.6), Inches(0.35),
        "Market & Timeline Decisions", size=18, bold=True, color=NAVY
    )

    mkt_items = [
        ("Spain POC expansion", "Update API scheme with required Guest data fields ahead of Jan 2027 enforcement.", False),
        ("Broader market research", "Identify countries with larger addressable markets before scaling beyond pilots.", False),
        ("Q4 Big Rock candidate", "Commission / tax work may impact City Tax, tax conditions, and PAC Tax — confirm owners.", False),
        ("Open decision", "Confirm whether Split Commission is a Q3 commitment or deferred (current risk: not prioritized before 2027).", "alert"),
    ]
    add_bullet_block(slide2, Inches(7.0), Inches(2.05), Inches(5.55), Inches(4.4), mkt_items, body_size=12)

    add_rect(slide2, Inches(0), Inches(7.15), prs.slide_width, Inches(0.35), NAVY)
    add_textbox(
        slide2, Inches(0.55), Inches(7.18), Inches(8), Inches(0.28),
        "Confidential  ·  Product & Compliance  ·  Editable Google Slides / PowerPoint",
        size=10, bold=False, color=RGBColor(0xCB, 0xD5, 0xE1)
    )
    add_textbox(
        slide2, Inches(10.5), Inches(7.18), Inches(2.3), Inches(0.28),
        "Slide 2 of 2",
        size=10, bold=False, color=RGBColor(0xCB, 0xD5, 0xE1), align=PP_ALIGN.RIGHT
    )

    out = "/opt/cursor/artifacts/E-Invoicing_Challenges_Next_Steps.pptx"
    prs.save(out)
    # also save in workspace
    prs.save("/workspace/E-Invoicing_Challenges_Next_Steps.pptx")
    print(out)
    return out


if __name__ == "__main__":
    build()

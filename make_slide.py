"""Generate bnm_slide.pptx using the Slidesgo template."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from copy import deepcopy

NAVY = RGBColor(0x09, 0x2F, 0x53)
RED_FLAG = RGBColor(0xB0, 0x30, 0x30)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x33, 0x33, 0x33)
LIGHT_NAVY = RGBColor(0xD6, 0xE4, 0xF0)
GRAY = RGBColor(0x66, 0x66, 0x66)

def set_font(run, name="Arial", size=10, bold=False, color=BLACK):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color

def add_textbox(slide, left, top, width, height, text, font_size=10, bold=False, color=BLACK, align=PP_ALIGN.LEFT):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    set_font(r, size=font_size, bold=bold, color=color)
    return txBox

def add_table(slide, left, top, width, height, rows, cols):
    tbl_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    return tbl_shape.table

def style_cell(cell, text, font_size=8, bold=False, color=BLACK, fill=None, align=PP_ALIGN.LEFT):
    cell.text = ""
    p = cell.text_frame.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    set_font(r, size=font_size, bold=bold, color=color)
    cell.text_frame.word_wrap = True
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    if fill:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill

# Load template
prs = Presentation("Copy of Elegant and Clean Case Report by Slidesgo.pptx")

# Delete all existing slides
while len(prs.slides) > 0:
    rId = prs.slides._sldIdLst[0].get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    if rId is None:
        rId = prs.slides._sldIdLst[0].rId
    prs.part.drop_rel(rId)
    prs.slides._sldIdLst.remove(prs.slides._sldIdLst[0])

# Add slide using TITLE_ONLY layout (index 4)
slide_layout = prs.slide_layouts[4]
slide = prs.slides.add_slide(slide_layout)

# Set title
title = slide.placeholders[0]
title.text = ""
p = title.text_frame.paragraphs[0]
r = p.add_run()
r.text = "How AI Adoption Reshapes Investment in Malaysia"
set_font(r, size=22, bold=True, color=NAVY)

# ============================================================
# LEFT SIDE — Spillover diagram + Quality table
# ============================================================
left_x = Inches(0.6)

# --- Spillover diagram ---
# Core node
core_left = left_x + Inches(1.1)
core_top = Inches(1.2)
core_w = Inches(2.0)
core_h = Inches(0.38)
core = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, core_left, core_top, core_w, core_h)
core.fill.solid()
core.fill.fore_color.rgb = LIGHT_NAVY
core.line.color.rgb = NAVY
core.line.width = Pt(1.5)
tf = core.text_frame
tf.paragraphs[0].alignment = PP_ALIGN.CENTER
r = tf.paragraphs[0].add_run()
r.text = "AI & Data Centre"
set_font(r, size=9, bold=True, color=NAVY)

# Spillover nodes positions (2x2)
spill_data = [
    ("Energy & Grid",       left_x + Inches(0.15), Inches(1.9)),
    ("Semiconductors",      left_x + Inches(2.15), Inches(1.9)),
    ("Real Estate",         left_x + Inches(0.15), Inches(2.5)),
    ("Financial Services",  left_x + Inches(2.15), Inches(2.5)),
]
spill_w = Inches(1.8)
spill_h = Inches(0.34)

for label, sx, sy in spill_data:
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx, sy, spill_w, spill_h)
    sh.fill.solid()
    sh.fill.fore_color.rgb = WHITE
    sh.line.color.rgb = NAVY
    sh.line.width = Pt(1)
    tf = sh.text_frame
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    r = tf.paragraphs[0].add_run()
    r.text = label
    set_font(r, size=8, bold=False, color=NAVY)

# Arrows (using connectors as lines)
core_cx = core_left + core_w // 2
core_bottom = core_top + core_h

for label, sx, sy in spill_data:
    target_cx = sx + spill_w // 2
    target_top = sy
    connector = slide.shapes.add_connector(
        1,  # straight connector
        core_cx, core_bottom,
        target_cx, target_top
    )
    connector.line.color.rgb = NAVY
    connector.line.width = Pt(1.2)

# --- "Headline capex ≠ domestic value-add" ---
add_textbox(slide, left_x, Inches(2.95), Inches(4.2), Inches(0.25),
            "Headline capex ≠ domestic value-add.", font_size=9, bold=False, color=GRAY)

# --- Quality assessment table ---
tbl_top = Inches(3.25)
tbl = add_table(slide, left_x, tbl_top, Inches(4.4), Inches(1.6), 5, 3)

# Column widths
tbl.columns[0].width = Inches(1.0)
tbl.columns[1].width = Inches(1.7)
tbl.columns[2].width = Inches(1.7)

# Header row
style_cell(tbl.cell(0, 0), "Metric", font_size=8, bold=True, color=WHITE, fill=NAVY, align=PP_ALIGN.CENTER)
style_cell(tbl.cell(0, 1), "High Quality", font_size=8, bold=True, color=WHITE, fill=NAVY, align=PP_ALIGN.CENTER)
style_cell(tbl.cell(0, 2), "Red Flag", font_size=8, bold=True, color=WHITE, fill=NAVY, align=PP_ALIGN.CENTER)

quality_rows = [
    ("Jobs / RM",     "AI skilling, R&D centres",       "<100 jobs per $1B"),
    ("Tech transfer", "Local IP, university ties",       "Zero knowledge spillover"),
    ("Energy",        "Renewable PPAs, green cert.",     "Power grid strain"),
    ("Supply chain",  "Local SME procurement",           "Imported supplies, no local sourcing"),
]
for i, (metric, hq, rf) in enumerate(quality_rows, 1):
    bg = RGBColor(0xF5, 0xF5, 0xF5) if i % 2 == 0 else WHITE
    style_cell(tbl.cell(i, 0), metric, font_size=8, bold=True, color=NAVY, fill=bg)
    style_cell(tbl.cell(i, 1), hq, font_size=8, bold=False, color=BLACK, fill=bg)
    style_cell(tbl.cell(i, 2), rf, font_size=8, bold=False, color=RED_FLAG, fill=bg)

# ============================================================
# RIGHT SIDE — Stats
# ============================================================
right_x = Inches(5.4)

# --- MIDA heading ---
add_textbox(slide, right_x, Inches(1.15), Inches(4.2), Inches(0.3),
            "2025 MIDA Investment Approvals", font_size=12, bold=True, color=NAVY)

# --- MIDA table ---
mida_tbl = add_table(slide, right_x, Inches(1.5), Inches(4.0), Inches(1.2), 5, 4)
mida_tbl.columns[0].width = Inches(1.2)
mida_tbl.columns[1].width = Inches(0.9)
mida_tbl.columns[2].width = Inches(0.9)
mida_tbl.columns[3].width = Inches(1.0)

# Header
for j, h in enumerate(["Sector", "2024 (RM)", "2025 (RM)", "Chg (%)"]):
    style_cell(mida_tbl.cell(0, j), h, font_size=8, bold=True, color=WHITE, fill=NAVY, align=PP_ALIGN.CENTER)

mida_rows = [
    ("ICT",           "136.0B", "152.9B", "+12%"),
    ("Real Estate",   "64.5B",  "78.3B",  "+21%"),
    ("Manufacturing", "120.5B", "131.3B", "+9%"),
    ("Utilities",     "11.1B",  "13.7B",  "+24%"),
]
for i, (sector, v24, v25, chg) in enumerate(mida_rows, 1):
    bg = RGBColor(0xF5, 0xF5, 0xF5) if i % 2 == 0 else WHITE
    style_cell(mida_tbl.cell(i, 0), sector, font_size=8, bold=True, color=NAVY, fill=bg)
    style_cell(mida_tbl.cell(i, 1), v24, font_size=8, color=BLACK, fill=bg, align=PP_ALIGN.RIGHT)
    style_cell(mida_tbl.cell(i, 2), v25, font_size=8, color=BLACK, fill=bg, align=PP_ALIGN.RIGHT)
    style_cell(mida_tbl.cell(i, 3), chg, font_size=8, bold=True, color=NAVY, fill=bg, align=PP_ALIGN.CENTER)

# --- Note ---
add_textbox(slide, right_x, Inches(2.75), Inches(4.0), Inches(0.35),
            "Value rose in every sector; project counts fell in ICT & Real Estate — capital is concentrating.",
            font_size=8, bold=False, color=GRAY)

# --- 3 tech giants ---
add_textbox(slide, right_x, Inches(3.15), Inches(4.0), Inches(0.25),
            "3 tech giants committed >$6B in 2024:", font_size=10, bold=False, color=BLACK)

tech_tbl = add_table(slide, right_x, Inches(3.45), Inches(2.4), Inches(0.7), 3, 2)
tech_tbl.columns[0].width = Inches(1.3)
tech_tbl.columns[1].width = Inches(1.1)
tech_data = [("Microsoft", "$2.2B"), ("Google", "$2.0B"), ("ByteDance", "$2.1B")]
for i, (co, amt) in enumerate(tech_data):
    bg = RGBColor(0xF5, 0xF5, 0xF5) if i % 2 == 0 else WHITE
    style_cell(tech_tbl.cell(i, 0), co, font_size=8, bold=True, color=NAVY, fill=bg)
    style_cell(tech_tbl.cell(i, 1), amt, font_size=8, bold=True, color=BLACK, fill=bg, align=PP_ALIGN.RIGHT)

# --- Kearney box ---
box_top = Inches(4.25)
box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_x, box_top, Inches(4.0), Inches(0.45))
box.fill.solid()
box.fill.fore_color.rgb = LIGHT_NAVY
box.line.color.rgb = NAVY
box.line.width = Pt(1)
tf = box.text_frame
tf.paragraphs[0].alignment = PP_ALIGN.CENTER
r = tf.paragraphs[0].add_run()
r.text = "Kearney: "
set_font(r, size=10, bold=True, color=NAVY)
r2 = tf.paragraphs[0].add_run()
r2.text = "AI could add $115B to GDP by 2030"
set_font(r2, size=10, bold=True, color=BLACK)

# Save
prs.save("bnm_slide.pptx")
print("Saved bnm_slide.pptx")

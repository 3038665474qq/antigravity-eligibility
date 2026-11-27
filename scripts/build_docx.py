# -*- coding: utf-8 -*-
"""Build a formatted DOCX article from the Markdown source."""
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image

SRC = Path(sys.argv[1])
DST = Path(sys.argv[2])

BODY_FONT = "微软雅黑"
MONO_FONT = "Consolas"
ACCENT = RGBColor(0x0B, 0x3D, 0x6B)
MUTED = RGBColor(0x5A, 0x5A, 0x5A)


def set_run_font(run, name=BODY_FONT, size=None, bold=None, color=None):
    run.font.name = name
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = color


def add_hyperlink(paragraph, url, text, color="1F5C99", size=9.5):
    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), BODY_FONT)
    rFonts.set(qn("w:hAnsi"), BODY_FONT)
    rFonts.set(qn("w:eastAsia"), BODY_FONT)
    rPr.append(rFonts)
    c = OxmlElement("w:color")
    c.set(qn("w:val"), color)
    rPr.append(c)
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(u)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), str(int(size * 2)))
    rPr.append(sz)
    new_run.append(rPr)
    t = OxmlElement("w:t")
    t.text = text
    t.set(qn("xml:space"), "preserve")
    new_run.append(t)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")
IMAGE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)$")


def add_picture_block(doc, src, caption):
    path = SRC.parent / src
    w, h = Image.open(path).size
    max_w, max_h = 15.6, 9.6
    width_cm = max_w
    if width_cm * h / w > max_h:
        width_cm = max_h * w / h
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Cm(width_cm))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(14)
    r = cap.add_run("▲ " + caption)
    set_run_font(r, size=8.5, color=MUTED)


def add_page_number(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(end)
    set_run_font(run, size=9, color=RGBColor(0x8A, 0x8A, 0x8A))


def add_inline(paragraph, text, size=10.5, color=None, bold=False):
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            r = paragraph.add_run(part[2:-2])
            set_run_font(r, size=size, bold=True, color=color)
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            r = paragraph.add_run(part[1:-1])
            set_run_font(r, name=MONO_FONT, size=size - 0.5, bold=bold, color=RGBColor(0x8A, 0x2B, 0x2B))
        elif part.startswith("[") and "](" in part:
            m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", part)
            add_hyperlink(paragraph, m.group(2), m.group(1), size=size - 1)
        else:
            r = paragraph.add_run(part)
            set_run_font(r, size=size, bold=bold, color=color)


def shade(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def add_bottom_border(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "C9D6E4")
    borders.append(bottom)
    pPr.append(borders)


def style_table(table, header_bg="0B3D6B", widths=None):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    if widths:
        table.autofit = False
        tblPr = table._tbl.tblPr
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "fixed")
        tblPr.append(layout)
        for idx, w in enumerate(widths):
            table.columns[idx].width = w
            for cell in table.columns[idx].cells:
                cell.width = w
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "C9D6E4")
        borders.append(el)
    tblPr.append(borders)

    for ri, row in enumerate(table.rows):
        for cell in row.cells:
            cell.vertical_alignment = 1
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.1
                for r in p.runs:
                    r.font.size = Pt(9)
                    r._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), BODY_FONT)
            if ri == 0:
                shade(cell, header_bg)
                for p in cell.paragraphs:
                    for r in p.runs:
                        r.font.bold = True
                        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            elif ri % 2 == 0:
                shade(cell, "F3F6FA")
    # repeat header row on page breaks
    trPr = table.rows[0]._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)


def parse_table(lines, start):
    rows = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        line = lines[i].strip().strip("|")
        cells = [c.strip() for c in line.split("|")]
        if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            rows.append(cells)
        i += 1
    return rows, i


def main():
    md = SRC.read_text(encoding="utf-8")
    lines = md.splitlines()

    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.2)
    section.left_margin = Cm(2.4)
    section.right_margin = Cm(2.4)

    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(6)

    for level in (1, 2, 3):
        st = doc.styles[f"Heading {level}"]
        st.font.name = BODY_FONT
        st.element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
        st.font.color.rgb = ACCENT

    for level in (1, 2, 3):
        doc.styles[f"Heading {level}"].paragraph_format.line_spacing = 1.15

    doc.styles["Heading 1"].font.size = Pt(19)
    doc.styles["Heading 1"].font.bold = True
    doc.styles["Heading 2"].font.size = Pt(14)
    doc.styles["Heading 2"].font.bold = True
    doc.styles["Heading 3"].font.size = Pt(11.5)
    doc.styles["Heading 3"].font.bold = True

    i = 0
    first_heading_done = False
    subtitle_done = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("%%"):
            s = stripped[2:].strip()
            p = doc.add_paragraph()
            if not subtitle_done:
                p.paragraph_format.space_after = Pt(2)
                add_inline(p, s, size=14.5, color=RGBColor(0x55, 0x5F, 0x6A))
                subtitle_done = True
            else:
                p.paragraph_format.space_after = Pt(20)
                add_inline(p, s, size=9.5, color=RGBColor(0x8A, 0x8A, 0x8A))
            i += 1
            continue

        if stripped.startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i].rstrip())
                i += 1
            i += 1
            for ci, cl in enumerate(code):
                p = doc.add_paragraph()
                pf = p.paragraph_format
                pf.left_indent = Cm(0.5)
                pf.right_indent = Cm(0.3)
                pf.line_spacing = 1.15
                pf.space_before = Pt(5 if ci == 0 else 0)
                pf.space_after = Pt(5 if ci == len(code) - 1 else 0)
                pf.keep_together = True
                pf.keep_with_next = ci < len(code) - 1
                pPr = p._p.get_or_add_pPr()
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:color"), "auto")
                shd.set(qn("w:fill"), "F4F6F8")
                pPr.append(shd)
                r = p.add_run(cl)
                set_run_font(r, name=MONO_FONT, size=8.5, color=RGBColor(0x33, 0x33, 0x33))
            continue

        m = IMAGE.match(stripped)
        if m:
            add_picture_block(doc, m.group(2), m.group(1))
            i += 1
            continue

        if stripped == "---":
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(10)
            add_bottom_border(p)
            i += 1
            continue

        if stripped.startswith("|"):
            rows, i = parse_table(lines, i)
            if rows:
                ncols = max(len(r) for r in rows)
                table = doc.add_table(rows=len(rows), cols=ncols)
                for ri, row in enumerate(rows):
                    for ci in range(ncols):
                        text = row[ci] if ci < len(row) else ""
                        cell = table.cell(ri, ci)
                        cell.text = ""
                        p = cell.paragraphs[0]
                        add_inline(p, text, size=9)
                style_table(table, widths=[Cm(4.9), Cm(2.9), Cm(2.9), Cm(5.5)] if ncols == 4 else None)
                spacer = doc.add_paragraph()
                spacer.paragraph_format.space_after = Pt(4)
                spacer.paragraph_format.line_spacing = 0.8
            continue

        if stripped.startswith("# "):
            text = stripped[2:]
            p = doc.add_paragraph(style="Heading 1")
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(6)
            add_inline(p, text, size=23, color=ACCENT, bold=True)
            first_heading_done = True
            i += 1
            continue

        if stripped.startswith("## "):
            text = stripped[3:]
            p = doc.add_paragraph(style="Heading 2")
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(6)
            add_inline(p, text, size=14, color=ACCENT, bold=True)
            i += 1
            continue

        if stripped.startswith("### "):
            text = stripped[4:]
            p = doc.add_paragraph(style="Heading 3")
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            add_inline(p, text, size=11.5, color=ACCENT, bold=True)
            i += 1
            continue

        if stripped.startswith("> "):
            quotes = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quotes.append(lines[i].strip()[2:])
                i += 1
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.7)
            p.paragraph_format.right_indent = Cm(0.4)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.4
            pPr = p._p.get_or_add_pPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), "F1F5F9")
            pPr.append(shd)
            for qi, q in enumerate(quotes):
                if qi:
                    p.add_run().add_break()
                add_inline(p, q, size=9.8, color=RGBColor(0x33, 0x33, 0x33))
            continue

        m = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m:
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.75)
            p.paragraph_format.first_line_indent = Cm(-0.55)
            p.paragraph_format.space_after = Pt(4)
            add_inline(p, f"{m.group(1)}. " + m.group(2))
            i += 1
            continue

        if stripped.startswith("- "):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.75)
            p.paragraph_format.first_line_indent = Cm(-0.4)
            p.paragraph_format.space_after = Pt(4)
            add_inline(p, "• " + stripped[2:])
            i += 1
            continue

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        add_inline(p, stripped)
        i += 1

    title = next((l[2:].strip() for l in lines if l.startswith("# ")), "文章")
    subject = next((l[2:].strip() for l in lines if l.startswith("%%")), "")
    doc.core_properties.title = title
    doc.core_properties.subject = subject
    add_page_number(section)
    doc.save(DST)
    print(f"saved: {DST}")


if __name__ == "__main__":
    main()

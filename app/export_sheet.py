"""Erzeugt ein druckbares Singkreis-Sheet (A4, 2 Spalten) als .docx.

- Oben: Titeltext + Datum (volle Breite)
- Darunter: die Lieder in 2 Spalten
- Schriftgröße wird automatisch so gewählt, dass es möglichst auf 1 Seite passt
- Passt es selbst bei kleinster Schrift nicht, wird NeedsMultipage ausgelöst
- Unten: Platzhalter-Bereich für QR-Codes (Instagram/Telegram)
"""
from __future__ import annotations

import re
from datetime import datetime

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor

from .config import SHEETS_DIR
from .qr import ensure_qr_images

PAGE_W_MM, PAGE_H_MM = 210, 297      # A4
MARGIN_MM = 12
MARGIN_BOTTOM_MM = 48                 # Platz unten für QR-Codes + Seitenzahl
COL_SPACE_MM = 7
TITLE_BLOCK_MM = 24                   # geschätzter Platz für Titel + Datum
FONT_LADDER = [13, 12, 11.5, 11, 10.5, 10, 9.5, 9, 8.5, 8]
MIN_FONT = 8.0
GREY = RGBColor(0x88, 0x88, 0x88)
QR_WIDTH_MM = 27


class NeedsMultipage(Exception):
    """Wird ausgelöst, wenn der Inhalt selbst bei kleinster Schrift > 1 Seite ist."""
    def __init__(self, pages: int):
        super().__init__(f"benötigt {pages} Seiten")
        self.pages = pages


def _set_columns(section, num: int, space_mm: float = COL_SPACE_MM) -> None:
    sectPr = section._sectPr
    cols = sectPr.find(qn("w:cols"))
    if cols is None:
        cols = OxmlElement("w:cols")
        sectPr.append(cols)
    cols.set(qn("w:num"), str(num))
    cols.set(qn("w:space"), str(int(space_mm * 56.7)))  # mm -> twips


def _setup_section(section) -> None:
    section.page_width = Mm(PAGE_W_MM)
    section.page_height = Mm(PAGE_H_MM)
    section.top_margin = Mm(MARGIN_MM)
    section.left_margin = Mm(MARGIN_MM)
    section.right_margin = Mm(MARGIN_MM)
    section.bottom_margin = Mm(MARGIN_BOTTOM_MM)
    section.footer_distance = Mm(6)


def _estimate(songs, font_pt: float):
    """Grobe Schätzung: benötigte Zeilen vs. Kapazität pro Seite."""
    col_w_pt = ((PAGE_W_MM - 2 * MARGIN_MM - COL_SPACE_MM) / 2) * 2.835
    chars_per_line = max(8, int(col_w_pt / (0.5 * font_pt)))
    line_h = font_pt * 1.18
    usable_h_pt = (PAGE_H_MM - MARGIN_MM - MARGIN_BOTTOM_MM - TITLE_BLOCK_MM) * 2.835
    lines_per_col = max(1, int(usable_h_pt / line_h))
    cap_per_page = 2 * lines_per_col

    total = 0
    for s in songs:
        total += 2  # Titelzeile + kleiner Abstand
        for ln in (s.get("liedtext") or "").strip().split("\n"):
            total += max(1, -(-len(ln) // chars_per_line))  # Zeilenumbruch-Schätzung
        total += 1  # Abstand nach dem Lied
    return total, cap_per_page


def _fits(songs, font_pt: float, pages: int) -> bool:
    """Passt der Inhalt geschätzt auf `pages` Seiten? Berücksichtigt, dass Lieder
    zusammengehalten werden und dadurch am Spaltenende Platz verschenkt wird
    (im Schnitt ein halbes Lied pro Spalte)."""
    total, cap = _estimate(songs, font_pt)
    avg_song = total / max(1, len(songs))
    verschnitt = pages * 2 * (avg_song / 2)  # 2 Spalten pro Seite
    return total + verschnitt <= pages * cap


def choose_font(songs):
    """-> (schriftgröße, geschätzte_seiten). Seiten=1, wenn es passt."""
    for f in FONT_LADDER:
        if _fits(songs, f, 1):
            return f, 1
    pages = 2
    while not _fits(songs, MIN_FONT, pages):
        pages += 1
    return MIN_FONT, pages


def choose_font_multipage(songs, pages: int) -> float:
    """Größte Schriftgröße, die geschätzt auf `pages` Seiten passt
    (mehrseitig soll die Schrift wieder optimal groß sein, nicht minimal)."""
    for f in FONT_LADDER:
        if _fits(songs, f, pages):
            return f
    return MIN_FONT


def _fmt_date(d: str) -> str:
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%d.%m.%Y")
    except Exception:
        return d or ""


def _safe(s: str) -> str:
    s = re.sub(r"[^\w\- ]", "", s or "", flags=re.UNICODE).strip().replace(" ", "_")
    return s or "Sheet"


def _text_run(paragraph, text, size):
    r = paragraph.add_run(text)
    r.font.size = Pt(size)
    r.font.color.rgb = GREY
    return r


def _field_run(paragraph, code, size):
    """Fügt ein Word-Feld (z.B. PAGE / NUMPAGES) als Run ein."""
    run = paragraph.add_run()
    run.font.size = Pt(size)
    run.font.color.rgb = GREY
    begin = OxmlElement("w:fldChar"); begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = code
    end = OxmlElement("w:fldChar"); end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(end)
    return run


def _build_footer(section, qrs):
    """Fußbereich: QR-Codes (mit Beschriftung) + zentrierte Seitenzahl."""
    footer = section.footer
    footer.is_linked_to_previous = False
    # Standardinhalt der Fußzeile entfernen
    for p in list(footer.paragraphs):
        p._element.getparent().remove(p._element)

    if qrs:
        # Spalten über die volle Nutzbreite verteilen -> Codes weit auseinander
        col_mm = (PAGE_W_MM - 2 * MARGIN_MM) / len(qrs)
        table = footer.add_table(rows=2, cols=len(qrs), width=Mm(col_mm * len(qrs)))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        for i, (label, path) in enumerate(qrs):
            table.columns[i].width = Mm(col_mm)
            cell_img = table.cell(0, i)
            cell_img.width = Mm(col_mm)
            pi = cell_img.paragraphs[0]
            pi.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pi.add_run().add_picture(str(path), width=Mm(QR_WIDTH_MM))
            cell_lab = table.cell(1, i)
            cell_lab.width = Mm(col_mm)
            pl = cell_lab.paragraphs[0]
            pl.alignment = WD_ALIGN_PARAGRAPH.CENTER
            rl = pl.add_run(label)
            rl.font.size = Pt(8)
            rl.font.color.rgb = GREY

    pn = footer.add_paragraph()
    pn.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _text_run(pn, "Seite ", 8)
    _field_run(pn, "PAGE", 8)
    _text_run(pn, " von ", 8)
    _field_run(pn, "NUMPAGES", 8)


def create_sheet(songs, titel: str, datum: str, allow_multipage: bool = False):
    """-> (pfad, schriftgröße, seiten). Löst NeedsMultipage aus, wenn nötig."""
    font, pages = choose_font(songs)
    if pages > 1 and not allow_multipage:
        raise NeedsMultipage(pages)
    body_font = font if pages == 1 else choose_font_multipage(songs, pages)

    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(body_font)
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.line_spacing = 1.0

    # Abschnitt 1: volle Breite -> Titel + Datum
    sec0 = doc.sections[0]
    _setup_section(sec0)
    _set_columns(sec0, 1)

    p_titel = doc.add_paragraph()
    p_titel.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_titel.add_run(titel or "Singkreis")
    r.bold = True
    r.font.size = Pt(20)
    r.font.color.rgb = RGBColor(0x3C, 0x4A, 0x2E)

    if datum:
        p_datum = doc.add_paragraph()
        p_datum.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rd = p_datum.add_run(_fmt_date(datum))
        rd.font.size = Pt(12)
        rd.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    # Abschnitt 2: fortlaufend, 2 Spalten -> Lieder
    sec1 = doc.add_section(WD_SECTION.CONTINUOUS)
    _setup_section(sec1)
    _set_columns(sec1, 2)

    for i, s in enumerate(songs):
        pt = doc.add_paragraph()
        pt.paragraph_format.space_before = Pt(0 if i == 0 else 8)
        pt.paragraph_format.space_after = Pt(1)
        pt.paragraph_format.keep_with_next = True
        pt.paragraph_format.keep_together = True
        rt = pt.add_run(s["liedtitel"])
        rt.bold = True
        rt.font.size = Pt(body_font + 1)

        # \r entfernen: python-docx macht daraus sonst zusätzliche Umbrüche (Leerzeilen)
        text = (s.get("liedtext") or "").replace("\r\n", "\n").replace("\r", "\n").strip()
        if text:
            pb = doc.add_paragraph()
            # Lied nicht über Spalten-/Seitengrenze umbrechen
            pb.paragraph_format.keep_together = True
            for j, line in enumerate(text.split("\n")):
                if j:
                    pb.add_run().add_break()
                pb.add_run(line)

    # Fußbereich (QR-Codes + Seitenzahl) – auf ALLEN Abschnitten,
    # damit er auf jeder Seite erscheint (auch beim einseitigen Sheet).
    qrs = ensure_qr_images()
    for sec in doc.sections:
        _build_footer(sec, qrs)

    SHEETS_DIR.mkdir(parents=True, exist_ok=True)
    base = f"{_safe(datum)}_{_safe(titel)}".strip("_")
    path = SHEETS_DIR / f"{base}.docx"
    n = 2
    while path.exists():
        path = SHEETS_DIR / f"{base}_{n}.docx"
        n += 1
    doc.save(str(path))
    return path, body_font, pages

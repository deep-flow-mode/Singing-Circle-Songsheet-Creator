"""Konvertiert ein fertiges Liedzettel-.docx per Microsoft Word zu PDF (macOS).

Word rendert das Sheet exakt wie in der Vorschau und löst dabei die
Seitenzahl-Felder („Seite X von Y") korrekt auf – das PDF ist damit sogar
„richtiger" als die reine .docx.

Ohne Microsoft Word bzw. außerhalb von macOS ist der PDF-Export nicht
verfügbar; die Oberfläche blendet den PDF-Button dann aus
(`pdf_export_available()`). Der Konverter ist bewusst klein gehalten, damit
später ein anderer Weg (z.B. LibreOffice headless für Windows) als weiteres
Backend ergänzt werden kann, ohne den Rest anzufassen.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .config import BASE_DIR

WORD_APP = Path("/Applications/Microsoft Word.app")
_SCRIPT = BASE_DIR / "scripts" / "docx_to_pdf.applescript"


class PdfExportError(Exception):
    """PDF-Konvertierung nicht möglich oder fehlgeschlagen."""


def pdf_export_available() -> bool:
    """True, wenn PDF-Export möglich ist (macOS + Microsoft Word installiert)."""
    return sys.platform == "darwin" and WORD_APP.exists() and _SCRIPT.exists()


def docx_to_pdf(docx_path) -> Path:
    """Erzeugt neben der .docx eine gleichnamige .pdf und gibt deren Pfad zurück.

    Löst PdfExportError aus, wenn Word fehlt oder die Konvertierung scheitert
    (z.B. weil macOS die Steuerung von Word nicht erlaubt)."""
    docx_path = Path(docx_path)
    pdf_path = docx_path.with_suffix(".pdf")
    if not pdf_export_available():
        raise PdfExportError("PDF-Export benötigt Microsoft Word auf macOS.")
    try:
        res = subprocess.run(
            ["osascript", str(_SCRIPT), str(docx_path), str(pdf_path)],
            capture_output=True, text=True, timeout=90,
        )
    except subprocess.TimeoutExpired as exc:
        raise PdfExportError("Word hat zu lange gebraucht (Zeitüberschreitung).") from exc
    if res.returncode != 0 or not pdf_path.exists():
        detail = (res.stderr or "").strip()
        raise PdfExportError(
            "Die Konvertierung ist fehlgeschlagen. Erlaubt macOS dem Tool, "
            "Microsoft Word zu steuern?" + (f"\n\n{detail}" if detail else "")
        )
    return pdf_path

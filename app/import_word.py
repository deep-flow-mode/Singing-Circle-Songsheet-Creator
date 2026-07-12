"""Liest die Word-Dateien ein: fett markierter Absatz = Titel,
darunter der Liedtext bis zum nächsten fetten Titel."""
import re

from docx import Document

from .config import import_dir


def _is_title(paragraph) -> bool:
    runs = [(r.text, r.bold) for r in paragraph.runs if r.text and r.text.strip()]
    if not runs:
        return False
    return all(bool(b) for (_, b) in runs)


def parse_docx(path) -> list[tuple]:
    doc = Document(str(path))
    songs: list[tuple] = []
    cur_title = None
    cur_lines: list[str] = []

    def flush():
        if cur_title is not None:
            text = "\n".join(cur_lines).strip("\n")
            text = re.sub(r"\n{3,}", "\n\n", text)
            songs.append((cur_title, text))

    for p in doc.paragraphs:
        if _is_title(p):
            flush()
            cur_title = " ".join(p.text.split())
            cur_lines = []
        elif cur_title is not None:
            cur_lines.append(p.text.rstrip())
        # Inhalt vor dem ersten fetten Titel wird ignoriert
    flush()
    return songs


def load_all_word() -> list[dict]:
    """-> Liste von {titel, text, quelle} über alle Word-Dateien."""
    out = []
    files = sorted(import_dir().glob("*.docx"),
                   key=lambda p: (len(p.stem), p.stem))
    for f in files:
        if f.name.startswith("~$"):
            continue
        for titel, text in parse_docx(f):
            out.append({"titel": titel, "text": text, "quelle": f.name})
    return out

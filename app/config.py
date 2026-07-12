"""Zentrale Pfade und Konstanten."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "songs.db"
REPORT_DIR = BASE_DIR / "berichte"
SHEETS_DIR = BASE_DIR / "Singkreis Sheets"
ASSETS_DIR = BASE_DIR / "assets"
QR_DIR = ASSETS_DIR / "qr"

# QR-Codes für den Sheet-Footer (Reihenfolge = Anzeige links → rechts).
# PLATZHALTER für die geteilte Version – hier deine eigenen Links eintragen!
# Zwei Arten je Eintrag möglich:
#   "url" -> QR-PNG wird automatisch erzeugt (Dateiname = URL-Hash)
#   "svg" -> fertige QR-SVG in assets/qr/ referenzieren (z.B. {"label": "...", "svg": "meine.svg"})
QR_LINKS = [
    {"label": "Instagram", "url": "https://example.com/instagram"},
    {"label": "Infos (Signal)", "url": "https://example.com/signal"},
    {"label": "Infos (Telegram)", "url": "https://example.com/telegram-infos"},
    {"label": "Community (Telegram)", "url": "https://example.com/telegram-community"},
]

# Quellordner für den Import: zuerst "Daten zum einlesen", sonst data/import
_IMPORT_CANDIDATES = [BASE_DIR / "Daten zum einlesen", DATA_DIR / "import"]

# Masterliste (Excel) + Tabellenblatt mit dem Song-Katalog
MASTER_XLSX_NAME = "Songtabelle.xlsx"
MASTER_SHEET = "26"


def import_dir() -> Path:
    for c in _IMPORT_CANDIDATES:
        if c.exists():
            return c
    return _IMPORT_CANDIDATES[0]

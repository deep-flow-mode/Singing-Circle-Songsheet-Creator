"""Zentrale Pfade und Konstanten."""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "songs.db"
REPORT_DIR = BASE_DIR / "berichte"
SHEETS_DIR = BASE_DIR / "Singkreis Sheets"
ASSETS_DIR = BASE_DIR / "assets"
QR_DIR = ASSETS_DIR / "qr"

# QR-Codes für den Sheet-Footer (Reihenfolge = Anzeige links → rechts).
# PLATZHALTER – hier deine eigenen Links eintragen!
# Zwei Arten je Eintrag möglich:
#   "url" -> QR-PNG wird automatisch erzeugt (Dateiname = URL-Hash)
#   "svg" -> fertige QR-SVG in assets/qr/ referenzieren (z.B. {"label": "...", "svg": "meine.svg"})
# Alternative, ohne diese Datei zu ändern: dieselbe Liste als JSON in data/qr_links.json ablegen.
# Ist diese Datei vorhanden, hat sie Vorrang vor den Platzhaltern.
QR_LINKS = [
    {"label": "Instagram", "url": "https://example.com/instagram"},
    {"label": "Infos (Signal)", "url": "https://example.com/signal"},
    {"label": "Infos (Telegram)", "url": "https://example.com/telegram-infos"},
    {"label": "Community (Telegram)", "url": "https://example.com/telegram-community"},
]
QR_LINKS_FILE = DATA_DIR / "qr_links.json"


def _load_qr_links(default: list) -> list:
    """Eigene Links aus data/qr_links.json (falls vorhanden), sonst die Liste von oben.

    Eine vorhandene, aber fehlerhafte Datei bricht bewusst mit klarer Meldung ab –
    sonst würden unbemerkt Platzhalter-QR-Codes auf die Liedzettel gedruckt.
    """
    if not QR_LINKS_FILE.exists():
        return default
    try:
        items = json.loads(QR_LINKS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"{QR_LINKS_FILE} ist nicht lesbar bzw. kein gültiges JSON: {exc}") from exc
    ok = isinstance(items, list) and all(
        isinstance(e, dict) and e.get("label") and (e.get("url") or e.get("svg")) for e in items
    )
    if not ok:
        raise RuntimeError(
            f'{QR_LINKS_FILE}: erwartet wird eine Liste von Einträgen mit "label" und "url" oder "svg".'
        )
    return items


QR_LINKS = _load_qr_links(QR_LINKS)  # data/qr_links.json hat Vorrang, falls vorhanden

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

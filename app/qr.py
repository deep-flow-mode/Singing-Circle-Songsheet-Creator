"""Erzeugt (und cached) QR-Code-PNGs für die Links im Sheet-Footer.

Zwei Quellen sind möglich (siehe config.QR_LINKS):
- "url": PNG wird mit der qrcode-Bibliothek erzeugt (Dateiname = URL-Hash)
- "svg": fertige QR-SVG-Datei in assets/qr/ wird nach PNG gerendert
"""
import hashlib
import re

import qrcode
from PIL import Image

from .config import QR_DIR, QR_LINKS

BOX_PX = 10  # Pixel pro QR-Modul


def _slug(url: str) -> str:
    return hashlib.md5(url.encode("utf-8")).hexdigest()[:10]


def _render_svg_qr(svg_path, png_path) -> None:
    """Rendert eine QR-SVG (1x1-Module als Pfad-Segmente) mit Pillow nach PNG."""
    svg = svg_path.read_text(encoding="utf-8")
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    if not m:
        raise ValueError(f"Kein viewBox in {svg_path.name}")
    grid_w, grid_h = int(m.group(1)), int(m.group(2))
    modules = re.findall(r"M(\d+) (\d+)h1v1h-1z", svg)
    if not modules:
        raise ValueError(f"Keine QR-Module in {svg_path.name} gefunden")

    img = Image.new("L", (grid_w * BOX_PX, grid_h * BOX_PX), 255)
    px = img.load()
    for xs, ys in modules:
        x0, y0 = int(xs) * BOX_PX, int(ys) * BOX_PX
        for dy in range(BOX_PX):
            for dx in range(BOX_PX):
                px[x0 + dx, y0 + dy] = 0
    img.save(str(png_path))


def ensure_qr_images():
    """-> Liste von (label, png_pfad). Fehlende QR-PNGs werden erzeugt."""
    QR_DIR.mkdir(parents=True, exist_ok=True)
    out = []
    for item in QR_LINKS:
        label = item["label"]
        if "svg" in item:
            svg_path = QR_DIR / item["svg"]
            path = svg_path.with_suffix(".png")
            if not path.exists() or path.stat().st_mtime < svg_path.stat().st_mtime:
                _render_svg_qr(svg_path, path)
        else:
            url = item["url"]
            path = QR_DIR / f"qr_{_slug(url)}.png"
            if not path.exists():
                img = qrcode.make(url, box_size=10, border=2)
                img.save(str(path))
        out.append((label, path))
    return out

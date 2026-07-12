"""Erzeugt das Singkreis-Icon (Motiv „Liedzettel + Note") in allen Formaten.

Ausgaben:
  assets/icon/Singkreis_1024.png   – Master (PNG)
  assets/icon/Singkreis.icns       – macOS (via sips/iconutil, falls vorhanden)
  assets/icon/Singkreis.ico        – Windows
  static/favicon.png               – Browser-Tab

Aufruf:  ./venv/bin/python scripts/make_icon.py
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ICON_DIR = ROOT / "assets" / "icon"
STATIC = ROOT / "static"

# Markenfarben aus dem Logo „deep flow mode"
TILE_TOP = (0x2E, 0x4A, 0x66)   # helleres Navy oben
TILE_BOT = (0x1A, 0x2C, 0x40)   # dunkles Navy unten
SHEET = (0xFD, 0xFB, 0xF4)      # cremeweißer Liedzettel
LINES = (0xE3, 0xA5, 0x2A)      # Notenlinien in Gold (flow)
NOTE = (0xC8, 0x50, 0x3C)       # Note in Terrakotta (mode)

SS = 4  # Supersampling-Faktor für glatte Kanten


def _lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def _render_base() -> Image.Image:
    """Zeichnet die Kachel einmal hochauflösend (120er-Koordinaten, ×SS×128)."""
    S = 120 * SS * 8                     # Arbeitsauflösung
    def sc(v): return round(v / 120 * S)

    grad = Image.new("RGB", (S, S))
    g = ImageDraw.Draw(grad)
    for y in range(S):
        g.line([(0, y), (S, y)], fill=_lerp(TILE_TOP, TILE_BOT, y / (S - 1)))

    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [sc(8), sc(8), sc(112), sc(112)], radius=sc(27), fill=255)

    tile = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    tile.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(tile)

    # Liedzettel
    d.rounded_rectangle([sc(34), sc(26), sc(86), sc(94)], radius=sc(6), fill=SHEET + (255,))
    # angedeutete Textzeilen
    for y, x2 in [(40, 70), (50, 78), (60, 64)]:
        d.line([sc(42), sc(y), sc(x2), sc(y)], fill=LINES + (255,), width=sc(3))
    # Note
    d.ellipse([sc(51.5), sc(73), sc(64.5), sc(83)], fill=NOTE + (255,))
    d.rectangle([sc(63), sc(58), sc(66.5), sc(78)], fill=NOTE + (255,))
    d.polygon([(sc(66.5), sc(58)), (sc(75), sc(61)), (sc(76), sc(67)), (sc(67), sc(64))],
              fill=NOTE + (255,))
    return tile


def main():
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    STATIC.mkdir(parents=True, exist_ok=True)
    base = _render_base()

    def at(px): return base.resize((px, px), Image.LANCZOS)

    master = at(1024)
    master.save(ICON_DIR / "Singkreis_1024.png")
    master.save(ICON_DIR / "Singkreis.ico",
                sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    at(128).save(STATIC / "favicon.png")

    if shutil.which("sips") and shutil.which("iconutil"):
        with tempfile.TemporaryDirectory() as tmp:
            iconset = Path(tmp) / "Singkreis.iconset"
            iconset.mkdir()
            for px, name in [(16, "16x16"), (32, "16x16@2x"), (32, "32x32"), (64, "32x32@2x"),
                             (128, "128x128"), (256, "128x128@2x"), (256, "256x256"),
                             (512, "256x256@2x"), (512, "512x512"), (1024, "512x512@2x")]:
                at(px).save(iconset / f"icon_{name}.png")
            subprocess.run(["iconutil", "-c", "icns", "-o",
                            str(ICON_DIR / "Singkreis.icns"), str(iconset)], check=True)
        print("✓ macOS-Icon:", ICON_DIR / "Singkreis.icns")
    else:
        print("Hinweis: sips/iconutil fehlen – .icns übersprungen (nur auf macOS nötig).")

    print("✓ Master  :", ICON_DIR / "Singkreis_1024.png")
    print("✓ Windows :", ICON_DIR / "Singkreis.ico")
    print("✓ Favicon :", STATIC / "favicon.png")


if __name__ == "__main__":
    main()

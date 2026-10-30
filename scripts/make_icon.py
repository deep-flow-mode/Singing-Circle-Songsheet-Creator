"""Erzeugt das App-Icon aus dem Logo-Symbol von deep flow mode in allen Formaten.

Quelle:  assets/icon/logo-symbol.png (logo-24-icon.png, transparenter Hintergrund)

Ausgaben:
  assets/icon/Singkreis_1024.png            – Master (PNG)
  assets/icon/Singkreis.icns                – macOS (via iconutil, falls vorhanden)
  Singkreis.app/Contents/Resources/...icns  – Icon der Doppelklick-App
  assets/icon/Singkreis.ico                 – Windows
  static/favicon.png                        – Browser-Tab

Aufruf:  ./venv/bin/python scripts/make_icon.py
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ICON_DIR = ROOT / "assets" / "icon"
SOURCE = ICON_DIR / "logo-symbol.png"
APP_ICNS = ROOT / "Singkreis.app" / "Contents" / "Resources" / "Singkreis.icns"
STATIC = ROOT / "static"


def main():
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    STATIC.mkdir(parents=True, exist_ok=True)
    base = Image.open(SOURCE).convert("RGBA")

    def at(px): return base.resize((px, px), Image.LANCZOS)

    master = at(1024)
    master.save(ICON_DIR / "Singkreis_1024.png")
    master.save(ICON_DIR / "Singkreis.ico",
                sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    at(128).save(STATIC / "favicon.png")

    if shutil.which("iconutil"):
        with tempfile.TemporaryDirectory() as tmp:
            iconset = Path(tmp) / "Singkreis.iconset"
            iconset.mkdir()
            for px, name in [(16, "16x16"), (32, "16x16@2x"), (32, "32x32"), (64, "32x32@2x"),
                             (128, "128x128"), (256, "128x128@2x"), (256, "256x256"),
                             (512, "256x256@2x"), (512, "512x512"), (1024, "512x512@2x")]:
                at(px).save(iconset / f"icon_{name}.png")
            subprocess.run(["iconutil", "-c", "icns", "-o",
                            str(ICON_DIR / "Singkreis.icns"), str(iconset)], check=True)
        shutil.copyfile(ICON_DIR / "Singkreis.icns", APP_ICNS)
        APP_ICNS.parent.parent.parent.touch()   # Finder soll das neue Icon übernehmen
        print("✓ macOS-Icon:", ICON_DIR / "Singkreis.icns", "+ Singkreis.app")
    else:
        print("Hinweis: iconutil fehlt – .icns übersprungen (nur auf macOS nötig).")

    print("✓ Master  :", ICON_DIR / "Singkreis_1024.png")
    print("✓ Windows :", ICON_DIR / "Singkreis.ico")
    print("✓ Favicon :", STATIC / "favicon.png")


if __name__ == "__main__":
    main()

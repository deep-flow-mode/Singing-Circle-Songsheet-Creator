#!/bin/bash
# Doppelklick-Starter für macOS.
# Richtet beim ersten Mal automatisch alles ein und startet danach das Tool.
# Funktioniert auch, wenn der Ordner auf einen anderen Mac kopiert wurde:
# eine nicht passende/kaputte Umgebung wird automatisch neu aufgebaut.
cd "$(dirname "$0")" || exit 1

# Falls aus dem Internet geladen: macOS-Quarantäne dieses Ordners entfernen (Gatekeeper).
# Ohne macOS/xattr passiert nichts – etwaige Fehler werden ignoriert.
xattr -dr com.apple.quarantine "$PWD" 2>/dev/null

PYBIN="venv/bin/python"

# Prüft, ob die Python-Umgebung vorhanden UND lauffähig ist (alle Pakete importierbar).
venv_ok() {
  [ -x "$PYBIN" ] && "$PYBIN" -c "import flask, docx, openpyxl, qrcode, PIL" >/dev/null 2>&1
}

if ! venv_ok; then
  echo "Richte die Python-Umgebung ein (einmalig, benötigt Internet) ..."
  rm -rf venv
  if command -v python3 >/dev/null 2>&1; then PY="python3"; else PY="python"; fi
  if ! "$PY" -m venv venv; then
    echo
    echo "FEHLER: Python 3 wurde nicht gefunden."
    echo "Bitte Python 3 installieren: https://www.python.org/downloads/"
    read -r -p "Mit Enter schließen ..."
    exit 1
  fi
  "$PYBIN" -m pip install --upgrade pip >/dev/null
  if ! "$PYBIN" -m pip install -r requirements.txt; then
    echo "FEHLER bei der Installation der Pakete."
    read -r -p "Mit Enter schließen ..."
    exit 1
  fi
fi

if [ ! -f data/songs.db ]; then
  if [ -f "Daten zum einlesen/Songtabelle.xlsx" ]; then
    echo "Baue die Datenbank erstmalig aus den Quelldateien auf ..."
    "$PYBIN" -m app.build_db
  else
    echo "Erstelle eine leere Lieder-Datenbank ..."
    "$PYBIN" -c "from app.db import init_db; init_db()"
  fi
fi

export SINGKREIS_OPEN_BROWSER=1
echo "Starte das Singkreis-Tool ... (zum Beenden: Strg+C)"
"$PYBIN" run.py

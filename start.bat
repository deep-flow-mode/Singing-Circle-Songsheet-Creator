@echo off
REM Doppelklick-Starter fuer Windows.
REM Richtet beim ersten Mal automatisch alles ein und startet danach das Tool.
REM Voraussetzung: Python 3 ist installiert (https://www.python.org/downloads/,
REM bei der Installation "Add Python to PATH" anhaken).
cd /d "%~dp0"

set "PYEXE=venv\Scripts\python.exe"

REM Vorhandene Umgebung pruefen (laeuft sie?). Wenn nicht: verwerfen und neu bauen.
if exist "%PYEXE%" (
  "%PYEXE%" -c "import flask, docx, openpyxl, qrcode, PIL" >nul 2>&1
  if errorlevel 1 rmdir /s /q venv
)

if not exist "%PYEXE%" (
  echo Richte die Python-Umgebung ein ^(einmalig, benoetigt Internet^) ...
  where py >nul 2>&1
  if errorlevel 1 ( python -m venv venv ) else ( py -3 -m venv venv )
  if not exist "%PYEXE%" (
    echo.
    echo FEHLER: Python 3 wurde nicht gefunden.
    echo Bitte Python 3 installieren: https://www.python.org/downloads/
    echo Wichtig: bei der Installation "Add Python to PATH" anhaken.
    pause
    exit /b 1
  )
  "%PYEXE%" -m pip install --upgrade pip >nul
  "%PYEXE%" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo FEHLER bei der Installation der Pakete.
    pause
    exit /b 1
  )
)

if not exist "data\songs.db" (
  echo Erstelle eine leere Lieder-Datenbank ...
  "%PYEXE%" -c "from app.db import init_db; init_db()"
)

set SINGKREIS_OPEN_BROWSER=1
echo Starte das Singkreis-Tool ... (zum Beenden: Strg+C, dann Fenster schliessen)
"%PYEXE%" run.py
pause

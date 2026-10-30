# Singkreis Sheet Erstellungs-Tool

Lokales Werkzeug zum **Verwalten von Liedern** und **Drucken von Liedzetteln**.
Alles läuft offline auf deinem Rechner; deine Daten liegen in diesem Ordner.

> **Hinweis zu dieser (geteilten) Version:** Dies ist die frei teilbare Fassung des Tools und wird mit einer
> **leeren Lieder-Datenbank** ausgeliefert. Beim ersten Start ist die Liste leer – lege deine Lieder einfach
> über „➕ Neues Lied" an. Es sind bewusst **keine Liedtexte** enthalten.

## Herunterladen von GitHub

**Für alle (einfachster Weg):** Oben auf der Repo-Seite den grünen Knopf **„Code"** anklicken →
**„Download ZIP"**. Die geladene ZIP-Datei per Doppelklick **entpacken** – fertig. Danach weiter bei „Schnellstart".

**Für Technische (empfohlen, ganz ohne Sicherheitsmeldung):** im Terminal klonen – dabei setzt macOS
keine „Quarantäne", und die Startdateien bleiben ausführbar:
```bash
git clone <URL-dieses-Repos>.git
```

> **Warum kommt beim Start eine Sicherheitsmeldung?** Aus dem Internet geladene Dateien (besonders per
> „Download ZIP") markiert macOS als „Quarantäne". Deshalb erscheint beim ersten Start die Meldung
> „… kann nicht auf Schadsoftware geprüft werden". Das ist **normal** und **keine** echte Schadsoftware
> (das Tool ist nur nicht von Apple signiert). Wie du es einmalig freigibst, steht gleich unten.

## Schnellstart

**macOS – Doppelklick:**
Doppelklick auf die App **`Singkreis`** (`Singkreis.app`, mit dem deep-flow-mode-Logo) – oder auf **`start.command`**.
Beim ersten Mal richtet sich alles ein (Umgebung + Pakete) und der Browser öffnet automatisch
`http://127.0.0.1:5001`. Beenden: im Terminalfenster **Strg+C** drücken.

> **macOS meldet „nicht verifiziert" bzw. „kann nicht auf Schadsoftware geprüft werden"?**
> Das ist normal (das Tool ist nicht von Apple signiert) – **keine** echte Schadsoftware. So gibst du es **einmalig** frei:
> 1. Doppelklick auf **`Singkreis`** (oder `start.command`) → die Meldung mit **„Fertig"** schließen.
> 2. **Systemeinstellungen → Datenschutz & Sicherheit** öffnen → ganz nach unten scrollen →
>    beim Hinweis auf „Singkreis" den Knopf **„Dennoch öffnen"** klicken und bestätigen.
> 3. Nochmal doppelklicken → jetzt startet es. *(Ältere macOS: einfach **Rechtsklick** auf die App → **„Öffnen"**.)*
>
> Beim ersten erfolgreichen Start entfernt das Tool die „Quarantäne" des Ordners selbst – weitere Starts laufen dann ohne Nachfrage.

> **Windows:** Meldet „Der Computer wurde durch Windows geschützt", auf **„Weitere Informationen" → „Trotzdem ausführen"** klicken.

**Windows – Doppelklick:**
Doppelklick auf **`start.bat`**. Gleicher Ablauf. Voraussetzung: **Python 3** ist installiert
(siehe Abschnitt „Auf anderen Rechner mitnehmen").

**Variante für Fachleute (Terminal):**
```bash
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
./venv/bin/python run.py            # -> http://127.0.0.1:5001
```

## Bedienung

**Lieder ansehen & suchen:** Auf der Startseite alle Lieder mit Nummer, Titel und
Vorschau. Oben das Suchfeld (durchsucht Titel **und** Liedtext), darunter Filter.
Klick auf eine Zeile → ganzer Liedtext.

**Lied anlegen / bearbeiten / löschen:**
- **Neu:** Kachel „➕ Neues Lied" → Nummer (Vorschlag, überschreibbar), Titel, Text → *Speichern*.
- **Bearbeiten:** in der Einzelansicht oder Zeile „✏️ Bearbeiten" (auch für die 15 noch fehlenden Texte).
- **Frühere Versionen:** Jede Änderung sichert automatisch den vorherigen Stand. In der Einzelansicht erscheint
  unten **„🕘 Frühere Versionen"** mit Datum. Eine Version kannst du **ansehen**, per **„🔍 Vergleichen"**
  farbig sehen, was sich geändert hat (− entfernt / + neu), und mit **„↩️ Wiederherstellen"** zurückholen –
  der aktuelle Stand wird dabei selbst als Version gesichert, du verlierst also nichts.
- **Löschen:** in der Einzelansicht „🗑 Löschen" (mit Sicherheitsabfrage).

**Liedzettel (Singkreis Sheet) erstellen:**
1. In der Übersicht die gewünschten Lieder **anhaken** (die Auswahl bleibt auch beim Suchen erhalten).
2. Unten **„🎵 Singkreis Sheet erstellen"** klicken.
3. **Reihenfolge** per ↑ ↓ festlegen (✕ entfernt ein Lied), **Überschrift** und **Datum** eingeben.
4. **„Singkreis Sheet erstellen"** → es entsteht eine **A4-Word-Datei** (2 Spalten, Schrift automatisch so groß wie
   möglich – 20 bis 17 pt, Ziel 2 Seiten –, Titel + Datum oben, auf Seite 1 unten vier Platzhalter-QR-Codes (siehe „QR-Codes im Fußbereich anpassen“) und eine Seitenzahl „Seite X von Y").
   Reichen selbst bei 17 pt keine 3 Seiten, warnt das Tool vorher und du entscheidest.
5. Datei **herunterladen** – wahlweise als **Word** oder als **PDF** (der PDF-Export nutzt Microsoft Word und
   ist nur auf dem Mac mit installiertem Word verfügbar). Die Dateien liegen auch im Ordner `Singkreis Sheets/`.

## Was ist wo?

| Ort | Inhalt |
|-----|--------|
| `data/songs.db` | die SQLite-Datenbank (deine Lieder) |
| `Singkreis Sheets/` | erzeugte Liedzettel (.docx) |
| `assets/qr/` | erzeugte QR-Bilder; der Ordner ist nicht im Repo und entsteht beim ersten Sheet (siehe „QR-Codes im Fußbereich anpassen“) |
| `assets/icon/` | App-Icons (`.icns` für macOS, `.ico` für Windows) – neu erzeugbar mit `scripts/make_icon.py` |
| `assets/logo/` | dein Logo fürs Kopfband – einfach eine Bilddatei hineinlegen (siehe „Eigenes Logo") |
| `Singkreis.app` · `start.command` · `start.bat` | Doppelklick-Starter (macOS-App · macOS · Windows) |
| `app/`, `templates/`, `static/` | Programmcode & Web-Oberfläche |

## Datenmodell (Tabelle `songs`)

`liednummer` · `liedtitel` · `liedtext` (mehrzeilig) · `tonart` (in DB, im Tool ausgeblendet) ·
`quelle` · `status` · `notiz` · Zeitstempel.

## Sprache und Dark Mode

Oben rechts schaltest du die Oberfläche zwischen **Deutsch und Englisch (DE/EN)** um und wechselst per
Mond/Sonne zwischen **hell und dunkel**. Beides merkt sich der Browser. Solange du nichts gewählt hast, richtet sich
hell/dunkel nach deinem Betriebssystem. Übersetzt wird nur das Tool – **Liedtitel und Liedtexte bleiben unverändert**.
Der neue Liedzettel übernimmt die eingestellte Sprache bei Seitenzahl und Datum.

## Eigenes Logo im Kopfband

Oben links im Tool steht dein Logo und daneben die Überschrift **„Liederverwaltung"**.

- **Logo einsetzen/ändern:** eine Bilddatei (PNG/JPG/SVG …) in den Ordner **`assets/logo/`** legen
  (per Finder hineinziehen). Die **zuletzt hineingelegte** Datei wird verwendet – Name/Format egal.
  Eine zweite Datei namens `<name>-dark.<endung>` wird im Dark Mode gezeigt.
  **Weiße (oder transparente) Ränder werden automatisch weggeschnitten** – du musst nichts zuschneiden.
  Danach Browser-Seite neu laden (das Tool muss nicht neu starten).
- **Kein Logo vorhanden?** Dann zeigt das Kopfband den Schriftzug **deep · flow · mode** in den drei Markenfarben.
- Die **Farben des Tools** (Navy, Gold, Terrakotta) stammen aus dem Logo und sind zentral in
  `static/style.css` ganz oben (`:root`) hinterlegt.

## Auf anderen Rechner mitnehmen (Mac oder Windows)

Den **ganzen Projektordner kopieren** (USB-Stick, Cloud …). Wichtig:

- Den Unterordner **`venv/` nicht mitkopieren** (oder einfach löschen) – er passt nur zum ursprünglichen
  Rechner und wird beim ersten Start automatisch neu erstellt.
- Auf dem Zielrechner muss **Python 3** installiert sein:
  - **macOS:** meist schon vorhanden; sonst von <https://www.python.org/downloads/>.
  - **Windows:** von <https://www.python.org/downloads/> – bei der Installation **„Add Python to PATH" anhaken**.
- Der **erste Start braucht einmalig Internet** (lädt die Pakete). Danach läuft alles offline.
- Starten: macOS per **`Singkreis`-App** bzw. **`start.command`**, Windows per **`start.bat`**.
  Eine nicht passende Umgebung wird dabei automatisch erkannt und neu aufgebaut.

> Hinweis: Eine fertige Programmdatei **ohne** Python-Installation (echte Standalone-App) ist nicht enthalten –
> die müsste je Betriebssystem separat gebaut werden. Die Start-Skripte sind der wartbare Weg für Mac **und** Windows.

## QR-Codes im Fußbereich anpassen

Auf der ersten Seite jedes Liedzettels stehen unten vier QR-Codes. In dieser Version sind das **Platzhalter**: Sie
zeigen auf `example.com` und führen zu keinem echten Kanal. Beschriftet sind sie mit Instagram, Infos (Signal),
Infos (Telegram) und Community (Telegram). Die Bilder liegen nicht im Repo, das Tool erzeugt sie beim ersten Sheet in
`assets/qr/`.

Deine eigenen Links trägst du in [`app/config.py`](app/config.py) unter `QR_LINKS` ein
(Reihenfolge = links → rechts). Beim nächsten Sheet werden die QR-Bilder automatisch neu erzeugt.

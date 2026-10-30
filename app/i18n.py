"""Deutsch/Englisch-Umschaltung der Bedienoberfläche.

Die Texte stehen deutsch im Code, EN enthält die englische Fassung. Übersetzt wird nur das
Tool selbst – Liedtitel und Liedtexte bleiben immer so, wie sie in der Datenbank stehen.
"""
from flask import has_request_context, request

LANGS = ("de", "en")


def current_lang() -> str:
    if has_request_context():
        lang = request.cookies.get("lang")
        if lang in LANGS:
            return lang
    return "de"


def _(text: str, **values) -> str:
    if current_lang() == "en":
        text = EN.get(text, text)
    return text.format(**values) if values else text


EN = {
    # Grundgerüst
    "Liederverwaltung": "Song Manager",
    "Sprache": "Language",
    "Hell/Dunkel umschalten": "Switch light/dark",
    "Lokale Datenbank": "Local database",
    "Installationshilfe": "Installation help",
    "← zurück zur Übersicht": "← back to overview",
    "← zurück": "← back",
    "Singkreis": "Singing Circle",
    "Seite ": "Page ",
    " von ": " of ",
    # Übersicht
    "Lieder": "Songs",
    "mit Text": "with lyrics",
    "ohne Text": "without lyrics",
    "Neues Lied": "New song",
    "Suchen in Titel & Liedtext …": "Search titles & lyrics …",
    "Suchen": "Search",
    "Suche löschen": "Clear search",
    "Alle": "All",
    "Mit Text": "With lyrics",
    "Ohne Text": "Without lyrics",
    "{n} Lieder angezeigt": "{n} songs shown",
    " · Suche nach „{q}“": " · search for “{q}”",
    "· Lieder anhaken, dann unten „Sheet erstellen“": "· tick songs, then “Create song sheet” below",
    "Nr": "No.",
    "Titel": "Title",
    "Vorschau": "Preview",
    "kein Text": "no lyrics",
    "— Noch kein Liedtext —": "— No lyrics yet —",
    "✏️ Bearbeiten": "✏️ Edit",
    "Einzelansicht ↗": "Single view ↗",
    "Keine Lieder gefunden.": "No songs found.",
    "ausgewählt": "selected",
    "🎵 Singkreis Sheet erstellen": "🎵 Create song sheet",
    "Auswahl leeren": "Clear selection",
    # Einzelansicht
    "— Noch kein Liedtext — über „Bearbeiten“ ergänzen.": "— No lyrics yet — add them via “Edit”.",
    "📄 Quelle: {quelle}": "📄 Source: {quelle}",
    "Dieses Lied wirklich löschen?": "Really delete this song?",
    "🗑 Löschen": "🗑 Delete",
    "🕘 Frühere Versionen": "🕘 Earlier versions",
    "Bei jeder Änderung wird der vorherige Stand automatisch gesichert.":
        "Every change automatically saves the previous state.",
    "— ohne Text —": "— no lyrics —",
    "ansehen ↗": "view ↗",
    # Formular
    "Lied bearbeiten": "Edit song",
    "Neues Lied anlegen": "Add new song",
    "Liednummer": "Song number",
    "z. B. {n}": "e.g. {n}",
    "Titel *": "Title *",
    "Liedtext": "Lyrics",
    "Liedtext hier eingeben … (Zeilenumbrüche bleiben erhalten)": "Enter lyrics here … (line breaks are kept)",
    "Speichern": "Save",
    "Abbrechen": "Cancel",
    "Bitte einen Titel eingeben.": "Please enter a title.",
    # Frühere Version
    "Frühere Version": "Earlier version",
    "← zurück zum Lied „{titel}“": "← back to song “{titel}”",
    "🕘 Frühere Version – gesichert am <b>{wann}</b>. Du kannst sie ansehen, mit dem aktuellen Stand vergleichen oder wiederherstellen.":
        "🕘 Earlier version – saved on <b>{wann}</b>. You can view it, compare it with the current state or restore it.",
    "— Diese Fassung hatte keinen Liedtext —": "— This version had no lyrics —",
    "Vergleich ausblenden": "Hide comparison",
    "🔍 Mit aktueller Fassung vergleichen": "🔍 Compare with current version",
    "Diese frühere Fassung wiederherstellen?\n\nDer aktuelle Stand wird dabei automatisch als Version gesichert – du kannst also nichts verlieren.":
        "Restore this earlier version?\n\nThe current state is saved automatically as a version, so you can't lose anything.",
    "↩️ Diese Version wiederherstellen": "↩️ Restore this version",
    "← zurück zum aktuellen Stand": "← back to current state",
    "🔍 Vergleich: diese Version → aktueller Stand": "🔍 Comparison: this version → current state",
    "− entfernt": "− removed",
    "+ hinzugekommen": "+ added",
    "gegenüber dieser alten Fassung.": "compared with this old version.",
    "Kein Unterschied – diese Fassung ist identisch mit dem aktuellen Stand.":
        "No difference – this version is identical to the current state.",
    # Sheet zusammenstellen
    "Singkreis Sheet erstellen": "Create song sheet",
    "Keine Lieder ausgewählt. Gehe zur <a href=\"/\">Übersicht</a>, hake Lieder an und klicke „Singkreis Sheet erstellen“.":
        "No songs selected. Go to the <a href=\"/\">overview</a>, tick some songs and click “Create song sheet”.",
    "Überschrift / Titel *": "Heading / title *",
    "z. B. Singkreis im Juni": "e.g. Singing circle in June",
    "Datum": "Date",
    "{n} Lieder · Reihenfolge mit ↑ ↓ ändern, ✕ entfernt ein Lied:": "{n} songs · change the order with ↑ ↓, ✕ removes a song:",
    "nach oben": "move up",
    "nach unten": "move down",
    "entfernen": "remove",
    "Mindestens ein Lied muss bleiben.": "At least one song must remain.",
    "Keine Lieder ausgewählt.": "No songs selected.",
    # Warnhinweis
    "⚠️ Mehr als {n} Seiten": "⚠️ More than {n} pages",
    "← zurück zur Auswahl": "← back to selection",
    "Die {anzahl} ausgewählten Lieder passen auch bei der kleinsten Schrift ({font} pt) nicht auf {n} Seiten, sondern brauchen <b>{pages} Seiten</b>.":
        "Even at the smallest font size ({font} pt), the {anzahl} selected songs don't fit on {n} pages. They need <b>{pages} pages</b>.",
    "Du kannst das Sheet trotzdem mit {pages} Seiten erstellen oder zurückgehen und einzelne Lieder entfernen.":
        "You can still create the sheet with {pages} pages, or go back and remove some songs.",
    "Trotzdem mit {pages} Seiten erstellen": "Create with {pages} pages anyway",
    "Zurück & Lieder entfernen": "Back & remove songs",
    # Fertig
    "Sheet erstellt": "Sheet created",
    "✅ Sheet erstellt": "✅ Sheet created",
    "mit <b>{n}</b> Liedern.": "with <b>{n}</b> songs.",
    "Schriftgröße {font} pt · {pages} Seite(n) · gespeichert im Ordner": "Font size {font} pt · {pages} page(s) · saved in the folder",
    "als": "as",
    "⬇️ Word herunterladen": "⬇️ Download Word",
    "⬇️ PDF herunterladen": "⬇️ Download PDF",
    "Zur Übersicht": "To overview",
    "⏳ PDF wird erstellt – Word öffnet sich dafür kurz im Hintergrund. Einen Moment bitte…":
        "⏳ Creating PDF – Word opens briefly in the background. One moment please…",
    "Ein PDF-Export ist hier nicht verfügbar (dafür wird Microsoft Word auf macOS benötigt). Die Word-Datei lässt sich in Word oder Pages öffnen und dort als PDF speichern.":
        "PDF export isn't available here (it needs Microsoft Word on macOS). You can open the Word file in Word or Pages and save it as a PDF there.",
    "Tipp: Datei in Word/Pages öffnen, prüfen und drucken.": "Tip: open the file in Word/Pages, check it and print.",
    # PDF-Fehler
    "PDF-Export": "PDF export",
    "PDF konnte nicht erstellt werden": "The PDF could not be created",
    "Beim ersten Mal fragt macOS, ob das Tool „Microsoft Word“ steuern darf – bitte einmal erlauben. Alternativ die Word-Datei öffnen und dort als PDF speichern.":
        "The first time, macOS asks whether the tool may control “Microsoft Word” – please allow this once. Alternatively, open the Word file and save it as a PDF there.",
    "PDF-Export benötigt Microsoft Word auf macOS.": "PDF export needs Microsoft Word on macOS.",
    "Word hat zu lange gebraucht (Zeitüberschreitung).": "Word took too long (timeout).",
    "Die Konvertierung ist fehlgeschlagen. Erlaubt macOS dem Tool, Microsoft Word zu steuern?":
        "The conversion failed. Does macOS allow the tool to control Microsoft Word?",
    # Installationshilfe
    "Installation für Einsteiger": "Installation for beginners",
    "🎵 Installation für Einsteiger": "🎵 Installation for beginners",
    "In wenigen Schritten läuft das Singkreis-Tool auf deinem Mac – ganz ohne Vorkenntnisse. Nimm dir etwa 5 Minuten Zeit und folge einfach den Schritten der Reihe nach.":
        "In just a few steps the tool runs on your Mac – no prior knowledge needed. Take about 5 minutes and simply follow the steps in order.",
    "Voraussetzung: Python 3": "Requirement: Python 3",
    "Das Tool benötigt einmalig „Python 3“ auf dem Rechner. Auf vielen Macs ist es schon vorhanden – falls nicht, lädst du es hier kostenlos herunter:":
        "The tool needs “Python 3” on your computer once. Many Macs already have it – if not, you can download it for free here:",
    "Python 3 sicherstellen": "Make sure you have Python 3",
    "Falls noch nicht vorhanden: die oben verlinkte Seite öffnen, den großen Knopf <b>„Download Python“</b> klicken und den Installer ausführen (einfach durchklicken). Das war's – melden musst du dich nirgends.":
        "If you don't have it yet: open the page linked above, click the big <b>“Download Python”</b> button and run the installer (just click through). That's it – you don't need to sign up anywhere.",
    "Tool von GitHub herunterladen": "Download the tool from GitHub",
    "Auf der GitHub-Seite des Tools den grünen Knopf <span class=\"pill\">Code</span> anklicken – dann hast du zwei Wege:":
        "On the tool's GitHub page, click the green <span class=\"pill\">Code</span> button – then you have two options:",
    "Einfachster Weg": "Easiest way",
    "<span class=\"pill\">Download ZIP</span> wählen. Die Datei landet im Ordner „Downloads“.":
        "Choose <span class=\"pill\">Download ZIP</span>. The file ends up in your “Downloads” folder.",
    "Noch reibungsloser": "Even smoother",
    "Mit der Gratis-App <b>GitHub Desktop</b> auf <b>„Clone“</b> – dann erscheint <b>keine</b> Sicherheitsmeldung, und Schritt 5 entfällt.":
        "Use <b>“Clone”</b> in the free <b>GitHub Desktop</b> app – then <b>no</b> security message appears and you can skip step 5.",
    "Ordner entpacken": "Unzip the folder",
    "Die heruntergeladene ZIP-Datei per <b>Doppelklick</b> entpacken. Es entsteht ein Ordner mit dem Tool.":
        "<b>Double-click</b> the downloaded ZIP file to unzip it. This creates a folder containing the tool.",
    "(Wenn du „Clone“ genutzt hast, ist der Ordner schon fertig – überspringe diesen Schritt.)":
        "(If you used “Clone”, the folder is already there – skip this step.)",
    "Tool starten": "Start the tool",
    "Den Ordner öffnen und <b>Doppelklick</b> auf die App <span class=\"pill\">Singkreis</span> (mit dem Logo als Symbol) – alternativ auf <span class=\"pill\">start.command</span>.":
        "Open the folder and <b>double-click</b> the <span class=\"pill\">Singkreis</span> app (with the logo as its icon) – or <span class=\"pill\">start.command</span>.",
    "Beim <b>ersten</b> Start richtet sich alles automatisch ein (kurz Internet nötig, ca. 1 Minute). Bitte einfach warten und nicht abbrechen.":
        "On the <b>first</b> start everything sets itself up automatically (needs internet briefly, about 1 minute). Please just wait and don't cancel.",
    "🔒 macOS-Sicherheitsmeldung freigeben": "🔒 Allow the macOS security message",
    "Erscheint „<i>… kann nicht auf Schadsoftware geprüft werden</i>“? Das ist <b>normal</b> (das Tool ist nur nicht von Apple signiert) – <b>keine</b> echte Schadsoftware. So gibst du es <b>einmalig</b> frei:":
        "Do you see “<i>Apple could not verify … is free of malware</i>”? That's <b>normal</b> (the tool just isn't signed by Apple) – it is <b>not</b> actual malware. Here's how to allow it <b>once</b>:",
    "1. Die Meldung mit <b>„Fertig“</b> schließen.<br>2. <b>Systemeinstellungen → Datenschutz &amp; Sicherheit</b> öffnen, ganz nach unten scrollen → beim Hinweis auf „Singkreis“ den Knopf <b>„Dennoch öffnen“</b> anklicken und bestätigen.<br>3. Die App noch einmal doppelklicken → jetzt startet sie.":
        "1. Close the message with <b>“Done”</b>.<br>2. Open <b>System Settings → Privacy &amp; Security</b>, scroll all the way down → next to the note about “Singkreis”, click <b>“Open Anyway”</b> and confirm.<br>3. Double-click the app again → now it starts.",
    "Ab jetzt merkt sich der Mac das – weitere Starts laufen <b>ohne</b> Nachfrage.":
        "From now on your Mac remembers this – further starts run <b>without</b> asking.",
    "(Ältere macOS: einfach <b>Rechtsklick</b> auf die App → „Öffnen“.)":
        "(Older macOS: just <b>right-click</b> the app → “Open”.)",
    "✅ Fertig!": "✅ Done!",
    "Der Browser öffnet sich automatisch mit dem Tool unter <code>http://127.0.0.1:5001</code>.":
        "Your browser opens the tool automatically at <code>http://127.0.0.1:5001</code>.",
    "Zum <b>Beenden</b>: im schwarzen Terminal-Fenster <b>Strg&nbsp;+&nbsp;C</b> drücken.":
        "To <b>quit</b>: press <b>Ctrl&nbsp;+&nbsp;C</b> in the black Terminal window.",
    "Windows statt Mac?": "Windows instead of Mac?",
    "Fast gleich: ZIP entpacken, dann <span class=\"pill\">start.bat</span> doppelklicken. Meldet Windows „Der Computer wurde durch Windows geschützt“, auf <b>„Weitere Informationen“ → „Trotzdem ausführen“</b> klicken. Voraussetzung ist ebenfalls <b>Python 3</b> – bei dessen Installation unbedingt <b>„Add Python to PATH“</b> anhaken.":
        "Almost the same: unzip, then double-click <span class=\"pill\">start.bat</span>. If Windows says “Windows protected your PC”, click <b>“More info” → “Run anyway”</b>. You also need <b>Python 3</b> – when installing it, be sure to tick <b>“Add Python to PATH”</b>.",
}

-- Konvertiert eine .docx per Microsoft Word zu PDF (für den PDF-Button im Tool).
-- Aufruf:  osascript scripts/docx_to_pdf.applescript "/abs/in.docx" "/abs/out.pdf"
--
-- Die Datei wird über LaunchServices geöffnet ("open -a"). Das umgeht Word's
-- Start-/Galerie-Fenster, das ein scriptgesteuertes "open" bei kaltem Start
-- blockieren kann (dann wäre "active document" = missing value). Anschließend
-- wird gewartet, bis das Dokument wirklich da ist, und als PDF gespeichert.
on run argv
	set inPath to item 1 of argv
	set outPath to item 2 of argv
	set outHFS to (POSIX file outPath) as text
	set docName to do shell script "basename " & quoted form of inPath
	do shell script "open -a 'Microsoft Word' " & quoted form of inPath
	tell application "Microsoft Word"
		-- bis zu ~20 s auf genau DIESES Dokument warten (kalter Word-Start). Nicht "active
		-- document" nehmen: Das kann ein anderes offenes Dokument sein -> PDF vom falschen Zettel.
		set docOpen to false
		repeat 40 times
			if (name of every document) contains docName then
				set docOpen to true
				exit repeat
			end if
			delay 0.5
		end repeat
		if not docOpen then error "Word hat das Dokument nicht geöffnet."
		set d to document docName
		save as d file name outHFS file format format PDF
		delay 0.3
		close d saving no
	end tell
	return "ok"
end run

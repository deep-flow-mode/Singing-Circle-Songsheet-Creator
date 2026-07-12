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
	do shell script "open -a 'Microsoft Word' " & quoted form of inPath
	tell application "Microsoft Word"
		-- bis zu ~20 s auf das geöffnete Dokument warten (kalter Word-Start)
		set d to missing value
		repeat 40 times
			if (count of documents) > 0 then
				set d to active document
				exit repeat
			end if
			delay 0.5
		end repeat
		if d is missing value then error "Word hat das Dokument nicht geöffnet."
		save as d file name outHFS file format format PDF
		delay 0.3
		close d saving no
	end tell
	return "ok"
end run

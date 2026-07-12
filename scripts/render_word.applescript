-- Rendert eine .docx mit Microsoft Word zu PDF (für visuelle Kontrolle).
-- Aufruf:  osascript scripts/render_word.applescript "/pfad/in.docx" "/pfad/out.pdf"
on run argv
	set inPath to item 1 of argv
	set outPath to item 2 of argv
	set outHFS to (POSIX file outPath) as text
	-- Dokument gezielt über den Dateinamen ansprechen ("active document" wäre
	-- falsch, wenn in Word schon ein anderes Dokument offen ist).
	set docName to do shell script "basename " & quoted form of inPath
	tell application "Microsoft Word"
		activate
		open (POSIX file inPath)
		delay 1.5
		set d to document docName
		save as d file name outHFS file format format PDF
		delay 1
		close d saving no
	end tell
	return "ok"
end run

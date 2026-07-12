"""Baut die Datenbank neu auf: Master-Katalog (Songtabelle.xlsx, Blatt '26')
als Grundgerüst, Liedtexte aus den Word-Dateien zugeordnet.

Aufruf:  python -m app.build_db
Achtung: leert die songs-Tabelle und baut sie aus den Quelldateien neu auf.
"""
from __future__ import annotations

from . import db
from .config import REPORT_DIR
from .import_word import load_all_word
from .master import load_master
from .match_master import build_index, match_one

# Methoden, die eine menschliche Kontrolle verdienen
REVIEW = {"fuzzy", "prüfen"}


def build():
    master = load_master()
    words = load_all_word()
    by_full, prepared = build_index(master)

    lyrics_for: dict[str, dict] = {}   # master-titel -> beste Liedtext-Info
    review: list[dict] = []
    unmatched: list[dict] = []

    for w in words:
        m, conf, score = match_one(w["titel"], by_full, prepared)
        if m is None:
            unmatched.append({**w, "conf": conf, "score": score})
            continue
        cand = {"text": w["text"], "quelle": w["quelle"], "conf": conf,
                "score": score, "word_title": w["titel"],
                "nr": m["liednummer"], "master_titel": m["liedtitel"]}
        prev = lyrics_for.get(m["liedtitel"])
        if prev is None or len(cand["text"]) > len(prev["text"]):
            lyrics_for[m["liedtitel"]] = cand
        if conf in REVIEW:
            review.append(cand)

    rows = []
    for m in master:
        ly = lyrics_for.get(m["liedtitel"])
        has = ly is not None and ly["text"].strip() != ""
        if not has:
            status, notiz = "ohne_text", "Noch kein Liedtext importiert"
        elif ly["conf"] in REVIEW:
            status = "pruefen"
            notiz = (f"Liedtext aus {ly['quelle']} · Zuordnung „{ly['conf']}\" "
                     f"({ly['score']:.0f}) · Word-Titel: „{ly['word_title']}\"")
        else:
            status = "aktiv"
            notiz = f"Liedtext aus {ly['quelle']} · Zuordnung {ly['conf']}"
        rows.append({
            "liednummer": m["liednummer"], "liedtitel": m["liedtitel"],
            "liedtext": ly["text"] if ly else "", "tonart": m.get("tonart"),
            "quelle": ly["quelle"] if ly else None, "status": status, "notiz": notiz,
        })

    # Word-Lieder ohne Master-Treffer verlustfrei als eigene Einträge aufnehmen
    for u in unmatched:
        rows.append({
            "liednummer": None, "liedtitel": u["titel"], "liedtext": u["text"],
            "tonart": None, "quelle": u["quelle"], "status": "pruefen",
            "notiz": f"Kein Master-Treffer ({u['conf']}) – Nummer offen",
        })

    return rows, review, unmatched, master, words


def write_db(rows):
    db.init_db()
    conn = db.get_connection()
    try:
        db.clear_songs(conn)
        for r in rows:
            db.insert_song(conn, **r)
        conn.commit()
        return db.stats(conn)
    finally:
        conn.close()


def _nr_key(v):
    s = str(v)
    return int(s) if s.isdigit() else 99999


def write_report(rows, review, unmatched, master, words, st):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    L = ["# Import-/Abgleich-Bericht", ""]
    L.append(f"- Master-Katalog (Blatt '26'): **{len(master)}** Lieder")
    L.append(f"- Liedtext-Vorkommen in Word-Dateien: **{len(words)}**")
    L.append(f"- In der Datenbank: **{st['total']}** Lieder "
             f"(**{st['mit_text']}** mit Text, **{st['ohne_text']}** ohne Text)")
    L.append(f"- Unsichere Zuordnungen (Status 'prüfen'): **{st['pruefen']}**")
    L.append("")

    L.append("## 1) Zu prüfende Zuordnungen (Word → Master)")
    L.append("")
    if review:
        L.append("| Word-Titel | → Master-Titel | Nr | Methode | Score |")
        L.append("|---|---|---|---|---|")
        for r in sorted(review, key=lambda x: x["score"]):
            L.append(f"| {r['word_title']} | {r['master_titel']} | {r['nr']} "
                     f"| {r['conf']} | {r['score']:.0f} |")
    else:
        L.append("_Keine – alle eindeutig zugeordnet._")
    L.append("")

    if unmatched:
        L.append("## 2) Word-Lieder ohne Master-Treffer")
        L.append("")
        for u in unmatched:
            L.append(f"- {u['titel']}  (Datei {u['quelle']})")
        L.append("")

    ohne = [r for r in rows if (r["liedtext"] or "").strip() == "" and r["liednummer"]]
    L.append(f"## 3) Master-Lieder noch ohne Liedtext ({len(ohne)})")
    L.append("")
    for r in sorted(ohne, key=lambda x: _nr_key(x["liednummer"])):
        L.append(f"- Nr {r['liednummer']}: {r['liedtitel']}")
    L.append("")

    path = REPORT_DIR / "import_report.md"
    path.write_text("\n".join(L), encoding="utf-8")
    return path


def main():
    rows, review, unmatched, master, words = build()
    st = write_db(rows)
    rep = write_report(rows, review, unmatched, master, words, st)
    print("=== Datenbank-Aufbau abgeschlossen ===")
    print(f"Master-Katalog : {len(master)} Lieder")
    print(f"Word-Vorkommen : {len(words)}")
    print(f"In Datenbank   : {st['total']} ({st['mit_text']} mit Text, {st['ohne_text']} ohne Text)")
    print(f"Zu prüfen      : {st['pruefen']}")
    print(f"Ohne Master    : {len(unmatched)}")
    print(f"Bericht        : {rep}")


if __name__ == "__main__":
    main()

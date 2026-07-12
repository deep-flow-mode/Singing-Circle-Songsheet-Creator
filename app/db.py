"""SQLite-Datenbankschicht für das Singkreis-Tool."""
from __future__ import annotations

import re
import sqlite3

from .config import DATA_DIR, DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS songs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    liednummer   TEXT,
    liedtitel    TEXT NOT NULL,
    liedtext     TEXT DEFAULT '',
    tonart       TEXT,
    quelle       TEXT,
    status       TEXT DEFAULT 'aktiv',
    notiz        TEXT,
    erstellt_am  TEXT DEFAULT (datetime('now')),
    geaendert_am TEXT DEFAULT (datetime('now'))
);

CREATE VIRTUAL TABLE IF NOT EXISTS songs_fts
    USING fts5(liedtitel, liedtext, content='songs', content_rowid='id');

CREATE TRIGGER IF NOT EXISTS songs_ai AFTER INSERT ON songs BEGIN
    INSERT INTO songs_fts(rowid, liedtitel, liedtext)
    VALUES (new.id, new.liedtitel, new.liedtext);
END;
CREATE TRIGGER IF NOT EXISTS songs_ad AFTER DELETE ON songs BEGIN
    INSERT INTO songs_fts(songs_fts, rowid, liedtitel, liedtext)
    VALUES ('delete', old.id, old.liedtitel, old.liedtext);
END;
CREATE TRIGGER IF NOT EXISTS songs_au AFTER UPDATE ON songs BEGIN
    INSERT INTO songs_fts(songs_fts, rowid, liedtitel, liedtext)
    VALUES ('delete', old.id, old.liedtitel, old.liedtext);
    INSERT INTO songs_fts(rowid, liedtitel, liedtext)
    VALUES (new.id, new.liedtitel, new.liedtext);
END;

-- Versionierung: bei jeder Änderung wird der vorherige Stand hier gesichert.
CREATE TABLE IF NOT EXISTS song_versions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id       INTEGER NOT NULL,
    liednummer    TEXT,
    liedtitel     TEXT,
    liedtext      TEXT,
    tonart        TEXT,
    status        TEXT,
    geaendert_am  TEXT,                                  -- Stand dieser (alten) Fassung
    archiviert_am TEXT DEFAULT (datetime('now','localtime'))  -- wann gesichert/ersetzt
);
CREATE INDEX IF NOT EXISTS idx_song_versions_song ON song_versions(song_id);
"""

# Liedtext gilt als "leer", wenn nach Entfernen von Leerzeichen/Umbrüchen nichts bleibt.
_TEXT_TRIM = "TRIM(liedtext, char(10)||char(13)||char(9)||' ')"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        _sync_status(conn)
        conn.commit()
    finally:
        conn.close()


def _sync_status(conn) -> None:
    """Hält das Kennzeichen 'ohne_text' mit dem tatsächlichen Liedtext im Einklang
    – ohne den Sonderstatus 'pruefen' anzutasten. Korrigiert auch Altbestand."""
    conn.execute(
        f"UPDATE songs SET status='aktiv'     WHERE status='ohne_text' AND {_TEXT_TRIM} <> ''"
    )
    conn.execute(
        f"UPDATE songs SET status='ohne_text' WHERE status='aktiv'     AND {_TEXT_TRIM} =  ''"
    )
    # veralteten Import-Hinweis bei zwischenzeitlich ergänztem Text entfernen
    conn.execute(
        f"UPDATE songs SET notiz=NULL "
        f"WHERE notiz='Noch kein Liedtext importiert' AND {_TEXT_TRIM} <> ''"
    )


def clear_songs(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM songs;")
    # Versionen gehören zu den Liedern – beim Neuaufbau mit entfernen
    try:
        conn.execute("DELETE FROM song_versions;")
    except sqlite3.OperationalError:
        pass  # Tabelle existiert erst nach init_db
    # AUTOINCREMENT-Zähler zurücksetzen, damit IDs wieder bei 1 beginnen
    try:
        conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('songs','song_versions');")
    except sqlite3.OperationalError:
        pass  # sqlite_sequence existiert erst nach dem ersten Insert
    conn.commit()


def clean_liedtext(text: str) -> str:
    """Normalisiert Liedtext fürs Speichern: Windows-Zeilenenden (\\r\\n aus dem
    Browser-Formular) vereinheitlichen, unsichtbaren Leerraum am Zeilenende kappen,
    Leerzeilen am Textende streichen. So druckt das Sheet nur Leerzeilen,
    die im Tool auch sichtbar sind."""
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def insert_song(conn, *, liednummer=None, liedtitel, liedtext="", tonart=None,
                quelle=None, status="aktiv", notiz=None) -> int:
    cur = conn.execute(
        "INSERT INTO songs (liednummer, liedtitel, liedtext, tonart, quelle, status, notiz) "
        "VALUES (?,?,?,?,?,?,?)",
        (liednummer, liedtitel, clean_liedtext(liedtext), tonart, quelle, status, notiz),
    )
    return cur.lastrowid


def count_songs(conn) -> int:
    return conn.execute("SELECT COUNT(*) FROM songs").fetchone()[0]


def stats(conn) -> dict:
    total = count_songs(conn)
    mit = conn.execute(f"SELECT COUNT(*) FROM songs WHERE {_TEXT_TRIM} <> ''").fetchone()[0]
    pruefen = conn.execute("SELECT COUNT(*) FROM songs WHERE status='pruefen'").fetchone()[0]
    return {"total": total, "mit_text": mit, "ohne_text": total - mit, "pruefen": pruefen}


_WORD = re.compile(r"\w+", re.UNICODE)


def _fts_query(q: str) -> str:
    toks = _WORD.findall(q)
    if not toks:
        raise sqlite3.OperationalError("leere Suche")
    return " ".join(f'"{t}"*' for t in toks)


_ORDER = (" ORDER BY (liednummer IS NULL OR liednummer=''), "
          "CAST(liednummer AS INTEGER), liedtitel COLLATE NOCASE")


def list_songs(conn, q: str | None = None):
    q = (q or "").strip()
    if q:
        try:
            return conn.execute(
                "SELECT s.* FROM songs s JOIN songs_fts f ON f.rowid = s.id "
                "WHERE songs_fts MATCH ? ORDER BY rank",
                (_fts_query(q),),
            ).fetchall()
        except sqlite3.OperationalError:
            like = f"%{q}%"
            return conn.execute(
                "SELECT * FROM songs WHERE liedtitel LIKE ? OR liedtext LIKE ? "
                "OR IFNULL(liednummer,'') LIKE ?" + _ORDER,
                (like, like, like),
            ).fetchall()
    return conn.execute("SELECT * FROM songs" + _ORDER).fetchall()


def get_song(conn, song_id: int):
    return conn.execute("SELECT * FROM songs WHERE id = ?", (song_id,)).fetchone()


def update_song(conn, song_id: int, *, liednummer=None, liedtitel, liedtext="") -> None:
    text = clean_liedtext(liedtext)
    old = conn.execute("SELECT * FROM songs WHERE id=?", (song_id,)).fetchone()

    # Vorherigen Stand als Version sichern – nur wenn sich wirklich etwas geändert hat
    if old is not None and (
        (old["liednummer"] or "") != (liednummer or "")
        or (old["liedtitel"] or "") != (liedtitel or "")
        or (old["liedtext"] or "") != text
    ):
        conn.execute(
            "INSERT INTO song_versions "
            "(song_id, liednummer, liedtitel, liedtext, tonart, status, geaendert_am) "
            "VALUES (?,?,?,?,?,?,?)",
            (song_id, old["liednummer"], old["liedtitel"], old["liedtext"],
             old["tonart"], old["status"], old["geaendert_am"]),
        )

    # Status mitführen: Text vorhanden -> 'aktiv' (sofern vorher 'ohne_text'); leer -> 'ohne_text'
    status = old["status"] if old is not None else "aktiv"
    notiz = old["notiz"] if old is not None else None
    if text.strip():
        if status == "ohne_text":
            status = "aktiv"
        # veralteten Import-Hinweis entfernen, sobald ein Text ergänzt wurde
        if notiz == "Noch kein Liedtext importiert":
            notiz = None
    else:
        status = "ohne_text"

    conn.execute(
        "UPDATE songs SET liednummer=?, liedtitel=?, liedtext=?, status=?, notiz=?, "
        "geaendert_am=datetime('now','localtime') WHERE id=?",
        (liednummer, liedtitel, text, status, notiz, song_id),
    )


def delete_song(conn, song_id: int) -> None:
    conn.execute("DELETE FROM song_versions WHERE song_id=?", (song_id,))
    conn.execute("DELETE FROM songs WHERE id=?", (song_id,))


# ---------- Versionen (frühere Stände eines Liedes) ----------

def list_versions(conn, song_id: int):
    return conn.execute(
        "SELECT * FROM song_versions WHERE song_id=? "
        "ORDER BY archiviert_am DESC, id DESC",
        (song_id,),
    ).fetchall()


def get_version(conn, version_id: int):
    return conn.execute(
        "SELECT * FROM song_versions WHERE id=?", (version_id,)
    ).fetchone()


def count_versions(conn, song_id: int) -> int:
    return conn.execute(
        "SELECT COUNT(*) FROM song_versions WHERE song_id=?", (song_id,)
    ).fetchone()[0]


def next_free_number(conn) -> int:
    row = conn.execute(
        "SELECT MAX(CAST(liednummer AS INTEGER)) FROM songs "
        "WHERE liednummer GLOB '[0-9]*'"
    ).fetchone()
    return (row[0] or 0) + 1

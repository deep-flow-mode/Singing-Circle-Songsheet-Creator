"""Flask-Web-App: Visualisierung, Verwaltung (CRUD) und Sheet-Erzeugung."""
import difflib
import io
from datetime import date, datetime

from flask import (Flask, Response, abort, redirect, render_template, request,
                   send_file, url_for)

from . import db
from .config import BASE_DIR, DB_PATH, SHEETS_DIR
from .export_sheet import NeedsMultipage, create_sheet
from .to_pdf import PdfExportError, docx_to_pdf, pdf_export_available


def _preview(text: str, n: int = 100) -> str:
    if not text:
        return ""
    flat = " ".join(text.split())
    return flat[:n] + ("…" if len(flat) > n else "")


def _fmt_dt(s: str) -> str:
    """Zeitstempel 'YYYY-MM-DD HH:MM:SS' -> 'DD.MM.YYYY, HH:MM'."""
    if not s:
        return ""
    try:
        return datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y, %H:%M")
    except ValueError:
        return s


def _diff_lines(alt: str, neu: str):
    """Zeilenweiser Vergleich -> Liste (typ, zeile) mit typ in {'gleich','weg','neu'}.
    'weg' = nur in der alten Fassung, 'neu' = nur im aktuellen Stand."""
    a = (alt or "").rstrip().splitlines()   # Schluss-Leerzeilen ignorieren
    b = (neu or "").rstrip().splitlines()
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if tag == "equal":
            out += [("gleich", ln) for ln in a[i1:i2]]
        else:
            out += [("weg", ln) for ln in a[i1:i2]]
            out += [("neu", ln) for ln in b[j1:j2]]
    return out


def _parse_ids(raw: str):
    out = []
    for part in (raw or "").split(","):
        part = part.strip()
        if part.isdigit():
            out.append(int(part))
    return out


def _load_ordered(ids):
    if not ids:
        return []
    conn = db.get_connection()
    try:
        songs = []
        for i in ids:
            row = db.get_song(conn, i)
            if row:
                songs.append(dict(row))
        return songs
    finally:
        conn.close()


LOGO_EXT = (".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif")


def _find_logo():
    """Zuletzt abgelegte Bilddatei in assets/logo/ (Dateiname/Format egal) –
    so 'gewinnt' eine neu hineingezogene Logo-Datei automatisch."""
    d = BASE_DIR / "assets" / "logo"
    if d.is_dir():
        imgs = [p for p in d.iterdir()
                if p.is_file() and p.suffix.lower() in LOGO_EXT and not p.name.startswith(".")]
        if imgs:
            return max(imgs, key=lambda p: p.stat().st_mtime)
    return None


_logo_cache = {}  # pfad -> (mtime, bytes, mimetype)


def _prepare_logo(p):
    """Schneidet einfarbige (z. B. weiße) bzw. transparente Ränder weg, damit das
    Logo im Kopfband groß und scharf sitzt. SVG wird unverändert durchgereicht."""
    if p.suffix.lower() == ".svg":
        return p.read_bytes(), "image/svg+xml"
    try:
        from PIL import Image, ImageChops
        im = Image.open(p)
        if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
            im = im.convert("RGBA")
            bbox = im.getchannel("A").getbbox()           # transparente Ränder
        else:
            im = im.convert("RGB")
            bg = Image.new("RGB", im.size, im.getpixel((0, 0)))
            diff = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 16 else 0)
            bbox = diff.getbbox()                          # Rand mit Toleranz
        if bbox:
            pad = round((bbox[3] - bbox[1]) * 0.04)        # etwas Luft lassen
            im = im.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                          min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad)))
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        return buf.getvalue(), "image/png"
    except Exception:
        return p.read_bytes(), "image/png"


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    @app.context_processor
    def _globals():
        return {"db_name": DB_PATH.name, "has_logo": _find_logo() is not None}

    @app.after_request
    def _no_cache(resp):
        # Lokales Tool: immer frische Daten zeigen (z. B. Zähler nach dem Bearbeiten),
        # damit der Browser keine veraltete Seite aus dem Zwischenspeicher anzeigt.
        resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.route("/logo")
    def logo():
        p = _find_logo()
        if not p:
            abort(404)
        key, mtime = str(p), p.stat().st_mtime
        hit = _logo_cache.get(key)
        if not hit or hit[0] != mtime:
            data, mime = _prepare_logo(p)
            hit = (mtime, data, mime)
            _logo_cache[key] = hit
        return Response(hit[1], mimetype=hit[2])

    # ---------- Übersicht & Einzelansicht ----------
    @app.route("/")
    def index():
        q = request.args.get("q", "").strip()
        only = request.args.get("filter", "").strip()
        conn = db.get_connection()
        try:
            st = db.stats(conn)
            rows = db.list_songs(conn, q or None)
        finally:
            conn.close()

        songs = []
        for r in rows:
            d = dict(r)
            text = d.get("liedtext") or ""
            d["has_text"] = bool(text.strip())
            d["vorschau"] = _preview(text)
            if only == "mit" and not d["has_text"]:
                continue
            if only == "ohne" and d["has_text"]:
                continue
            songs.append(d)
        return render_template("index.html", songs=songs, stats=st, q=q, only=only)

    @app.route("/lied/<int:song_id>")
    def lied(song_id):
        conn = db.get_connection()
        try:
            row = db.get_song(conn, song_id)
            vrows = db.list_versions(conn, song_id) if row else []
        finally:
            conn.close()
        if not row:
            abort(404)
        versionen = []
        for v in vrows:
            d = dict(v)
            d["wann"] = _fmt_dt(d.get("archiviert_am"))
            d["vorschau"] = _preview(d.get("liedtext") or "")
            versionen.append(d)
        return render_template("detail.html", s=dict(row), versionen=versionen)

    @app.route("/lied/<int:song_id>/version/<int:version_id>")
    def version_ansehen(song_id, version_id):
        conn = db.get_connection()
        try:
            v = db.get_version(conn, version_id)
            row = db.get_song(conn, song_id)
        finally:
            conn.close()
        if not row or not v or v["song_id"] != song_id:
            abort(404)
        v = dict(v)
        s = dict(row)
        v["wann"] = _fmt_dt(v.get("archiviert_am"))
        vergleich = request.args.get("vergleich") == "1"
        diff = _diff_lines(v.get("liedtext") or "", s.get("liedtext") or "") if vergleich else None
        gleich = diff is not None and all(t == "gleich" for t, _ in diff)
        return render_template("version.html", v=v, s=s, vergleich=vergleich,
                               diff=diff, gleich=gleich)

    @app.route("/lied/<int:song_id>/version/<int:version_id>/wiederherstellen", methods=["POST"])
    def version_wiederherstellen(song_id, version_id):
        conn = db.get_connection()
        try:
            v = db.get_version(conn, version_id)
            row = db.get_song(conn, song_id)
            if not row or not v or v["song_id"] != song_id:
                abort(404)
            # update_song sichert den jetzigen Stand automatisch als neue Version
            db.update_song(conn, song_id, liednummer=v["liednummer"],
                           liedtitel=v["liedtitel"], liedtext=v["liedtext"])
            conn.commit()
        finally:
            conn.close()
        return redirect(url_for("lied", song_id=song_id))

    # ---------- Anlegen / Bearbeiten / Löschen ----------
    @app.route("/neu", methods=["GET", "POST"])
    def neu():
        conn = db.get_connection()
        try:
            if request.method == "POST":
                titel = request.form.get("liedtitel", "").strip()
                nr = request.form.get("liednummer", "").strip() or None
                text = request.form.get("liedtext", "")
                if not titel:
                    return render_template("form.html", s=None,
                                           suggested=nr or db.next_free_number(conn),
                                           error="Bitte einen Titel eingeben.")
                new_id = db.insert_song(
                    conn, liednummer=nr, liedtitel=titel, liedtext=text,
                    quelle="manuell",
                    status="aktiv" if text.strip() else "ohne_text",
                    notiz="manuell angelegt")
                conn.commit()
                return redirect(url_for("lied", song_id=new_id))
            suggested = db.next_free_number(conn)
        finally:
            conn.close()
        return render_template("form.html", s=None, suggested=suggested)

    @app.route("/lied/<int:song_id>/bearbeiten", methods=["GET", "POST"])
    def bearbeiten(song_id):
        conn = db.get_connection()
        try:
            row = db.get_song(conn, song_id)
            if not row:
                abort(404)
            if request.method == "POST":
                titel = request.form.get("liedtitel", "").strip()
                nr = request.form.get("liednummer", "").strip() or None
                text = request.form.get("liedtext", "")
                if not titel:
                    return render_template("form.html", s=dict(row),
                                           error="Bitte einen Titel eingeben.")
                db.update_song(conn, song_id, liednummer=nr,
                               liedtitel=titel, liedtext=text)
                conn.commit()
                return redirect(url_for("lied", song_id=song_id))
            s = dict(row)
        finally:
            conn.close()
        return render_template("form.html", s=s)

    @app.route("/lied/<int:song_id>/loeschen", methods=["POST"])
    def loeschen(song_id):
        conn = db.get_connection()
        try:
            db.delete_song(conn, song_id)
            conn.commit()
        finally:
            conn.close()
        return redirect(url_for("index"))

    # ---------- Sheet zusammenstellen & erstellen ----------
    @app.route("/sheet")
    def sheet():
        ids = _parse_ids(request.args.get("ids", ""))
        songs = _load_ordered(ids)
        return render_template("sheet.html", songs=songs,
                               heute=date.today().isoformat(),
                               ids=",".join(str(i) for i in ids))

    @app.route("/sheet/erstellen", methods=["POST"])
    def sheet_erstellen():
        ids = _parse_ids(request.form.get("ids", ""))
        titel = request.form.get("titel", "").strip()
        datum = request.form.get("datum", "").strip()
        allow = request.form.get("mehrseitig") == "1"
        songs = _load_ordered(ids)
        if not songs:
            return redirect(url_for("index"))
        try:
            path, font, pages = create_sheet(songs, titel, datum, allow_multipage=allow)
        except NeedsMultipage as e:
            return render_template("sheet_confirm.html", titel=titel, datum=datum,
                                   ids=",".join(str(i) for i in ids),
                                   pages=e.pages, anzahl=len(songs))
        return render_template("sheet_fertig.html", filename=path.name, titel=titel,
                               datum=datum, font=font, pages=pages, anzahl=len(songs),
                               pdf_available=pdf_export_available())

    @app.route("/sheet/download/<path:filename>")
    def sheet_download(filename):
        p = SHEETS_DIR / filename
        if not p.exists():
            abort(404)
        return send_file(str(p), as_attachment=True)

    @app.route("/sheet/pdf/<path:filename>")
    def sheet_pdf(filename):
        docx = SHEETS_DIR / filename
        if not docx.exists():
            abort(404)
        try:
            pdf = docx_to_pdf(docx)
        except PdfExportError as e:
            return render_template("sheet_pdf_fehler.html", meldung=str(e)), 503
        return send_file(str(pdf), as_attachment=True)

    # ---------- Installationshilfe (Einsteiger) ----------
    @app.route("/installation")
    def installation():
        return render_template("installation.html")

    return app

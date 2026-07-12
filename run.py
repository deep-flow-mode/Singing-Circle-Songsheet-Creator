"""Startet das Singkreis-Tool (lokaler Webserver)."""
import os
import threading
import webbrowser

from app import db
from app.server import create_app

HOST = "127.0.0.1"
PORT = 5001


def main():
    db.init_db()
    app = create_app()
    url = f"http://{HOST}:{PORT}"
    if os.environ.get("SINGKREIS_OPEN_BROWSER", "0") == "1":
        threading.Timer(1.3, lambda: webbrowser.open(url)).start()
    print(f"\n🎵  Singkreis-Tool läuft auf  {url}\n    (Zum Beenden: Strg+C drücken)\n")
    app.run(host=HOST, port=PORT, debug=False)


if __name__ == "__main__":
    main()

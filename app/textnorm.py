"""Titel-Normalisierung für den Abgleich Word <-> Masterliste."""
import re

_PAREN = re.compile(r"\(.*?\)", re.DOTALL)        # Klammerinhalt (Künstler/Version)
_PAREN_GET = re.compile(r"\((.*?)\)", re.DOTALL)
_KEEP = re.compile(r"[^a-z0-9äöüß ]+")
_WS = re.compile(r"\s+")


def _base(s: str) -> str:
    s = (s or "").lower().replace("\xa0", " ")
    return s.replace("’", "'").replace("`", "'").replace("´", "'")


def norm_full(s: str) -> str:
    """Volle Normalform inkl. Klammerinhalt."""
    s = _KEEP.sub(" ", _base(s))
    return _WS.sub(" ", s).strip()


def norm_core(s: str) -> str:
    """Kern-Normalform ohne Klammerinhalt."""
    s = _PAREN.sub(" ", _base(s))
    s = _KEEP.sub(" ", s)
    return _WS.sub(" ", s).strip()


def extract_paren(s: str) -> str:
    """Normalisierter Text aus den Klammern (z.B. der Künstlername)."""
    return norm_full(" ".join(_PAREN_GET.findall(s or "")))

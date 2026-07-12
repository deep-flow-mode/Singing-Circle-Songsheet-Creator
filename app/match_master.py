"""Ordnet Word-Titel den Einträgen der Masterliste zu.

Strategie:
  1. Exakter Voll-Treffer (Titel inkl. Klammer/Künstler identisch) -> sicher.
  2. Sonst: kombinierte Bewertung aller Master-Einträge aus
     Liedname-Ähnlichkeit (Kern ohne Klammer) + Künstler-Ähnlichkeit (Klammer).
     So werden Versionen desselben Liedes (z.B. Mantras mit verschiedenen
     Interpreten) am Künstlernamen unterschieden.
"""
from rapidfuzz import fuzz

from . import textnorm

# Gewichtung Liedname vs. Künstler, wenn beide Seiten einen Künstler haben
W_NAME, W_ARTIST = 0.6, 0.4


def build_index(master: list[dict]):
    by_full: dict[str, list] = {}
    prepared = []
    for m in master:
        by_full.setdefault(textnorm.norm_full(m["liedtitel"]), []).append(m)
        prepared.append({
            "m": m,
            "core": textnorm.norm_core(m["liedtitel"]),
            "art": textnorm.extract_paren(m["liedtitel"]),
        })
    return by_full, prepared


def match_one(word_title: str, by_full, prepared):
    """-> (master_eintrag | None, methode, score)."""
    wf = textnorm.norm_full(word_title)
    if len(by_full.get(wf, [])) == 1:
        return by_full[wf][0], "exakt", 100.0

    wc = textnorm.norm_core(word_title)
    wart = textnorm.extract_paren(word_title)

    scored = []
    for p in prepared:
        name_sim = float(fuzz.token_sort_ratio(wc, p["core"]))
        if wart and p["art"]:
            art_sim = float(fuzz.token_sort_ratio(wart, p["art"]))
            score = W_NAME * name_sim + W_ARTIST * art_sim
        else:
            score = name_sim
        scored.append((score, name_sim, p["m"]))

    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_name, best_m = scored[0]
    ties = sum(1 for s, _, _ in scored if abs(s - best_score) <= 0.5)

    # eindeutiger, praktisch identischer Liedname -> automatisch übernehmen
    if best_name >= 99 and ties == 1:
        return best_m, "kern", round(best_score, 1)
    # mehrere gleich gute Kandidaten, nicht unterscheidbar -> prüfen
    if best_name >= 99 and ties > 1:
        return best_m, "prüfen", round(best_score, 1)
    # gute, aber nicht exakte Ähnlichkeit -> Vorschlag (prüfen)
    if best_score >= 90:
        return best_m, "fuzzy", round(best_score, 1)
    if best_score >= 78:
        return best_m, "prüfen", round(best_score, 1)
    return None, "kein_treffer", round(best_score, 1)

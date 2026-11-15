#!/usr/bin/env python3
"""Deterministic KDP interior checks. Exit 0 = all checks pass, 1 = at least one fails.

Usage: python3 kdp/tools/check_interior.py <interior.pdf> <theme.json>

Checks follow kdp/RULES.md. Nothing is edited. Requires pdftotext, pdffonts, pdfinfo (poppler).
"""
import json
import re
import subprocess
import sys

BANNED = [
    "E. P. Greenwood", "OUR PRESS", "our small press", "by hand", "every book",
    "bestseller",
]
# Developer placeholders: whole word, exact case. A case-insensitive substring
# match on "TODO" flags ordinary Spanish ("Todos los derechos reservados").
BANNED_TOKENS = ["Lorem", "TODO", "PLACEHOLDER"]


def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    pdf, theme_path = sys.argv[1], sys.argv[2]
    theme = json.load(open(theme_path, encoding="utf-8"))
    author = theme.get("author", "").strip()
    text = run(["pdftotext", "-layout", pdf, "-"])
    fonts = run(["pdffonts", pdf])
    info = run(["pdfinfo", pdf])
    results: list[tuple[str, bool, str]] = []

    # 1. author on copyright line
    if not author:
        results.append(("author set in theme", False, "theme author is empty"))
    else:
        ok = re.search(r"Copyright © \d{4} " + re.escape(author) + r"\.", text) is not None
        results.append(("copyright names author", ok, f"author={author!r}"))

    # 2. banned / placeholder text
    hits = [b for b in BANNED if b.lower() in text.lower()]
    hits += [t for t in BANNED_TOKENS if re.search(r"\b" + re.escape(t) + r"\b", text)]
    results.append(("no placeholders or invented claims", not hits, ", ".join(hits) or "none"))

    # 3. fonts embedded
    rows = [ln.split() for ln in fonts.splitlines()[2:] if ln.strip()]
    unembedded = [r[0] for r in rows if len(r) >= 4 and r[-4] == "no"]
    results.append(("all fonts embedded", not unembedded, ", ".join(unembedded) or f"{len(rows)} fonts"))

    # 4. page size 8.5x11 in
    m = re.search(r"Page size:\s+([\d.]+) x ([\d.]+) pts", info)
    size_ok = bool(m) and abs(float(m.group(1)) - 612) < 1 and abs(float(m.group(2)) - 792) < 1
    results.append(("page size 8.5x11 in", size_ok, m.group(0) if m else "not found"))

    # 5. puzzle count matches theme
    n_expected = len(theme.get("puzzles", []))
    # puzzle pages print "<LABEL> N"; solution pages print "<LABEL> N — NAME": expect both for each puzzle.
    # LABEL comes from the theme ("puzzle_label"), default "PUZZLE".
    label = theme.get("puzzle_label", "PUZZLE")
    n_found = len(re.findall(re.escape(label) + r" \d+", text))
    results.append(("puzzle count (pages + solutions)", n_found == 2 * n_expected,
                    f"expected {2 * n_expected}, found {n_found}"))

    # 6. every puzzle word appears in the text (words placed in the grid is checked by the generator's note lines)
    missing_words = []
    for p in theme.get("puzzles", []):
        for w in p.get("words", []):
            if w.upper() not in text.upper():
                missing_words.append(w)
    results.append(("all listed words appear in book", not missing_words,
                    ", ".join(missing_words[:10]) or "none"))

    failed = [r for r in results if not r[1]]
    for name, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}  ({detail})")
    print("READY FOR HUMAN REVIEW" if not failed else f"BLOCKED: {len(failed)} check(s) failed")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())

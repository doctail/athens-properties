#!/usr/bin/env python3
"""Print-ready large-print word-search book for Amazon KDP. Swap the themes
JSON and it's a new book in a new niche -- that's the whole premise: code
generates books at a volume a hand-maker can't match, not a one-off script
for a single title.

Outputs an 8.5x11 interior PDF with front matter, puzzles, and full
solutions. KDP needs a separate cover, either from their free Cover Creator
or generated separately here."""
from __future__ import annotations
import argparse, json, math, os, random, string, unicodedata
from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

PAGE_W, PAGE_H = letter            # 612 x 792 pt  (8.5 x 11 in)
MARGIN = 54                        # 0.75in uniform — safe KDP gutter (<150pg) + roomy large print
GRID_N = 15
DIRS = [(0, 1), (1, 0), (1, 1), (1, -1), (0, -1), (-1, 0), (-1, -1), (-1, 1)]

Cell = tuple[int, int]
Grid = list[list[str]]

def _pick(*cands: str) -> str:
    """First font file that exists: macOS path first, then Linux fallback."""
    for c in cands:
        if os.path.exists(c):
            return c
    raise FileNotFoundError(f"none of these fonts exist: {cands}")


FONTS = {
    "Sans":  _pick("/System/Library/Fonts/Supplemental/Arial.ttf",
                   "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    "SansB": _pick("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                   "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    "MonoB": _pick("/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
                   "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"),
}


# Every visible string of the interior, per language. Keep claims factual:
# nothing about publishers, teams, sales or reviews (kdp/RULES.md).
STRINGS = {
    "en": {
        "find": "FIND THESE WORDS",
        "label": "PUZZLE",
        "solutions": "SOLUTIONS",
        "how_title": "HOW TO PLAY",
        "how_all": [
            "Each puzzle hides a list of words in a grid of letters.", "",
            "Words run in straight lines — across, down, diagonally,",
            "and sometimes backwards.", "",
            "Find every word in the list and circle it in the grid.", "",
            "Stuck? Full solutions are at the back of the book.", "",
            "Take your time. There is no clock. Enjoy the quiet.",
        ],
        "how_forward": [
            "Each puzzle hides a list of words in a grid of letters.", "",
            "Words run only left to right or top to bottom.",
            "Never diagonally, never backwards.", "",
            "Find every word in the list and circle it in the grid.", "",
            "Stuck? Full solutions are at the back of the book.", "",
            "Take your time. There is no clock. Enjoy the quiet.",
        ],
        "copyright": [
            "All rights reserved.", "",
            "No part of this publication may be reproduced, distributed, or",
            "transmitted in any form without the prior written permission of",
            "the author, except for brief quotations in reviews.", "",
            "The puzzles in this book are an original compilation.",
            "Printed editions produced via Amazon KDP.",
        ],
        "review_title": "DID YOU ENJOY THIS BOOK?",
        "review": [
            "",
            "If you enjoyed these puzzles, you can leave a short review on Amazon.",
            "",
            "Even one honest sentence helps other readers find this book.",
            "",
        ],
        "thanks": "Thank you, {author}.",
        "also_title": "ALSO FROM {author}",
        "also_hint": "Search the titles below on Amazon to find them:",
        "about_title": "ABOUT THIS BOOK",
        "about": [
            "",
            "This book is set in large type,",
            "with full solutions at the back.",
            "", "", "",
            "Thank you for spending your time with this book.",
        ],
    },
    "es": {
        "find": "BUSQUE ESTAS PALABRAS",
        "label": "SOPA",
        "solutions": "SOLUCIONES",
        "how_title": "CÓMO SE JUEGA",
        "how_all": [
            "Cada sopa de letras esconde una lista de palabras.", "",
            "Las palabras van en línea recta, en cualquier dirección,",
            "incluso en diagonal o al revés.", "",
            "Busque cada palabra de la lista y enciérrela en la cuadrícula.", "",
            "¿No encuentra una? Las soluciones están al final del libro.", "",
            "Tómese su tiempo. No hay reloj. Disfrute la calma.",
        ],
        "how_forward": [
            "Cada sopa de letras esconde una lista de palabras.", "",
            "Las palabras van solo de izquierda a derecha",
            "o de arriba hacia abajo. Nunca en diagonal ni al revés.",
            "Las palabras aparecen sin tildes.", "",
            "Busque cada palabra de la lista y enciérrela en la cuadrícula.", "",
            "¿No encuentra una? Las soluciones están al final del libro.", "",
            "Tómese su tiempo. No hay reloj. Disfrute la calma.",
        ],
        "copyright": [
            "Todos los derechos reservados.", "",
            "Ninguna parte de esta publicación puede reproducirse, distribuirse",
            "ni transmitirse en ninguna forma sin el permiso previo por escrito",
            "del autor, salvo citas breves en reseñas.", "",
            "Las sopas de letras de este libro son una recopilación original.",
            "Edición impresa producida a través de Amazon KDP.",
        ],
        "review_title": "¿LE GUSTÓ ESTE LIBRO?",
        "review": [
            "",
            "Si disfrutó estas sopas de letras, puede dejar una reseña breve en Amazon.",
            "",
            "Una sola frase sincera ayuda a otros lectores a encontrar este libro.",
            "",
        ],
        "thanks": "Gracias, {author}.",
        "also_title": "OTROS LIBROS DE {author}",
        "also_hint": "Busque estos títulos en Amazon:",
        "about_title": "SOBRE ESTE LIBRO",
        "about": [
            "",
            "Este libro está impreso en letra grande,",
            "con todas las soluciones al final.",
            "", "", "",
            "Gracias por dedicar su tiempo a este libro.",
        ],
    },
}
S = STRINGS["en"]           # set in main() from --lang / theme "lang"
FORWARD = False             # set in main() from --forward-only
FILL = string.ascii_uppercase
FILL_WEIGHTS: list[float] | None = None


def strip_accents(word: str) -> str:
    """Uppercase, accents removed, Ñ kept (Spanish word searches print words without tildes)."""
    out = []
    for ch in word.upper():
        if ch == "Ñ":
            out.append(ch)
            continue
        base = unicodedata.normalize("NFD", ch)
        out.append("".join(x for x in base if not unicodedata.combining(x)))
    return "".join(out)


def register_fonts() -> None:
    for name, path in FONTS.items():
        pdfmetrics.registerFont(TTFont(name, path))


# ---------------- puzzle generation ----------------
FORWARD_DIRS = [(0, 1), (1, 0)]    # left-to-right and top-to-bottom only


def _try_place(grid: Grid, word: str, N: int, dirs: list[tuple[int, int]] = DIRS) -> list[Cell] | None:
    dr, dc = random.choice(dirs)
    r, c = random.randint(0, N - 1), random.randint(0, N - 1)
    cells: list[Cell] = []
    for k, ch in enumerate(word):
        rr, cc = r + dr * k, c + dc * k
        if not (0 <= rr < N and 0 <= cc < N):
            return None
        cur = grid[rr][cc]
        if cur and cur != ch:
            return None
        cells.append((rr, cc))
    for (rr, cc), ch in zip(cells, word):
        grid[rr][cc] = ch
    return cells


def generate_puzzle(words: list[str], N: int = GRID_N,
                    dirs: list[tuple[int, int]] = DIRS) -> tuple[Grid, list[list[Cell]], list[str]]:
    grid: Grid = [["" for _ in range(N)] for _ in range(N)]
    placements: list[list[Cell]] = []
    placed: list[str] = []
    for w in sorted(words, key=len, reverse=True):
        cells = None
        for _ in range(500):
            cells = _try_place(grid, w, N, dirs)
            if cells:
                break
        if cells:
            placements.append(cells)
            placed.append(w)
    for r in range(N):
        for c in range(N):
            if not grid[r][c]:
                grid[r][c] = random.choices(FILL, weights=FILL_WEIGHTS)[0]
    return grid, placements, placed


# ---------------- drawing helpers ----------------
def draw_grid(c: Canvas, grid: Grid, gx: float, gy_top: float, cell: float,
              font_size: float, highlights: list[list[Cell]] | None = None) -> None:
    N = len(grid)
    h = N * cell
    # faint internal gridlines
    c.setLineWidth(0.5)
    c.setStrokeColorRGB(0.86, 0.86, 0.86)
    for i in range(N + 1):
        c.line(gx + i * cell, gy_top, gx + i * cell, gy_top - h)
        c.line(gx, gy_top - i * cell, gx + N * cell, gy_top - i * cell)
    # solution highlighters (drawn UNDER the letters)
    if highlights:
        c.setLineCap(1)
        c.setStrokeColorRGB(1.0, 0.78, 0.20)
        c.setStrokeAlpha(0.5)
        c.setLineWidth(cell * 0.72)
        for cells in highlights:
            (r0, c0), (r1, c1) = cells[0], cells[-1]
            x0, y0 = gx + c0 * cell + cell / 2, gy_top - r0 * cell - cell / 2
            x1, y1 = gx + c1 * cell + cell / 2, gy_top - r1 * cell - cell / 2
            c.line(x0, y0, x1, y1)
        c.setStrokeAlpha(1.0)
        c.setLineCap(0)
    # outer border
    c.setStrokeColorRGB(0.25, 0.25, 0.25)
    c.setLineWidth(1.3)
    c.rect(gx, gy_top - h, N * cell, h)
    # letters
    c.setFillColorRGB(0, 0, 0)
    c.setFont("MonoB", font_size)
    for r in range(N):
        for col in range(N):
            cx = gx + col * cell + cell / 2
            cy = gy_top - r * cell - cell / 2 - font_size * 0.34
            c.drawCentredString(cx, cy, grid[r][col])


def draw_word_list(c: Canvas, words: list[str], gx: float, top_y: float,
                    grid_w: float, cols: int = 3) -> None:
    c.setFillColorRGB(0, 0, 0)
    c.setFont("SansB", 14)
    c.drawCentredString(PAGE_W / 2, top_y, S["find"])
    words = sorted(words)
    rows = math.ceil(len(words) / cols)
    col_w = grid_w / cols
    c.setFont("Sans", 16)
    start_y = top_y - 28
    for i, w in enumerate(words):
        col, row = i // rows, i % rows
        x = gx + col * col_w + 8
        y = start_y - row * 26
        c.drawString(x, y, w)


def footer(c: Canvas, page_no: int) -> None:
    c.setFillColorRGB(0.45, 0.45, 0.45)
    c.setFont("Sans", 9)
    c.drawCentredString(PAGE_W / 2, 34, str(page_no))


# ---------------- pages ----------------
# ---------------- utils ----------------
def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [text]


def front_matter(c: Canvas, title: str, subtitle: str, author: str) -> None:
    # title page: main title (before ": ") big, the rest smaller, then subtitle.
    # Positions follow the line count so long titles never overlap the subtitle.
    main_t, _, tail_t = title.partition(": ")
    c.setFillColorRGB(0.10, 0.10, 0.10)
    y = PAGE_H - 230
    c.setFont("SansB", 30)
    for line in _wrap(main_t.upper(), 16):
        c.drawCentredString(PAGE_W / 2, y, line)
        y -= 38
    if tail_t:
        c.setFont("SansB", 20)
        y -= 6
        for line in _wrap(tail_t.upper(), 28):
            c.drawCentredString(PAGE_W / 2, y, line)
            y -= 28
    y -= 24
    c.setFont("Sans", 15)
    for line in _wrap(subtitle, 40):
        c.drawCentredString(PAGE_W / 2, y, line)
        y -= 22
    y -= 26
    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.setLineWidth(1)
    c.line(PAGE_W / 2 - 80, y, PAGE_W / 2 + 80, y)
    c.setFont("Sans", 13)
    c.drawCentredString(PAGE_W / 2, 120, author)
    c.showPage()

    # copyright page (the first line's exact form is checked by check_interior.py)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.setFont("Sans", 10)
    lines = [("Copyright © 2026 " + author + ".") if author else "Copyright © 2026."] + S["copyright"]
    for i, ln in enumerate(lines):
        c.drawString(MARGIN, PAGE_H - 120 - i * 16, ln)
    c.showPage()

    # how to play
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("SansB", 22)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 140, S["how_title"])
    c.setFont("Sans", 13)
    how = S["how_forward"] if FORWARD else S["how_all"]
    for i, ln in enumerate(how):
        c.drawCentredString(PAGE_W / 2, PAGE_H - 200 - i * 22, ln)
    c.showPage()


def puzzle_page(c: Canvas, idx: int, name: str, grid: Grid, words: list[str],
                 page_no: int, running_title: str) -> None:
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Sans", 10)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 40, running_title)
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("SansB", 12)
    c.drawString(MARGIN, PAGE_H - 64, f"{S['label']} {idx}")
    c.setFont("SansB", 22)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 96, name.upper())

    cell = 30
    N = len(grid)
    grid_w = N * cell
    gx = (PAGE_W - grid_w) / 2
    gy_top = PAGE_H - 122          # grid bottom = 670 - 450 = 220
    draw_grid(c, grid, gx, gy_top, cell, 18)

    draw_word_list(c, words, gx, gy_top - N * cell - 26, grid_w, cols=3)
    footer(c, page_no)
    c.showPage()


def solutions_pages(c: Canvas, solutions: list[tuple[int, str, Grid, list[list[Cell]]]],
                     page_no_start: int, running_title: str) -> int:
    page_no = page_no_start
    # section divider
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("SansB", 30)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 10, S["solutions"])
    footer(c, page_no)
    c.showPage()
    page_no += 1

    cell = 17
    N = GRID_N
    grid_w = N * cell
    gx = (PAGE_W - grid_w) / 2
    slots_top = [PAGE_H - 96, PAGE_H - 96 - 320]   # two solutions per page
    for i in range(0, len(solutions), 2):
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.setFont("Sans", 10)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 40, running_title)
        for slot, sol in zip(slots_top, solutions[i:i + 2]):
            idx, name, grid, placements = sol
            c.setFillColorRGB(0.1, 0.1, 0.1)
            c.setFont("SansB", 13)
            c.drawCentredString(PAGE_W / 2, slot, f"{S['label']} {idx}  —  {name.upper()}")
            draw_grid(c, grid, gx, slot - 16, cell, 10, highlights=placements)
        footer(c, page_no)
        c.showPage()
        page_no += 1
    return page_no


def back_matter(c: Canvas, author: str, also_from: list[dict]) -> None:
    """Back-matter pages — the highest-leverage thing for a new KDP book:
      1. Review request (lifts review count = lifts ranking).
      2. 'Also from [author]' cross-sell (when one book sells, the others get free shelf space).
      3. Short 'About' note.
    """
    # --- review request ---
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("SansB", 28)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 200, S["review_title"])
    c.setFont("Sans", 14)
    lines = S["review"] + ([S["thanks"].format(author=author)] if author else [])
    for i, ln in enumerate(lines):
        c.drawCentredString(PAGE_W / 2, PAGE_H - 260 - i * 24, ln)
    # decorative rule
    c.setStrokeColorRGB(0.5, 0.55, 0.5)
    c.setLineWidth(1)
    c.line(PAGE_W / 2 - 80, PAGE_H - 470, PAGE_W / 2 + 80, PAGE_H - 470)
    # five star icons drawn as polygons (no font glyph dependency)
    c.setFillColorRGB(0.95, 0.78, 0.12)
    c.setStrokeColorRGB(0.7, 0.55, 0.08)
    c.setLineWidth(0.6)
    import math as _m
    star_y = PAGE_H - 510
    spacing = 32
    total_w = spacing * 4
    start_x = PAGE_W / 2 - total_w / 2
    R = 11
    for i in range(5):
        cx = start_x + i * spacing
        pts = []
        for k in range(10):
            ang = -_m.pi / 2 + k * _m.pi / 5
            r = R if k % 2 == 0 else R * 0.45
            pts.append((cx + r * _m.cos(ang), star_y + r * _m.sin(ang)))
        p = c.beginPath()
        p.moveTo(*pts[0])
        for pt in pts[1:]:
            p.lineTo(*pt)
        p.close()
        c.drawPath(p, stroke=1, fill=1)
    c.showPage()

    # --- also from <author> (series cross-sell) ---
    if also_from:
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.setFont("SansB", 26)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 180, S["also_title"].format(author=author.upper()))
        c.setStrokeColorRGB(0.5, 0.55, 0.5)
        c.line(PAGE_W / 2 - 80, PAGE_H - 200, PAGE_W / 2 + 80, PAGE_H - 200)
        c.setFont("Sans", 13)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 230, S["also_hint"])
        y = PAGE_H - 290
        for entry in also_from:
            c.setFont("SansB", 14)
            c.drawCentredString(PAGE_W / 2, y, entry.get("title", ""))
            sub = entry.get("subtitle", "")
            if sub:
                c.setFont("Sans", 11)
                c.setFillColorRGB(0.4, 0.4, 0.4)
                c.drawCentredString(PAGE_W / 2, y - 18, sub)
                c.setFillColorRGB(0.1, 0.1, 0.1)
            y -= 64
        c.showPage()

    if author:
        # --- about this book: facts about the book only, no claims about the author ---
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.setFont("SansB", 22)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 180, S["about_title"])
        c.setFont("Sans", 13)
        for i, ln in enumerate(S["about"]):
            c.drawCentredString(PAGE_W / 2, PAGE_H - 240 - i * 22, ln)
        c.showPage()




def clean_words(words: list[str]) -> list[str]:
    out: list[str] = []
    for w in words:
        w = "".join(ch for ch in strip_accents(w) if ch.isalpha())
        if w and len(w) <= GRID_N:
            out.append(w)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--themes", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title")
    ap.add_argument("--subtitle")
    ap.add_argument("--author")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--forward-only", action="store_true",
                    help="words only left-to-right or top-to-bottom (dementia-friendly)")
    ap.add_argument("--lang", choices=sorted(STRINGS), help="interior language (default: theme 'lang', else en)")
    a = ap.parse_args()
    dirs = FORWARD_DIRS if a.forward_only else DIRS

    random.seed(a.seed)
    data = json.load(open(a.themes, encoding="utf-8"))
    global S, FORWARD, FILL, FILL_WEIGHTS
    lang = a.lang or data.get("lang", "en")
    S = dict(STRINGS[lang])
    S["label"] = data.get("puzzle_label", S["label"])
    FORWARD = a.forward_only
    if lang == "es":
        FILL = string.ascii_uppercase + "Ñ"
        FILL_WEIGHTS = [1.0] * 26 + [0.3]   # Ñ is rare in Spanish text
    title = a.title or data.get("title", "Word Search")
    subtitle = a.subtitle or data.get("subtitle", "")
    author = a.author or data.get("author", "")
    running = title

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    register_fonts()
    c = canvas.Canvas(a.out, pagesize=letter, initialFontName="Sans", initialFontSize=12)
    c.setTitle(title)
    c.setAuthor(author)

    front_matter(c, title, subtitle, author)

    solutions = []
    page_no = 1
    for i, p in enumerate(data["puzzles"], start=1):
        words = clean_words(p["words"])
        grid, placements, placed = generate_puzzle(words, dirs=dirs)
        puzzle_page(c, i, p["name"], grid, placed, page_no, running)
        solutions.append((i, p["name"], grid, placements))
        if len(placed) < len(words):
            print(f"  note: puzzle {i} '{p['name']}' placed {len(placed)}/{len(words)} words")
        page_no += 1

    solutions_pages(c, solutions, page_no, running)

    # Back-matter: review request + cross-sell + about
    also_from = data.get("also_from", [])
    back_matter(c, author, also_from)

    c.save()

    n_puzzles = len(data["puzzles"])
    size_kb = os.path.getsize(a.out) / 1024
    print(f"DONE -> {a.out}")
    print(f"  {n_puzzles} puzzles + solutions, {size_kb:.0f} KB, 8.5x11 print-ready")


if __name__ == "__main__":
    main()

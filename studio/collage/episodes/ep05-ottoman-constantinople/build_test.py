#!/usr/bin/env python3
"""Spec JSON del test EP05 (prime 13 pagine con voce) per episode_render.py.
Uso: python3 -I build_test.py <flow_dir con all/Vnnn.jpg e cut_Vnnn.png> <out_spec.json> <out_mp4>
Ogni pagina: INQUADRATURE (cambio ogni 3-5 s, agganciato all'inizio di una frase) + biglietti accanto al soggetto (vivono 2-3 s)
+ solo elementi che puntano a qualcosa. Tempi dalla voce: silencedetect + posizione proporzionale dei caratteri (errore ~0,5-1 s)."""
import json, os, re, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "tools"))
import episode_render as ER
FLOW, OUT, MP4 = sys.argv[1:4]
script = open(os.path.join(HERE, "script.md"), encoding="utf-8").read()
TXT = {v: n for v, n in re.findall(r"^\[V(\w+)\] NARRATOR: (.+)$", script, flags=re.M)}
SHOTS = {}


def speech_bounds(path):
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))
    log = subprocess.run(["ffmpeg", "-i", path, "-af", "silencedetect=n=-38dB:d=0.12", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    ss = en[0] if (st and st[0] < 0.05 and en) else 0.0
    se = st[-1] if (st and (d - st[-1]) < 1.5 and st[-1] > d * 0.5) else d
    return ss, se, d


def T(v, phrase, off=0.0):
    if phrase == 0: return 0.0
    ss, se, _ = speech_bounds(os.path.join(HERE, "audio", f"V{v}.mp3"))
    t = TXT[v]; i = t.lower().find(phrase.lower())
    assert i >= 0, (v, phrase)
    return round(max(0.0, ss + (i / len(t)) * (se - ss) + off), 2)


def S(v, t, sx, sy):
    """punto della sorgente (0-1) -> coordinate schermo nell'inquadratura attiva a t (dopo lo scorrimento)."""
    sh = SHOTS[v]; cur = [s for s in sh if s[0] <= t + 0.45][-1]
    x, y = ER.to_screen(cur[1:4], sx, sy, 2752, 1536)
    return round(min(max(x, 0.13), 0.87), 3), round(min(max(y, 0.09), 0.91), 3)


def LB(v, id_, text, phrase, src, dur=2.8, size=56, rot=-2, frm=0, off=0.0, color=None):
    t = T(v, phrase, off); x, y = S(v, t, *src)
    e = {"type": "label", "id": id_, "text": text, "x": x, "y": y, "t": t, "size": size, "rot": rot, "from": frm, "dur": dur, "typeon": True}
    if color: e["color"] = color
    return e


PAGES = []
# Movimento degli attori (usato SOLO se esiste lo sfondo senza personaggi <FLOW>/bg/Vnnn_bg.png|jpg, richiesto in flow-sfondi-test.md)
ACT = {
    "002a": {"from": "left", "dist": 0.45, "t": 0.2, "dur": 1.8},
    "003a": {"from": "left", "dist": 0.0, "t": 0.0, "dur": 0.1, "drift": 0.012, "shadow": False},
    "004a": {"from": "auto", "dist": 0.35, "t": 0.3, "stagger": 0.45, "dur": 1.4, "bob": 4, "split": True, "shadow": False},
    "004b": {"from": "auto", "dist": 0.40, "t": 0.2, "stagger": 0.35, "dur": 1.5, "bob": 4, "split": True, "shadow": False, "drift": 0.01},
    "005": {"from": "left", "dist": 0.30, "t": 0.3, "dur": 1.3},
    "008": {"from": "left", "dist": 0.30, "t": 0.3, "dur": 1.3},
    "009": {"from": "left", "dist": 0.0, "t": 0.0, "dur": 0.1, "split": True, "bob": 4, "drift": 0.01, "shadow": False},
}


def bg_path(v):
    for ext in ("png", "jpg", "jpeg"):
        p = os.path.join(FLOW, "bg", f"V{v}_bg.{ext}")
        if os.path.exists(p): return p
    return None


def flow(v, shots, cut, els_fn):
    SHOTS[v] = [(T(v, p), cx, cy, z) for p, cx, cy, z in shots]
    p = {"id": f"V{v}", "audio": os.path.join(HERE, "audio", f"V{v}.mp3"), "image": os.path.join(FLOW, "all", f"V{v}.jpg"),
         "shots": [list(s) for s in SHOTS[v]], "fgpush": 0.035}
    bgp = bg_path(v)
    if bgp and v in ACT:
        p["bg"], p["act"] = bgp, ACT[v]
        print("attori attivi:", v)
    elif cut: p["cut"] = os.path.join(FLOW, f"cut_V{v}.png")
    p["boards"] = [{"t0": 0, "els": els_fn(), "dur": 1}]
    PAGES.append(p)

def mine(v, boards):
    PAGES.append({"id": f"V{v}", "audio": os.path.join(HERE, "audio", f"V{v}.mp3"), "boards": boards})

# ---------------- V001: mura, poi tende e bandiera
flow("001", [(0, .5, .5, 1.0), ("A city", .32, .58, 1.8), ("The man", .55, .76, 1.9)], True, lambda: [
    LB("001", "d", "MAY 29, 1453", "May 29", (.20, .40), 3.0, 62),
    LB("001", "o", "ONCE IN 11 CENTURIES", "fallen only once", (.38, .46), 3.2, 50, 2, 1),
    LB("001", "a", "AGE 21", "twenty-one years", (.62, .70), 2.8, 70, 3, 1, -0.2)])
# ---------------- V002a: cannone
flow("002a", [(0, .5, .5, 1.0), ("But it fired", .6, .33, 1.6), ("repaired", .5, .45, 1.3)], True, lambda: [
    LB("002a", "s", "7 SHOTS / DAY", "seven times", (.46, .10), 3.0, 56),
    {"type": "cross", "at": list(S("002a", T("002a", "repaired", -0.2), .52, .20)), "r": 0.07, "t": T("002a", "repaired", -0.2), "dur": 0.6}])
# ---------------- V002b: bacheca delle sette scelte (mia)
mine("002b", [{"t0": 0, "els": [lab_ for lab_ in (
    [{"type": "label", "id": "q", "text": "SEVEN CHOICES", "x": .5, "y": .22, "t": .2, "size": 100, "rot": -1.5, "from": 0, "typeon": True}] +
    [{"type": "label", "id": f"n{i}", "text": str(i + 1), "x": .5 + (i - 3) * .115, "y": .58, "t": 1.0 + i * .45, "size": 96, "rot": (-1) ** i * 2,
      "from": 3 if i % 2 else 2, "color": ((46, 84, 120) if i % 2 == 0 else (110, 46, 110))} for i in range(7)])], "dur": 1}])
# ---------------- V003a: la citta'
flow("003a", [(0, .5, .5, 1.0), ("By 1453", .66, .46, 1.8)], True, lambda: [
    LB("003a", "y", "1453", "Constantinople", (.62, .30), 3.0, 64),
    LB("003a", "c", "ONE CITY", "single city", (.66, .62), 3.0, 60, 2, 1)])
# ---------------- V003b: citta' circolare
flow("003b", [(0, .5, .5, 1.0), ("in villages", .5, .35, 1.9), ("double wall", .5, .82, 1.9)], True, lambda: [
    LB("003b", "p", "< 50,000 PEOPLE", "Fewer than", (.50, .10), 3.0, 56),
    LB("003b", "w", "DOUBLE WALL + MOAT", "double wall", (.30, .64), 3.0, 52, 2, 1),
    {"type": "arrow", "pts": ["w", list(S("003b", T("003b", "double wall", 0.3), .27, .82))], "t": T("003b", "double wall", 0.6), "dur": 0.7}])
# ---------------- V004a: crociati alla torre
flow("004a", [(0, .5, .5, 1.0), ("Only once", .70, .35, 1.9)], True, lambda: [
    LB("004a", "y", "1204", "attacked", (.58, .10), 3.0, 70),
    LB("004a", "c", "CRUSADERS", "Crusader", (.55, .62), 2.6, 56, -2, 1)])
# ---------------- V004b: 1422
flow("004b", [(0, .5, .5, 1.0), ("He struggled", .35, .66, 1.9), ("a rebellion", .85, .25, 1.9)], True, lambda: [
    LB("004b", "y", "1422", "In 1422", (.15, .30), 2.8, 70),
    LB("004b", "b", "BYZANTINE BLOCKADE", "blockade", (.40, .50), 3.0, 50, -1, 3),
    LB("004b", "r", "REBELLION AT HOME", "rebellion", (.82, .40), 2.8, 48, 2, 1)])
# ---------------- V005: Mehmed al tavolo, poi inserto mappa
flow("005", [(0, .5, .5, 1.0), ("The courts", .35, .40, 1.9), ("What he did", .5, .5, 1.1)], True, lambda: [
    LB("005", "y", "1451", "In 1451", (.62, .22), 2.6, 66, 3, 1),
    LB("005", "e", "EXPECTED: INEXPERIENCED", "expected", (.55, .26), 3.2, 46, -2, 1),
    {"type": "map", "id": "mm", "x": .78, "y": .60, "w": .30, "bbox": [28.78, 40.93, 29.32, 41.32], "world": "world_10m_med.json", "land": "all",
     "from": 1, "t": T("005", "the strait"), "colors": {"turkey": [205, 170, 118]}},
    {"type": "label", "id": "st", "text": "THE STRAIT", "x": .78, "y": .26, "t": T("005", "the strait", 0.3), "size": 58, "rot": -2, "from": 0, "typeon": True}])
# ---------------- V006: mappa Bosforo (mia): vista larga, poi zoom sulle fortezze
BOS = [28.78, 40.93, 29.32, 41.32]; BOSZ = [28.97, 41.03, 29.13, 41.14]
mine("006", [
 {"t0": 0, "dur": 1, "els": [
    {"type": "map", "id": "m", "x": .40, "y": .54, "w": .46, "bbox": BOS, "world": "world_10m_med.json", "land": "all", "from": 3, "t": 0, "colors": {"turkey": [205, 170, 118]}},
    {"type": "label", "id": "d", "text": "APRIL 15, 1452", "x": .80, "y": .16, "t": T("006", "April 15"), "size": 64, "rot": 2, "from": 1, "typeon": True},
    {"type": "pin", "id": "cst", "map": "m", "lon": 28.955, "lat": 41.0136, "label": "Constantinople", "t": 1.2, "side": "left", "dy": 14}]},
 {"t0": T("006", "narrowest") - 0.3, "dur": 1, "els": [
    {"type": "map", "id": "m", "x": .38, "y": .54, "w": .48, "bbox": BOSZ, "world": "world_10m_med.json", "land": "all", "from": 1, "t": 0, "colors": {"turkey": [205, 170, 118]}},
    {"type": "pin", "id": "rum", "map": "m", "lon": 29.0561, "lat": 41.0847, "label": "Rumeli Hisari", "t": 0.5, "side": "left", "dy": -26},
    {"type": "pin", "id": "ana", "map": "m", "lon": 29.0669, "lat": 41.0819, "label": "Anadolu Hisari", "t": 0.9, "dx": 34, "dy": 40},
    {"type": "label", "id": "w", "text": "660 m ACROSS", "x": .80, "y": .52, "t": 1.4, "size": 60, "rot": -2, "from": 1, "typeon": True},
    {"type": "arrow", "pts": [[.625, .53], [.58, .54], "ana"], "t": 2.0, "dur": 0.8}]}])
# ---------------- V007a: due fortezze e fuoco incrociato
flow("007a", [(0, .22, .38, 1.8), ("Together", .5, .45, 1.2)], False, lambda: [
    {"type": "arrow", "pts": [list(S("007a", T("007a", "Together"), .18, .30)), list(S("007a", T("007a", "Together"), .40, .18)),
                              list(S("007a", T("007a", "Together"), .60, .22)), list(S("007a", T("007a", "Together"), .78, .40))], "t": T("007a", "Together"), "dur": 1.1},
    {"type": "arrow", "pts": [list(S("007a", T("007a", "Together"), .80, .30)), list(S("007a", T("007a", "Together"), .62, .28)),
                              list(S("007a", T("007a", "Together"), .42, .30)), list(S("007a", T("007a", "Together"), .22, .42))], "t": T("007a", "Together", 0.5), "dur": 1.1}])
# ---------------- V007b: Mar Nero (mia)
mine("007b", [{"t0": 0, "dur": 1, "els": [
    {"type": "map", "id": "m", "x": .5, "y": .55, "w": .70, "bbox": [24, 39.8, 42, 47.2], "land": "all", "from": 3, "t": 0, "colors": {"turkey": [205, 170, 118]}},
    {"type": "pin", "id": "cst", "map": "m", "lon": 28.955, "lat": 41.01, "label": "Constantinople", "t": .6, "side": "left", "dy": 36},
    {"type": "pin", "id": "caf", "map": "m", "lon": 35.38, "lat": 45.03, "label": "Caffa", "t": 1.1, "dx": 20, "dy": -28},
    {"type": "pin", "id": "sin", "map": "m", "lon": 35.15, "lat": 42.03, "label": "Sinope", "t": 1.4, "dx": 22, "dy": 30},
    {"type": "arrow", "pts": ["caf", {"map": "m", "lon": 31.0, "lat": 43.4}, {"map": "m", "lon": 29.4, "lat": 41.5}], "t": T("007b", "shortest route"), "dur": 1.0},
    {"type": "cross", "at": {"map": "m", "lon": 29.15, "lat": 41.3}, "r": 0.03, "t": T("007b", "cut"), "dur": 0.5},
    {"type": "label", "id": "hc", "text": "HELP CUT OFF", "x": .80, "y": .90, "t": T("007b", "cut"), "size": 60, "rot": -2, "from": 1, "typeon": True}]}])
# ---------------- V008: imperatore
flow("008", [(0, .5, .5, 1.0), ("Mehmed answered", .85, .30, 1.9), ("Local churches", .5, .5, 1.15)], True, lambda: [
    LB("008", "pr", "PROTEST", "protested", (.42, .20), 2.6, 66),
    LB("008", "ny", "NOT YOURS", "owned nothing", (.78, .14), 2.8, 64, 2, 1)])
# ---------------- V009: fortezza
flow("009", [(0, .5, .5, 1.0), ("The Turks", .55, .45, 1.8), ("It was a pun", .5, .4, 1.2)], False, lambda: [
    LB("009", "m", "4+ MONTHS", "four months", (.30, .18), 2.6, 60),
    LB("009", "b", "BOGAZKESEN", "Boğazkesen", (.36, .26), 3.6, 68),
    LB("009", "s", "STRAIT-CUTTER / THROAT-CUTTER", "strait-cutter", (.40, .40), 2.8, 40, 2, 0)])
json.dump({"out": MP4, "seed": 7, "gap": 0.25, "lufs": -14, "pages": PAGES}, open(OUT, "w"), indent=1)
print("spec ok:", len(PAGES), "pagine")

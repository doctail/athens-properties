#!/usr/bin/env python3
"""Costruisce lo spec JSON del test EP05 (prime 13 pagine con voce) per episode_render.py.
Uso: python3 -I build_test.py <flow_dir con all/Vnnn.jpg e cut_Vnnn.png> <out_spec.json> <out_mp4>
Tempi delle scritte: inizio/fine del parlato di ogni pagina da silencedetect, poi posizione proporzionale dei caratteri (errore atteso ~0,5-1 s)."""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
FLOW, OUT, MP4 = sys.argv[1:4]
script = open(os.path.join(HERE, "script.md"), encoding="utf-8").read()
TXT = {v: n for v, n in re.findall(r"^\[V(\w+)\] NARRATOR: (.+)$", script, flags=re.M)}


def speech_bounds(path):
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))
    log = subprocess.run(["ffmpeg", "-i", path, "-af", "silencedetect=n=-38dB:d=0.12", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    ss = en[0] if (st and st[0] < 0.05 and en) else 0.0
    se = st[-1] if (st and (d - st[-1]) < 1.5 and st[-1] > d * 0.5) else d
    return ss, se, d


def T(v, phrase, off=0.0):
    ss, se, _ = speech_bounds(os.path.join(HERE, "audio", f"V{v}.mp3"))
    t = TXT[v]; i = t.lower().find(phrase.lower())
    assert i >= 0, (v, phrase)
    return round(max(0.3, ss + (i / len(t)) * (se - ss) + off), 2)


def lab(id_, text, x, y, t, size=60, rot=-2, frm=0, color=None, style="strip"):
    e = {"type": "label", "id": id_, "text": text, "x": x, "y": y, "t": t, "size": size, "rot": rot, "from": frm, "style": style}
    if color: e["color"] = color
    return e


PAGES = []
def page(v, img=True, cut=False, push=0.05, fg=0.035, focus=(0.5, 0.5), els=None):
    p = {"id": f"V{v}", "audio": os.path.join(HERE, "audio", f"V{v}.mp3"), "push": push, "fgpush": fg, "focus": list(focus)}
    if img: p["image"] = os.path.join(FLOW, "all", f"V{v}.jpg")
    if cut: p["cut"] = os.path.join(FLOW, f"cut_V{v}.png")
    p["board"] = {"els": els or [], "dur": 1}
    PAGES.append(p)

page("001", cut=True, focus=(0.5, 0.6), els=[
    lab("d", "MAY 29, 1453", 0.17, 0.09, T("001", "May 29"), 62),
    {"type": "circle", "at": [0.5, 0.56], "r": 0.14, "t": T("001", "fallen only once"), "dur": 0.9},
    lab("age", "AGE 21", 0.84, 0.10, T("001", "twenty-one years", -0.3), 64, 3, 1)])
page("002a", cut=True, focus=(0.5, 0.4), els=[
    lab("sh", "7 SHOTS / DAY", 0.80, 0.09, T("002a", "seven times"), 58),
    {"type": "cross", "at": [0.52, 0.30], "r": 0.075, "t": T("002a", "repaired", -0.4), "dur": 0.6}])
page("002b", img=False, els=[
    lab("q", "SEVEN CHOICES", 0.5, 0.22, 0.2, 100, -1.5, 0)] + [
    lab(f"n{i}", str(i + 1), 0.5 + (i - 3) * 0.115, 0.58, 1.0 + i * 0.45, 96, (-1) ** i * 2, 3 if i % 2 else 2,
        color=((46, 84, 120) if i % 2 == 0 else (110, 46, 110))) for i in range(7)])
page("003a", cut=True, focus=(0.6, 0.5), els=[
    lab("y", "1453", 0.15, 0.10, 0.4, 64), lab("c", "ONE CITY", 0.80, 0.90, T("003a", "single city"), 60, 2, 1)])
page("003b", cut=True, els=[
    lab("p", "< 50,000 PEOPLE", 0.22, 0.09, T("003b", "fifty thousand"), 58),
    {"type": "arrow", "pts": ["p", [0.30, 0.25], [0.42, 0.33]], "t": T("003b", "fifty thousand", 0.5), "dur": 0.9},
    lab("w", "DOUBLE WALL + MOAT", 0.25, 0.93, T("003b", "double wall"), 54, 2, 1),
    {"type": "arrow", "pts": ["w", [0.16, 0.86], [0.10, 0.74]], "t": T("003b", "double wall", 0.4), "dur": 0.8}])
page("004a", cut=True, focus=(0.65, 0.3), els=[
    lab("y", "1204", 0.16, 0.10, T("004a", "1204"), 70),
    {"type": "circle", "at": [0.70, 0.24], "r": 0.10, "t": T("004a", "Crusader"), "dur": 0.8}])
page("004b", cut=True, els=[
    lab("y", "1422", 0.14, 0.10, T("004b", "In 1422"), 70),
    lab("b", "BYZANTINE BLOCKADE", 0.5, 0.93, T("004b", "blockade"), 54, -1, 3)])
page("005", cut=True, focus=(0.35, 0.55), els=[
    lab("y", "1451", 0.90, 0.09, T("005", "In 1451"), 66, 3, 1),
    lab("s", "THE STRAIT", 0.70, 0.20, T("005", "the strait"), 58, -2, 1),
    {"type": "arrow", "pts": ["s", [0.58, 0.40], [0.42, 0.60]], "t": T("005", "the strait", 0.5), "dur": 0.9}])
page("006", img=False, els=[
    {"type": "map", "id": "m", "x": 0.40, "y": 0.54, "w": 0.46, "bbox": [28.78, 40.93, 29.32, 41.32], "world": "world_10m_med.json", "land": "all", "from": 3, "t": 0.0,
     "colors": {"turkey": [205, 170, 118]}},
    lab("d", "APRIL 15, 1452", 0.80, 0.14, T("006", "April 15"), 64, 2, 1),
    {"type": "pin", "id": "rum", "map": "m", "lon": 29.0561, "lat": 41.0847, "label": "Rumeli Hisari", "t": T("006", "fortress"), "side": "left", "dy": -26},
    {"type": "pin", "id": "ana", "map": "m", "lon": 29.0669, "lat": 41.0819, "label": "Anadolu Hisari", "t": T("006", "fortress", 0.5), "dx": 34, "dy": 40},
    lab("w", "660 m ACROSS", 0.80, 0.52, T("006", "six hundred", -0.2), 60, -2, 1),
    {"type": "arrow", "pts": [[0.625, 0.53], [0.58, 0.54], "ana"], "t": T("006", "six hundred", 0.5), "dur": 0.8}])
page("007a", cut=False, els=[
    {"type": "arrow", "pts": [[0.24, 0.34], [0.40, 0.22], [0.58, 0.24], [0.74, 0.42]], "t": T("007a", "Together"), "dur": 1.1},
    {"type": "arrow", "pts": [[0.76, 0.34], [0.60, 0.30], [0.42, 0.32], [0.27, 0.44]], "t": T("007a", "Together", 0.5), "dur": 1.1}])
page("007b", img=False, els=[
    {"type": "map", "id": "m", "x": 0.5, "y": 0.55, "w": 0.70, "bbox": [24, 39.8, 42, 47.2], "land": "all", "from": 3, "t": 0.0,
     "colors": {"turkey": [205, 170, 118]}},
    {"type": "pin", "id": "cst", "map": "m", "lon": 28.955, "lat": 41.01, "label": "Constantinople", "t": 0.6, "side": "left", "dy": 36},
    {"type": "pin", "id": "caf", "map": "m", "lon": 35.38, "lat": 45.03, "label": "Caffa", "t": 1.1, "dx": 20, "dy": -28},
    {"type": "pin", "id": "sin", "map": "m", "lon": 35.15, "lat": 42.03, "label": "Sinope", "t": 1.4, "dx": 22, "dy": 30},
    {"type": "arrow", "pts": ["caf", {"map": "m", "lon": 31.0, "lat": 43.4}, {"map": "m", "lon": 29.4, "lat": 41.5}], "t": T("007b", "shortest route"), "dur": 1.0},
    {"type": "cross", "at": {"map": "m", "lon": 29.15, "lat": 41.3}, "r": 0.03, "t": T("007b", "cut", 0.0), "dur": 0.5},
    lab("hc", "HELP CUT OFF", 0.80, 0.90, T("007b", "cut"), 60, -2, 1)])
page("008", cut=True, focus=(0.3, 0.5), els=[
    lab("pr", "PROTEST", 0.72, 0.10, T("008", "protested"), 64, -2, 1),
    lab("ny", "NOT YOURS", 0.74, 0.24, T("008", "owned nothing"), 64, 2, 1)])
page("009", cut=False, els=[
    lab("b", "BOGAZKESEN", 0.2, 0.09, T("009", "Boğazkesen"), 66),
    lab("s", "STRAIT-CUTTER / THROAT-CUTTER", 0.30, 0.20, T("009", "strait-cutter"), 44, 2, 0),
    {"type": "circle", "at": [0.5, 0.55], "r": 0.17, "t": T("009", "pun"), "dur": 0.9}])
json.dump({"out": MP4, "seed": 7, "gap": 0.25, "lufs": -14, "pages": PAGES}, open(OUT, "w"), indent=1)
print("spec ok:", len(PAGES), "pagine")

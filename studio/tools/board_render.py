#!/usr/bin/env python3
"""Pagine "stile Vox" in carta: piu' elementi per pagina che entrano a tempo.

Elementi (coordinate x,y normalizzate 0..1 sul centro; w = larghezza come frazione della larghezza video; t = secondo d'ingresso):
  image   {"id","img","x","y","w","rot","t","focus","ratio","tape"}     foto/incisione a bordo strappato
  map     {"id","x","y","w","bbox":[lon0,lat0,lon1,lat1],"land":[slug..],"colors":{slug:[r,g,b]},"names":{slug:"TESTO"},"t"}
  pin     {"id","map","lon","lat","label","t"}                           puntina con etichetta (ancora per fili/frecce)
  label   {"id","text","x","y","size","rot","t","style":"strip|plain"}   testo a pennarello
  circle  {"at":id|[x,y],"r","t","dur","color":"red|yellow"}             evidenziatore a mano libera
  arrow   {"pts":[id|[x,y]|{"map","lon","lat"}..],"t","dur"}             freccia a pennarello (curva liscia)
  thread  {"from":id,"to":id,"t","dur","sag"}                            filo di lana con due puntine
Spec: {"out","size","fps","step_fps","audio","seed","boards":[{"dur","els":[...]}]}
Solo Pillow/OpenCV/numpy + ffmpeg. Nessuna rete, nessun modello.
"""
import json, math, os, random, subprocess, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import collage_render as C

HERE = Path(__file__).resolve().parent.parent / "collage"
GEO, MARKER = HERE / "geo", HERE / "fonts" / "PermanentMarker.ttf"
LAND = [(224, 200, 152), (205, 160, 108), (176, 184, 128), (216, 176, 128), (196, 176, 138)]
RED, YELLOW, WOOL = (214, 36, 36), (250, 214, 40), (178, 30, 42)


ALIAS = {"north_macedonia": "macedonia"}
_WORLD = {}


def world(name="world_50m.json"):
    if name not in _WORLD:
        _WORLD[name] = json.load(open(GEO / name, encoding="utf-8"))
    return _WORLD[name]


def font(sz):
    return ImageFont.truetype(str(MARKER), sz)


def text_sprite(text, size, style="strip", color=(38, 28, 20)):
    f = font(size)
    d = ImageDraw.Draw(Image.new("L", (4, 4)))
    tw = d.textlength(text, font=f)
    if style == "plain":
        w, h, pad = int(tw + 40), int(size * 1.5), 10
        img = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((pad + 20, pad + size * 0.15), text, font=f, fill=color + (255,), stroke_width=6, stroke_fill=(244, 238, 224, 255))
        a = np.asarray(img)
        return C.premult(a[..., :3], a[..., 3]), a[..., 3].copy()
    w, h, pad = int(tw + size * 1.4), int(size * 1.9), 20
    rng = np.random.default_rng(len(text))
    m = np.zeros((h + 2 * pad, w + 2 * pad), np.uint8)
    m[pad:pad + h, pad:pad + w] = C.poly_mask(w, h, C.torn_poly(w, h, 1, 6, rng, 8))
    sh = cv2.GaussianBlur(np.roll(np.roll(m, 7, 0), 5, 1), (0, 0), 7) // 3
    img = Image.new("RGB", (w + 2 * pad, h + 2 * pad), (244, 238, 224))
    ImageDraw.Draw(img).text((pad + size * 0.7, pad + size * 0.42), text, font=f, fill=color)
    A = np.maximum(m, sh).astype(np.uint8)
    rgb = (np.asarray(img, np.float32) * (m[..., None] / 255.0) + 25 * (sh[..., None] / 255.0) * (1 - m[..., None] / 255.0)) / np.maximum(A[..., None] / 255.0, 1e-3)
    return C.premult(np.clip(rgb, 0, 255).astype(np.uint8), A), A


def build_map(el, W, H, rng):
    lon0, lat0, lon1, lat1 = el["bbox"]
    mw = int(W * el["w"])
    k = math.cos(math.radians((lat0 + lat1) / 2))
    mh = int(mw * (lat1 - lat0) / ((lon1 - lon0) * k))
    pad = 24
    SW, SH = mw + 2 * pad, mh + 2 * pad
    sea = np.zeros((SH, SW, 3), np.float32)
    sea[:] = el.get("sea", (92, 120, 138))
    sea += np.random.default_rng(5).normal(0, 3, sea.shape)
    sea = np.clip(sea, 0, 255).astype(np.uint8)
    sm = np.zeros((SH, SW), np.uint8)
    sm[pad:pad + mh, pad:pad + mw] = C.poly_mask(mw, mh, C.torn_poly(mw, mh, 1, 9, rng, 9))

    def proj(lon, lat):
        return pad + (lon - lon0) / (lon1 - lon0) * mw, pad + (lat1 - lat) / (lat1 - lat0) * mh

    shadow = np.zeros((SH, SW), np.uint8)
    polys = []  # (slug, pts)
    Wd = world(el.get("world", "world_50m.json"))
    slugs = list(Wd) if el["land"] == "all" else [ALIAS.get(x, x) for x in el["land"]]
    for slug in slugs:
        g = Wd.get(slug)
        if g is None:
            print("manca geo:", slug); continue
        for poly in g["coordinates"]:
            pts = np.array([proj(x, y) for x, y in poly[0]], np.float32)
            if cv2.contourArea(pts) < 70:
                continue
            pts += np.random.default_rng(len(pts)).normal(0, 1.1, pts.shape).astype(np.float32)
            polys.append((slug, pts.astype(np.int32)))
    for _, p in polys:
        cv2.fillPoly(shadow, [p + np.array([7, 9], np.int32)], 255)
    shadow = cv2.GaussianBlur(shadow, (0, 0), 6)
    sea = (sea.astype(np.float32) * (1 - 0.38 * shadow[..., None] / 255.0)).astype(np.uint8)
    cols = {ALIAS.get(k, k): v for k, v in el.get("colors", {}).items()}
    order = {s: i for i, s in enumerate(slugs)}
    for slug, p in polys:
        c = tuple(cols.get(slug, LAND[order[slug] % len(LAND)]))
        cv2.polylines(sea, [p], True, (244, 238, 224), 7, cv2.LINE_AA)
        cv2.fillPoly(sea, [p], c, cv2.LINE_AA)
        cv2.polylines(sea, [p], True, tuple(int(v * 0.78) for v in c), 1, cv2.LINE_AA)
    pil = Image.fromarray(sea)
    dr = ImageDraw.Draw(pil)
    for slug, txt in {ALIAS.get(k, k): v for k, v in el.get("names", {}).items()}.items():
        big = max((p for s, p in polys if s == slug), key=cv2.contourArea, default=None)
        if big is None:
            continue
        mo = cv2.moments(big)
        cx, cy = mo["m10"] / mo["m00"], mo["m01"] / mo["m00"]
        dr.text((cx, cy), txt, font=font(el.get("name_size", 40)), fill=(58, 38, 28), anchor="mm", stroke_width=3, stroke_fill=(244, 238, 224))
    sea = np.asarray(pil)
    a = np.maximum(sm, 0)
    return C.premult(sea, a), a, proj, (SW, SH)


def make_pin(r=15):
    S = r * 4
    rgb = np.zeros((S, S, 3), np.uint8); a = np.zeros((S, S), np.uint8)
    sh = np.zeros((S, S), np.uint8)
    cv2.circle(sh, (S // 2 + 4, S // 2 + 7), r, 255, -1, cv2.LINE_AA)
    sh = cv2.GaussianBlur(sh, (0, 0), 4) // 2
    cv2.circle(rgb, (S // 2, S // 2), r, (200, 28, 36), -1, cv2.LINE_AA)
    cv2.circle(rgb, (S // 2 - r // 3, S // 2 - r // 3), max(2, r // 4), (255, 190, 190), -1, cv2.LINE_AA)
    cv2.circle(a, (S // 2, S // 2), r, 255, -1, cv2.LINE_AA)
    A = np.maximum(a, sh)
    col = rgb.astype(np.float32) * (a[..., None] / 255.0)
    return np.clip(col, 0, 255).astype(np.uint8), A


def catmull(pts, per=22):
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = [np.array(q, np.float32) for q in P[i - 1:i + 3]]
        for t in np.linspace(0, 1, per, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(np.array(pts[-1], np.float32))
    return np.array(out)


def blend_mask(frame, mask, color, alpha):
    m = (mask.astype(np.float32) / 255.0 * alpha)[..., None]
    frame[:] = (frame.astype(np.float32) * (1 - m) + np.array(color, np.float32) * m).clip(0, 255).astype(np.uint8)


def stroke(frame, pts, color, th, alpha, upto, jit_rng, rough=1.4, head=False):
    n = max(2, int(len(pts) * min(1.0, upto)))
    p = pts[:n] + jit_rng.normal(0, rough, (n, 2)).astype(np.float32)
    mask = np.zeros(frame.shape[:2], np.uint8)
    cv2.polylines(mask, [p.astype(np.int32)], False, 255, th, cv2.LINE_AA)
    if head and upto >= 0.999:
        d = pts[-1] - pts[max(0, len(pts) - 6)]
        ang = math.atan2(d[1], d[0])
        L = th * 3.4
        tip = pts[-1]
        tri = np.array([tip + L * np.array([math.cos(ang), math.sin(ang)]),
                        tip + L * 0.8 * np.array([math.cos(ang + 2.5), math.sin(ang + 2.5)]),
                        tip + L * 0.8 * np.array([math.cos(ang - 2.5), math.sin(ang - 2.5)])], np.int32)
        cv2.fillPoly(mask, [tri], 255, cv2.LINE_AA)
    mask = cv2.GaussianBlur(mask, (0, 0), 0.9)
    blend_mask(frame, mask, color, alpha)


def wool(frame, p0, p1, sag, upto, jit_rng, seed):
    mid = (np.array(p0) + np.array(p1)) / 2 + np.array([0, sag])
    ts = np.linspace(0, 1, 90)[:, None]
    P = (1 - ts) ** 2 * np.array(p0) + 2 * (1 - ts) * ts * mid + ts ** 2 * np.array(p1)
    P = P.astype(np.float32)
    n = max(2, int(len(P) * min(1.0, upto)))
    Q = P[:n]
    sh = np.zeros(frame.shape[:2], np.uint8)
    cv2.polylines(sh, [(Q + np.array([5, 8], np.float32)).astype(np.int32)], False, 255, 7, cv2.LINE_AA)
    blend_mask(frame, cv2.GaussianBlur(sh, (0, 0), 5), (30, 20, 14), 0.38)
    base = np.zeros(frame.shape[:2], np.uint8)
    cv2.polylines(base, [Q.astype(np.int32)], False, 255, 9, cv2.LINE_AA)
    blend_mask(frame, base, (146, 22, 34), 1.0)
    tw = np.zeros(frame.shape[:2], np.uint8)
    d = np.gradient(Q, axis=0)
    nrm = np.stack([-d[:, 1], d[:, 0]], 1)
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-3)
    off = 2.6 * np.sin(np.arange(len(Q)) * 0.95 + seed)[:, None]
    cv2.polylines(tw, [(Q + nrm * off).astype(np.int32)], False, 255, 3, cv2.LINE_AA)
    blend_mask(frame, tw, (226, 78, 80), 0.9)
    return Q[-1]


class Board:
    def __init__(self, spec, W, H, seed):
        self.W, self.H, self.dur = W, H, float(spec["dur"])
        self.els, self.anchor, self.maps, self.center = [], {}, {}, {}
        rng = np.random.default_rng(seed)
        self.pin = make_pin()
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for k, el in enumerate(spec["els"]):
            e = dict(el); e["k"] = k; t = e.get("t", 0)
            ty = e["type"]
            if ty in ("image", "map", "label"):
                if ty == "image":
                    sp = C.make_card(e["img"], W, H, rng, e.get("focus", 0.35), e.get("ratio", 1.3), e["w"], e.get("tape", True))
                elif ty == "map":
                    s_, a_, proj, size = build_map(e, W, H, rng)
                    sp = (s_, a_); e["proj"], e["size"] = proj, size
                else:
                    sp = text_sprite(e["text"], e.get("size", 60), e.get("style", "strip"), tuple(e.get("color", (38, 28, 20))))
                e["sprite"] = sp
                e["cx"], e["cy"] = e["x"] * W, e["y"] * H
                e["acy"] = e["cy"] - sp[0].shape[0] / 2 + 36 if ty == "image" else e["cy"]
                e["dir"] = dirs[e.get("from", k % 4)] if isinstance(e.get("from", k % 4), int) else (0, 1)
                if "id" in e:
                    self.anchor[e["id"]] = (e["cx"], e["acy"])
                    self.center[e["id"]] = (e["cx"], e["cy"])
                if ty == "map":
                    self.maps[e["id"]] = e
            elif ty == "pin":
                m = self.maps[e["map"]]
                px, py = m["proj"](e["lon"], e["lat"])
                e["cx"] = m["cx"] - m["size"][0] / 2 + px
                e["cy"] = m["cy"] - m["size"][1] / 2 + py
                self.anchor[e["id"]] = (e["cx"], e["cy"])
                if e.get("label"):
                    e["sprite"] = text_sprite(e["label"], e.get("size", 38), "strip")
                    wsp = e["sprite"][0].shape[1] / 2
                    e["lx"] = e["cx"] - 30 - wsp + e.get("dx", 0) if e.get("side") == "left" else e["cx"] + e.get("dx", 30) + wsp
                    e["ly"] = e["cy"] + e.get("dy", -34)
                    e["lsize"] = e["sprite"][0].shape[1]
            self.els.append(e)

    def pt(self, p):
        if isinstance(p, str):
            return self.anchor[p]
        if isinstance(p, dict):
            m = self.maps[p["map"]]
            px, py = m["proj"](p["lon"], p["lat"])
            return (m["cx"] - m["size"][0] / 2 + px, m["cy"] - m["size"][1] / 2 + py)
        return (p[0] * self.W, p[1] * self.H)

    def render(self, frame, tt, gk):
        W, H = self.W, self.H
        r = random.Random(gk)
        jit = (r.uniform(-1.6, 1.6), r.uniform(-1.6, 1.6), r.uniform(-0.25, 0.25))
        nr = np.random.default_rng(gk)
        for e in self.els:
            if tt < e.get("t", 0):
                continue
            ty, lt = e["type"], tt - e.get("t", 0)
            if ty in ("image", "map", "label"):
                en = C.ease_out(lt / 0.5)
                dx, dy = e["dir"]
                cx = e["cx"] + dx * W * 0.5 * (1 - en) + jit[0]
                cy = e["cy"] + dy * H * 0.6 * (1 - en) + jit[1]
                ang = e.get("rot", 0) + 7.0 * (1 - en) * (1 if e["k"] % 2 else -1) + jit[2] + 0.4 * math.sin(tt * 0.9 + e["k"])
                sc = (1.0 + 0.05 * (1 - en)) * (1 + 0.018 * min(tt, self.dur) / self.dur)
                C.draw(frame, e["sprite"][0], e["sprite"][1], cx, cy, ang, sc)
            elif ty == "pin":
                pop = C.ease_out(lt / 0.3)
                bounce = 1.0 + 0.25 * math.sin(min(1.0, lt / 0.3) * math.pi)
                if "sprite" in e and lt > 0.18:
                    en = C.ease_out((lt - 0.18) / 0.35)
                    sp, sa = e["sprite"]
                    C.draw(frame, sp, sa, e["lx"] + e["lsize"] / 2 * 0.0 + (1 - en) * 30 + jit[0], e["ly"] + jit[1], -2 + jit[2], max(0.01, en))
                s_, a_ = self.pin
                C.draw(frame, s_, a_, e["cx"] + jit[0] * 0.5, e["cy"] + jit[1] * 0.5, 0, max(0.01, pop) * bounce)
            elif ty == "circle":
                cx, cy = self.center.get(e["at"]) if isinstance(e["at"], str) and e["at"] in self.center else self.pt(e["at"])
                rr = e["r"] * W
                th = np.linspace(0, 2 * math.pi * 1.13, 110)
                wob = 1 + 0.05 * np.sin(3 * th + e["k"]) + 0.03 * np.sin(5 * th) + 0.05 * th / (2 * math.pi)
                x, y = rr * 1.25 * wob * np.cos(th + e["k"]), rr * 0.95 * wob * np.sin(th + e["k"])
                a = math.radians(-9)
                pts = np.stack([cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)], 1).astype(np.float32)
                p = C.ease_out(lt / e.get("dur", 0.8))
                col = YELLOW if e.get("color") == "yellow" else RED
                stroke(frame, pts, col, 16, 0.62, p, nr, 1.1)
                stroke(frame, pts + 3, col, 9, 0.35, p, nr, 1.1)
            elif ty == "cross":
                cx, cy = self.pt(e["at"]); rr = e.get("r", 0.05) * W
                p = C.ease_out(lt / e.get("dur", 0.5))
                a1 = np.array([[cx - rr, cy - rr * 0.8], [cx + rr, cy + rr * 0.8]], np.float32)
                a2 = np.array([[cx + rr, cy - rr * 0.8], [cx - rr, cy + rr * 0.8]], np.float32)
                stroke(frame, np.linspace(a1[0], a1[1], 30), RED, 20, 0.92, min(1, p * 2), nr, 1.4)
                if p > 0.5:
                    stroke(frame, np.linspace(a2[0], a2[1], 30), RED, 20, 0.92, min(1, (p - 0.5) * 2), nr, 1.4)
            elif ty == "arrow":
                P = catmull([self.pt(p) for p in e["pts"]])
                p = C.ease_out(lt / e.get("dur", 1.0))
                stroke(frame, P, RED, 15, 0.92, p, nr, 1.3, head=True)
            elif ty == "thread":
                p0, p1 = self.pt(e["from"]), self.pt(e["to"])
                p = C.ease_out(lt / e.get("dur", 0.9))
                wool(frame, p0, p1, e.get("sag", 0.07) * H, p, nr, e["k"])
                s_, a_ = self.pin
                C.draw(frame, s_, a_, p0[0], p0[1], 0, 0.8)
                if p >= 0.999:
                    C.draw(frame, s_, a_, p1[0], p1[1], 0, 0.8)


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    W, H = spec.get("size", [1920, 1080])
    fps, step, seed = spec.get("fps", 30), spec.get("step_fps", 12), spec.get("seed", 7)
    bg = C.paper_bg(W, H, seed)
    boards = [Board(b, W, H, seed + i * 11) for i, b in enumerate(spec["boards"])]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-"]
    if spec.get("audio"):
        cmd += ["-i", spec["audio"], "-shortest", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "medium", spec["out"]]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    gt, cache, last_final = 0.0, {}, None
    TR = 0.45
    for bi, b in enumerate(boards):
        n = int(round(b.dur * fps))
        for f in range(n):
            t = f / fps
            gk = int((gt + t) * step)
            key = (bi, gk)
            if key not in cache:
                tt = max(0.0, gk / step - gt)
                fr = bg.copy()
                b.render(fr, tt, gk)
                if bi > 0 and tt < TR:  # la pagina nuova scivola da destra sopra la vecchia
                    e = C.ease_out(tt / TR)
                    x0 = int((1 - e) * W)
                    out = last_final.copy()
                    out[:, x0:] = fr[:, :W - x0]
                    if x0 > 8:
                        sh = np.linspace(0.45, 0.0, 30)[None, :, None]
                        lo = max(0, x0 - 30)
                        out[:, lo:x0] = (out[:, lo:x0] * (1 - sh[:, -(x0 - lo):])).astype(np.uint8)
                    fr = out
                cache = {key: fr}
            ff.stdin.write(cache[key].tobytes())
        fin = bg.copy()
        b.render(fin, b.dur, int((gt + b.dur) * step))
        last_final = fin
        gt += b.dur
    ff.stdin.close(); ff.wait()
    print("ok", spec["out"], round(gt, 1), "s")


if __name__ == "__main__":
    main()

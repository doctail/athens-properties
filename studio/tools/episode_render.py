#!/usr/bin/env python3
"""Montaggio di un episodio collage: pagine = immagine Flow (zoom lento) + primo piano ritagliato (zoom un po' piu' forte, ombra)
+ elementi miei (board_render: etichette, cerchi, frecce, fili, mappe) + voce per pagina.

Uso: episode_render.py spec.json
spec = {"out","size","fps","step_fps","gap":0.25,"lufs":-14,"seed",
        "pages":[{"id","audio","image":path|null,"cut":path|null,"push":0.05,"fgpush":0.035,"focus":[0.5,0.5],
                  "board":{"els":[...]}}]}
Durata pagina = durata audio + gap. L'audio e' la voce concatenata e normalizzata a -14 LUFS. Solo ffmpeg/OpenCV/Pillow/numpy.
"""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cv2
import collage_render as C
import board_render as B


def probe(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))


def cover(im, W, H, margin):
    h, w = im.shape[:2]
    s = max(W * margin / w, H * margin / h)
    im = cv2.resize(im, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    y0, x0 = (im.shape[0] - H) // 2, (im.shape[1] - W) // 2
    return im, (x0, y0)


def clean_alpha(a):
    """Toglie le parti sbiadite/fantasma e i frammenti piccoli."""
    a = np.clip((a.astype(np.float32) / 255 - 0.30) / 0.45, 0, 1)
    m = (a > 0.5).astype(np.uint8)
    n, lbl, st, _ = cv2.connectedComponentsWithStats(m)
    keep = np.zeros_like(m)
    for i in range(1, n):
        if st[i, 4] >= 0.004 * m.size:
            keep[lbl == i] = 1
    keep = cv2.dilate(keep, np.ones((3, 3), np.uint8))
    a = a * keep
    return cv2.GaussianBlur((a * 255).astype(np.uint8), (0, 0), 0.9)


def camera_rect(cx, cy, z, W0, H0):
    """Ritaglio 16:9 della sorgente: centro normalizzato (cx,cy), zoom z (1 = tutta l'altezza). Ritorna X0,Y0,cw,ch in pixel sorgente."""
    ch = H0 / z
    cw = ch * 16 / 9
    X0 = min(max(cx * W0 - cw / 2, 0), W0 - cw)
    Y0 = min(max(cy * H0 - ch / 2, 0), H0 - ch)
    return X0, Y0, cw, ch


def to_screen(shot, sx, sy, W0, H0):
    """Punto sorgente normalizzato -> coordinate schermo normalizzate nell'inquadratura 'shot' (cx,cy,z)."""
    X0, Y0, cw, ch = camera_rect(shot[0], shot[1], shot[2], W0, H0)
    return (sx * W0 - X0) / cw, (sy * H0 - Y0) / ch


def ease_back(x):
    x = min(1.0, max(0.0, x)); c1 = 1.1; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def blit(scene, spr, x, y):
    """Compone uno sprite premoltiplicato RGBA su scene (RGB) con clipping; x,y = angolo in alto a sinistra."""
    H, W = scene.shape[:2]; h, w = spr.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0:
        return
    s = spr[y0 - y:y1 - y, x0 - x:x1 - x]
    a = s[..., 3:4].astype(np.uint16)
    d = scene[y0:y1, x0:x1].astype(np.uint16)
    scene[y0:y1, x0:x1] = (d * (255 - a) // 255 + s[..., :3]).clip(0, 255).astype(np.uint8)


def shade(scene, shd, x, y, k=0.30):
    H, W = scene.shape[:2]; h, w = shd.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0:
        return
    a = shd[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32)[..., None] / 255.0
    scene[y0:y1, x0:x1] = (scene[y0:y1, x0:x1].astype(np.float32) * (1 - k * a)).astype(np.uint8)


def extract_actors(orig, bg, cut_a, act):
    """Attori = cio' che e' sparito dallo sfondo (differenza orig-bg), eventualmente ristretto al ritaglio automatico."""
    d = np.abs(orig.astype(np.int16) - bg.astype(np.int16)).max(axis=2).astype(np.uint8)
    d = cv2.GaussianBlur(d, (0, 0), 2.0)
    m = (d > act.get("thr", 28)).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    if act.get("within_cut") and cut_a is not None:
        m = cv2.bitwise_and(m, cv2.dilate((cut_a > 40).astype(np.uint8) * 255, np.ones((3, 3), np.uint8), iterations=6))
    n, lbl, st, cen = cv2.connectedComponentsWithStats((m > 0).astype(np.uint8))
    area = m.shape[0] * m.shape[1]
    comps = [i for i in range(1, n) if st[i, 4] >= act.get("min_area", 0.0015) * area]
    if not act.get("split"):
        comps = [None] if comps else []
    out = []
    for i in comps:
        mk = (np.isin(lbl, [j for j in range(1, n) if st[j, 4] >= act.get("min_area", 0.0015) * area]) if i is None else (lbl == i)).astype(np.uint8) * 255
        mk = cv2.dilate(mk, np.ones((3, 3), np.uint8), iterations=2)
        mk = cv2.GaussianBlur(mk, (0, 0), 1.2)
        ys, xs = np.where(mk > 8)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        a = mk[y0:y1, x0:x1]
        spr = np.dstack([C.premult(orig[y0:y1, x0:x1], a), a])
        shd = cv2.GaussianBlur(np.roll(np.roll(np.pad(a, 30), 14, 0), 9, 1), (0, 0), 14)
        out.append({"x": int(x0), "y": int(y0), "spr": spr, "shd": shd, "cx": (x0 + x1) / 2 / orig.shape[1]})
    out.sort(key=lambda o: o["cx"])
    return out


class Page:
    TR = 0.40  # durata dello scorrimento tra due inquadrature

    def __init__(self, spec, W, H, seed):
        self.id, self.W, self.H = spec["id"], W, H
        self.audio = spec["audio"]
        self.dur = probe(self.audio) + spec.get("gap", 0.25)
        self.fgpush = spec.get("fgpush", 0.035)
        self.base = self.fg = self.shadow = None
        self.shots = [(0.0, 0.5, 0.5, 1.0)]
        if spec.get("image"):
            self.base = cv2.cvtColor(cv2.imread(spec["image"]), cv2.COLOR_BGR2RGB)
            self.H0, self.W0 = self.base.shape[:2]
            if spec.get("shots"):
                self.shots = [tuple(x) for x in spec["shots"]]
            self.actors, self.act = [], spec.get("act", {})
            if spec.get("bg"):
                bgim = cv2.cvtColor(cv2.imread(spec["bg"]), cv2.COLOR_BGR2RGB)
                bgim = cv2.resize(bgim, (self.W0, self.H0), interpolation=cv2.INTER_CUBIC)
                cut_a = None
                if spec.get("cut") and self.act.get("within_cut"):
                    cut_a = clean_alpha(cv2.imread(spec["cut"], cv2.IMREAD_UNCHANGED)[..., 3])
                self.actors = extract_actors(self.base, bgim, cut_a, self.act)
                self.orig_base, self.base = self.base, bgim
                spec = dict(spec); spec.pop("cut", None)
            if spec.get("cut"):
                c = cv2.imread(spec["cut"], cv2.IMREAD_UNCHANGED)
                a = clean_alpha(c[..., 3])
                rgb = cv2.cvtColor(c[..., :3], cv2.COLOR_BGR2RGB)
                self.fg = np.dstack([C.premult(rgb, a), a])
                self.shadow = cv2.GaussianBlur(np.roll(np.roll(a, 20, 0), 13, 1), (0, 0), 20)
        self.boards = []
        for bs in (spec.get("boards") or ([spec["board"]] if spec.get("board") else [])):
            bd = B.Board(bs, W, H, seed + len(self.boards) * 3)
            bd.dur = self.dur
            self.boards.append((float(bs.get("t0", 0.0)), bd))

    def cam(self, tt):
        i = max(k for k, s in enumerate(self.shots) if s[0] <= tt + 1e-6)
        t0 = self.shots[i][0]
        t1 = self.shots[i + 1][0] if i + 1 < len(self.shots) else self.dur
        def state(k, t):
            s = self.shots[k]; e = self.shots[k + 1][0] if k + 1 < len(self.shots) else self.dur
            f = min(1.0, max(0.0, (t - s[0]) / max(e - s[0], 0.1)))
            return s[1], s[2], s[3] * (1 + 0.03 * f)
        cur = state(i, tt)
        if i > 0 and tt - t0 < self.TR:
            prev = state(i - 1, t0)
            e = C.ease_out((tt - t0) / self.TR)
            return tuple(prev[k] + (cur[k] - prev[k]) * e for k in range(3))
        return cur

    def frame(self, tt, gk, paper):
        W, H = self.W, self.H
        if self.base is not None:
            cx, cy, z = self.cam(tt)
            def M(zz):
                X0, Y0, cw, ch = camera_rect(cx, cy, zz, self.W0, self.H0)
                return np.array([[W / cw, 0, -X0 * W / cw], [0, H / ch, -Y0 * H / ch]], np.float64)
            src = self.base
            if self.actors:
                src = self.base.copy(); act = self.act
                d_ = {"left": (-1, 0), "right": (1, 0), "top": (0, -1), "bottom": (0, 1)}
                for k, ac in enumerate(self.actors):
                    te = act.get("t", 0.3) + k * act.get("stagger", 0.0)
                    if tt < te:
                        continue
                    side = act.get("from", "left")
                    if side == "auto":
                        side = "left" if ac["cx"] < 0.5 else "right"
                    vx, vy = d_.get(side, (0, 0))
                    e = ease_back((tt - te) / act.get("dur", 1.2))
                    dist = act.get("dist", 0.0)
                    ox = int(vx * dist * self.W0 * (1 - e) + act.get("drift", 0.0) * self.W0 * (tt - te) * (1 if side != "right" else -1) * (1 if act.get("drift_dir", 1) > 0 else -1))
                    oy = int(vy * dist * self.H0 * (1 - e) + act.get("bob", 0) * np.sin(2 * np.pi * tt / 2.6 + k * 1.3))
                    if act.get("shadow", True):
                        shade(src, ac["shd"], ac["x"] - 30 + ox, ac["y"] - 30 + oy)
                    blit(src, ac["spr"], ac["x"] + ox, ac["y"] + oy)
            fr = cv2.warpAffine(src, M(z), (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            if self.fg is not None:
                e = C.ease_out(min(1.0, tt / max(self.dur * 0.6, 0.1)))
                i = max(k for k, sh_ in enumerate(self.shots) if sh_[0] <= tt + 1e-6)
                dt = tt - self.shots[i][0]
                punch = 0.06 * (1 - C.ease_out(dt / 0.5)) if dt < 0.5 else 0.0   # il pezzo di carta "scatta" a ogni inquadratura
                Mf = M(z * (1.0 + self.fgpush * e + punch))
                sh = cv2.warpAffine(self.shadow, Mf, (W, H), flags=cv2.INTER_LINEAR)
                fr = (fr.astype(np.float32) * (1 - 0.34 * sh[..., None] / 255.0)).astype(np.uint8)
                f = cv2.warpAffine(self.fg, Mf, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
                fr = (fr.astype(np.uint16) * (255 - f[..., 3:4]) // 255 + f[..., :3]).clip(0, 255).astype(np.uint8)
        else:
            fr = paper.copy()
        cur = None
        for t0, bd in self.boards:
            if t0 <= tt + 1e-6:
                cur = (t0, bd)
        if cur:
            cur[1].render(fr, tt - cur[0], gk)
        return fr


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    W, H = spec.get("size", [1920, 1080])
    fps, step, seed = spec.get("fps", 30), spec.get("step_fps", 12), spec.get("seed", 7)
    paper = C.paper_bg(W, H, seed)
    pages = []
    for i, ps in enumerate(spec["pages"]):
        ps = dict(ps); ps.setdefault("gap", spec.get("gap", 0.25))
        pages.append(Page(ps, W, H, seed + i * 5)); print("pagina", ps["id"], "ok", flush=True)
    # audio: ogni pagina + silenzio, concatenate, normalizzate
    tmp = tempfile.mkdtemp(prefix="ep_")
    lst = []
    for i, p in enumerate(pages):
        wav = os.path.join(tmp, f"{i:02d}.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", p.audio, "-af", f"apad=pad_dur={spec.get('gap', 0.25)}", "-t", f"{p.dur:.3f}", "-ar", "44100", "-ac", "1", wav], check=True)
        lst.append(f"file '{wav}'")
    open(os.path.join(tmp, "list.txt"), "w").write("\n".join(lst))
    cat = os.path.join(tmp, "voice.wav")
    raw = os.path.join(tmp, "raw.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "list.txt"), "-ar", "44100", raw], check=True)
    tgt = spec.get("lufs", -14)
    m = subprocess.run(["ffmpeg", "-i", raw, "-af", f"loudnorm=I={tgt}:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    af = (f"loudnorm=I={tgt}:TP=-1.5:LRA=7:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", af, "-ar", "44100", cat], check=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-i", cat,
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-shortest", spec["out"]]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    gt, cache = 0.0, {}
    for bi, p in enumerate(pages):
        n = int(round(p.dur * fps))
        for f in range(n):
            t = f / fps
            gk = int((gt + t) * step)
            key = (bi, gk)
            if key not in cache:
                tt = max(0.0, gk / step - gt)
                cache = {key: p.frame(tt, gk, paper)}
            ff.stdin.write(cache[key].tobytes())
        print("renderizzata", p.id, round(gt, 1), flush=True)
        gt += p.dur
    ff.stdin.close(); ff.wait()
    print("ok", spec["out"], round(gt, 1), "s")


if __name__ == "__main__":
    main()

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


class Page:
    def __init__(self, spec, W, H, seed):
        self.id, self.W, self.H = spec["id"], W, H
        self.audio = spec["audio"]
        self.dur = probe(self.audio) + spec.get("gap", 0.25)
        self.push, self.fgpush = spec.get("push", 0.05), spec.get("fgpush", 0.035)
        fx, fy = spec.get("focus", [0.5, 0.5])
        self.focus = (fx * W, fy * H)
        self.base = self.fg = self.shadow = None
        if spec.get("image"):
            m = 1.0
            im = cv2.cvtColor(cv2.imread(spec["image"]), cv2.COLOR_BGR2RGB)
            self.base, _ = cover(im, W, H, m)
            self.base = self.base[(self.base.shape[0] - H) // 2:(self.base.shape[0] - H) // 2 + H, (self.base.shape[1] - W) // 2:(self.base.shape[1] - W) // 2 + W]
            if spec.get("cut"):
                c = cv2.imread(spec["cut"], cv2.IMREAD_UNCHANGED)  # BGRA
                a = clean_alpha(c[..., 3])
                rgb = cv2.cvtColor(c[..., :3], cv2.COLOR_BGR2RGB)
                rgb, _ = cover(rgb, W, H, m); a, _ = cover(a, W, H, m)
                oy, ox = (rgb.shape[0] - H) // 2, (rgb.shape[1] - W) // 2
                rgb, a = rgb[oy:oy + H, ox:ox + W], a[oy:oy + H, ox:ox + W]
                self.fg = np.dstack([C.premult(rgb, a), a])
                sh = cv2.GaussianBlur(np.roll(np.roll(a, 14, 0), 9, 1), (0, 0), 14)
                self.shadow = sh
        self.board = B.Board(spec["board"], W, H, seed) if spec.get("board") else None
        if self.board:
            self.board.dur = self.dur
        self.paper = None

    def frame(self, tt, gk, paper):
        W, H = self.W, self.H
        e = C.ease_out(min(1.0, tt / max(self.dur, 0.1)))
        t = min(1.0, tt / self.dur)
        if self.base is not None:
            zb = 1.0 + self.push * t
            M = cv2.getRotationMatrix2D(self.focus, 0, zb)
            fr = cv2.warpAffine(self.base, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            if self.fg is not None:
                zf = zb * (1.0 + self.fgpush * e)
                Mf = cv2.getRotationMatrix2D(self.focus, 0, zf)
                if self.shadow is not None:
                    sh = cv2.warpAffine(self.shadow, Mf, (W, H), flags=cv2.INTER_LINEAR)
                    fr = (fr.astype(np.float32) * (1 - 0.36 * sh[..., None] / 255.0)).astype(np.uint8)
                f = cv2.warpAffine(self.fg, Mf, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
                fr = (fr.astype(np.uint16) * (255 - f[..., 3:4]) // 255 + f[..., :3]).clip(0, 255).astype(np.uint8)
        else:
            fr = paper.copy()
        if self.board:
            self.board.render(fr, tt, gk)
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

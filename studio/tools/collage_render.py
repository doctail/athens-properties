#!/usr/bin/env python3
"""Paper-collage renderer: immagini d'archivio -> carte a bordo strappato su fondo carta, movimento stop-motion.

Uso:  collage_render.py spec.json
spec = {"out":"clip.mp4","size":[1920,1080],"fps":30,"step_fps":12,"audio":null,
        "scenes":[{"img":"a.jpg","dur":3.2,"caption":"Thermopylae, 480 BCE"}, ...]}
Dipendenze: numpy, opencv (headless), Pillow, ffmpeg. Nessun modello, nessuna rete.
"""
import json, math, random, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
PAPER = (222, 205, 172)
SCRAPS = [(196, 160, 110), (170, 82, 58), (74, 96, 112), (214, 190, 140), (120, 110, 70)]


def ease_out(x):
    return 1 - (1 - min(1.0, max(0.0, x))) ** 3


def paper_bg(W, H, seed=1):
    rng = np.random.default_rng(seed)
    low = cv2.resize(rng.normal(0, 1, (H // 6, W // 6)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    low = cv2.GaussianBlur(low, (0, 0), 25)
    grain = rng.normal(0, 1, (H, W)).astype(np.float32)
    img = np.empty((H, W, 3), np.float32)
    for c in range(3):
        img[..., c] = PAPER[c] + low * 7 + grain * 3
    for _ in range(900):  # fibre
        x, y = int(rng.integers(0, W)), int(rng.integers(0, H))
        a, l = rng.uniform(0, math.pi), rng.uniform(6, 26)
        cv2.line(img, (x, y), (int(x + l * math.cos(a)), int(y + l * math.sin(a))), (PAPER[0] - 14, PAPER[1] - 14, PAPER[2] - 12), 1, cv2.LINE_AA)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    img *= (1 - 0.14 * np.clip(r - 0.5, 0, 1))[..., None]
    return np.clip(img, 0, 255).astype(np.uint8)


def torn_poly(w, h, inset, jag, rng, step=7):
    def edge(n):
        o = rng.uniform(0, jag, n)
        o = np.convolve(o, np.ones(3) / 3, mode="same")
        o[rng.random(n) < 0.04] += jag * 1.6
        return o + inset
    pts = []
    nx, ny = max(2, int(w / step)), max(2, int(h / step))
    top, bot, lef, rig = edge(nx), edge(nx), edge(ny), edge(ny)
    for i in range(nx): pts.append((i * w / nx, top[i]))
    for i in range(ny): pts.append((w - rig[i], i * h / ny))
    for i in range(nx): pts.append((w - i * w / nx, h - bot[i]))
    for i in range(ny): pts.append((lef[i], h - i * h / ny))
    return np.array(pts, np.int32)


def poly_mask(w, h, poly):
    m = np.zeros((h, w), np.uint8)
    cv2.fillPoly(m, [poly], 255, cv2.LINE_AA)
    return m


def premult(rgb, a):
    return (rgb.astype(np.uint16) * a[..., None] // 255).astype(np.uint8)


def treat(im):
    """Stampa invecchiata: desatura un po', vira caldo, contrasto lieve, grana."""
    a = np.asarray(im.convert("RGB"), np.float32)
    g = a.mean(axis=2, keepdims=True)
    a = a * 0.68 + g * 0.32
    a *= np.array([1.0, 0.95, 0.85], np.float32)
    a = (a - 128) * 1.06 + 128 + np.random.default_rng(3).normal(0, 2.2, a.shape)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def make_card(path, W, H, rng, focus=0.35, ratio=1.5):
    im = Image.open(path).convert("RGB")
    im.thumbnail((2600, 2600))
    if im.width / im.height < ratio * 0.9:  # verticale: ritaglio largo su un dettaglio (focus 0=alto, 1=basso)
        ch_ = int(im.width / ratio)
        top = int((im.height - ch_) * focus)
        im = im.crop((0, top, im.width, top + ch_))
    im = treat(im)
    maxw, maxh = int(W * 0.68), int(H * 0.74)
    s = min(maxw / im.width, maxh / im.height)
    im = im.resize((max(8, int(im.width * s)), max(8, int(im.height * s))), Image.LANCZOS)
    b, pad = 26, 30
    cw, ch = im.width + 2 * b, im.height + 2 * b
    CW, CH = cw + 2 * pad, ch + 2 * pad
    rgba = np.zeros((CH, CW, 4), np.uint8)
    # ombra
    sh = np.zeros((CH, CW), np.uint8)
    sh[pad + 12:pad + 12 + ch, pad + 8:pad + 8 + cw] = poly_mask(cw, ch, torn_poly(cw, ch, 1, 5, rng))
    sh = cv2.GaussianBlur(sh, (0, 0), 9) * 0.5
    sh = sh.astype(np.uint8)
    # bordo di carta
    pm = np.zeros((CH, CW), np.uint8)
    pm[pad:pad + ch, pad:pad + cw] = poly_mask(cw, ch, torn_poly(cw, ch, 1, 6, rng))
    base = np.zeros((CH, CW, 3), np.float32)
    base[:] = (244, 238, 224)
    # immagine strappata
    iw, ih = im.size
    im_mask = poly_mask(iw, ih, torn_poly(iw, ih, 0, 4, rng, 5))
    layer = np.zeros((CH, CW, 3), np.uint8); lm = np.zeros((CH, CW), np.uint8)
    layer[pad + b:pad + b + ih, pad + b:pad + b + iw] = np.asarray(im)
    lm[pad + b:pad + b + ih, pad + b:pad + b + iw] = im_mask
    comp = base.copy()
    a = (lm.astype(np.float32) / 255)[..., None]
    comp = comp * (1 - a) + layer.astype(np.float32) * a
    # ombra (nera) sotto, carta sopra
    out_rgb = np.zeros((CH, CW, 3), np.float32)
    sa = (sh.astype(np.float32) / 255)[..., None]
    pa = (pm.astype(np.float32) / 255)[..., None]
    out_a = np.maximum(sa, pa)
    out_rgb = (comp * pa + 20 * sa * (1 - pa)) / np.maximum(out_a, 1e-3)
    # nastro adesivo
    tape = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    td = ImageDraw.Draw(tape)
    tw, th = 150, 44
    tx, ty = CW // 2 - tw // 2, pad - 18
    td.polygon([(tx, ty), (tx + tw, ty + 4), (tx + tw - 6, ty + th), (tx + 4, ty + th - 5)], fill=(236, 214, 140, 175))
    tape = tape.rotate(rng.uniform(-6, 6), center=(CW // 2, pad), resample=Image.BICUBIC)
    t = np.asarray(tape, np.float32)
    ta = t[..., 3:4] / 255
    out_rgb = out_rgb * (1 - ta) + t[..., :3] * ta
    out_a = np.maximum(out_a, ta)
    A = (out_a[..., 0] * 255).astype(np.uint8)
    return premult(np.clip(out_rgb, 0, 255).astype(np.uint8), A), A


def make_scrap(rng, color):
    w, h = int(rng.uniform(420, 820)), int(rng.uniform(260, 600))
    pad = 24
    rgb = np.zeros((h + 2 * pad, w + 2 * pad, 3), np.float32)
    rgb[:] = color
    rgb += np.random.default_rng(int(rng.integers(1 << 30))).normal(0, 3.5, rgb.shape)
    m = np.zeros((h + 2 * pad, w + 2 * pad), np.uint8)
    m[pad:pad + h, pad:pad + w] = poly_mask(w, h, torn_poly(w, h, 1, 9, rng, 9))
    sh = cv2.GaussianBlur(np.roll(np.roll(m, 8, 0), 6, 1), (0, 0), 8) // 3
    a = np.maximum(m, sh).astype(np.uint8)
    col = (np.clip(rgb, 0, 255) * (m[..., None] / 255.0) + 25 * (sh[..., None] / 255.0) * (1 - m[..., None] / 255.0))
    col = col / np.maximum(a[..., None] / 255.0, 1e-3)
    return premult(np.clip(col, 0, 255).astype(np.uint8), a), a


def make_caption(text, W):
    f = ImageFont.truetype(FONT, 58)
    d = ImageDraw.Draw(Image.new("L", (4, 4)))
    tw = d.textlength(text, font=f)
    w, h = int(tw + 110), 112
    pad = 20
    rng = np.random.default_rng(len(text))
    m = np.zeros((h + 2 * pad, w + 2 * pad), np.uint8)
    m[pad:pad + h, pad:pad + w] = poly_mask(w, h, torn_poly(w, h, 1, 6, rng, 8))
    sh = cv2.GaussianBlur(np.roll(np.roll(m, 7, 0), 5, 1), (0, 0), 7) // 3
    img = Image.new("RGB", (w + 2 * pad, h + 2 * pad), (244, 238, 224))
    ImageDraw.Draw(img).text((pad + 55, pad + 22), text, font=f, fill=(38, 28, 20))
    rgb = np.asarray(img, np.float32)
    A = np.maximum(m, sh).astype(np.uint8)
    rgb = (rgb * (m[..., None] / 255.0) + 25 * (sh[..., None] / 255.0) * (1 - m[..., None] / 255.0)) / np.maximum(A[..., None] / 255.0, 1e-3)
    return premult(np.clip(rgb, 0, 255).astype(np.uint8), A), A


def draw(frame, sprite, A, cx, cy, ang, scale):
    h, w = sprite.shape[:2]
    H, W = frame.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, scale)
    M[0, 2] += cx - w / 2
    M[1, 2] += cy - h / 2
    sp = cv2.warpAffine(sprite, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    a = cv2.warpAffine(A, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    frame[:] = (frame.astype(np.uint16) * (255 - a[..., None]) // 255 + sp).clip(0, 255).astype(np.uint8)


class Scene:
    def __init__(self, i, sc, W, H, seed):
        rng = np.random.default_rng(seed + i * 17)
        self.dur = float(sc["dur"])
        self.dir = 1 if i % 2 == 0 else -1
        self.rot0 = float(rng.uniform(-3.2, 3.2))
        self.card = make_card(sc["img"], W, H, rng, sc.get("focus", 0.35))
        self.cap = make_caption(sc["caption"], W) if sc.get("caption") else None
        self.scraps = []
        corners = [(0.08, 0.12), (0.92, 0.18), (0.1, 0.9), (0.9, 0.86), (0.5, 0.05)]
        rng.shuffle(corners)
        for k in range(3):
            col = SCRAPS[int(rng.integers(len(SCRAPS)))]
            s, a = make_scrap(rng, col)
            fx, fy = corners[k]
            self.scraps.append((s, a, fx * W, fy * H, float(rng.uniform(-18, 18)), float(rng.choice([-1, 1]))))
        self.W, self.H = W, H

    def render(self, frame, t, jit, entering_only=False, final=False):
        W, H = self.W, self.H
        e = 1.0 if final else ease_out(t / 0.5)
        for (s, a, x, y, r, d) in self.scraps:
            off = (1 - e) * W * 0.6 * self.dir * 0.8
            draw(frame, s, a, x + off + d * 6 * t + jit[0], y + jit[1], r + 0.5 * math.sin(t * 0.7), 1.0)
        s, a = self.card
        scale = (1.0 + 0.045 * (1 - e)) * (1 + 0.05 * min(t, self.dur) / self.dur)
        ang = self.rot0 + 8.0 * (1 - e) * self.dir + 0.5 * math.sin(t * 0.9) + jit[2]
        cx = W / 2 + (1 - e) * W * 0.55 * self.dir + jit[0]
        cy = H / 2 - 18 + jit[1]
        draw(frame, s, a, cx, cy, ang, scale)
        if self.cap is not None and (final or t > 0.55):
            cs, ca = self.cap
            ce = 1.0 if final else ease_out((t - 0.55) / 0.35)
            draw(frame, cs, ca, W / 2 + jit[0] * 0.5, H - 118 + (1 - ce) * 90, -1.2 + jit[2], 1.0)


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    W, H = spec.get("size", [1920, 1080])
    fps, step = spec.get("fps", 30), spec.get("step_fps", 12)
    seed = spec.get("seed", 7)
    bg = paper_bg(W, H, seed)
    scenes = [Scene(i, sc, W, H, seed) for i, sc in enumerate(spec["scenes"])]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-"]
    if spec.get("audio"):
        cmd += ["-i", spec["audio"], "-shortest", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "medium", spec["out"]]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    ENTER = 0.5
    gt = 0.0
    cache = {}
    for i, sc in enumerate(scenes):
        n = int(round(sc.dur * fps))
        for f in range(n):
            t = f / fps
            gk = int((gt + t) * step)  # indice di passo globale (stop-motion)
            key = (i, gk)
            if key not in cache:
                tt = (gk / step) - gt
                tt = max(0.0, tt)
                r = random.Random(gk)
                jit = (r.uniform(-1.8, 1.8), r.uniform(-1.8, 1.8), r.uniform(-0.28, 0.28))
                fr = bg.copy()
                if i > 0 and tt < ENTER:
                    scenes[i - 1].render(fr, scenes[i - 1].dur, jit, final=True)
                sc.render(fr, tt, jit)
                cache = {key: fr}
            ff.stdin.write(cache[key].tobytes())
        gt += sc.dur
    ff.stdin.close()
    ff.wait()
    print("ok", spec["out"], round(gt, 1), "s")


if __name__ == "__main__":
    main()

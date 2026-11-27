#!/usr/bin/env python3
"""Render a cliffhanger EXCERPT Short (1080x1920) cut from the long's narration (no loop, no new voice).

Spec: {"audio": "<long section mp3>", "src_start": s, "src_end": s, "lead": 0.3, "tail": 4.0, "card_dur": 2.2,
 "hook": "...", "badge": "...", "out": "x.mp4", "card": "FULL STORY: LINK BELOW",
 "captions": [[t0, t1, "text", ["key",...]]...]  (source-time),
 "shots": [[t0, "images/NNN.jpg", zoom, cx, cy]...] (source-time of each shot start; last runs to the end)}
Paths relative to the spec file. Audio is cut hard at src_end (a 40 ms fade), then the tail holds the last frame.
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_short import cover, W, H, FPS, FB, MUSTARD, INK, WHITE, SFX
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def main(sp_path):
    sp = json.load(open(sp_path)); base = os.path.dirname(os.path.abspath(sp_path)); P = lambda p: os.path.join(base, p)
    s0, s1, lead, tail = sp["src_start"], sp["src_end"], sp.get("lead", 0.3), sp.get("tail", 4.0)
    vd = s1 - s0; total = lead + vd + tail; card_dur = sp.get("card_dur", 2.2)
    wav = P(sp["out"]) + ".wav"
    cuts = [sh[0] for sh in sp["shots"][1:]]
    ms = lambda t: int((t - s0 + lead) * 1000)
    inputs = ["-i", P(sp["audio"]), "-i", os.path.join(SFX, "whoosh.wav")]
    filt = f"[0:a]atrim={s0}:{s1},asetpts=PTS-STARTPTS,afade=t=out:st={vd-0.04:.3f}:d=0.04,adelay={int(lead*1000)}|{int(lead*1000)}[v]"
    labels = ["[v]"]
    for k, c in enumerate(cuts):
        d = max(0, ms(c) - 100)
        filt += f";[1:a]volume=0.22,adelay={d}|{d}[w{k}]"; labels.append(f"[w{k}]")
    filt += ";" + "".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest,apad=whole_dur={total:.3f},loudnorm=I=-14:TP=-1.5[a]"
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", filt, "-map", "[a]", "-t", f"{total:.3f}", "-ar", "48000", wav])
    cache = {}
    def img(p):
        if p not in cache:
            im = Image.open(P(p)).convert("RGB")
            bg = cover(im, W, H).filter(ImageFilter.GaussianBlur(30)); bg = Image.blend(bg, Image.new("RGB", (W, H), (10, 8, 6)), 0.45)
            cache[p] = (im, bg)
        return cache[p]
    fh, fy = 1350, 300
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-t", f"{total:.3f}", "-movflags", "+faststart", P(sp["out"])]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    f_hook = ImageFont.truetype(FB, 64); f_big = ImageFont.truetype(FB, 96)
    # caption groups (<=3 words) timed by characters inside each caption window
    groups = []
    for c0, c1, text, keys in sp["captions"]:
        ws = text.split(); gs = [ws[i:i + 3] for i in range(0, len(ws), 3)]; L = [len(" ".join(g)) for g in gs]; acc = 0
        for g, l in zip(gs, L):
            groups.append((c0 + (c1 - c0) * acc / sum(L), c0 + (c1 - c0) * (acc + l) / sum(L), " ".join(g), keys)); acc += l
    shots = sp["shots"]; src_end_out = lead + vd
    for fi in range(int(round(total * FPS))):
        t = fi / FPS; st = min(max(t - lead + s0, s0), s1)  # source time (frozen in tail)
        k = max([i for i, s in enumerate(shots) if s[0] <= st + 1e-6] or [0])
        nxt = shots[k + 1][0] if k + 1 < len(shots) else s1
        p = min(1, max(0, (t - lead + s0 - shots[k][0]) / max(0.01, nxt - shots[k][0])))
        _, name, z, cx, cy = shots[k]
        im, bg = img(name)
        fg = cover(im, W, fh, zoom=z * (1 + 0.07 * p), cx=cx, cy=cy)
        fr = bg.copy(); fr.paste(fg, (0, fy)); d = ImageDraw.Draw(fr)
        fhk = f_hook; hw = d.textlength(sp["hook"], font=fhk)
        if hw > W - 60: fhk = ImageFont.truetype(FB, int(64 * (W - 60) / hw)); hw = d.textlength(sp["hook"], font=fhk)
        d.text(((W - hw) / 2, 150), sp["hook"], font=fhk, fill=WHITE, stroke_width=7, stroke_fill=INK)
        f = ImageFont.truetype(FB, 110); tw = d.textlength(sp["badge"], font=f)
        if tw > W - 180: f = ImageFont.truetype(FB, int(110 * (W - 180) / tw)); tw = d.textlength(sp["badge"], font=f)
        d.rounded_rectangle(((W - tw) / 2 - 40, 270, (W + tw) / 2 + 40, 270 + f.size + 50), radius=30, fill=MUSTARD, outline=INK, width=8)
        d.text(((W - tw) / 2, 290), sp["badge"], font=f, fill=INK)
        card = t >= total - card_dur
        if card:
            line = sp["card"]; f2 = ImageFont.truetype(FB, 84); tw = d.textlength(line, font=f2)
            if tw > W - 120: f2 = ImageFont.truetype(FB, int(84 * (W - 120) / tw)); tw = d.textlength(line, font=f2)
            d.rounded_rectangle(((W - tw) / 2 - 40, 1440, (W + tw) / 2 + 40, 1440 + f2.size + 60), radius=30, fill=MUSTARD, outline=INK, width=8)
            d.text(((W - tw) / 2, 1465), line, font=f2, fill=INK)
        else:
            cur = [g for g in groups if g[0] <= st + 1e-6]
            if t < lead: cur = []
            if cur:
                g = cur[-1]; line = g[2].upper()
                if t > src_end_out and g is groups[-1]: line += "..."
                f2 = f_big; tw = d.textlength(line, font=f2)
                if tw > W - 80: f2 = ImageFont.truetype(FB, int(96 * (W - 80) / tw)); tw = d.textlength(line, font=f2)
                x = (W - tw) / 2; keys = [w.capitalize() for w in g[3]]
                for wd in line.split(" "):
                    col = MUSTARD if wd.strip(".,?!").capitalize() in keys else WHITE
                    d.text((x, 1450), wd, font=f2, fill=col, stroke_width=9, stroke_fill=INK); x += d.textlength(wd + " ", font=f2)
        pr.stdin.write(fr.tobytes())
    pr.stdin.close(); pr.wait(); os.remove(wav)
    print("EXCERPT", P(sp["out"]), round(total, 2), "s")


if __name__ == "__main__":
    main(sys.argv[1])

#!/usr/bin/env python3
"""Render a loopable vertical Short (1080x1920) from a JSON spec.

Spec (JSON): {
  "audio": "path.mp3", "out": "path.mp4", "hook": "HOW LONG WOULD YOU LAST?",
  "phrases": [{"text": "Ten seconds.", "img": "path.jpg", "key": ["Ten","seconds"], "badge": "~10 SECONDS", "shake": false}, ...],
  "gap": 0.12
}
Phrases are matched in order to the speech chunks found by silence detection in the audio; long pauses are
cut to `gap` so the Short is tight, and the audio ends on the last word so it loops into the first one.
The last phrase reuses the first image/framing so the last frame matches the first.
"""
import json, os, re, subprocess, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920; FPS = 30
FB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
MUSTARD = (255, 205, 60); INK = (30, 20, 12); WHITE = (255, 255, 255)
SFX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "sfx")


def chunks(audio):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", audio, "-af", "silencedetect=n=-35dB:d=0.12", "-f", "null", "-"], capture_output=True, text=True).stderr
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio]))
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    starts = [0.0] + en; ends = st + [dur]
    segs = [(max(0, s - 0.03), min(dur, e + 0.05)) for s, e in zip(starts, ends) if e - s > 0.15]
    return segs


def cover(img, w, h, zoom=1.0, cx=0.5, cy=0.5):
    r = max(w / img.width, h / img.height) * zoom
    nw, nh = img.width * r, img.height * r
    x0 = (nw - w) * cx; y0 = (nh - h) * cy
    return img.resize((w, h), Image.LANCZOS, box=(x0 / r, y0 / r, (x0 + w) / r, (y0 + h) / r))


def main(spec_path):
    sp = json.load(open(spec_path)); base = os.path.dirname(os.path.abspath(spec_path))
    P = lambda p: os.path.join(base, p)
    segs = chunks(P(sp["audio"])); phrases = sp["phrases"]
    assert len(segs) == len(phrases), f"{len(segs)} speech chunks vs {len(phrases)} phrases: {segs}"
    gap = sp.get("gap", 0.12)
    # build tight audio
    parts = []; t = 0; timeline = []
    for (s, e), ph in zip(segs, phrases):
        timeline.append((t, t + (e - s), ph)); t += (e - s) + gap
    total = t - gap
    filt = "".join(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,apad=pad_dur={gap if i < len(segs)-1 else 0}[p{i}];" for i, (s, e) in enumerate(segs))
    filt += "".join(f"[p{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1[v]"
    sfx = [("boom", 0.0, 0.5)] + [("whoosh", max(0, a - 0.1), 0.35) for a, _, _ in timeline[1:]]
    inputs = ["-i", P(sp["audio"])]
    for k, (n, at, vol) in enumerate(sfx):
        inputs += ["-i", os.path.join(SFX, n + ".wav")]; ms = int(at * 1000)
        filt += f";[{k+1}:a]volume={vol},adelay={ms}|{ms}[s{k}]"
    filt += ";[v]" + "".join(f"[s{k}]" for k in range(len(sfx))) + f"amix=inputs={len(sfx)+1}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5[a]"
    wav = P(sp["out"]) + ".wav"
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", filt, "-map", "[a]", "-t", f"{total:.3f}", "-ar", "48000", wav])
    # images
    cache = {}
    def img(p):
        if p not in cache:
            im = Image.open(P(p)).convert("RGB")
            bg = cover(im, W, H).filter(ImageFilter.GaussianBlur(30)); bg = Image.blend(bg, Image.new("RGB", (W, H), (10, 8, 6)), 0.45)
            cache[p] = (im, bg)
        return cache[p]
    fh = 1350; fy = 300
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-t", f"{total:.3f}", "-movflags", "+faststart", P(sp["out"])]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    fh_big = ImageFont.truetype(FB, 96); fh_hook = ImageFont.truetype(FB, 64); fh_badge = ImageFont.truetype(FB, 120)
    n = int(round(total * FPS))
    for fi in range(n):
        t = fi / FPS
        k = max(i for i, (a, _, _) in enumerate(timeline) if a <= t + 1e-6) if t >= timeline[0][0] else 0
        a, b, ph = timeline[k]; nxt = timeline[k + 1][0] if k + 1 < len(timeline) else total
        p = (t - a) / max(0.01, nxt - a)
        im, bg = img(ph["img"])
        last = k == len(timeline) - 1
        z = 1.0 + 0.08 * p if not last else 1.08 - 0.08 * p  # last shot zooms back to the first shot's start framing
        if k == 0: z = 1.0 + 0.08 * p
        if last and ph["img"] == timeline[0][2]["img"]: z = 1.0 + 0.08 * max(0.0, 1 - p) * 0  # end exactly at first framing
        fg = cover(im, W, fh, zoom=z, cx=ph.get("cx", 0.5), cy=0.5)
        if ph.get("shake"):
            m = 18 * max(0, 1 - p * 2); fg = fg.transform(fg.size, Image.AFFINE, (1, 0, random.uniform(-m, m), 0, 1, random.uniform(-m, m)))
        fr = bg.copy(); fr.paste(fg, (0, fy))
        d = ImageDraw.Draw(fr)
        # hook (static, top)
        hw = d.textlength(sp["hook"], font=fh_hook)
        d.text(((W - hw) / 2, 150), sp["hook"], font=fh_hook, fill=WHITE, stroke_width=7, stroke_fill=INK)
        # badge
        if ph.get("badge"):
            s = min(1, (t - a) / 0.18); s = 1 + 0.25 * (1 - s) if s < 1 else 1
            f = ImageFont.truetype(FB, int(120 * s)); tw = d.textlength(ph["badge"], font=f)
            d.rounded_rectangle(((W - tw) / 2 - 40, 420, (W + tw) / 2 + 40, 420 + f.size + 50), radius=30, fill=MUSTARD, outline=INK, width=8)
            d.text(((W - tw) / 2, 440), ph["badge"], font=f, fill=INK)
        # captions: phrase split into chunks of up to 3 words, timed by characters
        words = ph["text"].split(); groups = [words[i:i + 3] for i in range(0, len(words), 3)]
        lens = [len(" ".join(g)) for g in groups]; acc = 0; gi = 0
        for i, L in enumerate(lens):
            if (t - a) / max(0.01, b - a) >= acc / sum(lens): gi = i
            acc += L
        g = groups[gi]; line = " ".join(g).upper()
        tw = d.textlength(line, font=fh_big)
        if tw > W - 80:
            f2 = ImageFont.truetype(FB, int(96 * (W - 80) / tw)); tw = d.textlength(line, font=f2)
        else: f2 = fh_big
        x = (W - tw) / 2; y = fy + fh - 60
        for wd in line.split(" "):
            col = MUSTARD if wd.strip(".,?!").capitalize() in [w.capitalize() for w in ph.get("key", [])] else WHITE
            d.text((x, y), wd, font=f2, fill=col, stroke_width=9, stroke_fill=INK)
            x += d.textlength(wd + " ", font=f2)
        pr.stdin.write(fr.tobytes())
    pr.stdin.close(); pr.wait(); os.remove(wav)
    print("SHORT", P(sp["out"]), round(total, 2), "s")


if __name__ == "__main__":
    main(sys.argv[1])

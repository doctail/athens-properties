#!/usr/bin/env python3
"""Render a Dave vs History episode (v2: animated HUD, timed callouts, transitions, SFX).

Usage: python3 render_episode.py <episode_dir> [--only i ...] [--jobs 4] [--fps 30]
Inputs : <ep>/edit.json, <ep>/script.md (narration text, for anchor timing), <ep>/images/NNN.jpg,
         <ep>/audio/*.mp3, studio/assets/sfx/*.wav (python3 studio/tools/make_sfx.py)
Output : <ep>/build/final.mp4
"""
import json, os, re, subprocess, math, argparse, random
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
MUSTARD = (227, 167, 47); SAND = (234, 217, 184); INK = (59, 42, 30); BLUE = (31, 58, 95); RED = (196, 98, 58); GREEN = (107, 140, 58)
XFADE = 0.45
SFX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "sfx")
_F = {}


def font(path, size):
    k = (path, size)
    if k not in _F: _F[k] = ImageFont.truetype(path, size)
    return _F[k]


def probe(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))


def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3


def back(x):  # overshoot ease for pop-ins
    x = max(0.0, min(1.0, x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def narration_texts(ep):
    t = open(os.path.join(ep, "script.md")).read()
    secs = re.split(r"^## ", t, flags=re.M)[1:]
    return [" ".join(l.split(":", 1)[1].strip() for l in s.splitlines() if l.startswith("NARRATOR:")).replace("*", "") for s in secs]


def anchor_time(text, anchor, ndur):
    i = text.find(anchor)
    if i < 0: raise ValueError(f"anchor not found: {anchor!r}")
    return max(0.0, i / len(text) * ndur - 0.15)


def load_cover(path, scale=1.12):
    im = Image.open(path).convert("RGB")
    tw, th = int(W * scale), int(H * scale)
    r = max(tw / im.width, th / im.height)
    im = im.resize((math.ceil(im.width * r), math.ceil(im.height * r)), Image.LANCZOS)
    x, y = (im.width - tw) // 2, (im.height - th) // 2
    return im.crop((x, y, x + tw, y + th))


def kenburns(img, p, mode, shake=(0, 0)):
    iw, ih = img.size
    z = {0: 1 - 0.10 * p, 1: 0.90 + 0.10 * p, 2: 0.92, 3: 0.92}[mode % 4]
    vw, vh = iw * z, ih * z
    cx, cy = iw / 2 + shake[0], ih / 2 + shake[1]
    if mode % 4 == 2: cx = vw / 2 + (iw - vw) * p + shake[0]
    if mode % 4 == 3: cx = iw - vw / 2 - (iw - vw) * p + shake[0]
    cx = min(max(cx, vw / 2), iw - vw / 2); cy = min(max(cy, vh / 2), ih - vh / 2)
    return img.resize((W, H), Image.BILINEAR, box=(cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2))


def glitch(frame, amt, seed):
    if amt <= 0: return frame
    a = np.asarray(frame).copy(); rnd = random.Random(seed)
    dx = int(28 * amt)
    a[:, :, 0] = np.roll(a[:, :, 0], dx, axis=1); a[:, :, 2] = np.roll(a[:, :, 2], -dx, axis=1)
    for _ in range(int(14 * amt)):
        y = rnd.randrange(0, H - 40); h = rnd.randrange(6, 40); s = rnd.randrange(-120, 120)
        a[y:y + h] = np.roll(a[y:y + h], int(s * amt), axis=1)
    return Image.fromarray(a)


def rounded(d, box, fill, r=28, outline=None, width=0):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def outlined_text(d, xy, txt, f, fill, stroke=INK, sw=6, alpha=255):
    d.text(xy, txt, font=f, fill=fill + (alpha,), stroke_width=sw, stroke_fill=stroke + (alpha,))


def draw_board(d, board, highlight, alpha=1.0, x0=None, reveal=1.0):
    A = lambda c, k=255: c + (int(k * alpha),)
    bw, rowh = 700, 74
    x0 = (W - bw) // 2 if x0 is None else x0
    y0 = (H - (rowh * 12 + 90)) // 2
    rounded(d, (x0 - 20, y0 - 20, x0 + bw + 20, y0 + rowh * 12 + 90), A(BLUE, 235), outline=A(INK), width=6)
    d.text((x0 + 10, y0 - 5), "WORST  →  BEST", font=font(FONT_BLACK, 52), fill=A(MUSTARD))
    for i, e in enumerate(board):
        rank = 12 - i; y = y0 + 80 + i * rowh; hl = highlight == rank
        ra = alpha * ease((reveal * 12 - i) / 1.0) if reveal < 1 else alpha
        B = lambda c, k=255: c + (int(k * ra),)
        fill = B(MUSTARD) if hl else (B((255, 255, 255), 40) if e is None else B((255, 255, 255), 230))
        rounded(d, (x0, y, x0 + bw, y + rowh - 10), fill, r=16)
        d.text((x0 + 18, y + 8), f"#{rank}", font=font(FONT_BLACK, 44), fill=B(INK))
        if e:
            d.text((x0 + 130, y + 10), e["era"], font=font(FONT_BOLD, 40), fill=B(INK))
            f = font(FONT_BLACK, 38); sw = d.textlength(e["survival"], font=f)
            d.text((x0 + bw - 20 - sw, y + 12), e["survival"], font=f, fill=B(INK if hl else RED))


def draw_meters(d, meters, a, t_in):
    """Survival HUD, top-left: AIR/FOOD/WATER (good=green) and DANGER (red)."""
    if a <= 0: return
    x0, y0 = 50, H - 300
    rounded(d, (x0, y0, x0 + 430, y0 + 250), (31, 58, 95, int(215 * a)), r=24, outline=INK + (int(255 * a),), width=5)
    for i, (k, v) in enumerate(meters.items()):
        y = y0 + 22 + i * 56
        d.text((x0 + 22, y + 2), k, font=font(FONT_BLACK, 34), fill=(255, 255, 255, int(255 * a)))
        col = RED if k == "DANGER" else (GREEN if v >= 3 else (MUSTARD if v >= 2 else RED))
        for s in range(5):
            on = s < v and t_in > 0.15 * (s + 1) + 0.1 * i
            bx = x0 + 200 + s * 42
            rounded(d, (bx, y + 6, bx + 34, y + 40), (col if on else (20, 30, 50)) + (int((255 if on else 200) * a),), r=8)


def draw_progress(d, rank, a):
    if a <= 0 or not rank: return
    cx0 = W // 2 - 11 * 34 // 2
    for i in range(12):
        r_ = 12 - i; x = cx0 + i * 34; y = 46
        done = r_ > rank; cur = r_ == rank
        rad = 13 if cur else 9
        fill = MUSTARD if cur else ((255, 255, 255) if done else (255, 255, 255))
        al = 255 if (cur or done) else 90
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=fill + (int(al * a),), outline=INK + (int(255 * a),), width=3)


def overlays(frame, sec, t, dur, ev, board):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    rank = sec.get("rank")
    # progress dots + meters
    if rank:
        draw_progress(d, rank, ease((t - 0.6) / 0.4))
        if sec.get("meters"):
            ti = t - 4.6
            draw_meters(d, sec["meters"], ease(ti / 0.4), ti)
    # era banner (#rank) or generic banner (big label, e.g. a clock time)
    bn = sec.get("banner")
    if rank or bn:
        big = f"#{rank}" if rank else bn["big"]; title = sec["era"] if rank else bn["title"]; sub = sec["when"] if rank else bn.get("sub", "")
        a = ease((t - 0.2) / 0.5) * (1 - ease((t - 4.3) / 0.5))
        if a > 0:
            dx = int(-120 * (1 - a)); fb = font(FONT_BLACK, 120 if rank else 92)
            bw = d.textlength(big, font=fb); tx = 95 + bw + 40
            tw = max(d.textlength(title, font=font(FONT_BLACK, 62)), d.textlength(sub, font=font(FONT_BOLD, 40)))
            rounded(d, (60 + dx, H - 300, tx + tw + 50 + dx, H - 70), BLUE + (int(225 * a),), outline=INK + (int(255 * a),), width=6)
            d.text((95 + dx, H - 290 + (0 if rank else 22)), big, font=fb, fill=MUSTARD + (int(255 * a),))
            d.text((tx + dx, H - 265), title, font=font(FONT_BLACK, 62), fill=(255, 255, 255, int(255 * a)))
            d.text((tx + dx, H - 180), sub, font=font(FONT_BOLD, 40), fill=SAND + (int(255 * a),))
    # threat tally (top centre): N of M dots filled, label on the left
    if sec.get("tally"):
        tl = sec["tally"]; n = tl["before"] + (tl["add"] if ev.get("survival_t") is not None and t >= ev["survival_t"] else 0)
        a = ease((t - 0.6) / 0.4)
        if a > 0:
            lab = tl.get("label", "THREATS"); f = font(FONT_BLACK, 34); lw = d.textlength(lab, font=f)
            total = tl["total"]; x0 = W // 2 - (lw + 20 + total * 40) // 2
            d.text((x0, 30), lab, font=f, fill=(255, 255, 255, int(255 * a)), stroke_width=4, stroke_fill=INK + (int(255 * a),))
            for i in range(total):
                x = x0 + lw + 40 + i * 40; on = i < n
                d.ellipse((x - 14, 32, x + 14, 60), fill=(RED if on else (255, 255, 255)) + (int((255 if on else 110) * a),), outline=INK + (int(255 * a),), width=3)
    # callouts (pop-in cards, top centre)
    for c in ev["callouts"]:
        lt = t - c["t"]
        if 0 <= lt <= 3.6:
            s = back(lt / 0.35) * (1 - ease((lt - 3.2) / 0.4)); a = min(1, lt / 0.15) * (1 - ease((lt - 3.2) / 0.4))
            f = font(FONT_BLACK, int(64 * max(0.3, s)))
            tw = d.textlength(c["text"], font=f); bh = int(110 * max(0.3, s))
            badge_on = sec.get("survival") and ev.get("survival_t") is not None and t >= ev["survival_t"]
            x = (W - tw) / 2; y = 330 if badge_on else 130
            rounded(d, (x - 40, y, x + tw + 40, y + bh), SAND + (int(245 * a),), r=24, outline=INK + (int(255 * a),), width=6)
            d.text((x, y + (bh - f.size) / 2 - 6), c["text"], font=f, fill=INK + (int(255 * a),))
    # survival badge, appears when narrator says it
    if sec.get("survival") and ev.get("survival_t") is not None:
        lt = t - ev["survival_t"]
        if lt >= 0:
            s = back(lt / 0.4); a = min(1, lt / 0.15)
            sh = int(10 * math.sin(lt * 40) * max(0, 1 - lt / 0.5))
            bw, bh = int(max(720, d.textlength(sec["survival"], font=font(FONT_BLACK, 96)) + 80) * s), int(210 * s)
            x1, y1 = W - 60 - bw + sh, 60
            rounded(d, (x1, y1, x1 + bw, y1 + bh), MUSTARD + (int(245 * a),), outline=INK + (int(255 * a),), width=7)
            if s > 0.6:
                d.text((x1 + 34, y1 + 18), sec.get("badge_title", "SURVIVAL TIME"), font=font(FONT_BOLD, 42), fill=INK + (int(255 * a),))
                d.text((x1 + 34, y1 + 70), sec["survival"], font=font(FONT_BLACK, 96), fill=INK + (int(255 * a),))
    # speech bubbles
    for b in sec.get("bubbles", []):
        if b["t0"] <= t <= b["t1"]:
            s = back((t - b["t0"]) / 0.3); a = min(1, (t - b["t0"]) / 0.1) * (1 - ease((t - b["t1"] + 0.25) / 0.25))
            f = font(FONT_BLACK, int(56 * max(0.3, s))); tw = d.textlength(b["text"], font=f)
            x, y = b["x"], b["y"]
            rounded(d, (x, y, x + tw + 70, y + int(110 * s)), (255, 255, 255, int(245 * a)), r=50, outline=INK + (int(255 * a),), width=6)
            d.polygon([(x + 60, y + 104 * s), (x + 110, y + 104 * s), (x + 50, y + 160 * s)], fill=(255, 255, 255, int(245 * a)))
            d.text((x + 35, y + 22 * s), b["text"], font=f, fill=INK + (int(255 * a),))
    # title card
    if sec.get("title_card") and t >= sec["title_card"]:
        lt = t - sec["title_card"]; a = ease(lt / 0.3); s = back(lt / 0.45)
        d.rectangle((0, 0, W, H), fill=(20, 14, 10, int(150 * a)))
        f = font(FONT_BLACK, int(170 * max(0.3, s))); txt = "DAVE VS HISTORY"; tw = d.textlength(txt, font=f)
        outlined_text(d, ((W - tw) / 2, H / 2 - f.size * 0.65), txt, f, (255, 255, 255), sw=10, alpha=int(255 * a))
    # end board
    if sec.get("board_overlay") and t <= sec["board_overlay"]:
        a = ease(t / 0.5) * (1 - ease((t - sec["board_overlay"] + 0.5) / 0.5))
        draw_board(d, board, None, alpha=a, x0=W - 760, reveal=min(1, t / 6))
    out = Image.alpha_composite(frame.convert("RGBA"), ov).convert("RGB")
    # white flash
    for ft in ev["flashes"]:
        lt = t - ft
        if 0 <= lt < 0.8: out = Image.blend(out, Image.new("RGB", (W, H), (255, 250, 235)), 0.9 * (1 - lt / 0.8))
    return out


def mix_cmd(audio_in, sfx, out_audio, dur, tail):
    inputs = ["-i", audio_in]; filters = [f"[0:a]aresample=48000,apad=pad_dur={tail}[n]"]; labels = ["[n]"]
    for k, (name, at, vol) in enumerate(sfx):
        inputs += ["-i", os.path.join(SFX_DIR, name + ".wav")]
        ms = max(0, int(at * 1000))
        filters.append(f"[{k+1}:a]volume={vol},adelay={ms}|{ms}[s{k}]"); labels.append(f"[s{k}]")
    filters.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=first,alimiter=limit=0.95[a]")
    return ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filters), "-map", "[a]", "-t", f"{dur:.3f}",
            "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out_audio]


def render_section(args):
    ep, idx, sec, fps, text, board = args
    build = os.path.join(ep, "build"); os.makedirs(build, exist_ok=True)
    audio = os.path.join(ep, "audio", sec["audio"])
    ndur = probe(audio); tail = sec.get("tail", 0.7); dur = ndur + tail
    # images: int (evenly spread) or {"n": N, "at": "anchor phrase"} (starts when the narrator says it)
    entries = [e if isinstance(e, dict) else {"n": e} for e in sec["images"]]
    nums = [e["n"] for e in entries]
    imgs = [load_cover(os.path.join(ep, "images", f"{n:03d}.jpg")) for n in nums]
    starts = []
    for i, e in enumerate(entries):
        if i == 0: starts.append(0.0)
        elif "at" in e: starts.append(anchor_time(text, e["at"], ndur))
        else: starts.append(None)
    # fill unanchored starts evenly between anchored neighbours
    known = [(i, v) for i, v in enumerate(starts) if v is not None] + [(len(starts), dur)]
    for (i0, v0), (i1, v1) in zip(known, known[1:]):
        for k in range(i0 + 1, i1): starts[k] = v0 + (v1 - v0) * (k - i0) / (i1 - i0)
    for i in range(1, len(starts)):
        if starts[i] <= starts[i - 1] + 0.8: raise ValueError(f"section {idx}: image {nums[i]} starts too close/before previous ({starts[i]:.2f})")
    ends = starts[1:] + [dur]
    seg = dur / len(imgs)
    sec = dict(sec); sec["images"] = nums
    ev = {"callouts": [], "flashes": [], "survival_t": None}
    sfx = []
    for c in sec.get("callouts", []):
        tt = anchor_time(text, c["anchor"], ndur); ev["callouts"].append({"text": c["text"], "t": tt}); sfx.append(("pop", tt, 0.7))
    if sec.get("survival_anchor"):
        ev["survival_t"] = anchor_time(text, sec["survival_anchor"], ndur) + 0.6; sfx.append(("ding", ev["survival_t"], 0.6))
    for n in sec.get("flash_images", []):
        ft = starts[nums.index(n)]; ev["flashes"].append(ft); sfx.append(("boom", ft, 1.0))
    if sec.get("rank"):
        sfx += [("glitch", 0.0, 0.6), ("whoosh", 0.15, 0.6)]
    elif sec.get("banner"):
        sfx += [("whoosh", 0.15, 0.6)]
        if sec.get("meters"): sfx.append(("tick", 4.6, 0.6))
    for b in sec.get("bubbles", []): sfx.append(("pop", b["t0"], 0.7))
    if sec.get("title_card"):
        sfx.append(("boom", sec["title_card"], 0.8))
        if sec.get("riser_before_title"): sfx.append(("riser", sec["title_card"] - 1.2, 0.6))
    if sec.get("board_overlay"): sfx.append(("whoosh", 0.0, 0.5))
    wav = os.path.join(build, f"seg{idx:02d}.wav")
    subprocess.check_call(mix_cmd(audio, sfx, wav, dur, tail))
    out = os.path.join(build, f"seg{idx:02d}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
           "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-t", f"{dur:.3f}", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(int(round(dur * fps))):
        t = fi / fps
        k = max(i for i in range(len(starts)) if starts[i] <= t + 1e-9); lt = t - starts[k]; seg = ends[k] - starts[k]
        mode = (sec["images"][k] + idx) % 4
        shake = (0, 0)
        for ft in ev["flashes"]:
            if 0 <= t - ft < 1.0:
                m = 30 * (1 - (t - ft)); shake = (random.uniform(-m, m), random.uniform(-m, m))
        fr = kenburns(imgs[k], min(1, lt / seg), mode, shake)
        if k + 1 < len(imgs) and lt > seg - XFADE:
            fr = Image.blend(fr, kenburns(imgs[k + 1], 0, (sec["images"][k + 1] + idx) % 4), (lt - (seg - XFADE)) / XFADE)
        if sec.get("rank") and t < 0.5: fr = glitch(fr, 1 - t / 0.5, fi)
        p.stdin.write(overlays(fr, sec, t, dur, ev, board).tobytes())
    p.stdin.close(); p.wait()
    return out, dur


def render_card(args):
    ep, idx, card, fps = args
    build = os.path.join(ep, "build"); os.makedirs(build, exist_ok=True)
    bg = load_cover(os.path.join(ep, "images", f"{card['bg']:03d}.jpg")).resize((W, H)).filter(ImageFilter.GaussianBlur(14))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (20, 14, 10)), 0.35).convert("RGBA")
    dur = card.get("dur", 2.2)
    wav = os.path.join(build, f"card{idx:02d}.wav")
    hl_row = 12 - card["highlight"]
    sfx = [("whoosh", 0.0, 0.5)] + [("tick", 0.05 + i * 0.04, 0.4) for i in range(0, hl_row + 1)] + [("pop", 0.55, 0.7)]
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-t", f"{dur}", "-i", "anullsrc=r=48000:cl=stereo",
                           "-c:a", "pcm_s16le", wav + ".silence.wav"])
    subprocess.check_call(mix_cmd(wav + ".silence.wav", sfx, wav, dur, 0))
    out = os.path.join(build, f"card{idx:02d}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
           "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-t", f"{dur:.3f}", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(int(round(dur * fps))):
        t = fi / fps
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        draw_board(d, card["board"], card["highlight"] if t > 0.5 else None, alpha=ease(t / 0.25), reveal=min(1, t / 0.5))
        p.stdin.write(Image.alpha_composite(bg, ov).convert("RGB").tobytes())
    p.stdin.close(); p.wait()
    return out, dur


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("ep"); ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--only", type=int, nargs="*"); ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    cfg = json.load(open(os.path.join(a.ep, "edit.json")))
    secs = cfg["sections"]; texts = narration_texts(a.ep)
    assert len(texts) == len(secs), (len(texts), len(secs))
    board = [None] * 12; timeline = []
    for i, s in enumerate(secs):
        timeline.append(("sec", i, s))
        if s.get("rank"):
            board[12 - s["rank"]] = {"era": s["era_short"], "survival": s["survival"]}
            timeline.append(("card", i, {"board": list(board), "highlight": s["rank"], "bg": s["images"][-1]}))
    final_board = list(board)
    with ProcessPoolExecutor(a.jobs) as ex:
        jobs = []
        for kind, i, obj in timeline:
            if a.only is not None and i not in a.only: continue
            arg = (a.ep, i, obj, a.fps, texts[i], final_board) if kind == "sec" else (a.ep, i, obj, a.fps)
            jobs.append(ex.submit(render_section if kind == "sec" else render_card, arg))
        outs = [j.result() for j in jobs]
    if a.only is None:
        lst = os.path.join(a.ep, "build", "concat.txt")
        with open(lst, "w") as f:
            for o, _ in outs: f.write(f"file '{os.path.abspath(o)}'\n")
        final = os.path.join(a.ep, "build", "final.mp4")
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", final])
        print("FINAL", final, probe(final))
    else:
        for o, d in outs: print(o, round(d, 2))


if __name__ == "__main__":
    main()

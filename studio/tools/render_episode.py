#!/usr/bin/env python3
"""Render a Dave vs History episode from numbered images + per-section narration.

Usage: python3 render_episode.py <episode_dir> [--only SECTION_INDEX ...] [--fps 30]
Reads <episode_dir>/edit.json, writes <episode_dir>/build/ segments and final.mp4.
"""
import json, os, subprocess, sys, math, argparse
from concurrent.futures import ProcessPoolExecutor
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
MUSTARD = (227, 167, 47); SAND = (234, 217, 184); INK = (59, 42, 30); BLUE = (31, 58, 95); RED = (196, 98, 58)
XFADE = 0.45  # seconds of crossfade between images


def font(path, size):
    return ImageFont.truetype(path, size)


def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(out)


def load_cover(path, scale=1.12):
    im = Image.open(path).convert("RGB")
    tw, th = int(W * scale), int(H * scale)
    r = max(tw / im.width, th / im.height)
    im = im.resize((math.ceil(im.width * r), math.ceil(im.height * r)), Image.LANCZOS)
    x, y = (im.width - tw) // 2, (im.height - th) // 2
    return im.crop((x, y, x + tw, y + th))


def kenburns(img, p, mode):
    """p in [0,1]; return WxH frame cropped from img (which is 1.12x)."""
    iw, ih = img.size
    zmin, zmax = 1.0, 1.0 / 1.12 * iw / W  # view width as fraction
    # zoom in or out between full image and W-size window
    if mode % 4 == 0:   z = 1 - 0.10 * p            # zoom in
    elif mode % 4 == 1: z = 0.90 + 0.10 * p         # zoom out
    elif mode % 4 == 2: z = 0.92                     # pan right
    else:               z = 0.92                     # pan left
    vw, vh = iw * z, ih * z
    cx, cy = iw / 2, ih / 2
    if mode % 4 == 2: cx = vw / 2 + (iw - vw) * p
    if mode % 4 == 3: cx = iw - vw / 2 - (iw - vw) * p
    box = (cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2)
    return img.resize((W, H), Image.BILINEAR, box=box)


def rounded(draw, box, fill, r=28, outline=None, width=0):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3


def overlay_era(frame, sec, t, dur):
    """Era banner at start, survival badge at end."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    if sec.get("rank"):
        a = ease((t - 0.2) / 0.5) * (1 - ease((t - 4.3) / 0.5))
        if a > 0:
            dx = int(-80 * (1 - a))
            rounded(d, (60 + dx, H - 300, 900 + dx, H - 70), (31, 58, 95, int(225 * a)), outline=(59, 42, 30, int(255 * a)), width=6)
            d.text((95 + dx, H - 290), f"#{sec['rank']}", font=font(FONT_BLACK, 120), fill=MUSTARD + (int(255 * a),))
            d.text((330 + dx, H - 265), sec["era"], font=font(FONT_BLACK, 62), fill=(255, 255, 255, int(255 * a)))
            d.text((330 + dx, H - 180), sec["when"], font=font(FONT_BOLD, 40), fill=SAND + (int(255 * a),))
    if sec.get("survival"):
        start = dur - 6.0
        a = ease((t - start) / 0.5)
        if a > 0:
            dy = int(-60 * (1 - a))
            rounded(d, (W - 760, 50 + dy, W - 60, 250 + dy), (227, 167, 47, int(240 * a)), outline=(59, 42, 30, int(255 * a)), width=6)
            d.text((W - 725, 70 + dy), "SURVIVAL TIME", font=font(FONT_BOLD, 40), fill=INK + (int(255 * a),))
            d.text((W - 725, 120 + dy), sec["survival"], font=font(FONT_BLACK, 92), fill=INK + (int(255 * a),))
    for b in sec.get("bubbles", []):
        if b["t0"] <= t <= b["t1"]:
            a = ease((t - b["t0"]) / 0.25) * (1 - ease((t - b["t1"] + 0.25) / 0.25))
            f = font(FONT_BLACK, 56); tw = d.textlength(b["text"], font=f)
            x, y = b["x"], b["y"]
            rounded(d, (x, y, x + tw + 70, y + 110), (255, 255, 255, int(245 * a)), r=50, outline=INK + (int(255 * a),), width=6)
            d.polygon([(x + 60, y + 104), (x + 110, y + 104), (x + 50, y + 160)], fill=(255, 255, 255, int(245 * a)))
            d.text((x + 35, y + 22), b["text"], font=f, fill=INK + (int(255 * a),))
    if sec.get("title_card") and t >= sec["title_card"]:
        a = ease((t - sec["title_card"]) / 0.4)
        d.rectangle((0, 0, W, H), fill=(20, 14, 10, int(140 * a)))
        f = font(FONT_BLACK, 170); txt = "DAVE VS HISTORY"; tw = d.textlength(txt, font=f)
        x, y = (W - tw) / 2, H / 2 - 110
        for ox in range(-8, 9, 4):
            for oy in range(-8, 9, 4):
                d.text((x + ox, y + oy), txt, font=f, fill=INK + (int(255 * a),))
        d.text((x, y), txt, font=f, fill=(255, 255, 255, int(255 * a)))
    if sec.get("board_overlay") and t <= sec["board_overlay"]:
        a = ease(t / 0.5) * (1 - ease((t - sec["board_overlay"] + 0.5) / 0.5))
        draw_board(d, sec["board"], highlight=None, alpha=a, x0=W - 760)
    return Image.alpha_composite(frame.convert("RGBA"), ov).convert("RGB")


def draw_board(d, board, highlight, alpha=1.0, x0=None):
    """board: list of 12 entries from rank 12 down to 1: {rank, era, survival} or None."""
    A = lambda c, k=255: c + (int(k * alpha),)
    bw, rowh = 700, 74
    x0 = (W - bw) // 2 if x0 is None else x0
    y0 = (H - (rowh * 12 + 90)) // 2
    rounded(d, (x0 - 20, y0 - 20, x0 + bw + 20, y0 + rowh * 12 + 90), A((31, 58, 95), 235), outline=A(INK), width=6)
    d.text((x0 + 10, y0 - 5), "WORST  →  BEST", font=font(FONT_BLACK, 52), fill=A(MUSTARD))
    for i, e in enumerate(board):
        rank = 12 - i
        y = y0 + 80 + i * rowh
        hl = highlight == rank
        fill = A(MUSTARD) if hl else (A((255, 255, 255), 40) if e is None else A((255, 255, 255), 230))
        rounded(d, (x0, y, x0 + bw, y + rowh - 10), fill, r=16)
        d.text((x0 + 18, y + 8), f"#{rank}", font=font(FONT_BLACK, 44), fill=A(INK))
        if e:
            d.text((x0 + 130, y + 10), e["era"], font=font(FONT_BOLD, 40), fill=A(INK))
            sw = d.textlength(e["survival"], font=font(FONT_BLACK, 38))
            d.text((x0 + bw - 20 - sw, y + 12), e["survival"], font=font(FONT_BLACK, 38), fill=A(RED if not hl else INK))


def render_section(args):
    ep, idx, sec, fps = args
    build = os.path.join(ep, "build"); os.makedirs(build, exist_ok=True)
    audio = os.path.join(ep, "audio", sec["audio"])
    dur = probe(audio) + sec.get("tail", 0.7)
    imgs = [load_cover(os.path.join(ep, "images", f"{n:03d}.jpg")) for n in sec["images"]]
    seg = dur / len(imgs)
    out = os.path.join(build, f"seg{idx:02d}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
           "-i", audio, "-filter_complex", f"[1:a]apad=pad_dur={sec.get('tail', 0.7)},aresample=48000[a]", "-map", "0:v", "-map", "[a]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           "-t", f"{dur:.3f}", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(round(dur * fps))
    for fi in range(n):
        t = fi / fps
        k = min(int(t / seg), len(imgs) - 1)
        lt = t - k * seg
        mode = (sec["images"][k] + idx) % 4
        fr = kenburns(imgs[k], min(1, lt / seg), mode)
        if k + 1 < len(imgs) and lt > seg - XFADE:
            nxt = kenburns(imgs[k + 1], 0, (sec["images"][k + 1] + idx) % 4)
            fr = Image.blend(fr, nxt, (lt - (seg - XFADE)) / XFADE)
        fr = overlay_era(fr, sec, t, dur)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    return out, dur


def render_card(args):
    ep, idx, card, fps = args
    build = os.path.join(ep, "build")
    bg = load_cover(os.path.join(ep, "images", f"{card['bg']:03d}.jpg")).resize((W, H)).filter(ImageFilter.GaussianBlur(14))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (20, 14, 10)), 0.35)
    out = os.path.join(build, f"card{idx:02d}.mp4")
    dur = card.get("dur", 1.8)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           "-t", f"{dur:.3f}", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(int(round(dur * fps))):
        t = fi / fps
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        draw_board(d, card["board"], card["highlight"], alpha=ease(t / 0.3))
        p.stdin.write(Image.alpha_composite(bg.convert("RGBA"), ov).convert("RGB").tobytes())
    p.stdin.close(); p.wait()
    return out, dur


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("ep"); ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--only", type=int, nargs="*"); ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    cfg = json.load(open(os.path.join(a.ep, "edit.json")))
    secs = cfg["sections"]
    # build tier boards progressively
    board = [None] * 12
    timeline = []
    for i, s in enumerate(secs):
        timeline.append(("sec", i, s))
        if s.get("rank"):
            board[12 - s["rank"]] = {"era": s["era_short"], "survival": s["survival"]}
            timeline.append(("card", i, {"board": list(board), "highlight": s["rank"], "bg": s["images"][-1]}))
    for s in secs:
        if s.get("board_overlay"): s["board"] = list(board)
    jobs = []
    with ProcessPoolExecutor(a.jobs) as ex:
        for kind, i, obj in timeline:
            if a.only is not None and i not in a.only: continue
            jobs.append(ex.submit(render_section if kind == "sec" else render_card, (a.ep, i, obj, a.fps)))
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

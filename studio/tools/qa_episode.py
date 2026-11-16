#!/usr/bin/env python3
"""QA gate for a Dave episode. Two modes, both write <ep>/qa_<mode>.json and exit 1 on FAIL.

  python3 qa_episode.py plan   <ep>   # BEFORE render: edit.json + images + audio (free, ~1 s)
  python3 qa_episode.py render <ep> [video.mp4]   # AFTER render: probe, loudness, frame spot-check

Idea borrowed from OpenMontage (slideshow-risk score + final self-review); code is original.
Thresholds are PROVISIONAL: calibrate them on published episodes with real retention data.
"""
import json, os, re, subprocess, sys, statistics

# --- provisional thresholds (tune with retention data) ---
MAX_STATIC_S = 9.0        # longest time one image stays on screen
MAX_MEAN_CUT_S = 6.0      # mean seconds per image across the episode
MAX_DEAD_SECTION_S = 20   # a section this long with zero overlays/callouts is flat
LUFS_TARGET, LUFS_TOL = -14.0, 1.5
TP_MAX = -1.0
MIN_FRAMES_OK = 4


def probe(path):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))


def verdict(fails, warns):
    return "FAIL" if fails else ("REVISE" if warns else "PASS")


def plan(ep):
    fails, warns, rows = [], [], []
    d = json.load(open(os.path.join(ep, "edit.json")))
    used = {}
    for i, s in enumerate(d["sections"]):
        a = os.path.join(ep, "audio", s["audio"])
        if not os.path.exists(a):
            fails.append(f"s{i:02d}: missing audio {s['audio']}"); continue
        dur = probe(a)
        imgs = s["images"]
        for im in imgs:
            n = im["n"]
            p = os.path.join(ep, "images", f"{n:03d}.jpg")
            if not os.path.exists(p): fails.append(f"s{i:02d}: missing images/{n:03d}.jpg")
            if n in used: warns.append(f"s{i:02d}: image {n:03d} already used in s{used[n]:02d}")
            used.setdefault(n, i)
        per = dur / max(1, len(imgs))
        overlays = sum(len(s.get(k, []) or []) for k in ("callouts", "bubbles")) + sum(
            1 for k in ("banner", "tally", "badge_title", "survival", "title_card") if s.get(k))
        if per > MAX_STATIC_S:
            warns.append(f"s{i:02d}: ~{per:.1f}s per image (> {MAX_STATIC_S}s): add images or a callout")
        if dur > MAX_DEAD_SECTION_S and overlays == 0:
            warns.append(f"s{i:02d}: {dur:.0f}s with no overlay/callout")
        rows.append((i, round(dur, 1), len(imgs), round(per, 1), overlays))
    tot = sum(r[1] for r in rows); nimg = sum(r[2] for r in rows)
    mean_cut = tot / max(1, nimg)
    if mean_cut > MAX_MEAN_CUT_S:
        warns.append(f"mean cut {mean_cut:.1f}s per image (> {MAX_MEAN_CUT_S}s)")
    # script claims must have a source (CLAUDE rule: every factual claim sourced)
    sp, sr = os.path.join(ep, "script.md"), os.path.join(ep, "sources.md")
    if not os.path.exists(sr): fails.append("sources.md missing")
    elif os.path.getsize(sr) < 200 and os.path.exists(sp): warns.append("sources.md looks empty")
    return {"mode": "plan", "verdict": verdict(fails, warns), "fails": fails, "warns": warns,
            "total_s": round(tot, 1), "images": nimg, "mean_cut_s": round(mean_cut, 2),
            "sections": [dict(zip(("i", "audio_s", "images", "s_per_image", "overlays"), r)) for r in rows]}


def render(ep, video):
    fails, warns = [], []
    if not os.path.exists(video):
        return {"mode": "render", "verdict": "FAIL", "fails": [f"{video} not found"], "warns": []}
    pj = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
         "-of", "json", video]))
    types = [s["codec_type"] for s in pj["streams"]]
    v = next((s for s in pj["streams"] if s["codec_type"] == "video"), {})
    dur = float(pj["format"]["duration"])
    if "video" not in types: fails.append("no video stream")
    if "audio" not in types: fails.append("no audio stream")
    if (v.get("width"), v.get("height")) not in ((1920, 1080), (1080, 1920)):
        warns.append(f"unexpected size {v.get('width')}x{v.get('height')}")
    # duration vs narration
    ad = os.path.join(ep, "audio")
    if os.path.isdir(ad):
        narr = sum(probe(os.path.join(ad, f)) for f in sorted(os.listdir(ad)) if re.fullmatch(r"s\d+\.mp3", f))
        if narr and abs(dur - narr) > 0.10 * narr + 5:
            warns.append(f"video {dur:.0f}s vs narration {narr:.0f}s (check tails/cold open)")
    # loudness
    lufs = tp = None
    if "audio" in types:
        r = subprocess.run(["ffmpeg", "-nostats", "-i", video, "-af", "ebur128=peak=true", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r); p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)
        lufs = float(m[-1]) if m else None; tp = float(p[-1]) if p else None
        if lufs is None: warns.append("could not measure loudness")
        else:
            if abs(lufs - LUFS_TARGET) > LUFS_TOL: warns.append(f"loudness {lufs} LUFS (target {LUFS_TARGET}±{LUFS_TOL})")
            if tp is not None and tp > TP_MAX: warns.append(f"true peak {tp} dBFS (> {TP_MAX})")
    # frame spot-check: 8 frames, flag black/frozen
    means, ok = [], 0
    for k in range(8):
        t = dur * (k + 0.5) / 8
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
                              "-vf", "scale=32:18,format=gray", "-f", "rawvideo", "-"],
                             capture_output=True).stdout
        if raw:
            mean = sum(raw) / len(raw); means.append(round(mean, 1)); ok += mean > 8
    if ok < MIN_FRAMES_OK: fails.append(f"only {ok}/8 sampled frames are non-black")
    elif ok < 8: warns.append(f"{8 - ok}/8 sampled frames near-black")
    return {"mode": "render", "verdict": verdict(fails, warns), "fails": fails, "warns": warns,
            "duration_s": round(dur, 1), "lufs": lufs, "true_peak_dbfs": tp, "frame_means": means}


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("plan", "render"):
        sys.exit(__doc__)
    mode, ep = sys.argv[1], sys.argv[2].rstrip("/")
    res = plan(ep) if mode == "plan" else render(ep, sys.argv[3] if len(sys.argv) > 3 else os.path.join(ep, "build", "final.mp4"))
    json.dump(res, open(os.path.join(ep, f"qa_{mode}.json"), "w"), indent=1)
    print(res["verdict"], "|", "; ".join(res["fails"] + res["warns"]) or "clean",
          "|", {k: v for k, v in res.items() if k in ("total_s", "images", "mean_cut_s", "duration_s", "lufs", "true_peak_dbfs")})
    sys.exit(1 if res["verdict"] == "FAIL" else 0)

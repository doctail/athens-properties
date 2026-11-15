#!/usr/bin/env python3
"""Align each narration section's text to its real audio, without any speech-recognition model.

Usage: python3 align_narration.py <episode_dir>
Reads : <ep>/script.md (NARRATOR lines, split on "## " like render_episode.py), <ep>/edit.json (audio file per section),
        <ep>/audio/*.mp3
Writes: <ep>/audio/align.json   {"s01.mp3": [[char_index, seconds], ...], ...}

How: ffmpeg silencedetect finds the pauses; a small dynamic program assigns the N-1 sentence starts of the text to
the pauses (long pauses preferred, close to the proportional guess), giving exact times at every sentence start.
Inside a sentence time is interpolated by characters. render_episode.py uses align.json when it exists, otherwise it
falls back to its old proportional guess. Run it again whenever the audio changes.
"""
import json, os, re, subprocess, sys


def probe(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))


def narration_texts(ep):
    t = open(os.path.join(ep, "script.md")).read()
    secs = re.split(r"^## ", t, flags=re.M)[1:]
    return [" ".join(l.split(":", 1)[1].strip() for l in s.splitlines() if l.startswith("NARRATOR:")).replace("*", "") for s in secs]


def pauses(audio):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", audio, "-af", "silencedetect=n=-33dB:d=0.12", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return [(s, e) for s, e in zip(st, en)]  # (pause start, speech restarts)


def speech_start_end(ps, nd):
    first = ps[0][1] if ps and ps[0][0] < 0.05 else 0.0
    last = ps[-1][0] if ps and ps[-1][1] >= nd - 0.05 else nd
    return first, last


def align_section(text, audio):
    nd = probe(audio)
    ps = pauses(audio)
    t0, t1 = speech_start_end(ps, nd)
    inner = [(s, e) for s, e in ps if s > t0 + 0.1 and e < t1 - 0.05]  # pauses between words
    starts = [m.end() for m in re.finditer(r"[.?!:]\s", text)]
    n = len(starts)
    knots = [[0, round(t0, 3)]]
    if n and inner:
        L = len(text)
        exp = [t0 + (c / L) * (t1 - t0) for c in starts]
        INF = 1e9
        # dp[k][j]: best cost placing sentence start k on pause j (strictly increasing j)
        m = len(inner)
        cost = lambda k, j: abs(inner[j][1] - exp[k]) * 0.5 - 4.0 * min(inner[j][1] - inner[j][0], 1.2)
        dp = [[INF] * m for _ in range(n)]; bp = [[-1] * m for _ in range(n)]
        for j in range(m): dp[0][j] = cost(0, j)
        for k in range(1, n):
            best, bj = INF, -1
            for j in range(m):
                if j > 0 and dp[k - 1][j - 1] < best: best, bj = dp[k - 1][j - 1], j - 1
                if best < INF: dp[k][j] = best + cost(k, j); bp[k][j] = bj
        if n <= m:
            j = min(range(m), key=lambda j: dp[n - 1][j])
            pick = [0] * n
            for k in range(n - 1, -1, -1):
                pick[k] = j; j = bp[k][j]
            for c, j in zip(starts, pick): knots.append([c, round(inner[j][1], 3)])
    knots.append([len(text), round(t1, 3)])
    return knots, nd


def main(ep):
    texts = narration_texts(ep)
    ed = json.load(open(os.path.join(ep, "edit.json")))
    res = {}
    for i, sec in enumerate(ed["sections"]):
        a = os.path.join(ep, "audio", sec["audio"])
        knots, nd = align_section(texts[i], a)
        # keep it monotone
        clean = [knots[0]]
        for c, t in knots[1:]:
            if c > clean[-1][0] and t > clean[-1][1]: clean.append([c, t])
        res[sec["audio"]] = clean
        print(f"{sec['audio']}: {len(clean) - 2} sentence starts placed, speech {clean[0][1]:.2f}-{clean[-1][1]:.2f}s of {nd:.2f}s")
    json.dump(res, open(os.path.join(ep, "audio", "align.json"), "w"))


if __name__ == "__main__":
    main(sys.argv[1])

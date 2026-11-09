#!/usr/bin/env python3
"""Generate original, royalty-free sound effects procedurally (numpy). Output: studio/assets/sfx/*.wav"""
import os, sys, wave
import numpy as np

SR = 48000
OUT = sys.argv[1] if len(sys.argv) > 1 else "studio/assets/sfx"
rng = np.random.default_rng(7)


def save(name, x, gain=0.8):
    x = np.asarray(x, dtype=np.float64)
    x = x / (np.max(np.abs(x)) + 1e-9) * gain
    st = np.stack([x, x], axis=1)
    os.makedirs(OUT, exist_ok=True)
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def t(d): return np.arange(int(SR * d)) / SR


def lowpass(x, a):  # one-pole, a in (0,1): higher = more smoothing
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc = acc * a + v * (1 - a); y[i] = acc
    return y


def env(n, attack, release):
    e = np.ones(n); a = int(SR * attack); r = int(SR * release)
    e[:a] = np.linspace(0, 1, a); e[-r:] *= np.linspace(1, 0, r) ** 2
    return e


# whoosh: band-swept noise
d = 0.7; n = int(SR * d); noise = rng.standard_normal(n)
sweep = np.linspace(0.995, 0.85, n)
y = np.empty(n); acc = 0
for i in range(n):
    acc = acc * sweep[i] + noise[i] * (1 - sweep[i]); y[i] = acc
y = y - lowpass(y, 0.999)
save("whoosh", y * env(n, 0.35, 0.3) * np.sin(np.linspace(0, np.pi, n)), 0.6)

# pop: short pitched blip
tt = t(0.12); f = 900 * np.exp(-tt * 25) + 350
save("pop", np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 40), 0.6)

# ding: bell (sine partials, decay)
tt = t(1.4)
bell = sum(a * np.sin(2 * np.pi * fr * tt) * np.exp(-tt * k) for fr, a, k in [(1320, 1, 3), (2640, .4, 5), (3960, .2, 8), (1980, .25, 4)])
save("ding", bell, 0.55)

# glitch: bitcrushed noise bursts + square chirps
n = int(SR * 0.55); y = np.zeros(n)
for k in range(9):
    s = rng.integers(0, n - 2400); L = rng.integers(600, 2400)
    seg = np.sign(np.sin(2 * np.pi * rng.uniform(200, 1800) * np.arange(L) / SR)) * rng.uniform(.4, 1)
    seg += rng.standard_normal(L) * .5
    y[s:s + L] += np.round(seg * 4) / 4
save("glitch", y * env(n, 0.01, 0.15), 0.5)

# boom: low sine drop + rumble
tt = t(2.2); f = 90 * np.exp(-tt * 1.5) + 32
boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 1.6)
rum = lowpass(rng.standard_normal(len(tt)), 0.995) * np.exp(-tt * 1.2) * 6
save("boom", boom + rum, 0.9)

# tick: tiny click
tt = t(0.04)
save("tick", np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt * 180), 0.35)

# riser: rising tone + noise for reveals
tt = t(1.2); f = 200 + 900 * (tt / 1.2) ** 2
save("riser", (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + lowpass(rng.standard_normal(len(tt)), 0.9) * 2) * (tt / 1.2) ** 1.5, 0.45)
print("sfx written to", OUT)

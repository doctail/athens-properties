#!/usr/bin/env python3
"""Focus Flow Lab thumbnail: dark gradient + big noise name + duration line. Zero credits.

Usage: python3 thumb.py "BROWN NOISE" "12 HOURS · BLACK SCREEN" out.jpg [accent_hex]
Matches the channel's best performer (big readable words, no scene). 1280x720 JPG.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

title, sub, out = sys.argv[1], sys.argv[2], sys.argv[3]
accent = sys.argv[4] if len(sys.argv) > 4 else "#C9A86A"
W, H = 1280, 720
img = Image.new("RGB", (W, H))
px = img.load()
for y in range(H):  # vertical gradient, near-black to deep brown
    t = y / H
    c = (int(10 + 30 * t), int(8 + 18 * t), int(6 + 10 * t))
    for x in range(W):
        px[x, y] = c
d = ImageDraw.Draw(img)
bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
reg = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def fit(text, path, max_w, start):
    size = start
    while size > 20:
        f = ImageFont.truetype(path, size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 4
    return ImageFont.truetype(path, size)

ft = fit(title, bold, W - 160, 170)
fs = fit(sub, reg, W - 200, 64)
tb = d.textbbox((0, 0), title, font=ft)
sb = d.textbbox((0, 0), sub, font=fs)
ty = H // 2 - (tb[3] - tb[1]) - 10
d.text(((W - (tb[2] - tb[0])) // 2, ty), title, font=ft, fill="#F2EBDD")
d.rectangle([(W // 2 - 90, ty + (tb[3] - tb[1]) + 40), (W // 2 + 90, ty + (tb[3] - tb[1]) + 46)], fill=accent)
d.text(((W - (sb[2] - sb[0])) // 2, ty + (tb[3] - tb[1]) + 80), sub, font=fs, fill=accent)
img.save(out, quality=92)
print("ok:", out)

#!/usr/bin/env python3
"""Genera flow-prompts.md da script.md (collage). Uso: make_flow_prompts.py <episode_dir>
Una riga IMAGE per pagina [Vnnn]; le pagine con 'IMAGE: none' non vanno in Flow (le costruisce il renderer).
File da scaricare: <Vnnn>.png (il nome e' l'ID della pagina, non un numero progressivo: niente ordine da indovinare)."""
import re, sys, os
ep = sys.argv[1]
t = open(os.path.join(ep, "script.md"), encoding="utf-8").read()
title = re.search(r"^# (.+)$", t, flags=re.M).group(1)
pages = re.findall(r"^\[V(\w+)\] NARRATOR: (.+)\nIMAGE: (.+)$", t, flags=re.M)
flow = [(v, n, i) for v, n, i in pages if not i.startswith("none")]
HEADER = """STYLE (paste at the start of EVERY run, then add the image line):
Editorial paper-collage illustration, 16:9. Torn-paper layers with visible fibers, cut-out figures with thin white outlines, halftone newsprint texture, muted palette (cream, sepia, slate blue, olive) with ONE red accent. Documentary tone, not cartoon.
HARD RULES:
1. NO TEXT of any kind: no letters, numbers, dates, labels, stamps, captions, signs, banners with writing, or pseudo-writing/scribbles. Flags and banners are plain colour or simple geometric shapes.
2. Period: 1440s-1450s Eastern Mediterranean. No modern objects, no clocks, hourglasses or watches, no photographs, no 19th-century European uniforms or shakos, no bowler hats.
3. Ottoman soldiers: turbans, mail, round shields, composite bows. Janissaries: tall white felt cap with a flap at the back, no feathers. Byzantines: late-medieval armor or lamellar, purple for the emperor. Italians: plate and mail with sallet helmets.
4. Faces: generic. No recognizable portrait likeness.
5. Keep the centre readable and the lower third calmer (my captions and arrows go there).
6. One idea per image: show exactly what the line says."""
out = [f"# {title} — Google Flow prompts ({len(flow)} images, 16:9)", "",
       "Status: v1, waiting for the owner's script OK. Owner runs Flow; do not generate through any API.", "",
       "How: paste the STYLE block + the image line. Run in batches of 10 images. After V001 is approved, attach it as a style reference for the rest (hypothesis: improves consistency; check on the first batch).",
       "Naming: save each file as its page ID, e.g. `V001.png`, `V004b.png` (NOT a running number). I match each file to its narration line and check it before render.",
       "If an image shows any text, modern object or wrong costume, re-run only that one with the fix in one line; do not re-run the batch.", "", HEADER, ""]
for v, n, i in flow:
    out += [f"## V{v}", f"LINE: {n}", f"IMAGE: {i}", ""]
open(os.path.join(ep, "flow-prompts.md"), "w", encoding="utf-8").write("\n".join(out))
print(len(flow), "immagini Flow;", len(pages) - len(flow), "pagine costruite da me")

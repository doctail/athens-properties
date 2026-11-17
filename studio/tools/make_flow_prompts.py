#!/usr/bin/env python3
"""Genera flow-prompts.md da script.md (collage): BLOCCHI da incollare interi in Flow (max 24 immagini ciascuno).
Uso: make_flow_prompts.py <episode_dir>
Ogni blocco = un solo copia-incolla: regole di stile una volta, poi una riga per immagine con il nome file esatto (<Vnnn>.png).
Le frasi della voce NON entrano nei blocchi (Flow potrebbe scriverle sull'immagine). Le pagine 'IMAGE: none' le costruisce il renderer."""
import re, sys, os
MAXB = 24
ep = sys.argv[1]
t = open(os.path.join(ep, "script.md"), encoding="utf-8").read()
title = re.search(r"^# (.+)$", t, flags=re.M).group(1)
pages = re.findall(r"^\[V(\w+)\] NARRATOR: (.+)\nIMAGE: (.+)$", t, flags=re.M)
flow = [(v, i) for v, n, i in pages if not i.startswith("none")]
RULES = """Rules for EVERY image in this batch:
- Style: editorial paper-collage illustration, 16:9. Torn-paper layers with visible fibers, cut-out figures with thin white outlines, halftone newsprint texture, muted palette (cream, sepia, slate blue, olive) with ONE red accent. Documentary tone, not cartoon.
- NO TEXT of any kind: no letters, numbers, dates, labels, stamps, captions, signs, or pseudo-writing. Flags and banners are plain colour or simple geometric shapes.
- Period: 1440s-1450s Eastern Mediterranean. No modern objects, no clocks, hourglasses or watches, no photographs, no 19th-century European uniforms or shakos, no bowler hats.
- Ottoman soldiers: turbans, mail, round shields, composite bows. Janissaries: tall white felt cap with a flap at the back, no feathers. Byzantines: late-medieval armor or lamellar, purple for the emperor. Italians: plate and mail with sallet helmets.
- No red crosses, crescents or any religious or medical emblem on clothing, shields or flags. Faces: generic, no recognizable portrait likeness.
- Keep the centre readable and the lower third calmer.
- One idea per image: show exactly what the description says."""
blocks = [flow[i:i + MAXB] for i in range(0, len(flow), MAXB)]
out = [f"# {title} — blocchi Flow ({len(flow)} immagini in {len(blocks)} blocchi)", "",
       "Come si usa: copia **tutto il contenuto di un blocco** (il riquadro grigio) e incollalo in Flow. Un blocco alla volta. Flow produce le immagini e le rinomina con il nome indicato.",
       "Se un'immagine ha del testo, un oggetto moderno o un costume sbagliato: rilancia **solo quella** (chiedimi il retake di una riga), non il blocco.",
       f"Le altre {len(pages) - len(flow)} pagine le costruisco io (mappe/diagrammi): non vanno in Flow.", ""]
for b, items in enumerate(blocks, 1):
    ids = f"V{items[0][0]} … V{items[-1][0]}"
    out += [f"## BLOCCO {b} — {len(items)} immagini ({ids})", "", "```text",
            f"Generate {len(items)} separate images for a history video, one per item below. Save each image with exactly the file name given.", "", RULES, "", "Images:"]
    for n, (v, i) in enumerate(items, 1):
        out.append(f"{n}. V{v}.png — {i}")
    out += ["```", ""]
open(os.path.join(ep, "flow-prompts.md"), "w", encoding="utf-8").write("\n".join(out))
print(len(flow), "immagini in", len(blocks), "blocchi:", [len(b) for b in blocks])

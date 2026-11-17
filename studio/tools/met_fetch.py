#!/usr/bin/env python3
"""Prelievo immagini CC0 dal Metropolitan Museum (Open Access), con credito.

Uso: met_fetch.py <queries.txt> <out_dir> [--per 2] [--minw 1400]
queries.txt: una riga per immagine:  V001 | query
Scrive <id>_<n>.jpg + met.json (oggetto, titolo, data, dipartimento, credito, url pagina) + credits.txt.
Solo oggetti isPublicDomain con immagine. API v1.1 (la v1 e' stata ritirata il 2026-10-01). Solo stdlib.
"""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path

B = "https://collectionapi.metmuseum.org/public/collection/v1"
UA = "YTStudioBroll/0.1 (historical explainer research tool)"


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
                return r.read()
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    opt = {sys.argv[i]: sys.argv[i + 1] for i in range(len(sys.argv) - 1) if sys.argv[i].startswith("--")}
    if len(a) < 2:
        sys.exit(__doc__)
    per, minw = int(opt.get("--per", 2)), int(opt.get("--minw", 1400))
    out = Path(a[1]); out.mkdir(parents=True, exist_ok=True)
    seen, man, cred = set(), {}, []
    for line in Path(a[0]).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        vid, q = [x.strip() for x in line.split("|")][:2]
        ids = json.loads(get(f"{B.replace('/v1', '/v1.1')}/search?hasImages=true&isPublicDomain=true&q={urllib.parse.quote(q)}")).get("objectIDs") or []
        got = []
        for oid in ids[:40]:
            if len(got) >= per:
                break
            if oid in seen:
                continue
            o = json.loads(get(f"{B}/objects/{oid}"))
            if not o.get("primaryImage") or not o.get("isPublicDomain"):
                continue
            f = out / f"{vid}_{len(got) + 1}.jpg"
            f.write_bytes(get(o["primaryImage"]))
            try:
                from PIL import Image
                w, h = Image.open(f).size
            except Exception:
                w = h = 0
            if w and max(w, h) < minw:
                f.unlink(); continue
            seen.add(oid)
            c = {"file": f.name, "objectID": oid, "title": o["title"], "date": o.get("objectDate"), "dept": o.get("department"),
                 "culture": o.get("culture"), "credit": o.get("creditLine"), "page": o.get("objectURL"), "size": [w, h]}
            got.append(c)
            cred.append(f'{f.stem}: "{o["title"]}" ({o.get("objectDate")}) — The Metropolitan Museum of Art, Open Access (CC0) — {o.get("objectURL")}')
            time.sleep(0.3)
        man[vid] = {"query": q, "candidates": got}
        print(f"{vid}: {len(got)}/{per}  [{q}]", flush=True)
    (out / "met.json").write_text(json.dumps(man, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "credits.txt").write_text("\n".join(cred) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

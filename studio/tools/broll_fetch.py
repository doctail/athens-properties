#!/usr/bin/env python3
"""Scarica foto/immagini d'archivio (B-roll) da Wikimedia Commons con licenza e credito.

Uso:
  broll_fetch.py <queries.txt> <out_dir> [--per 3] [--width 1920]

queries.txt: una riga per immagine:  V001 | giza pyramids aerial | (opzionale) parole da escludere
Scrive in out_dir: <id>_<n>.jpg + broll.json (candidati con licenza/autore/url) + credits.txt.
Solo Public domain / CC0 / CC BY / CC BY-SA (BY-SA segnato: richiede credito e stessa licenza).
Solo stdlib. Rispetta il rate-limit di Commons (pausa + backoff su 429).
"""
import json, re, sys, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
UA = "YTStudioBroll/0.1 (historical explainer research tool)"
OK = re.compile(r"^(public domain|pd|cc0|cc[ -]by(-sa)?[ -]?\d?\.?\d?)", re.I)
BAD = re.compile(r"(nc|nd|fair use|non-?commercial|copyrighted)", re.I)


def get(url, tries=5):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(8 * (i + 1))
                continue
            raise
    raise RuntimeError("troppi tentativi: " + url)


def strip(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def search(query, width, per):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrnamespace": 6, "gsrlimit": 25,
        "gsrsearch": f"{query} filetype:bitmap",
        "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": width,
    }
    d = json.loads(get(API + "?" + urllib.parse.urlencode(params)))
    pages = sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    out = []
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        m = ii.get("extmetadata", {})
        lic = strip(m.get("LicenseShortName", {}).get("value"))
        if not lic or BAD.search(lic) or not OK.match(lic):
            continue
        if ii.get("mime") not in ("image/jpeg", "image/png"):
            continue
        if ii.get("width", 0) < width or ii.get("width", 0) < ii.get("height", 0):
            continue  # solo landscape >= width
        out.append({
            "title": p["title"], "license": lic,
            "share_alike": "sa" in lic.lower(),
            "author": strip(m.get("Artist", {}).get("value"))[:120],
            "desc": strip(m.get("ImageDescription", {}).get("value"))[:200],
            "page": ii.get("descriptionurl"),
            # i thumbnail su thumb.wikimedia.org sono bloccati dal proxy: stesso percorso su upload.*
            "url": (ii.get("thumburl") or ii.get("url")).split("?")[0].replace("//thumb.wikimedia.org/", "//upload.wikimedia.org/"),
            "orig_size": [ii.get("width"), ii.get("height")],
        })
        if len(out) >= per:
            break
    return out


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    opt = {sys.argv[i]: sys.argv[i + 1] for i in range(len(sys.argv) - 1) if sys.argv[i].startswith("--")}
    if len(a) < 2:
        sys.exit(__doc__)
    per, width = int(opt.get("--per", 3)), int(opt.get("--width", 1920))
    outdir = Path(a[1]); outdir.mkdir(parents=True, exist_ok=True)
    manifest, credits = {}, []
    for line in Path(a[0]).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = [x.strip() for x in line.split("|")]
        vid, q = parts[0], parts[1]
        time.sleep(1.2)
        try:
            cands = search(q, width, per)
        except Exception as e:
            manifest[vid] = {"query": q, "error": str(e), "candidates": []}
            print(f"{vid}: ERRORE {e}")
            continue
        for n, c in enumerate(cands, 1):
            f = outdir / f"{vid}_{n}.jpg"
            try:
                time.sleep(1.0)
                f.write_bytes(get(c["url"]))
                c["file"] = f.name
                credits.append(f'{vid}_{n}: "{c["title"][5:]}" — {c["author"] or "unknown"} — {c["license"]} — {c["page"]}')
            except Exception as e:
                c["file"] = None; c["error"] = str(e)
        manifest[vid] = {"query": q, "candidates": cands}
        print(f"{vid}: {len([c for c in cands if c.get('file')])}/{per} scaricate  [{q}]")
    (outdir / "broll.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
    (outdir / "credits.txt").write_text("\n".join(credits) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Converte Natural Earth (npm: world-atlas, countries-50m.json, TopoJSON) in studio/collage/geo/world_50m.json:
{slug: {"name":..., "type":"MultiPolygon", "coordinates":[...]}}  (solo terraferma, coste vere; dominio pubblico).
Uso: geo_build.py <countries-50m.json>
I confini sono MODERNI: nelle mappe storiche servono come pezzi di carta con etichette antiche (stilizzazione)."""
import json, re, sys
from pathlib import Path
t = json.load(open(sys.argv[1], encoding="utf-8"))
sc, tr = t["transform"]["scale"], t["transform"]["translate"]
arcs = []
for a in t["arcs"]:
    x = y = 0; pts = []
    for dx, dy in a:
        x += dx; y += dy
        pts.append([round(x * sc[0] + tr[0], 3), round(y * sc[1] + tr[1], 3)])
    arcs.append(pts)
def ring(idx):
    out = []
    for i in idx:
        p = arcs[i] if i >= 0 else arcs[~i][::-1]
        out += p if not out else p[1:]
    return out
res = {}
for g in t["objects"]["countries"]["geometries"]:
    name = g.get("properties", {}).get("name")
    if not name or g["type"] not in ("Polygon", "MultiPolygon"):
        continue
    polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"]
    coords = [[ring(r) for r in poly] for poly in polys]
    res[re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")] = {"name": name, "type": "MultiPolygon", "coordinates": coords}
out = Path(__file__).resolve().parent.parent / "collage" / "geo" / "world_50m.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(res, separators=(",", ":")), encoding="utf-8")
print(len(res), "paesi ->", out, out.stat().st_size // 1024, "KB")

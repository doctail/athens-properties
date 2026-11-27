# Controllo history per citta' (27/11/2026) — letto da doctail/city3d, branch yb/integ (story.json + MISSING.md)
Conteggi di `history` in story.json (zones/walls/gutting/lost/fires/water/bridges):
- Copenaghen 0/0/0/0/0/0/0  -> VUOTA. Fonte: hist_copenhagen.py (main) + fires.json/reclaim.json/bridges.json.gz in data_copenhagen_src + BRIDGE_YEAR in fetch_dk_roads.py.
- Parigi 12/0/0/0/0/9/36 -> mancano walls, fires, lost, gutting Haussmann; 9 water ancora cerchi. Fonte: data_parigi_src (wall_p.json, landphases.json, hist.json ALPAGE) + hist_parigi.py.
- Roma 4/3/0/0/1/0/0 -> mancano gutting, lost, water, ponti (Ponte Elio 134), piene Tevere. Contorni Serviana/Leonina a mano.
- Madrid 5/3/3/1/4/0/0 -> history ok; ponti `bridges` non fatti (solo 2 landmark).
- Rotterdam 5/2/1/0/1/0/0 -> `bridges` vuoto (nessun bridges.json nei dati), canali interrati non supportati dal kit, porti prima del 1875 assenti.
- Siviglia 9/1/0/2/0/12/5 -> history completa; pacchetto dati incompleto (mancano roads/land/dem.npz per il kit).
- Lione 7/0/3/0/3/0/7, Valencia 9/2/6/2/1/14/5, Marsiglia 6/1/1/0/2/0/1 -> history compilata (hist_*.py e' solo uno stub che legge story.json).
Dove sta: tutto su doctail/city3d branch `yb/integ` (+ per-citta' yb/*). `main` ha story.json solo di lyon, marseille, nyc, pittsburgh, valencia.
Non rifare: fonti Wikipedia/Wikidata gia' scaricate e citazioni verificate per Madrid, Roma, Rotterdam, Siviglia, Parigi (MISSING.md di ciascuna).

# Istruzioni permanenti per ogni sessione

## Crediti vidIQ — dato del proprietario, NON contestarlo
- **150 crediti al mese**, si ricaricano il **27** di ogni mese.
- **+20 crediti ogni giorno** quando il proprietario fa login sulla pagina vidIQ.
- `vidiq_balance` può mostrare il rinnovabile a 0 e solo crediti "add-on": è il bonus giornaliero, è normale.
- I crediti sono **sufficienti**. Non scrivere mai osservazioni sulla scarsità dei crediti, non proporre di comprarne, non ridurre il lavoro per risparmiarli. Basta dichiarare il costo prima di una chiamata a pagamento e registrarla in Nodum `00 HQ/LEDGER`.

## Memoria
- La conoscenza dei 4 canali sta in **Nodum** (vault "My Vault"): parti da `00 HQ/00 START`, poi `00 HQ/RULES` e la CARD del canale su cui lavori. Non ricopiare quelle note nel repo.
- Year Built vive nel repo `doctail/city3d` (memoria tecnica in `PRODUZIONE_TIMELAPSE.md`).

## Il proprietario
- Rispondi in italiano. Titoli, testo a schermo e descrizioni in inglese americano.
- Ritmo: Dave 2 long a settimana, Year Built 2 a settimana, Focus 1 a settimana, Treasure 1 a settimana.

## Dove trovare cosa (leggi qui prima di dire "non trovo")
| Canale | Come si produce | Cosa fare adesso | File nel repo |
|---|---|---|---|
| Dave | Nodum `CH Dave/CARD Dave` + `STYLE Dave` + `FORMULA Dave` | Nodum `CH Dave/STATUS Dave` | `studio/episodes/<slug>/`, render `studio/tools/render_episode.py` |
| Year Built | repo `doctail/city3d`, `PRODUZIONE_TIMELAPSE.md` | Nodum `CH Year Built/STATUS Year Built` + `BACKLOG Year Built` | tutto in `doctail/city3d` |
| Focus | Nodum `CH Focus/RECIPE Focus` | Nodum `CH Focus/BACKLOG Focus` | `studio/focus/<nn-slug>/` con `make.sh`, `metadata.md`, `thumb.jpg`; strumenti `studio/tools/focus/` (`noise.sh`, `thumb.py`, zero crediti) |
| Treasure | Nodum `CH Treasure/RECIPE Treasure` | Nodum `CH Treasure/BACKLOG Treasure` | `studio/treasure/<slug>/` |

- **Focus, video 01 pronto da generare**: `bash studio/focus/01-super-deep-brown-sleep-12h/make.sh` (~75 min di CPU, crea `video.mp4` da ~0,8 GB, NON committarlo: supera il limite di GitHub). Titolo, descrizione, tag e copertina sono già nella cartella.
- Se lavori in una chat senza accesso al repo, le stesse informazioni sono in Nodum (vault "My Vault", cartella del canale).

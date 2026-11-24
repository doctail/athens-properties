# Istruzioni permanenti per ogni sessione

## Crediti vidIQ — dato del proprietario, NON contestarlo
- **150 crediti al mese**, si ricaricano il **27** di ogni mese.
- **+20 crediti ogni giorno** quando il proprietario fa login sulla pagina vidIQ.
- `vidiq_balance` può mostrare il rinnovabile a 0 e solo crediti "add-on": è il bonus giornaliero, è normale.
- I crediti sono **sufficienti**. Non scrivere mai osservazioni sulla scarsità dei crediti, non proporre di comprarne, non ridurre il lavoro per risparmiarli. Basta dichiarare il costo prima di una chiamata a pagamento e registrarla in Nodum `00 HQ/LEDGER`.

## Date, scadenze, ritmo di lavoro — NON rompere le scatole (ordine del proprietario, 17/11/2026, già detto più volte)
- **Mai** scrivere promemoria, avvisi, "tempi stretti", "margine", "entro mercoledì", date di render/uscita/consegna, né chiedere conferme sulle date. Le date le gestisce il proprietario, tutte.
- Mai chiedere "OK sullo script" o altri permessi a catena se il proprietario ha già detto di procedere: quando dice "fai la voce / montalo" è l'OK. Si lavora fino alla fine del compito, senza fermarsi a ogni passo.
- Il proprietario non guarda le immagini: **le controlla l'agente, una per una** (stile, personaggi, emblemi protetti come croci rosse, corrispondenza con la frase `[V nnn]`), poi voce, render e montaggio. Il costo si dichiara in una riga prima di una chiamata a pagamento, e si va avanti.
- Risposte brevi: cosa è stato fatto, cosa non va, cosa serve dal proprietario (solo se serve davvero).

## REGOLA SUPREMA di comunicazione (ordine del 20/11/2026, vale per ogni chat e ogni agente, per sempre)
- Scrivi il MINIMO: solo l'informazione necessaria. Niente liste di cosa stanno facendo gli agenti o la gente, niente elenchi di passi, niente riepiloghi dell'HANDOFF al proprietario. Se non c'è niente da decidere o riportare, una riga.
- **Le durate dei video NON si chiedono e NON si segnalano**: sono già fissate dalle regole e dalle schede (cartelli, capitoli). Mai "il video dura X, ok?".
- Agenti: massimo 15 righe di rapporto, dettagli in file nel repo o in Nodum.
- Il proprietario non risponde a domande che hanno già una regola: decidi tu e vai avanti.

## LISTA OBBLIGATORIA PRIMA DI OGNI GO PER IL POD (errore NYC, 20/11/2026: 2 ore di pod buttate)
Nessun GO senza TUTTO questo, verificato dalla chat sui file (non dagli agenti sulla parola):
1. Ogni decisione del proprietario in Nodum (navi, popolazioni, ecc.) e' ATTIVA nella configurazione che il pod scarica: controlla il valore reale nel file, non il default.
2. Foglio di fotogrammi veri per OGNI epoca, con attenzione a costa, porto, acqua, moli e isole: nessun edificio sull'acqua, navi presenti dove previsto. Misura il numero di edifici sull'acqua per anno (deve essere 0, salvo moli storici).
3. Il proprietario vede i fotogrammi prima del GO (almeno 5-6, epoca antica e moderna) e dice ok.
4. Costo con base misurata, e tempo per fotogramma misurato su un render locale rappresentativo.
5. Il commit nel GO e' su main e il diff-check dei file di render e' aggiornato.

## Comunicazione col proprietario (ordine del 19/11/2026: la chat era arrivata a 456K token di messaggi, in gran parte miei)
- **Messaggi brevi e concisi**: massimo 10-15 righe. Prima riga = il problema o l'esito. Niente tabelle, niente elenchi lunghi, niente ripetizione di quello che ha già letto, a meno che il proprietario li chieda. Se non capisce, chiede lui una spiegazione.
- **Il proprietario non vuole numeri tecnici di camera/drone** (tabelle di distanza, inclinazione, velocità, soglie R2): li controlla la chat e gli agenti. Gli si dice solo "ok" o "non va, perché in una riga". I numeri restano nei file e in Nodum.
- **Gli agenti riportano al massimo 15 righe**; i dettagli li scrivono in un file nel repo o in Nodum e la chat li legge solo se serve. Niente output grandi di tool o di agenti nella conversazione (usa estratti, `head`, conteggi).
- Non rispiegare le decisioni già prese; le decisioni piccole le prende la chat e le registra in Nodum, il proprietario le cambia se vuole.
- A ogni consegna di file: invia i file con `SendUserFile`, senza ricopiarne il contenuto nel messaggio.

## Stato corrente (19/11/2026)
- Nuovo canale: **Ledger of Cities** (`@ledgerofcities`, del proprietario). Pacchetto grafico e metadata in `canale/ledger-of-cities/`; confronto concorrenti in `report/CONFRONTO_CANALI.md`.
- **Marsiglia e Pittsburgh: da rifare con colori nuovi (ordine del proprietario, 24/11/2026; i vecchi video sono cancellati).** Stato in Nodum `CH Year Built/STATUS Year Built` (sezione 2026-11-24). Un agente alla volta.
- Il resto del lavoro, le decisioni e le istruzioni di ripresa sono in Nodum `CH Year Built/HANDOFF 2026-11-19` e `CH Year Built/REBUILD Year Built 2026-11-18`. Parti da lì.

## Memoria
- La conoscenza dei 4 canali sta in **Nodum** (vault "My Vault"): parti da `00 HQ/00 START`, poi `00 HQ/RULES` e la CARD del canale su cui lavori. Non ricopiare quelle note nel repo.
- Year Built vive nel repo `doctail/city3d` (memoria tecnica in `PRODUZIONE_TIMELAPSE.md`).

## Il proprietario
- Rispondi in italiano. Titoli, testo a schermo e descrizioni in inglese americano.
- Ritmo: Dave 2 long a settimana, Year Built 2 a settimana, Focus 1 a settimana, Treasure 1 a settimana.

## Year Built — regole operative (obbligatorie, dopo Lione, 16/11/2026)
Leggi PRIMA di qualsiasi lavoro: Nodum `CH Year Built/LESSONS Lione 2026-11-15` e `doctail/city3d` `kit/AVVIO_NUOVA_CITTA.md` (sezione "POST-MORTEM LYON"). Lione è costata quasi 10 ore di pod (oltre 5 euro, di cui 4 h 37 min di render vero), una chat di un giorno e molti token, perché la chat ha improvvisato invece di seguire il kit. Il proprietario non vuole che si ripeta.
- **La chat orchestra, gli agenti lavorano** (yb-scout haiku; yb-historian, yb-modeler, yb-qa sonnet; più yb-camera e yb-packaging), massimo 2-3 in parallelo, modello esplicito. La chat non scrive codice (salvo correzioni di una riga) e non prova un'idea alla volta.
- **Misura in locale PRIMA del pod** e confronta con le città di riferimento (distanza camera mediana >= 1.200 m equivalenti a 35 mm, inclinazione sotto 45 gradi, nessun volo di 12 s o più sotto 0,4 anni/s, nessun edificio all'anno 0, monumenti visibili durante il loro hover). `kit qa` verde prima di chiedere il pod.
- **Il pod si accende SOLO dopo un GO scritto della chat**, in UNA sessione, con nello stesso messaggio: controllo GPU, `git pull` + banner da verificare, lancio, comando di avanzamento in tempo reale, copertine, condizione per spegnere. Mai verifiche una alla volta sul pod. Città oltre 100K edifici: niente anteprima separata, direttamente `full`.
- **Dire il costo prima** con una base misurata (Lione: ~29 s di pod per secondo di video + 30 min di costruzione scena per processo). Se non è misurato, dirlo.
- **Consegna completa la prima volta:** miniatura, titolo, descrizione, capitoli in tutte le lingue con orari finali (con e senza cold open), tag, commento fissato (EN + lingua locale), Reddit, distribuzione, nota stampa, comando di montaggio su una riga per `cmd` (il proprietario non può scaricare `.bat`), file inviati. Se manca qualcosa, lo dici nella prima riga.
- **Nessuna affermazione non verificata:** usa prima lo strumento (Nodum funziona anche via curl con `kit/atlante/strumenti/nodum_mcp_curl.py`), etichetta [Certain]/[Likely]/[Guessing]. Leggi le analisi del proprietario (`analisi/`, CARD, RULES) prima di produrre.
- **Lavori lunghi tracciati** (background tracciato, processo verificato vivo, log non bufferizzato) e una sola modifica alla volta, mai non verificata sul branch che scarica il pod.
- **Economia di token:** niente file o log grandi stampati, niente immagini riviste, agenti con il lavoro intero e un solo report, risposte brevi: problema e correzione nella prima riga.

## Allineamento obbligatorio (ordine del proprietario, 16/11/2026)
Tutto va unito a tutto, sempre. A ogni consegna e prima di chiudere (e a ogni stop) ogni repo toccato (`doctail/city3d`, `doctail/athens-properties`) ha il branch di lavoro unito a `main` (fast-forward o merge, push su `main`) e Nodum aggiornato con lo stesso stato della chat: `STATUS Year Built`, `BACKLOG Year Built`, la nota della città, `LEDGER` se si spendono crediti, `LESSONS` se si impara qualcosa. Niente resta solo nella chat o solo su un branch. Se il server MCP di Nodum è disconnesso, usa `kit/atlante/strumenti/nodum_mcp_curl.py` (il token è iniettato dal proxy). Prima di dire "fatto", verifica che `main` e Nodum contengano quello che hai detto.

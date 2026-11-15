# KDP: regole non negoziabili

Fonte di verità per tutti gli agenti KDP. Ogni violazione blocca il libro: nessun upload, nessuna revisione umana finché non è corretta.

## Interior
- Ogni libro ha: frontespizio, copyright, come si gioca, puzzle numerati, soluzioni, pagina finale.
- Il copyright riporta sempre il nome dell'autore. Mai "Copyright © 2026." senza nome, mai campo vuoto.
- Font incorporati: `pdffonts` deve mostrare solo font embedded.
- Dimensione pagina: 8.5 x 11 pollici (612 x 792 pt).
- Parole nelle liste: 16pt minimo (large print).
- Eccezione approvata da Morgan (2026-11-15): le lettere delle griglie di soluzione possono restare a 14pt, per non aumentare il numero di pagine. Le word list restano a 16pt.
- Tutte le parole devono essere piazzate nella griglia. Se una manca, il puzzle non è pronto.
- Nessun testo inventato su editore, autore, metodo di produzione, recensioni, vendite.
- Vietati nel testo: "by hand", "our press", "our small press", "bestseller", placeholder tipo "E. P. Greenwood".

## Listing KDP
- Titolo: max 60 caratteri, formato [Keyword]: [Benefit].
- Sottotitolo: max 60 caratteri.
- Descrizione HTML con solo `<b> <p> <ul> <li> <i>`, max 4000 caratteri.
- La descrizione finisce SEMPRE con: `<i>Interior pages designed with AI assistance.</i>`
- 7 keyword: max 50 caratteri ciascuna, una frase per slot, senza virgole, senza parole già nel titolo, senza Amazon, KDP, bestseller, free, brand.
- 3 categorie: verificarle sempre nell'interfaccia KDP prima di scriverle.
- Titolo, sottotitolo, autore, edizione e ISBN si bloccano 72 ore dopo la pubblicazione: controllare prima.

## Operazioni
- Nessun upload o pubblicazione da strumenti o agenti. L'upload è manuale.
- Nessun automatismo sull'account KDP. Non usare `publish_tools/` (pilota Chrome loggato su KDP).
- Nessuna richiesta di recensioni che incentivi o compri recensioni.

## Ricerca
- Un nuovo libro si produce solo se la nicchia passa il gate di ricerca (`kdp-research-gate`).
- Nessuna nicchia dominata da un singolo autore sopra il 40% dei primi 20 risultati.

## Grafica
- Nessun logo di enti pubblici o marchi reali.
- Titolo leggibile a 150 px di larghezza (miniatura copertina).
- Stesso font e stessa griglia su tutte le pagine di un libro.

# Valutazione indipendente – pizzeria teglia + tonda, Pireo (24/11/2026)

Etichette: [Certain] verificato sul file o ricalcolato; [Likely] inferenza forte; [Guessing] stima mia.
Non ho verificato online né fonti Gemini (ΣΣΕ, aliquote, canoni, prezzi fornitori): tutto ciò che viene da Gemini è [Guessing] finché non confermato da commercialista/consulente del lavoro/preventivi.

## 1. Verdetto
**Il conto economico che mostra "+30 €/mese dopo il titolare" non regge.** [Certain] Ricalcolato sul tuo stesso file (baseline riprodotta al centesimo: EBITDA 2.216 €, residuo 30 €), con sole correzioni di omissioni, il risultato dopo i 1.500 € del titolare è **da −450 a −1.400 €/mese**, a parità di vendite.

| Passo (cumulativo, stesse vendite 109 unità/giorno) | EBITDA/mese | Dopo titolare 1.500 € |
|---|---:|---:|
| Modello come è | 2.216 | +30 |
| + costo ricetta dei 8 prodotti oggi a 0 € | 1.599 | −452 |
| + 815 €/mese di costi fissi tolti (Gemini cap. 16) | 784 | −1.088 |
| + maggiorazione domeniche/festivi (~200) | 584 | −1.244 |
| + invenduto teglia 25% invece di 10% | 414 | −1.376 |
| + app 65% e commissione 30% | −193 | −1.948 |

Pareggio economico (titolare 1.500 € netti) con costi corretti: circa **+30–35% di volumi** (≈ 145 unità/giorno, 45–50 ordini/giorno) [Likely]. Coerente con il pareggio di Gemini (40–48 ordini/giorno). Non è "scenario prudente + margine": è lo scenario che serve per stare in piedi.

## 2. Errori certi nel file Excel
1. **8 prodotti venduti hanno costo ricetta 0 €** (TN_PROS_FUN, TN_CAPRIC, TN_NAP, TN_MARIN, TN_SALS, TR_NAP, TR_ROSSA, TR_SCH). Nel foglio RICETTE la colonna H (modalità) è vuota → la formula usa il "costo manuale" E = 0. Il costo da distinta (colonna F, già calcolato) esiste ma non è usato. Impatto ≈ −617 €/mese. Fix: H = "Ingredienti" per quelle righe.
2. **Costi fissi: 815 €/mese spariti** rispetto a Gemini (commercialista 200, marketing 200, assicurazione/HACCP/manutenzioni 160, internet/software 110, acqua/rifiuti 85, banca/POS 60). La nota di COSTI FISSI A2 conferma che il "residuo generico" è stato eliminato. Medico del lavoro/tecnico sicurezza assenti.
3. **CASSA 12 MESI è fuorviante**: parte da 14.812 € e cresce di 1.530 €/mese fino a 33.169 €. Errori: (a) il "risultato netto" è il compenso del titolare (ditta individuale), non liquidità che si accumula; se il titolare preleva 1.500 €, la cassa resta piatta; (b) nessun capex, IVA, ramp-up, scorte; (c) PARAMETRI!B17 "esborsi pre-apertura" = cespiti + 1° mese affitto + 1° mese stipendi: non include cauzione, ingegnere/pratica KYE, costituzione, trifase, scorte, IVA anticipata. Il minimo di cassa mostrato (14.812 €) è falso per costruzione.
4. **CESPITI: cappa/estrazione vuota** (riga ESTRAZIONE, Gemini 2.500–3.500 €, obbligatoria); riga duplicata "Affettatrice e piccole attrezzature" (300 € con codice "Bialnci"); forno a 1.656,64 € è IVA inclusa mentre gli altri importi non sono omogenei (IVA 24% recuperabile → in cespite va il netto). Impatto ammortamenti piccolo, impatto cassa 3.500+ €.
5. **CONTO ECONOMICO C6** "Ricavi lordi/giorno" annuale = B6×12 (5.094 €): errore già notato; il vero lordo annuo è 132.444 €. Ingannevole nella colonna % (4,3%).
6. **Refusi di composizione** (non incidono finché la modalità è "Manuale", ma esplodono se passi a "Ingredienti"): TON_MARG farina 00 = 0,0128 kg (dovrebbe essere 0,128); TEG_MARG olio = 0,0015 kg (le altre teglie 0,015); lievito teglia 0,001 kg per 1,4 kg di impasto (0,07%: da validare con prove, [Likely] troppo basso se non fermentazione molto lunga/fredda).
7. **Teglia ripiena (TEG_SCH)**: la distinta usa una sola base di impasto; il sandwich ne richiede due. Costo sottostimato.
8. **Costi ricetta teglia "manuali di Gemini"** (7,19 / 5,90 / 10,21 / 14,46 / 11,06) sono stati calcolati da Gemini con quantità di farcitura su teglia da 6–8 tranci; tu li dividi per 12 senza rivedere le grammature per trancio (≈ 37 g di mozzarella a trancio nella Margherita). Se mantieni 12 tranci, o il prodotto è molto leggero o il costo reale è più alto.

## 3. Ipotesi ottimistiche
- **Volumi a regime dal giorno 1.** Non c'è rampa. ~35–40 ordini/giorno equivalenti (109 unità, 424 € lordi/giorno) subito. Un nuovo punto vendita ad Atene su efood/Wolt parte tipicamente molto sotto [Likely]; Gemini stesso mette M1 a 22 ordini/giorno. Con ramp realistica servono 6–9 mesi di perdite da finanziare.
- **Invenduto teglia 10%.** Con 8 gusti × ~5 tranci/giorno ognuno, produci ~0,5 teglia per gusto: sei costretto a mezze teglie o a cuocere per più di quanto vendi. 20–35% è più realistico [Likely]; il 10% vale solo con volumi per gusto 3–4 volte più alti. Soluzione: meno gusti (4–5) e rotazione.
- **8 gusti di teglia + 8 tonde = 16 SKU a 109 unità/giorno**: complessità di scorte (salumi a 17–20 €/kg che scadono) e sprechi non modellati.
- **Mix app 50% con commissione 28%**: nessuna fonte contrattuale; Gemini cita 20–30% + eventuale IVA 24% sulla commissione e promozioni cofinanziate. Un +2 pt di commissione e 65% app vale da solo ~600 €/mese. Le promozioni obbligatorie per posizionarsi non sono nel modello.
- **Scontrino**: i prezzi delle tonde (8–11 €) sono sotto la fascia italiana artigianale del Pireo (10–16,80 € secondo Gemini) e vicini al low-cost greco gouda: stai vendendo ingredienti italiani a prezzi quasi low-cost. Margherita 8 € con pack 0,42 € e commissione 28% lascia poco.
- **Costo personale = 2 FT a 1.335 €** (940 € lordi, 14 mensilità, 21,79%): il calcolo aritmetico è coerente con quanto detto da Gemini, ma: manca il +75% domeniche/festivi, sostituzioni ferie/malattia, TFR/indennità, medico del lavoro. Con 26 giorni di apertura, 12 ore/giorno e 2 FT da 40 h, il titolare copre da solo ~25–30 h/settimana oltre alla gestione: compenso 1.500 € per 60+ ore [Likely]. Gemini stesso sconsiglia 2 FT ("appesantisce il break-even") e propone 1 FT + 1 PT: nel tuo modello hai scelto l'opzione che lui scartava ma tenuto gli altri costi del suo scenario più leggero.
- **Imposta 22% piatta** su ditta individuale: l'imposta greca per liberi professionisti/imprese individuali è progressiva [Likely]; l'ordine di grandezza (4–5 k€/anno) è plausibile ma va fatta fare dal commercialista. Non incide sul verdetto.
- **IVA 13% su tutto**: Gemini indica 24% sulle bevande. Birra e lattine probabilmente non al 13% [Guessing]. Impatto ≈ −100 €/mese. Va confermato per prodotto.

## 4. Costi mancanti o sottodimensionati (non nel modello)
Sorpassi certi (assenti): costi di consegna per ordini diretti con rider propri (nessun rider nel modello; la quota non-app è assunta tutta banco); commissioni POS/carte (1%, Gemini); tassa rifiuti, acqua; packaging per delivery (borse, salse, tovaglioli); sfridi/rotture teglie; manutenzione forno/cappa (pulizia filtri carboni attivi); pratica KYE, ingegnere, HACCP; scorte iniziali e riserva di cassa; IVA anticipata su macchinari; deposito affitto; marketing di lancio; software/gestionale; interessi se c'è un prestito; ferie/chiusura estiva; costi di uscita (disdetta contratti).

Investimento iniziale: il file ha cespiti per 23.918 € (cappa a 0) + 42.000 € di capitale ma uscite pre-apertura contate solo 27.188 €. Gemini stima fabbisogno 28.500 € (locale già a norma, usato, cuscinetto minimo) – 45.800 € (standard). Il valore realistico per sentirti al sicuro è 40–46 k€ [Likely], non quello che appare dal foglio CASSA.

## 5. Cosa regge
- **Concept**: teglia romana con 4–5 gusti + tonda focalizzata, senza fritti, ha una nicchia documentata da Gemini (nessun banco specializzato; artigianali chiusi a pranzo) [Guessing: dati non verificati da me].
- **Prezzi ingredienti principali** reali dal fornitore greco (farine a 1,40–1,60 €/kg vs 2,19–3,01 € di Gemini): è un vantaggio vero se confermati su volumi e continuità.
- **Costo ricetta della tonda** (≈ 17–25% del netto) è credibile; il margine lordo per pizza è buono, il problema è il volume e la struttura dei costi fissi + commissioni.
- **Affitto 500–650 €, energia 520 €** plausibili per l'area [Likely], ma il locale a norma (destinazione d'uso, cappa, trifase) è il vero vincolo e il collo di bottiglia dei tempi/costi.
- L'aritmetica del conto economico è coerente (il problema non è la sottrazione, sono gli input).

## 6. Colli di bottiglia e logistica
- **Locale**: destinazione d'uso KYE, canna fumaria/filtri carboni attivi, regolamento condominiale, trifase (forno 9,6 kW). Un locale sbagliato annulla l'investimento. Clausola sospensiva nel contratto.
- **Forno**: due camere 70×70×14 cm (GGF 44 N); teglia 60×40 ci sta ma altezza 14 cm e tempi/temperature tonda vs teglia sono incompatibili nello stesso vano. Capacità serale tonde ~48–55/ora è teorica; picco 19–21 pizze tonde su 2 ore regge, ma con 16 SKU e precottura teglie al mattino è tutto da provare. Conferma scritta del produttore.
- **Teglia**: precottura al mattino + rigenerazione = qualità inferiore al "croccante appena sfornato" che giustifica il prezzo premium.
- **Delivery Pireo**: porto e Pasalimani hanno traffico, ZTL/sosta, strade a senso unico e scooter; tempi 30–45' sono realistici solo entro 2–3 km. Raggio piccolo = bacino piccolo. Con rider piattaforma non controlli tempi né qualità (pizza fredda → recensioni).
- **Orari**: banco pranzo 11:30–17:00 e sera 19:00–23:30: due picchi, due turni; il pomeriggio è morto per le tonde.
- **Dipendenza dalle piattaforme**: il 50% (o più) dei ricavi con commissioni 28–35% è fuori dal tuo controllo; clausole di parità prezzo.

## 7. Cosa fare prima di investire (in ordine di impatto)
1. **Correggere il modello**: H="Ingredienti" per le 8 ricette, rimettere i 815 €/mese, domeniche, cappa, deposito, ingegnere, trifase, scorte. Rifare CASSA con ramp (M1 15–20 ordini/giorno, M6 30, M12 38–45), prelievo titolare, IVA e capex. Presentare tre scenari (prudente/base/ottimista) come fa Gemini, non uno.
2. **Provare prima di aprire**: produrre prove reali di 2 teglie e 2 tonde, misurare grammature, rese e invenduto reali; ridurre i gusti di teglia a 4–5.
3. **Preventivi scritti**: forno (conferma 60×40), cappa/estrazione, trifase ΔΕΔΔΗΕ, ingegnere KYE, commercialista (costo personale, IVA per prodotto, forma giuridica), fornitori salumi/latticini a volume.
4. **Contratti piattaforme**: percentuale con/senza rider, promozioni, parità prezzi, commissione sulle promozioni, per efood, Wolt, Box.
5. **Decidere struttura personale**: 1 FT + 1 PT o titolare + 1 FT nei primi 6 mesi (risparmio ~600–900 €/mese) e domanda reale prima di assumere il secondo FT.
6. **Test di domanda a costo basso**: stand/pop-up o 4 settimane di delivery da cucina condivisa per misurare ordini/giorno e scontrino reali.
7. Rivedere la **politica prezzi** della tonda (9,50–12,50 € come Gemini?) e del trancio (misura reale del trancio per giustificare 3,50–4,00 €).

## 8. Giudizio finale
Concept: valido [Likely]. Modello finanziario: **non affidabile oggi**; con gli errori sistemati il progetto è in perdita rispetto all'obiettivo di 1.500 €/mese a volumi dati, e raggiunge il pareggio economico solo con +30–35% volumi, margini invariati. Non investire sul foglio attuale: sistema il modello, fai le prove e i preventivi, poi decidi con tre scenari e una cassa con ramp.

# Stato di avanzamento — Manuale "Forecast"

Ultimo aggiornamento: 2026-09-05 (turno di ricognizione iniziale).

## Fase del progetto

- [x] Fase 1 — Ricognizione: completata. Vedi `manuale/scheda_tecnica.md`.
- [x] Fase 2 — Analisi del dominio: dominio reale identificato (classificazione clinica binaria via embedding testuali, NON serie temporali). Dettagli in `scheda_tecnica.md` §0.
- [x] Fase 3 — Analisi statica e critica: 7 scoperte critiche documentate in `scheda_tecnica.md` §6.
- [x] Fase 4 — Indice: **approvato dall'utente** il 2026-09-05, dopo una verifica di completezza sui contenuti di machine learning che ha portato a 4 aggiunte (2 in Parte I, 2 in Parte VII). Indice definitivo in `manuale/indice.md` — 58 capitoli numerati + Parte 0 + 6 appendici. Questo è il riferimento autoritativo per nomi di file e numerazione da qui in avanti.
- [ ] Fase 5-6 — Stesura capitoli: **in corso**. Vedi tabella capitoli sotto.
- [ ] Fase 7 — Produzione PDF: non iniziata. Toolchain scelta provvisoriamente: Pandoc (già presente, v2.12) + `tectonic` (da installare via `brew install tectonic`) come motore PDF compatibile XeLaTeX; `@mermaid-js/mermaid-cli` (da installare via `npm install -g @mermaid-js/mermaid-cli`) per pre-renderizzare i diagrammi Mermaid in immagini vettoriali prima della conversione. Da confermare/installare quando si arriva a questa fase, con comandi reali documentati.

## Decisioni prese

- Cartella di lavoro del libro: `manuale/` nella radice del repository. Non ancora aggiunta a git (nessun commit/push finché l'utente non lo richiede esplicitamente).
- Nome file capitoli: `manuale/cap_00.md` (Parte 0, sezioni 0.1-0.3), poi un file per ogni capitolo numerato `manuale/cap_01.md` ... `manuale/cap_58.md` (ciascuno con le proprie sottosezioni x.1/x.2/x.3 incluse nello stesso file), poi appendici `manuale/app_A.md` ... `manuale/app_F.md`. Schema fissato in via definitiva in `manuale/indice.md`.
- Lo scheletro delle 13 Parti + appendici richiesto dall'utente è mantenuto integralmente; il *contenuto* delle Parti I, VI, VII, IX è stato riadattato dal dominio "forecasting di serie storiche" (presupposto dal template) al dominio reale del codice: classificazione clinica binaria da record tabellari convertiti in testo ed embedding. Motivazione: vincolo di verità del prompt stesso ("il nome suggerisce previsione, ma stabiliscilo dal codice").
- Metriche trattate nel libro: Accuracy, Macro-F1, ROC-AUC (le uniche presenti nel codice) + i tre test statistici (Wilcoxon, t-test appaiato, DeLong). MAE/RMSE/MAPE non saranno trattate: non compaiono nel codice.
- **Convenzione Markdown per i riquadri ricorrenti** (fissata in `cap_00.md` §0.2.2, da applicare identica in ogni capitolo successivo): blockquote con prefisso in grassetto maiuscolo, nessuna emoji, forma `> **ETICHETTA —** testo…`. Le sei etichette: `SE VIENI DA JAVA`, `ATTENZIONE`, `APPROFONDIMENTO FACOLTATIVO`, `PROVA TU`, `RIFERIMENTO AL CODICE`, `MATERIALE PER LA TESI`.
- **Convenzione capitolo**: ogni capitolo (tranne forse le appendici) apre con un blocco "Obiettivi" (elenco puntato breve) e chiude con "Riepilogo" (poche righe), "Domande di autoverifica" (3, con risposta subito sotto, non a fine libro), e il riquadro `MATERIALE PER LA TESI` con 3 elementi riutilizzabili.
- Numerazione dei semi/citazioni: si continua ad usare la label `[Fatto]`/`[Inferenza]`/`[Da verificare]` in grassetto quadro all'inizio del paragrafo o della frase interessata, non solo nella scheda tecnica interna — anche nei capitoli del libro stesso, dove un'affermazione tecnica lo richiede.

## Termini di dominio già definiti (da riportare nel glossario, non ridefinire)

(nessuno ancora — la stesura dei capitoli non è iniziata)

## Riferimenti al codice già citati nella scheda tecnica

Vedi `manuale/scheda_tecnica.md` per l'elenco completo con `file:riga`. Coprono tutti i 9 file Python di `master` (1387 righe totali), `README.md`, `docs/DATASET.md`, `docs/STATISTICAL_TESTS.md`, `run_pipeline.sh`, entrambi i `report.md` generati, e i tre file del branch `chatbot` (letti parzialmente, primi ~60-90 righe ciascuno).

## Riferimenti bibliografici già verificati

4 riferimenti trovati citati direttamente in `docs/DATASET.md` (Heart Disease UCI + paper Detrano 1989; Diabetes130 UCI + paper Strack 2014), con DOI verificabili. Nessun altro riferimento è stato ancora cercato/verificato con WebSearch/WebFetch (da fare in Appendice, Parte XIII e dove servono paper sui modelli di embedding: E5, GTE, BioClinicalBERT, PubMedBERT, BioBERT, DeLong 1988, SMOTE/SMOTENC, UMAP, bootstrap di Efron).

## Domanda chiusa dall'utente (2026-09-05)

Per la Parte IX (capitoli 43-47): **usare i risultati già presenti e tracciati in `datas/`**, non rieseguire `python main.py`. Decisione dell'utente, esplicita. Quando si scriverà il capitolo 43, chiarire nel testo che le tabelle numeriche vengono dai file già nel repository (citati con percorso esatto, es. `datas/heart_disease/reports/report.md`), non da un'esecuzione fatta in questa sessione — coerente con l'etichettatura Fatto/Inferenza/Da verificare del capitolo 0.

## Stato dei 58 capitoli + Parte 0 + 6 appendici

Legenda: ⬜ non iniziato · 🟨 in corso · ✅ completo e salvato.

| # | File | Titolo | Stato |
|---|---|---|---|
| 0 | cap_00.md | Come usare questo libro | ✅ |
| 1 | cap_01.md | Perché questo progetto esiste | ✅ |
| 2 | cap_02.md | Il quadro del machine learning supervisionato | ✅ |
| 3 | cap_03.md | Dalla tabella al testo | ✅ |
| 4 | cap_04.md | Classificazione binaria: l'essenziale | ✅ |
| 5 | cap_05.md | Rappresentazioni testuali ed embedding | ✅ |
| 6 | cap_06.md | Il gergo del codice | ✅ |
| 7 | cap_07.md | Sintassi minima e idiomi core | ✅ |
| 8 | cap_08.md | Strutture dati e comprehension | ✅ |
| 9 | cap_09.md | Funzioni, argomenti, trappole | ✅ |
| 10 | cap_10.md | Moduli, package, incapsulamento | ✅ |
| 11 | cap_11.md | Eccezioni, context manager, decoratori | ✅ |
| 12 | cap_12.md | Concorrenza e memoria | ✅ |
| 13 | cap_13.md | Tabella di traduzione Java→Python e trappole finali | ✅ |
| 14 | cap_14.md | Interprete e ambienti virtuali | ✅ |
| 15 | cap_15.md | Installazione passo passo su macOS | ✅ |
| 16 | cap_16.md | Troubleshooting e verifica dell'ambiente | ✅ |
| 17 | cap_17.md | Vista d'insieme: componenti e confini | ✅ |
| 18 | cap_18.md | Il ciclo di vita di un'esecuzione | ✅ |
| 19 | cap_19.md | Stato, configurazione, punti di estensione | ✅ |
| 20 | cap_20.md | function.py | ✅ |
| 21 | cap_21.md | preprocessing.py | ✅ |
| 22 | cap_22.md | embedding.py | ✅ |
| 23 | cap_23.md | classification.py | ✅ |
| 24 | cap_24.md | evaluation.py | ✅ |
| 25 | cap_25.md | error_analysis.py | ✅ |
| 26 | cap_26.md | statisticaltest.py | ✅ |
| 27 | cap_27.md | generatereport.py | ✅ |
| 28 | cap_28.md | main.py | ✅ |
| 29 | cap_29.md | Il dataset UCI Heart Disease | ✅ |
| 30 | cap_30.md | Il dataset Diabetes 130-US Hospitals | ✅ |
| 31 | cap_31.md | Qualità dei dati e casi limite | ✅ |
| 32 | cap_32.md | La regressione logistica | ✅ |
| 33 | cap_33.md | Come si valida correttamente un modello di classificazione | ✅ |
| 34 | cap_34.md | Le tre metriche del progetto | ✅ |
| 35 | cap_35.md | Soglie di decisione | ✅ |
| 36 | cap_36.md | Bootstrap e intervalli di confidenza | ✅ |
| 37 | cap_37.md | I tre test di significatività | ✅ |
| 38 | cap_38.md | Riduzione di dimensionalità e visualizzazione: UMAP | ✅ |
| 39 | cap_39.md | Iperparametri del progetto | ✅ |
| 40 | cap_40.md | Caso d'uso 1: Heart Disease dall'inizio alla fine | ✅ |
| 41 | cap_41.md | Caso d'uso 2: Diabetes130 e le differenze che contano | ✅ |
| 42 | cap_42.md | Caso d'uso 3: aggiungere un ottavo encoder | ✅ |
| 43 | cap_43.md | Protocollo sperimentale | ✅ |
| 44 | cap_44.md | Risultati — Heart Disease | ✅ |
| 45 | cap_45.md | Risultati — Diabetes130 | ✅ |
| 46 | cap_46.md | Analisi degli errori sui due dataset | ✅ |
| 47 | cap_47.md | Confronto con un modello di riferimento banale | ✅ |
| 48 | cap_48.md | Nessun test automatico | ✅ |
| 49 | cap_49.md | Scrivere il primo test | ✅ |
| 50 | cap_50.md | Debugging e log in pratica | ✅ |
| 51 | cap_51.md | Limiti metodologici del protocollo di valutazione | ✅ |
| 52 | cap_52.md | Il caso del reporting automatico non aggiornato | ✅ |
| 53 | cap_53.md | Posizionamento rispetto allo stato dell'arte | ✅ |
| 54 | cap_54.md | Il chatbot clinico non integrato | ✅ |
| 55 | cap_55.md | Direzioni di sviluppo difendibili | ✅ |
| 56 | cap_56.md | Mappa capitolo→tesi | ✅ |
| 57 | cap_57.md | Cosa è pronto, cosa manca | ✅ |
| 58 | cap_58.md | Venti domande della commissione | ✅ |
| A | app_A.md | Glossario | ✅ |
| B | app_B.md | Riferimento funzioni pubbliche | ✅ |
| C | app_C.md | Formulario | ✅ |
| D | app_D.md | Bibliografia annotata + bibliografia.bib | ✅ |
| E | app_E.md | Zone d'ombra | ✅ |
| F | app_F.md | Indice analitico | ✅ |

**TUTTI I CONTENUTI SONO COMPLETI: 58 capitoli + Parte 0 + 6 appendici + bibliografia.bib. 12 riferimenti bibliografici verificati con WebSearch (DOI/arXiv/ISBN reali), nessuno lasciato "plausibile ma non controllato" salvo 3 dettagli minori esplicitamente marcati in Appendice D/E.**

## Fase 7 — PDF: COMPLETATA

Toolchain effettivamente usata (comandi reali eseguiti in questa sessione): `brew install tectonic` (motore PDF compatibile XeLaTeX), `npm install -g @mermaid-js/mermaid-cli` + `npx puppeteer browsers install chrome-headless-shell` (per renderizzare i 6 diagrammi Mermaid in PDF vettoriale), `brew install poppler` (per verificare il PDF prodotto). I 6 diagrammi estratti in `manuale/diagrams/*.mmd` e renderizzati in `*.pdf`. Script `manuale/build_pdf.py` assembla tutti i 66 file sorgente in `_combined.md` sostituendo i blocchi ```mermaid con le immagini renderizzate. Build finale: `pandoc pandoc_meta.yaml _combined.md --pdf-engine=tectonic --resource-path=.:diagrams -o Forecast_Manuale_Completo_v1.pdf`.

Problemi reali incontrati e risolti: (1) il font "Latin Modern Roman" richiesto per nome a fontspec/XeTeX non era risolvibile come font di sistema — rimosso da `mainfont`/`monofont` in `pandoc_meta.yaml`, si usa il font serif di default di LaTeX (comunque serif per il testo, monospazio per il codice, come richiesto); (2) tre caratteri Unicode fuori da blocchi matematici (≤, τ×2, ≪) non presenti nel font monospazio/serif di default — corretti sostituendoli con notazione LaTeX (`$\leq$`, `$\tau$`, `$\ll$`) in cap_44.md, app_A.md, app_F.md, cap_32.md; (3) un diagramma di sequenza Mermaid (capitolo 18) non si analizzava per via di `&lt;dataset&gt;` nell'etichetta di un partecipante — semplificato in `datas/ dataset /`; (4) `lof`/`lot` automatici di Pandoc restavano vuoti perché il libro usa didascalie manuali numerate ("Figura X.Y") invece della sintassi nativa di Pandoc — sostituiti con un elenco compilato a mano (`cap_00b_elenchi.md`) con le stesse informazioni.

Limite noto e accettato consapevolmente: 2 emoji (📊, 🔍) dentro due estratti di codice **citati alla lettera** da `generatereport.py` (righe reali del progetto) non hanno un glifo nel font monospazio Latin Modern Mono — appaiono come carattere mancante nel PDF in quei due punti soltanto. Non li ho alterati perché sono citazioni letterali del codice sorgente reale; alterarli avrebbe violato il vincolo di fedeltà delle citazioni di codice. Interessa 2 caratteri su ~280 pagine.

Risultato: **280 pagine**, ~1 MB, generato con successo (`exit code 0`), indice generale con segnalibri PDF cliccabili (via hyperref, automatico con XeLaTeX), formule LaTeX numerate rese correttamente (verificato visivamente sul PDF stesso), tabelle e blocchi di codice entro i margini (verificato visivamente), evidenziazione sintattica presente (`highlight-style: tango`).

## CONSEGNA COMPLETA

Tutti gli elementi richiesti dalla consegna sono pronti in `manuale/`: `Forecast_Manuale_Completo_v1.pdf`, tutti i sorgenti Markdown (66 file: cap_00a/00b + cap_00-58 + app_A-F), `bibliografia.bib`, questo file di stato, e le zone d'ombra sono in `app_E.md`.

**L'utente ha chiesto di completare tutto il lavoro ("ok finisci") il 2026-09-05. Si procede senza ulteriori check-in fino a consegna completa (Parti XI-XIII, appendici, PDF).**

**Traguardo raggiunto: Parte IX completa. 48 capitoli/parti su 65 unità totali (~74%).**

**Traguardo raggiunto: Parte VIII completa. 43 capitoli/parti su 65 unità totali.**

**Traguardo raggiunto: Parte VII completa (la parte più densa di formule). 40 capitoli/parti su 65 unità totali.**

**Traguardo raggiunto: Parte VI completa. Tutte le Parti 0-VI sono ora scritte (31 capitoli/parti su 65 unità totali).**

**Traguardo raggiunto: Parte V completa (capitoli 20-28) — tutti e 9 i file Python di `master` sono ora trattati in un capitolo dedicato, uno per uno. Checklist finale, punto 4, soddisfatto per il branch master (il chatbot resta in Parte XII).**

Parte III (capitoli 14-16, Ecosistema e ambiente) completata e salvata.

Parte 0, Parte I (capitoli 1-6) e Parte II (capitoli 7-13) completate e salvate. Questa tabella va aggiornata ad ogni capitolo completato (non solo a fine sessione), rigenerandola per intero ogni volta che serve.

## Impegno esplicito dell'utente da onorare a fine lavoro

L'utente ha chiesto esplicitamente (turno del 2026-09-05) di non dimenticare l'esportazione finale in PDF (Fase 7). Non va fatta ora (mancano ancora 45 capitoli + 6 appendici): va fatta a lavoro concluso, con la toolchain Pandoc + tectonic (da installare via `brew install tectonic`) + mermaid-cli (da installare via `npm install -g @mermaid-js/mermaid-cli`), documentando i comandi reali eseguiti. **Non chiudere questo progetto senza aver prodotto `Forecast_Manuale_Completo_v1.pdf`.**

## Termini di dominio già definiti (da riprendere nel glossario, non ridefinire)

Classificazione binaria, sbilanciamento delle classi, vero/falso positivo/negativo, embedding, tokenizzazione, encoder transformer, pooling (mean pooling), modello generalista vs. biomedico, apprendimento supervisionato/non supervisionato/per rinforzo, addestramento/validazione/inferenza, overfitting/underfitting, generalizzazione, data leakage (definizione generale; il dettaglio tecnico è rimandato al capitolo 33), soglia di decisione, SMOTENC (nome introdotto ma non ancora spiegato in dettaglio — dettaglio rimandato al capitolo 31.2).

## Riferimenti al codice aggiunti in questa sessione di scrittura (oltre a quelli già nella scheda tecnica)

`function.py:38-61` (dizionari modelli, MODEL_FAMILY, FAMILY_COLORS), `classification.py:26-37`, `preprocessing.py:41,53,66-70`, `embedding.py:43-59,146,155,170,178`, `error_analysis.py:24,26-27,58-75`, `evaluation.py:23-25,56`, `generatereport.py:221`, `docs/DATASET.md:17,59-64,109-110`, `README.md:5-16,56-61,78`.

## Riferimenti bibliografici marcati [DA VERIFICARE] durante la scrittura (da chiudere in Appendice D)

E5 (Wang et al.), GTE (Li et al.), Hastie/Tibshirani/Friedman "The Elements of Statistical Learning" — nessuno di questi è stato ancora cercato con WebSearch/WebFetch. Si aggiungono ai quattro riferimenti già verificati elencati sopra (Heart Disease UCI + Detrano 1989; Diabetes130 UCI + Strack 2014).

## Fatti tecnici verificati con grep durante la scrittura della Parte II (validi per tutto il libro, non ripetere la verifica)

Zero `class` definite nei 9 file di `master`; zero `def __init__`; zero decoratori (`@`); zero `yield`; zero annotazioni di tipo (`: tipo` o `->`); zero `assert`; zero operatore walrus (`:=`); zero `*args`/`**kwargs` in firme; zero `global`; un solo `raise ... from` (`embedding.py:199`); tre `with` (`embedding.py:117,203`, `generatereport.py:245`); tre `lambda`, identiche (`function.py:246,292,363`); un solo `hasattr` (`preprocessing.py:109`, nessun `isinstance`); nessun `__init__.py` in tutto il repository. Fonte: comandi `grep` eseguiti sui 9 file, sessione del 2026-09-05.

## Nuova scoperta critica durante la Parte III (aggiunta a scheda_tecnica.md §7ter)

Il comando `ollama pull yxchia/multilingual-e5-base` in `README.md:104` scarica un modello diverso da quello richiesto da `function.py:39` (`jeffh/intfloat-e5-base-v2:q8_0`). Verificato incrociando README, function.py e l'output reale di `ollama list` in questo ambiente (che ha il modello corretto installato, non quello del README). Chi seguisse il README alla lettera otterrebbe un errore "model not found" per e5-base. Trattato nei capitoli 15.2 e 16.1.

## Fatti architetturali stabiliti nella Parte IV (validi per tutto il libro)

Il grafo delle dipendenze interne è una stella a due livelli: `function.py` non importa nessun altro modulo del progetto; tutti gli altri 7 file importano solo da `function.py`, mai l'uno dall'altro; `main.py` importa da tutti gli 8. Solo il passaggio fase 1→fase 2 (`preprocessing_data` → `embeddings`) avviene in memoria; da `classification.py` in poi ogni fase rilegge da disco l'output della precedente. Nessun `try`/`except` in `main.py` attorno alle 7 fasi: un fallimento a metà lascia l'albero di output parzialmente popolato, senza modo di riprendere se non rilanciando tutto da capo. Aggiungere un modello a `models_all` di una famiglia esistente è quasi gratuito; di una famiglia nuova richiede due modifiche manuali puntuali (`FAMILY_COLORS`, `family_order` in `function.py:349`) altrimenti silenziosamente incomplete.

## Nuove scoperte durante la Parte V (aggiunte implicitamente nei capitoli, utile riepilogo qui)

- `preprocessing.py:23` usa la variabile `datasetChoosen` in camelCase, incoerente con lo snake_case del resto del file — refuso di stile, nessuna conseguenza funzionale (cap. 21.1).
- La formula di deviazione di feature in `error_analysis.py` è concettualmente imparentata alla *d* di Cohen mai nominata esplicitamente nel codice (cap. 25.3) — buon materiale per il formulario (Appendice C).
- `statisticaltest.py` salva il flag di significatività come stringa `"1"`/`"0"`, non intero/booleano — un dettaglio che romperebbe un filtro numerico diretto sul CSV (cap. 26.1).
- Confermata con precisione, confrontando i due `report.md` reali carattere per carattere, l'identità esatta del testo statico in `generatereport.py:192-225` (cap. 27.2) — probabilmente il miglior singolo argomento critico di tutto il libro.

## Scoperta maggiore durante la Parte VI (aggiunta a scheda_tecnica.md §7quater)

Scomponendo il missing-value count per centro clinico (comandi Python eseguiti su tutti e 4 i file sorgente di Heart Disease): `ca` manca nell'1% di Cleveland ma nel 99% di Hungarian, 96% di Switzerland, 99% di VA; `thal` analogamente 1%/90%/42%/83%. Sul totale concatenato (920 righe): 66.4% di `ca` mancante, 52.8% di `thal` mancante — imputati comunque con mediana/moda su tutte le 920 righe. Cleveland da sola ha solo 6 righe con questi due valori mancanti (4+2), il che spiega esattamente la cifra "297" della documentazione (303-6=297). Pattern parallelo confermato in Diabetes130: `max_glu_serum` mancante al 94.7%, `A1Cresult` all'83.3% sull'intero file grezzo. Probabilmente la scoperta più quantitativamente forte di tutto il libro finora. Trattata per esteso nei capitoli 29, 30, 31.

## Scoperta maggiore durante la Parte VII (aggiunta a scheda_tecnica.md §7quinquies)

Il rapporto fra dimensione dell'embedding e dimensione del training set per fold si inverte fra i due dataset: per Heart Disease (814 righe post-SMOTE, ~651/fold) i modelli a 1024 dimensioni (gte-large, e5-large) hanno **più parametri (1024) che esempi di training (~651)** in ciascun fold — rapporto 1.57. Per Diabetes130 (28.428 righe post-SMOTE, verificato caricando bioclinicalbert_embeddings.npy) lo stesso rapporto è 0.045, del tutto sicuro. Inoltre: `datas/diabetes130/embeddings/e5_large_embeddings.npy` e `gte_large_embeddings.npy` non esistono più né su disco né in git (esclusi esplicitamente da `.gitignore:12-13`, presumibilmente perché supererebbero i 100MB per file di GitHub — coerente con il file analogo a 768 dim visto pesare 87.3MB nel diff del commit chatbot). Trattato per esteso nel capitolo 32.

Formule numerate 32.1 attraverso 37.3 usate in Parte VII (continua la numerazione da 25.1); prossima parte (VIII) non userà formule nuove salvo necessario, si riparte da 40.x se serve.

## Riferimenti bibliografici marcati [DA VERIFICARE] aggiunti in Parte VII

DeLong, DeLong & Clarke-Pearson (1988), Biometrics — volume/pagine/DOI da confermare. McInnes/Healy/Melville (UMAP, 2018) — riferimento arXiv/DOI da confermare. Si aggiungono a E5 (Wang et al.), GTE (Li et al.), Hastie/Tibshirani/Friedman già marcati in Parte I. Tutti da verificare con WebSearch/WebFetch in Appendice D, non prima.

## Scoperta maggiore durante la Parte IX (la più forte del libro, verificata rigorosamente)

Gli "hardest cases" di Heart Disease (record sbagliati da tutti e 7 i modelli) sono in parte dimostrabile artefatti, non casi clinicamente ambigui: (a) due dei primi casi hanno età non intera (55.2321, 54.0393) — impossibile per un paziente reale, prova diretta di origine sintetica SMOTENC; (b) la maggioranza condivide `ca=0, thal=3`, e ho verificato con un comando reale che la mediana osservata di `ca` è esattamente 0.0 e la moda osservata di `thal` è esattamente 3.0 — gli stessi valori usati dall'imputazione. I "casi più difficili" sono quindi in buona parte il profilo "generico imputato", amplificato da SMOTE, non pazienti clinicamente complessi. Trattato per esteso nel capitolo 46.2.

Altre scoperte/calcoli reali di Parte IX: baseline a maggioranza calcolato con `DummyClassifier` su `y_true.npy` già tracciati (50.00%/0.3333 per entrambi i dataset, essendo il pool esattamente bilanciato da SMOTE) — ogni modello lo supera nettamente (+11.7/+32.1 punti di accuratezza), ma il confronto rivela anche che un baseline sulla popolazione REALE di Diabetes130 (88.84%) supererebbe ogni modello misurato sul pool riequilibrato, rendendo concreto il costo del test set mai usato (capitolo 47.3). Su Heart Disease, il test di DeLong mostra un quadro sfumato (superiorità biomedica netta solo contro i 2 generalisti piccoli, capitolo 44.3); su Diabetes130 è netto (20/21 coppie significative, capitolo 45.2) — spiegato dalla potenza statistica molto maggiore con n=28.428 contro n=814.

## Prossimo passo

Proseguire con la Parte X (capitoli 48-50, test/debugging/qualità — 3 capitoli) in una prossima sessione di scrittura. Nessuna domanda aperta rimanente. Da qui in poi tutte le parti restanti (X-XIII + appendici) possono attingere liberamente a tutto il materiale già prodotto nelle Parti IV-IX.

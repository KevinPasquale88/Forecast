# Scheda tecnica interna — progetto "Forecast"

> Documento di lavoro (Fasi 1-3 del prompt). Non è un capitolo del libro: è il dossier di verità su cui il libro viene scritto. Ogni riga è marcata Fatto / Inferenza / Da verificare.

Data ricognizione: 2026-09-05. Repository: `/Users/robertopasquale/Documents/Percorso di tesi/PythonProject/Forecast`, branch `master` (pulito, HEAD `41bf90e`).

## 0. La scoperta più importante

**[Fatto]** Il progetto si chiama "Forecast" (nome della cartella e titolo storico) ma il codice, i dati e il README (`README.md:1`, "Forecast — Local Clinical Text-Embedding Pipeline") mostrano che **non è un sistema di previsione di serie temporali**. È una pipeline che:
1. prende record clinici tabellari (non testo libero) da due dataset UCI,
2. li converte in frasi in linguaggio naturale,
3. genera embedding (vettori numerici densi) di quelle frasi con modelli linguistici locali,
4. addestra un classificatore binario su quei vettori,
5. confronta rigorosamente le prestazioni di 7 modelli di embedding diversi con bootstrap e test statistici.

**Conseguenza vincolante per il libro:** il template di Fase 2/Fase 5 fornito dall'utente presuppone concetti di serie storiche (stagionalità, trend, autocorrelazione, MAE/RMSE/MAPE). Questi concetti **non compaiono nel codice** e verrebbero inventati se inclusi. Il libro li sostituisce con i concetti realmente usati: classificazione binaria, imbalanced learning (SMOTE/SMOTENC), embedding testuali/NLP, validazione incrociata stratificata, bootstrap, test di significatività (Wilcoxon, t-test appaiato, DeLong), metriche di classificazione (Accuracy, Macro-F1, ROC-AUC). Lo scheletro strutturale (Parti 0-XIII + appendici) resta quello richiesto: cambia solo il contenuto di dominio, coerentemente con l'istruzione esplicita del prompt di stabilire il dominio dal codice, non dal nome della cartella.

## 1. Albero del progetto (esclusi `.git/` e `env/`)

```
Forecast/
├── main.py                     56 righe  — orchestratore CLI (7 fasi)
├── function.py                386 righe  — config modelli, I/O cartelle, tutte le funzioni di plotting
├── preprocessing.py           121 righe  — caricamento, imputazione, SMOTENC, scaling
├── embedding.py               209 righe  — tabellare→testo, generazione embedding (Ollama + HF)
├── classification.py           79 righe  — LogisticRegression + StratifiedKFold(5) + soglia F1-ottima
├── evaluation.py                83 righe  — bootstrap 10.000, grafici, CI
├── error_analysis.py            81 righe  — tracciamento FP/FN sui record originali
├── statisticaltest.py          123 righe  — Wilcoxon, t-test appaiato, DeLong
├── generatereport.py           249 righe  — assemblaggio report Markdown
├── requirements.txt             67 righe  — dipendenze pip (nessun pyproject.toml/setup.py)
├── run_pipeline.sh/.bat/.ps1              — bootstrap ambiente + esecuzione one-shot
├── README.md                   220 righe  — documentazione architetturale già esistente
├── docs/
│   ├── DATASET.md             115 righe  — origine/etica dei due dataset UCI
│   └── STATISTICAL_TESTS.md    96 righe  — metodologia dei test statistici
├── datasets/                    19 MB    — dati grezzi UCI (sola lettura, mai scritti dalla pipeline)
│   ├── heart+disease/                     — 4 file .data (Cleveland, Hungarian, Switzerland, VA)
│   └── diabetes+130-us+hospitals-.../      — diabetic_data.csv (101.766 righe), IDS_mapping.csv
└── datas/                      477 MB    — output generati dalla pipeline, isolati per dataset
    ├── heart_disease/{preprocessing,embeddings,results,graphics,reports}/
    └── diabetes130/{preprocessing,embeddings,results,graphics,reports}/
```

Totale codice Python applicativo: **1387 righe** su 9 file (`wc -l`, comando eseguito). Nessun package/modulo (`__init__.py` assente): è un progetto "flat", tutti gli import sono al livello radice.

**[Fatto]** Non esistono: file di test (nessun `test_*.py`, nessun `pytest`/`unittest` nei sorgenti — verificato con `find`/`grep`), configurazioni CI (nessuna cartella `.github/`, nessuno `.yml`), file `LICENSE`, `pyproject.toml`, `setup.py`. La gestione delle dipendenze è interamente `pip` + `requirements.txt` con versioni fissate (`==`).

## 2. Ambiente ed esecuzione

- **[Fatto]** Python 3.14 (`README.md:84`; confermato dal percorso reale `env/lib/python3.14/…` e da `env/bin/python3 --version` → `Python 3.14.0`, comando eseguito in questa sessione).
- **[Fatto]** Gestore pacchetti: pip puro, nessun ambiente Conda. Virtualenv locale in `env/` (esclusa da `.gitignore:1`, mai committata).
- **[Fatto]** Due dipendenze runtime esterne al processo Python: **Ollama** (server locale per i modelli general-purpose, comunicazione via `ollama.Client` su HTTP locale, `embedding.py:10,105`) e **Hugging Face Hub** (download modelli biomedici via `sentence-transformers`, `embedding.py:7,11`).
- **[Fatto]** Variabili d'ambiente attese: `HF_READ_TOKEN`, `OFFLINE_MODE` in un file `.env` (letto con `python-dotenv`, `embedding.py:6,143`). Il file `.env` non è presente in questa working copy (verificato) e non è mai stato committato (`.gitignore:2`) — nessuna credenziale esposta nel repository.
- **[Fatto]** In questo ambiente: rete disponibile (verificato con `curl` verso pypi.org → HTTP 200), `ollama` installato (`/usr/local/bin/ollama`) ma stato del servizio/modelli scaricati non verificato, `brew` e `npm` disponibili, 121 GiB di spazio libero. Pandoc 2.12 presente; XeLaTeX, Typst, WeasyPrint, wkhtmltopdf, `mmdc` (mermaid-cli), `reportlab` **assenti** — andranno installati al momento della generazione del PDF (Fase 7), con i comandi usati dichiarati nel libro.

## 3. Dipendenze esterne (da `requirements.txt`, una riga = una libreria realmente importata nel codice)

| Libreria | Dove è importata | Ruolo in questo progetto |
|---|---|---|
| `pandas` | quasi ovunque | DataFrame per i record clinici tabellari |
| `numpy` | quasi ovunque | array per embedding, etichette, bootstrap |
| `scikit-learn` | preprocessing.py, classification.py, evaluation.py | `StandardScaler`, `OneHotEncoder`, `ColumnTransformer`, `LogisticRegression`, `StratifiedKFold`, metriche |
| `imbalanced-learn` | preprocessing.py:7 | `SMOTENC` per il bilanciamento delle classi su feature miste |
| `ollama` | embedding.py:10 | client HTTP verso il server locale Ollama (modelli general-purpose) |
| `sentence-transformers` | embedding.py:11 | caricamento ed esecuzione dei modelli biomedici HuggingFace |
| `huggingface_hub` | embedding.py:7 | autenticazione/login verso l'hub HF |
| `transformers`, `torch` | dipendenze indirette di sentence-transformers | motore di inferenza dei modelli biomedici |
| `python-dotenv` | embedding.py:6 | caricamento `.env` |
| `umap-learn` | function.py:4 | proiezione 2D per la visualizzazione (non per la pipeline di classificazione) |
| `seaborn`, `matplotlib` | function.py | tutti i grafici del progetto |
| `scipy` | statisticaltest.py:6-7 | `ttest_rel`, `wilcoxon` |
| `MLstatkit` | statisticaltest.py:3 | implementazione del test DeLong (`Delong_test`) |
| `tabulate` | usato indirettamente da `DataFrame.to_markdown()` in generatereport.py | tabelle Markdown nel report |
| `ucimlrepo` | elencata in requirements.txt, **non trovata in alcun import nei file letti** | presumibilmente usata in una fase esplorativa iniziale non presente nello stato attuale del codice — **[Da verificare]** |

## 4. Punti di ingresso

- **[Fatto]** `main.py` — unico entry point applicativo, CLI con `argparse`, un solo flag `--dataset {heart_disease,diabetes130}` (default `heart_disease`, `main.py:15`). Nessuna API HTTP, nessun notebook, nessun job schedulato nel branch `master`.
- **[Fatto]** `run_pipeline.sh` / `.bat` / `.ps1` — script di bootstrap che creano/attivano `env/`, installano `requirements.txt`, avviano `ollama serve`, scaricano i 4 modelli Ollama richiesti, poi invocano `python3 main.py "$@"`.
- **[Fatto, ma non in `master`]** Sul branch `chatbot` (mai unito, verificato con `git merge-base --is-ancestor` → non-ancestor) esistono tre file aggiuntivi non presenti nella working copy attuale: `app_streamlit.py` (interfaccia web Streamlit), `bot_telegram.py` (bot Telegram), `chatbot_core.py` (307 righe, logica condivisa). Riusano `record_to_text_heart_disease`/`record_to_text_diabetes130` e le etichette di `embedding.py`. Riferiscono un simbolo `EMBEDDING_MODEL` in `function.py` che **non esiste nella versione di `function.py` su `master`** — segno che quel branch ha una copia divergente di `function.py`. Trattato in Parte XII come estensione esistente ma non integrata; approfondimento del meccanismo di inferenza rimandato a quella sezione.

## 5. Dati: origine, schema, dimensioni reali

| Dataset | File grezzo | Righe reali (`wc -l`, comando eseguito) | Feature usate | Target | Split/bilanciamento |
|---|---|---|---|---|---|
| UCI Heart Disease | 4 file `.data` in `datasets/heart+disease/` | 303+294+123+200 righe concatenate (`preprocessing.py`→`function.py:96-113`) | 13 (`function.py:10-15`) | `num` binarizzato a `(num>0)` (`preprocessing.py:41`) | 80/20 poi SMOTENC solo sul train |
| Diabetes 130-US Hospitals | `diabetic_data.csv` | 101.767 righe incl. header (comando `wc -l` eseguito), 50 colonne originali | 19 selezionate (`function.py:21-27`) | `readmitted` binarizzato a "<30 giorni" (`function.py:124`) | campionamento stratificato a 20.000 righe, poi 80/20 poi SMOTENC |

**[Fatto]** Dopo SMOTENC, il set di embedding per `heart_disease` ha **814 record** per modello, ma **non tutti i modelli producono vettori della stessa lunghezza** (verificato caricando i 7 file `.npy` con NumPy, comando Python eseguito in questa sessione):

| Modello | Dimensione embedding | Fonte della dimensione |
|---|---|---|
| e5-base | 768 | Ollama (`embedding_length` in `ollama list` via API) + verificato su file |
| gte-base | 768 | idem |
| gte-large | **1024** | idem |
| e5-large | **1024** | idem |
| bioclinicalbert | 768 | verificato su file |
| pubmedbert | 768 | verificato su file |
| sentence-biobert | 768 | verificato su file |

Punto didattico per Parte VII: `classification.py` addestra un `LogisticRegression` separato per ciascuno dei 7 modelli, e ogni volta lo spazio vettoriale di partenza ha una dimensione diversa (768 o 1024) a seconda del modello. È del tutto normale in Python: la stessa funzione `training_classifier` si adatta a runtime alla forma dell'array caricato da disco, senza alcuna dichiarazione esplicita della dimensione. In Java un'API equivalente avrebbe quasi certamente un tipo generico o un controllo a compile-time sulla dimensionalità del vettore; qui è NumPy che "si adatta" silenziosamente, e un errore di forma emergerebbe solo a runtime (tipicamente come `ValueError` in `fit()`).

**[Fatto]** Ollama è in esecuzione in questo ambiente (pid verificato con `pgrep`) e tutti e 4 i modelli general-purpose richiesti risultano già scaricati (`ollama list`, comando eseguito). Anche i 3 modelli biomedici HuggingFace risultano già presenti nella cache locale (`~/.cache/huggingface/hub`, 2.0 GB, comando `find` eseguito). **Conseguenza pratica:** l'intera pipeline (`python main.py --dataset ...`) è oggi tecnicamente eseguibile in questo ambiente senza alcun download aggiuntivo, per entrambi i dataset — ma eseguirla sovrascriverebbe i file di risultato già tracciati da git in `datas/`. Decisione rimandata all'utente (vedi messaggio di checkpoint).

## 6. Scoperte critiche (Fase 3) — da riprendere in Parte XI e nei capitoli pertinenti

1. **[Fatto]** `preprocessing.py:43` calcola `X_test, y_test` con `train_test_split(test_size=0.2, ...)` ma la funzione restituisce solo `X_train_bal, y_train_bal` (riga 70). `X_test`/`y_test` non vengono mai più referenziati in nessun file del progetto (verificato con lettura completa di tutti i moduli). **Conseguenza:** il 20% di dati messo da parte non è mai usato come test set finale indipendente; l'unica validazione è la 5-fold `StratifiedKFold` di `classification.py`, eseguita sugli embedding derivati dal restante 80% (dopo SMOTENC). Punto da discutere criticamente: non è "data leakage" in senso stretto, ma è una risorsa di validazione sprecata e un nome di variabile fuorviante.
2. **[Fatto]** `classification.py:30-37`: per ogni fold, la soglia di decisione ottimale (quella che massimizza F1) è calcolata da `precision_recall_curve(y_val, y_score)` **sullo stesso fold di validazione** su cui poi si misura la metrica. È una forma mite di ottimismo statistico (non riguarda l'addestramento del modello, solo la scelta della soglia): il modello non "vede" le etichette di validazione per allenarsi, ma la soglia sì. Effetto atteso: F1/Accuracy leggermente sovrastimati rispetto a una soglia fissata a priori (es. 0.5) o scelta su un fold di calibrazione separato.
3. **[Fatto]** `generatereport.py:192-225`: le sezioni "Discussion and Observations", "Conclusions" e "Potential Improvements" del report generato sono **stringhe Python statiche**, identiche in entrambi i report reali già presenti nel repository (`datas/heart_disease/reports/report.md` e `datas/diabetes130/reports/report.md`), nonostante le tabelle numeriche sopra siano molto diverse tra i due dataset. La frase fissa "GTE-large tends to achieve higher ROC-AUC" è **contraddetta dai numeri nella stessa pagina**: in `heart_disease` l'AUC di `gte-large` (0.854) è inferiore a `pubmedbert` (0.885) ed `e5-large` (0.866); in `diabetes130` è inferiore a `sentence-biobert` (0.768), `bioclinicalbert` e `pubmedbert` (~0.757-0.758). Il testo narrativo del report non è calcolato dai dati: è un template fisso. Punto di forte interesse critico, ottimo materiale per la tesi (limite di riproducibilità/validità del reporting automatico).
4. **[Fatto]** `embedding.py:101`: un `threading.Semaphore(1)` serializza tutte le chiamate al client Ollama anche se `generate_all_embeddings` (riga 201) usa `ThreadPoolExecutor(max_workers=3)`. La concorrenza reale copre quindi solo l'esecuzione parallela tra un modello Ollama alla volta e i modelli HuggingFace; motivato in un commento (righe 95-100) da limiti pratici del server locale Ollama (esaurimento di porte effimere).
5. **[Fatto]** `function.py:67-72`: il dizionario globale `results` è pre-inizializzato con solo 4 delle 7 chiavi modello; `classification.py:51` aggiunge le altre 3 (`bioclinicalbert`, `pubmedbert`, `sentence-biobert`) per assegnazione diretta, sfruttando la creazione implicita di chiavi nei dict Python. Stato globale mutabile a livello di modulo: se richiamato più volte nello stesso processo Python (es. da un notebook), i valori restano finché non sovrascritti dalla stessa chiave — non un bug nell'uso da CLI attuale (un processo per dataset), ma un punto di attenzione se il codice venisse riusato come libreria.
6. **[Fatto]** Ogni esecuzione di `main.py` cancella e rigenera integralmente l'albero di output del dataset scelto (`main.py:28-31`, `function.py:179-209`): non esiste caching incrementale. La fase più costosa (generazione embedding per 7 modelli) viene sempre rieseguita per intero.
7bis. **[Fatto]** `classification.py:16` istanzia `LogisticRegression(max_iter=2000)` senza mai specificare il parametro `C` (inverso della forza di regolarizzazione L2 in scikit-learn). Resta quindi al default della libreria (`C=1.0`) per tutti e 7 i modelli e per entrambi i dataset: un iperparametro reale del progetto, mai reso esplicito né esplorato. Trattato in Parte VII, capitolo iperparametri.
8. **[Fatto]** Nessun seed globale unico: i semi casuali sono fissati puntualmente (`random_state=42` in `train_test_split`, `SMOTENC`, `UMAP`; `random_state=42` in `StratifiedKFold`; `seed=42` in `bootstrap_metrics`) — buona pratica di riproducibilità locale, ma non centralizzata in un'unica costante condivisa.

## 7. Bibliografia — fonti già verificabili trovate nel codice/documentazione del progetto

- Janosi, A., Steinbrunn, W., Pfisterer, M., Detrano, R. (1988). *Heart Disease*. UCI Machine Learning Repository. DOI: 10.24432/C52P4W. — citato in `docs/DATASET.md:67`.
- Detrano, R. et al. (1989). "International application of a new probability algorithm for the diagnosis of coronary artery disease." *American Journal of Cardiology*, 64(5), 304-310. — citato in `docs/DATASET.md:68`.
- Strack, B., DeShazo, J.P., Gennings, C., Olmo, J.L., Ventura, S., Cios, K.J., Clore, J. (2014). *Diabetes 130-US Hospitals for Years 1999-2008*. UCI Machine Learning Repository. DOI: 10.24432/C5230J. — citato in `docs/DATASET.md:113`.
- Strack, B. et al. (2014). "Impact of HbA1c Measurement on Hospital Readmission Rates: Analysis of 70,000 Clinical Database Patient Records." *BioMed Research International*, 2014. — citato in `docs/DATASET.md:114`.

Tutte le altre citazioni (paper originali di E5, GTE, BioClinicalBERT, PubMedBERT, BioBERT, DeLong 1988, SMOTE/SMOTENC, UMAP, bootstrap di Efron) andranno recuperate e verificate singolarmente in appendice con WebSearch/WebFetch prima di essere incluse in `bibliografia.bib` — nessuna verrà scritta a memoria senza controllo.

## 7bis. Discrepanza numerica tra documentazione e codice (Heart Disease)

**[Fatto]** `docs/DATASET.md:17` e la tabella dataset di `README.md:78` dichiarano **"297 istanze"** per Heart Disease. **[Fatto]** `load_heart_disease()` (`function.py:96-113`) concatena però i 4 file grezzi senza filtrare alcuna riga (`pd.concat(dfs, ignore_index=True)`, nessun `dropna`), e i 4 file contano rispettivamente 303+294+123+200 righe (verificato con `wc -l`, comando eseguito). **Risultato reale: 920 righe**, non 297 (verificato caricando i file con pandas esattamente come fa `load_heart_disease()`, comando Python eseguito in questa sessione). Distribuzione della classe target sulle 920 righe: 509 positive / 411 negative → **55.3% classe positiva** (comando eseguito).

**[Inferenza]** La cifra "297" è il numero storicamente noto in letteratura per il solo sottoinsieme Cleveland **dopo** aver scartato le righe con valori mancanti nelle feature `ca`/`thal` (303 righe Cleveland grezze − 6 righe con valori mancanti critici = 297) — un dataset diverso, più piccolo e mono-centro, da quello che `load_heart_disease()` carica davvero (4 centri, nessuna riga scartata, i mancanti vengono imputati non eliminati). La documentazione del progetto sembra riportare la cifra "canonica" della letteratura invece di quella realmente prodotta dal proprio codice. Punto critico di prim'ordine per Parte VI e Parte XI: un numero-chiave del progetto, citato sia nel README che in docs/DATASET.md, non corrisponde a ciò che il codice fa.

**[Fatto]** Coerenza incrociata: partendo da 920 righe con 55.3%/44.7% di split, l'80% usato per il training (736 righe) mantiene approssimativamente lo stesso rapporto (~407 positive, ~329 negative); SMOTENC porta la classe minoritaria a pareggiare quella maggioritaria, cioè 407+407 = **814** — esattamente il numero di righe osservato nei file `.npy` di embedding per `heart_disease` (§5). I due fatti si confermano a vicenda.

**[Fatto]** Diabetes130, calcolato sull'intero file grezzo (101.766 righe, prima del campionamento a 20.000): 90.409 casi negativi, 11.357 positivi → **11.16% classe positiva** (comando Python eseguito in questa sessione) — uno sbilanciamento molto più marcato di quello di Heart Disease, e un buon esempio didattico di due gradi diversi di sbilanciamento nello stesso libro.

## 7ter. Il comando di installazione del primo modello Ollama non corrisponde al modello usato dal codice

**[Fatto]** `README.md:104` istruisce a eseguire `ollama pull yxchia/multilingual-e5-base`. **[Fatto]** `function.py:39` configura il modello `"e5-base"` con `"name": "jeffh/intfloat-e5-base-v2:q8_0"` — un identificativo diverso, non un alias. **[Fatto]** `ollama list` in questo ambiente (comando eseguito in questa sessione) mostra installato `jeffh/intfloat-e5-base-v2:q8_0`, il nome corretto per `function.py`, non quello del README. Seguire il README alla lettera per l'installazione produrrebbe un errore "model not found" alla fase di embedding per questo modello specifico. Gli altri tre comandi `pull` del README (gte-base, gte-large, e5-large) corrispondono correttamente ai nomi in `function.py:40-42` — il problema è isolato al primo modello. Trattato nel capitolo 15.2 e nel capitolo 16 (troubleshooting).

## 7quater. Imputazione su maggioranza mancante: `ca`/`thal` (Heart Disease) e `max_glu_serum`/`A1Cresult` (Diabetes130)

**[Fatto]** Scomponendo il missing-value count per file sorgente di Heart Disease (comando Python eseguito in questa sessione): `ca` manca nel 1% di Cleveland (4/303) ma nel 99% di Hungarian (291/294), 96% di Switzerland (118/123), 99% di VA (198/200); `thal` manca nel 1% di Cleveland (2/303) ma nel 90% di Hungarian, 42% di Switzerland, 83% di VA; `slope` manca nello 0% di Cleveland ma nel 65% di Hungarian, 14% di Switzerland, 51% di VA. Sul totale concatenato di 920 righe, questo produce **611/920 (66.4%) valori mancanti per `ca`** e **486/920 (52.8%) per `thal`** (§7bis ha già il dettaglio aggregato). **[Fatto]** `preprocessing.py:78-81` (`impute_raw()`) sostituisce ogni valore mancante di `ca` con la **mediana calcolata sul 33.6% di dati realmente osservati** (quasi tutti da Cleveland) e ogni valore mancante di `thal` con la **moda calcolata sul 47.2% di dati realmente osservati** — cioè, per i due terzi (rispettivamente poco più della metà) delle 920 righe, il valore di queste due feature non riflette il paziente reale ma un singolo statistico aggregato derivato quasi interamente da un solo centro clinico su quattro.

**[Fatto]** Cleveland, presa da sola, ha solo 4 righe con `ca` mancante e 2 con `thal` mancante (verificato) — **4 + 2 = 6**, lo stesso numero che spiega esattamente la cifra "297" della documentazione (303 − 6 = 297, §7bis): la "versione pulita" storicamente citata in letteratura è, con ogni evidenza, il sottoinsieme Cleveland dopo aver scartato proprio queste 6 righe. Il progetto attuale non scarta nulla: concatena tutti e 4 i centri e imputa.

**[Fatto]** Un pattern quasi identico esiste in Diabetes130: sulle 19 feature selezionate (`function.py:21-27`), **`max_glu_serum` manca nel 94.7%** delle 101.766 righe originali e **`A1Cresult` manca nell'83.3%** (comando Python eseguito su `diabetic_data.csv`, prima del campionamento a 20.000). Entrambe sono in `cat_cols_diabetes130` (`function.py:32-35`) e vengono quindi imputate con la moda — cioè, per la grande maggioranza dei pazienti, il valore registrato per questi due esami di laboratorio non è mai stato osservato ma sostituito dal valore più frequente fra il 5-17% di casi in cui era davvero presente.

**[Interpretazione]** Questo non è un problema di codice (l'imputazione è implementata correttamente per quello che fa), ma un problema di **assunzione implicita sui dati**: sia `record_to_text_heart_disease()` sia `record_to_text_diabetes130()` (capitolo 22.1) scrivono comunque un valore concreto per queste feature in ogni frase generata (mai "non registrato", perché a quel punto della pipeline il valore è già stato imputato, non è più `NaN`) — un lettore del testo generato, umano o modello linguistico, non ha modo di distinguere una `thalassemia: normal` osservata da una imputata per il 53% delle volte. Punto di forte interesse per Parte VI, Parte VII (formula dell'imputazione) e soprattutto Parte XI (assunzioni fragili sui dati).

## 7quinquies. Il rapporto parametri/campioni si inverte fra i due dataset, e due file di embedding sono esclusi da git per dimensione

**[Fatto]** Il pool di embedding post-SMOTENC ha dimensioni molto diverse fra i due dataset: **814 righe per Heart Disease**, **28.428 righe per Diabetes130** (verificato caricando `bioclinicalbert_embeddings.npy` per entrambi, comando eseguito in questa sessione). Con `StratifiedKFold(n_splits=5)`, il training set di ciascun fold è quindi di circa **651 righe per Heart Disease** e circa **22.743 righe per Diabetes130**.

**[Fatto]** Per i modelli a 1024 dimensioni (gte-large, e5-large — verificato via Ollama, §5), il rapporto fra dimensione dell'embedding e dimensione del training set per fold è **1.57 per Heart Disease** (1024 dimensioni, ~651 esempi: più parametri che esempi) e **0.045 per Diabetes130** (1024 dimensioni, ~22.743 esempi: nessun problema). Per Heart Disease, in altre parole, il classificatore `LogisticRegression` più grande ha letteralmente più pesi da stimare che esempi su cui stimarli in ciascun fold — un regime statisticamente delicato (`p > n`), mitigato solo dalla regolarizzazione L2 di default (`C=1.0`, §7bis) mai esplicitamente validata per questo scopo.

**[Fatto]** `datas/diabetes130/embeddings/e5_large_embeddings.npy` e `gte_large_embeddings.npy` **non esistono**, né su disco in questo ambiente né in git — verificato con un controllo diretto di esistenza file. **[Fatto]** `.gitignore:12-13` li esclude esplicitamente per nome. **[Inferenza]** Con 28.428 righe × 1024 dimensioni × 4 byte (float32), ciascuno di questi due file peserebbe circa **111 MB** — sopra il limite di 100 MB per file imposto da GitHub (motivazione coerente con la dimensione osservata di 87.3 MB per il file analogo a 768 dimensioni di `bioclinicalbert`, riportata nel diff del commit `c870bd7`, §branch chatbot). Le stesse coppie di modelli per Heart Disease (814 righe) restano invece tracciate senza problemi, essendo circa 200 volte più piccole. **Conseguenza pratica:** i risultati per e5-large/gte-large su Diabetes130 (già presenti in `datas/diabetes130/results/`) provengono da embedding che, oggi, non sono più recuperabili dal repository stesso — solo rieseguendo la fase di embedding li si potrebbe rigenerare.

## 8. Zone d'ombra aperte finora (elenco vivo, confluirà in appendice)

1. A cosa serve `ucimlrepo` in `requirements.txt` se non risulta importata in nessun file letto finora? Possibile residuo di una versione precedente dello script di download dati.
2. Il branch `chatbot` usa un simbolo `EMBEDDING_MODEL` assente dalla versione di `function.py` su `master`: quale modello (tra i 7) alimenta l'inferenza conversazionale dal vivo? Richiede lettura della versione di `function.py` sul branch `chatbot`.
3. ~~Le dimensioni esatte degli embedding per gte-base, gte-large, e5-large, pubmedbert, sentence-biobert~~ — **risolto**: verificate direttamente sui file (768 per e5-base/gte-base/bioclinicalbert/pubmedbert/sentence-biobert, 1024 per gte-large/e5-large).
4. Perché il report generato contiene affermazioni narrative fisse non derivate dai dati (vedi punto 3 delle scoperte critiche)? Non è chiaro se si tratti di codice incompleto (funzionalità futura non implementata) o di una scelta consapevole per un primo prototipo di report.
4bis. La cifra "297" in `docs/DATASET.md:17`/`README.md:78` per Heart Disease è un refuso ereditato dalla letteratura, un dataset precedente poi ampliato a 4 centri senza aggiornare la documentazione, o un'altra causa? (Il codice attuale carica in modo verificabile 920 righe, non 297 — vedi §7bis.)
4ter. Il comando `ollama pull yxchia/multilingual-e5-base` in `README.md:104` è un refuso di battitura, o il residuo di una versione precedente del progetto che usava davvero quel modello prima di passare a `jeffh/intfloat-e5-base-v2:q8_0` in `function.py:39`? (vedi §7ter)
5. ~~Rieseguire la pipeline o usare i risultati già tracciati per la Parte IX~~ — **risolto dall'utente (2026-09-05): usare i risultati già tracciati in `datas/`.**

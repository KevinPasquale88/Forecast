# Capitolo 39 — Iperparametri del progetto: valori e razionale

**Obiettivi del capitolo**

- Avere in un solo posto ogni iperparametro del progetto, esplicito o implicito, con il suo valore e la sua posizione nel codice.
- Sapere quali di questi valori sono stati scelti deliberatamente e quali sono semplicemente il default di una libreria, mai messo in discussione.
- Avere una mappa completa dei semi casuali usati, per capire esattamente cosa "riproducibile" significa in questo progetto.

## 39.1 Tabella completa

**[Fatto]** Ogni riga di questa tabella è stata verificata leggendo il codice sorgente citato; nessuna deduce un valore dal nome della libreria.

| Iperparametro | Valore | Dove | Esplorato nel progetto? |
|---|---|---|---|
| `max_iter` (LogisticRegression) | 2.000 | `classification.py:16` | Esplicito, mai variato |
| `C` (LogisticRegression, forza di regolarizzazione L2) | 1.0 (default scikit-learn) | mai specificato, `classification.py:16` | **Mai reso esplicito né esplorato** (capitolo 32.2) |
| `penalty`/`solver` (LogisticRegression) | `'l2'`/`'lbfgs'` (default) | mai specificato | Mai esplorato |
| `n_splits` (StratifiedKFold) | 5 | `classification.py:15` | Fisso, mai variato |
| `random_state` (StratifiedKFold) | 42 | `classification.py:15` | — |
| `test_size` (split iniziale, usato dalla valutazione holdout) | 0.2 | `preprocessing.py:52` | — |
| `test_size` (fetta di calibrazione della soglia) | 0.2 | `classification.py:34`, `holdout_evaluation.py:60` | Introdotto dal fix anti-leakage (capitolo 23.2), mai variato |
| `MISSING_INDICATOR_THRESHOLD` (soglia indicatori di mancanza) | 0.30 | `preprocessing.py:24` | Motivato da un commento nel codice (colonne oltre soglia in entrambi i dataset), non da un'analisi di sensibilità |
| `sample_size` (campionamento Diabetes130) | 20.000 | `function.py:116` | Motivato da tempi di esecuzione (`docs/DATASET.md:78`), non da un'analisi di sensibilità |
| `random_state` (SMOTENC) | 42 | `preprocessing.py:164` | — |
| `batch_size` (embedding Ollama) | 16 | `embedding.py:118` | Mai variato |
| `max_retries`/`retry_delay` (embedding Ollama) | 5 / 2.0 s | `embedding.py:119` | — |
| `inter_batch_delay` | 0.3 s | `embedding.py:119` | — |
| `max_workers` (ThreadPoolExecutor) | 3 | `embedding.py:201` | Mai motivato esplicitamente nel codice |
| Permessi del semaforo Ollama | 1 | `embedding.py:116` | Motivato da un commento nel codice (capitolo 12.2) |
| `n_iter` (bootstrap) | 10.000 | `evaluation.py:62` | Motivato in `docs/STATISTICAL_TESTS.md:9` (capitolo 36.3) |
| `alpha` (livello di confidenza) | 0.95 | `evaluation.py:77` | Convenzione standard, non discussa |
| Soglia di significatività | 0.05 | `statisticaltest.py:72,85,142` (e su `p_value_bh` in `statisticaltest.py:35`) | Convenzione standard; dal fix di revisione è affiancata dalla correzione Benjamini-Hochberg |
| `n_components` (UMAP) | 2 | `function.py:247` | Necessario per la visualizzazione 2D |
| Altri iperparametri UMAP (vicini, distanza minima) | Default della libreria | non specificati | Mai esplorati (capitolo 38.2) |

## 39.2 Effetto di valori alternativi

**[Interpretazione]** Tre di questi valori meritano una riflessione su cosa cambierebbe con un'alternativa, perché sono scelte con un impatto potenzialmente sostanziale sui risultati riportati:

**`C` (regolarizzazione).** Un valore di `C` più basso di 1.0 aumenterebbe la penalizzazione L2 (Formula 32.2), spingendo i pesi $\mathbf{w}$ verso valori più piccoli — un effetto particolarmente rilevante per Heart Disease, dove il capitolo 32.3 ha già mostrato che alcuni modelli hanno più parametri che esempi di training per fold: una regolarizzazione più forte in quel regime tenderebbe a ridurre l'overfitting (capitolo 2.3), potenzialmente migliorando la generalizzazione reale anche se il punteggio di validazione (già mostrato al capitolo 33.1 come non pienamente indipendente) potesse apparire leggermente più basso. Nessuna prova in questo progetto conferma o smentisce questa ipotesi: il valore non è mai stato variato.

**`n_splits` (numero di fold).** Un valore più alto di 5 (per esempio 10) userebbe più dati per l'addestramento in ciascun fold (una frazione $\frac{k-1}{k}$ più vicina a 1) a scapito di fold di validazione più piccoli e quindi di stime di metrica più rumorose per singolo fold — un compromesso classico nella scelta di $k$, mai discusso esplicitamente nella documentazione del progetto.

**Soglia di significatività 0.05.** Con $B=10.000$ osservazioni bootstrap (capitolo 37.2), quasi ogni confronto fra modelli risulta "significativo" a questa soglia convenzionale, e il progetto esegue $\binom{7}{2}=21$ confronti per metrica (capitolo 26.1). **[Fatto]** Per questo, dal fix di revisione (`docs/CHANGES.md` §7), il progetto applica la correzione di Benjamini-Hochberg (capitolo 26.2bis): ogni CSV di confronto riporta sia il p-value grezzo sia `p_value_bh`/`significant_bh`, così la lettura corretta per confronti multipli è disponibile accanto a quella grezza. Un lettore della tesi dovrebbe citare, di regola, le colonne corrette.

## 39.3 Riproducibilità: la mappa completa dei semi casuali nel progetto

**[Fatto]** Il valore `42` — una scelta convenzionale nella comunità del machine learning, senza alcun significato matematico speciale — ricorre in **otto punti indipendenti** del codice: `train_test_split` (`preprocessing.py:52`), `SMOTENC` (`preprocessing.py:164`), `UMAP` (`function.py:247`), il campionamento di Diabetes130 (`function.py:127`), `StratifiedKFold` (`classification.py:15`), lo split di calibrazione della soglia (`classification.py:34`), il bootstrap (`evaluation.py:62`, come `seed=42`, non come `random_state`), e lo split fit/calibrazione della valutazione holdout (`holdout_evaluation.py:60`). **[Interpretazione]** Nessuno di questi otto punti condivide un generatore di numeri casuali con gli altri: sono otto semi indipendenti, ciascuno con lo stesso valore numerico per convenzione, non un'unica fonte di casualità centralizzata. Questo garantisce che *ciascuna* di queste operazioni sia riproducibile isolatamente (rieseguire la pipeline oggi produce lo stesso split, lo stesso bilanciamento sintetico, la stessa suddivisione in fold), ma non esiste, in nessun file del progetto, una singola costante condivisa (per esempio `RANDOM_SEED = 42` importata ovunque): il valore è scritto letteralmente otto volte, in cinque file diversi.

> **ATTENZIONE —** questo significa che cambiare la riproducibilità del progetto — per esempio, per eseguire più run indipendenti con semi diversi e misurare la variabilità dovuta al solo seme casuale — richiederebbe modificare otto righe in cinque file diversi, non una singola costante. È un piccolo ma reale costo di manutenzione, coerente con l'assenza di un file di configurazione centralizzato già notata al capitolo 19.1.

## Riepilogo

Il progetto ha una ventina di iperparametri, distribuiti fra scelte esplicite motivate (il numero di iterazioni bootstrap, la dimensione del campione di Diabetes130, la soglia degli indicatori di mancanza, la fetta di calibrazione della soglia) e default di libreria mai messi in discussione (la forza di regolarizzazione `C`, gli iperparametri di UMAP). La correzione per confronti multipli, un tempo assente, è oggi applicata con Benjamini-Hochberg. Il seme casuale 42 ricorre in otto punti indipendenti del codice, garantendo riproducibilità locale per ciascuna operazione ma senza una gestione centralizzata.

## Domande di autoverifica

**1. Perché `C=1.0` è, di fatto, un iperparametro del progetto quanto `max_iter=2000`, anche se solo il secondo compare esplicitamente nel codice?**
Perché entrambi determinano il comportamento dell'ottimizzazione della regressione logistica (Formula 32.2): `C` semplicemente assume il valore di default della libreria invece di un valore scelto consapevolmente, ma quel default è comunque il valore effettivamente usato in ogni addestramento del progetto.

**2. Perché una regolarizzazione più forte (un valore di `C` più basso) potrebbe essere particolarmente rilevante per Heart Disease rispetto a Diabetes130?**
Perché Heart Disease ha un rapporto dimensione-embedding/dimensione-training-set sfavorevole per i modelli più grandi (fino a 1.57, capitolo 32.3), un regime in cui l'overfitting è un rischio concreto e una regolarizzazione più forte potrebbe aiutare la generalizzazione — mentre Diabetes130, con un pool molto più ampio, è già in un regime sicuro indipendentemente da questa scelta.

**3. Il seme casuale 42 usato in otto punti diversi del progetto proviene da un'unica costante condivisa?**
No: è scritto letteralmente otto volte, in file diversi (`preprocessing.py`, `function.py`, `classification.py`, `evaluation.py`, `holdout_evaluation.py`), senza alcuna costante centralizzata che lo definisca una sola volta — una conseguenza dell'assenza di un file di configurazione unico già discussa al capitolo 19.1.

> **MATERIALE PER LA TESI**
> 1. La tabella completa degli iperparametri (§39.1) — riusabile integralmente in "Materiali e metodi" o in un'appendice della tesi dedicata alla riproducibilità sperimentale.
> 2. L'analisi dell'effetto ipotetico di valori alternativi per `C` e `n_splits`, insieme alla correzione Benjamini-Hochberg oggi applicata ai 21 confronti per metrica — riusabile nella sezione "Discussione e limiti" e come direzione concreta per lavori futuri (Parte XII).
> 3. La mappa degli otto semi casuali indipendenti, con l'osservazione sulla loro mancata centralizzazione — riusabile come nota tecnica sulla manutenibilità, in una sezione che discuta la qualità del codice.

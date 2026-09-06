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
| `test_size` (split iniziale, mai usato a valle) | 0.2 | `preprocessing.py:43` | — |
| `sample_size` (campionamento Diabetes130) | 20.000 | `function.py:116` | Motivato da tempi di esecuzione (`docs/DATASET.md:78`), non da un'analisi di sensibilità |
| `random_state` (SMOTENC) | 42 | `preprocessing.py:90` | — |
| `batch_size` (embedding Ollama) | 16 | `embedding.py:103` | Mai variato |
| `max_retries`/`retry_delay` (embedding Ollama) | 5 / 2.0 s | `embedding.py:104` | — |
| `inter_batch_delay` | 0.3 s | `embedding.py:104` | — |
| `max_workers` (ThreadPoolExecutor) | 3 | `embedding.py:201` | Mai motivato esplicitamente nel codice |
| Permessi del semaforo Ollama | 1 | `embedding.py:101` | Motivato da un commento nel codice (capitolo 12.2) |
| `n_iter` (bootstrap) | 10.000 | `evaluation.py:62` | Motivato in `docs/STATISTICAL_TESTS.md:9` (capitolo 36.3) |
| `alpha` (livello di confidenza) | 0.95 | `evaluation.py:77` | Convenzione standard, non discussa |
| Soglia di significatività | 0.05 | `statisticaltest.py:44,57,112` | Convenzione standard, non discussa |
| `n_components` (UMAP) | 2 | `function.py:224` | Necessario per la visualizzazione 2D |
| Altri iperparametri UMAP (vicini, distanza minima) | Default della libreria | non specificati | Mai esplorati (capitolo 38.2) |

## 39.2 Effetto di valori alternativi

**[Interpretazione]** Tre di questi valori meritano una riflessione su cosa cambierebbe con un'alternativa, perché sono scelte con un impatto potenzialmente sostanziale sui risultati riportati:

**`C` (regolarizzazione).** Un valore di `C` più basso di 1.0 aumenterebbe la penalizzazione L2 (Formula 32.2), spingendo i pesi $\mathbf{w}$ verso valori più piccoli — un effetto particolarmente rilevante per Heart Disease, dove il capitolo 32.3 ha già mostrato che alcuni modelli hanno più parametri che esempi di training per fold: una regolarizzazione più forte in quel regime tenderebbe a ridurre l'overfitting (capitolo 2.3), potenzialmente migliorando la generalizzazione reale anche se il punteggio di validazione (già mostrato al capitolo 33.1 come non pienamente indipendente) potesse apparire leggermente più basso. Nessuna prova in questo progetto conferma o smentisce questa ipotesi: il valore non è mai stato variato.

**`n_splits` (numero di fold).** Un valore più alto di 5 (per esempio 10) userebbe più dati per l'addestramento in ciascun fold (una frazione $\frac{k-1}{k}$ più vicina a 1) a scapito di fold di validazione più piccoli e quindi di stime di metrica più rumorose per singolo fold — un compromesso classico nella scelta di $k$, mai discusso esplicitamente nella documentazione del progetto.

**Soglia di significatività 0.05.** Con $B=10.000$ osservazioni bootstrap (capitolo 37.2), quasi ogni confronto fra modelli risulta "significativo" a questa soglia convenzionale — un valore più stringente (per esempio 0.01, o una correzione per confronti multipli come Bonferroni, applicabile dato che il progetto esegue $\binom{7}{2}=21$ confronti per metrica, capitolo 26.1) cambierebbe sostanzialmente quante delle "differenze significative" riportate nei capitoli 44-45 resterebbero tali. **[Da verificare]** Il progetto non applica alcuna correzione per confronti multipli: se questo sia un'omissione o una scelta consapevole (motivata, per esempio, dal fatto che i test servono più a descrivere i dati che a supportare un singolo test di ipotesi decisivo) resta una domanda aperta per l'Appendice E.

## 39.3 Riproducibilità: la mappa completa dei semi casuali nel progetto

**[Fatto]** Il valore `42` — una scelta convenzionale nella comunità del machine learning, senza alcun significato matematico speciale — ricorre in **sei punti indipendenti** del codice: `train_test_split` (`preprocessing.py:43`), `SMOTENC` (`preprocessing.py:90`), `UMAP` (`function.py:224`), il campionamento di Diabetes130 (`function.py:127`), `StratifiedKFold` (`classification.py:15`), e il bootstrap (`evaluation.py:62`, come `seed=42`, non come `random_state`). **[Interpretazione]** Nessuno di questi sei punti condivide un generatore di numeri casuali con gli altri: sono sei semi indipendenti, ciascuno con lo stesso valore numerico per convenzione, non un'unica fonte di casualità centralizzata. Questo garantisce che *ciascuna* di queste sei operazioni sia riproducibile isolatamente (rieseguire la pipeline oggi produce lo stesso split, lo stesso bilanciamento sintetico, la stessa suddivisione in fold), ma non esiste, in nessun file del progetto, una singola costante condivisa (per esempio `RANDOM_SEED = 42` importata ovunque): il valore è scritto letteralmente sei volte, in sei posti diversi.

> **ATTENZIONE —** questo significa che cambiare la riproducibilità del progetto — per esempio, per eseguire più run indipendenti con semi diversi e misurare la variabilità dovuta al solo seme casuale — richiederebbe modificare sei righe in quattro file diversi, non una singola costante. È un piccolo ma reale costo di manutenzione, coerente con l'assenza di un file di configurazione centralizzato già notata al capitolo 19.1.

## Riepilogo

Il progetto ha una ventina di iperparametri, distribuiti fra scelte esplicite motivate (il numero di iterazioni bootstrap, la dimensione del campione di Diabetes130) e default di libreria mai messi in discussione (la forza di regolarizzazione `C`, gli iperparametri di UMAP, l'assenza di correzione per confronti multipli). Il seme casuale 42 ricorre in sei punti indipendenti del codice, garantendo riproducibilità locale per ciascuna operazione ma senza una gestione centralizzata.

## Domande di autoverifica

**1. Perché `C=1.0` è, di fatto, un iperparametro del progetto quanto `max_iter=2000`, anche se solo il secondo compare esplicitamente nel codice?**
Perché entrambi determinano il comportamento dell'ottimizzazione della regressione logistica (Formula 32.2): `C` semplicemente assume il valore di default della libreria invece di un valore scelto consapevolmente, ma quel default è comunque il valore effettivamente usato in ogni addestramento del progetto.

**2. Perché una regolarizzazione più forte (un valore di `C` più basso) potrebbe essere particolarmente rilevante per Heart Disease rispetto a Diabetes130?**
Perché Heart Disease ha un rapporto dimensione-embedding/dimensione-training-set sfavorevole per i modelli più grandi (fino a 1.57, capitolo 32.3), un regime in cui l'overfitting è un rischio concreto e una regolarizzazione più forte potrebbe aiutare la generalizzazione — mentre Diabetes130, con un pool molto più ampio, è già in un regime sicuro indipendentemente da questa scelta.

**3. Il seme casuale 42 usato in sei punti diversi del progetto proviene da un'unica costante condivisa?**
No: è scritto letteralmente sei volte, in file diversi (`preprocessing.py`, `function.py`, `classification.py`, `evaluation.py`), senza alcuna costante centralizzata che lo definisca una sola volta — una conseguenza dell'assenza di un file di configurazione unico già discussa al capitolo 19.1.

> **MATERIALE PER LA TESI**
> 1. La tabella completa degli iperparametri (§39.1) — riusabile integralmente in "Materiali e metodi" o in un'appendice della tesi dedicata alla riproducibilità sperimentale.
> 2. L'analisi dell'effetto ipotetico di valori alternativi per `C`, `n_splits` e la soglia di significatività, con la proposta esplicita di correzione per confronti multipli — riusabile nella sezione "Discussione e limiti" e come direzione concreta per lavori futuri (Parte XII).
> 3. La mappa dei sei semi casuali indipendenti, con l'osservazione sulla loro mancata centralizzazione — riusabile come nota tecnica sulla manutenibilità, in una sezione che discuta la qualità del codice.

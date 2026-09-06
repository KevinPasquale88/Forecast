# Capitolo 24 — `evaluation.py`: bootstrap e grafici

**Obiettivi del capitolo**

- Leggere l'intera implementazione del bootstrap del progetto: sono quindici righe, non di più.
- Sapere leggere un intervallo di confidenza percentile, con la formula che lo produce.
- Vedere come i dati raccolti per sette modelli confluiscono in sei grafici diversi.

**[Fatto]** `evaluation.py` (83 righe) è la fase 4 (`main.py:43`): rilegge i risultati salvati da `classification.py`, li arricchisce con un bootstrap di 10.000 iterazioni, e produce la maggior parte dei grafici comparativi del progetto.

## 24.1 Il bootstrap in poche righe

**[Fatto]** L'intera logica del bootstrap sta in `bootstrap_metrics()` (righe 62-75):
```python
def bootstrap_metrics(y_true, y_score, y_pred, n_iter=10000, seed=42):
    rng = np.random.default_rng(seed)
    acc_list, f1_list, auc_list = [], [], []
    for _ in range(n_iter):
        idx = rng.integers(0, len(y_true), len(y_true))
        yt, yp, ys = y_true[idx], y_pred[idx], y_score[idx]
        acc_list.append(accuracy_score(yt, yp))
        f1_list.append(f1_score(yt, yp, average="macro"))
        auc_list.append(roc_auc_score(yt, ys))
    return {"acc": np.array(acc_list), "f1": np.array(f1_list), "auc": np.array(auc_list)}
```
**[Livello: teoria consolidata del settore]** L'idea del bootstrap è ricampionare *con reinserimento* dallo stesso insieme di predizioni già ottenuto — `rng.integers(0, len(y_true), len(y_true))` genera tanti indici casuali (con possibili ripetizioni) quanti sono i record originali — e ricalcolare la metrica su ciascun ricampionamento. Il risultato non è un singolo numero ma una **distribuzione** di 10.000 valori della stessa metrica: se il modello fosse instabile (piccole variazioni nei dati che cambiano molto il punteggio), questa distribuzione sarebbe ampia; se fosse stabile, sarebbe stretta. Nota che il bootstrap qui lavora sulle predizioni **già fatte** (`y_true`, `y_score`, `y_pred` salvate da `classification.py`), non riallena il modello 10.000 volte — sarebbe computazionalmente proibitivo, e non è quello che questo bootstrap misura: misura l'incertezza della *stima della metrica*, non l'incertezza dell'addestramento.

**[Fatto]** `rng = np.random.default_rng(seed)` (riga 63) è l'idioma moderno di NumPy per la generazione di numeri casuali — un generatore locale legato esplicitamente a un seme, invece della vecchia interfaccia globale `np.random.seed(...)` seguita da chiamate a `np.random.randint(...)`. La differenza pratica: due chiamate indipendenti a `bootstrap_metrics()` con lo stesso `seed` producono sempre la stessa sequenza di ricampionamenti, senza che uno stato globale condiviso (capitolo 8.3) possa essere alterato da qualche altra parte del codice nel frattempo.

## 24.2 Intervalli di confidenza: come si leggono i grafici

**[Fatto]** `ci()` (righe 77-81) trasforma le 10.000 osservazioni bootstrap in un intervallo leggibile:
```python
def ci(a, alpha=0.95):
    low = np.percentile(a, (1-alpha)/2 * 100)
    high = np.percentile(a, (1+alpha)/2 * 100)
    mean = a.mean()
    return mean, (low, high)
```
Con `alpha=0.95`, `(1-alpha)/2 * 100 = 2.5` e `(1+alpha)/2 * 100 = 97.5`: l'intervallo di confidenza al 95% è, semplicemente, l'intervallo fra il 2.5° e il 97.5° percentile della distribuzione bootstrap — il **metodo percentile**, il più semplice dei diversi modi di costruire un intervallo di confidenza bootstrap, e quello che questo progetto usa. Leggilo così: "il 95% dei 10.000 ricampionamenti ha prodotto un valore di questa metrica compreso in questo intervallo" — non una dichiarazione probabilistica sul valore vero e sconosciuto della metrica, ma sulla variabilità osservata nel ricampionamento.

**[Fatto]** `evaluate_results()` (righe 7-59), la funzione orchestratrice, chiama `bootstrap_metrics()` e `ci()` per ciascuno dei sette modelli, poi passa i risultati a `plot_mean_ci()` (`function.py:302-336`, righe 55 di questo file): il grafico che ne risulta mostra, per ciascun modello, un punto (la media) con due tipi di barra d'errore sovrapposte — quella sottile per l'intervallo di confidenza al 95%, quella spessa per ±1 deviazione standard (`bootstrap_metrics_dict['acc'].std()`, riga 37). Sono due informazioni diverse disegnate insieme: l'intervallo di confidenza dice quanto sei sicuro della stima della media; la deviazione standard dice quanto è dispersa la distribuzione dei singoli ricampionamenti.

## 24.3 Dal dizionario Python al PNG/PDF

**[Fatto]** `evaluate_results()` produce, in un solo passaggio sui sette modelli, i dati per sei grafici distinti: la matrice di confusione per modello (`plot_confusion`, riga 19), il confronto ROC unificato (`plot_roc_comparison`, riga 51, con i dati di tutti i modelli raccolti in `roc_data` durante il ciclo), il boxplot delle distribuzioni bootstrap (`plot_boxplots`, riga 50), il confronto per famiglia (`plot_family_comparison`, riga 52), e infine il grafico media±CI appena visto. Ogni funzione di plotting riceve dati già pronti — mai un DataFrame grezzo da ricalcolare — ed è quindi, in linea di principio, testabile passandole dati sintetici senza rieseguire l'intera pipeline (un punto ripreso al capitolo 49).

> **RIFERIMENTO AL CODICE —** `encoder_comparison_summary.csv` (riga 56) è il file riassuntivo definitivo di questa fase — una riga per modello, con media, deviazione standard e intervallo di confidenza per ciascuna delle tre metriche. È il file che `generatereport.py` (capitolo 27) rilegge per intero per costruire la tabella principale del report finale.

## Interfaccia pubblica

| Funzione | Parametri | Ritorna |
|---|---|---|
| `evaluate_results(dataset="heart_disease")` | Nome dataset | Nessuno (side-effect: grafici + CSV) |
| `bootstrap_metrics(y_true, y_score, y_pred, n_iter=10000, seed=42)` | Predizioni di un modello | Dizionario di 3 array da 10.000 valori |
| `ci(a, alpha=0.95)` | Array di valori bootstrap | `(media, (basso, alto))` |

## Errori tipici

Un `FileNotFoundError` su un file `_y_true.npy` in questa fase segnala che `classification.py` non ha completato con successo per quel modello (capitolo 18.3). Un tempo di esecuzione molto più lungo del previsto per questa fase, su Diabetes130 rispetto a Heart Disease, è atteso: il bootstrap ricampiona un numero di righe proporzionale alla dimensione del dataset di validazione, non fisso.

## Riepilogo

`evaluation.py` implementa il bootstrap dell'intero progetto in poche righe di NumPy puro, ricampionando con reinserimento le predizioni già ottenute, non riallenando il modello. L'intervallo di confidenza al 95% è il metodo percentile, il più semplice fra le tecniche bootstrap esistenti. Il file produce sei grafici diversi e il CSV riassuntivo che alimenta direttamente il report finale.

## Domande di autoverifica

**1. Perché il bootstrap di questo progetto non riallena il modello 10.000 volte?**
Perché misura l'incertezza della stima della metrica sulle predizioni già ottenute, non l'incertezza dell'addestramento: ricampiona con reinserimento le coppie (etichetta vera, predizione, punteggio) già calcolate da `classification.py`, un'operazione computazionalmente molto più economica di un nuovo addestramento per ciascuna delle 10.000 iterazioni.

**2. Cosa significa, con precisione, un intervallo di confidenza bootstrap al 95% costruito con il metodo percentile?**
Che il 95% dei 10.000 valori della metrica ricampionati cade fra il 2.5° e il 97.5° percentile della distribuzione osservata — una descrizione della variabilità del ricampionamento, non una dichiarazione probabilistica diretta sul valore vero e sconosciuto della metrica.

**3. Perché la barra d'errore sottile e quella spessa nel grafico media±CI non mostrano la stessa informazione?**
Perché la sottile rappresenta l'intervallo di confidenza al 95% (quanto è incerta la stima della media), mentre la spessa rappresenta ±1 deviazione standard (quanto è dispersa l'intera distribuzione bootstrap) — due misure di variabilità diverse, disegnate insieme sullo stesso grafico.

> **MATERIALE PER LA TESI**
> 1. La spiegazione formale del bootstrap con la formula dell'intervallo di confidenza percentile, affiancata al codice — riusabile in "Materiali e metodi", sezione sulla metodologia di valutazione.
> 2. La precisazione sull'interpretazione corretta dell'intervallo di confidenza bootstrap (non una probabilità sul valore vero) — riusabile come nota metodologica per prevenire un fraintendimento statistico comune nella tesi.
> 3. L'elenco dei sei grafici prodotti da questa fase, con la funzione di `function.py` responsabile di ciascuno — riusabile come indice delle figure disponibili per la sezione "Risultati".

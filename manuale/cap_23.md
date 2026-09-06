# Capitolo 23 — `classification.py`: addestrare e validare

**Obiettivi del capitolo**

- Leggere per intero il ciclo che addestra e valuta un modello per ciascuno dei sette embedding.
- Capire esattamente come viene scelta la soglia di decisione, e perché è il punto più delicato di questo file.
- Sapere cosa viene salvato su disco al termine di questa fase, e da quali capitoli successivi verrà riletto.

**[Fatto]** `classification.py` (79 righe) è la fase 3 (`main.py:40`), il file più corto della pipeline principale ma quello che contiene la decisione metodologicamente più delicata dell'intero progetto (capitolo 23.2).

## 23.1 `StratifiedKFold` e perché "stratified" conta

**[Fatto]** `training_classifier()` (righe 9-80) itera su ciascuno dei sette modelli, ricarica i suoi embedding da disco (righe 13-14, il punto di ingresso del "passaggio via file" già visto al capitolo 17.1), e addestra un `LogisticRegression` con validazione a 5 fold:
```python
X = np.load(os.path.join(dirs["embeddings"], model['filename']), allow_pickle=True)
y = np.load(os.path.join(dirs["embeddings"], model['filename_label']), allow_pickle=True)
kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
logisticReg = LogisticRegression(max_iter=2000)
```
**[Livello: teoria consolidata del settore]** Un k-fold ordinario divide i dati in `k` parti uguali senza guardare l'etichetta: con un dataset sbilanciato (capitolo 4.2), questo rischia di produrre fold con proporzioni di classe molto diverse fra loro, o nel caso estremo un fold senza esemplari della classe minoritaria. Un k-fold **stratificato** garantisce che ogni fold mantenga, il più possibile, la stessa proporzione fra classi del dataset intero — esattamente ciò che serve quando, come per Diabetes130 (11.16% di classe positiva, capitolo 4.2), lo sbilanciamento è marcato.

**[Fatto]** Nota che `X` e `y`, qui, sono gli embedding **dopo SMOTENC** (capitolo 21.2) — non i dati originali sbilanciati. Lo `StratifiedKFold` opera quindi su un pool già artificialmente riequilibrato dal bilanciamento sintetico, non sulla distribuzione reale delle classi: un fatto da tenere presente quando si interpreta "quanto conta la stratificazione qui" — conta comunque, ma su un problema già reso più facile dal bilanciamento a monte.

## 23.2 La soglia F1-ottima per fold

**[Fatto]** Il cuore del ciclo (righe 22-46) allena il modello sul training fold, poi cerca la soglia migliore sul fold di validazione:
```python
for train_idx, val_idx in kf.split(X, y):
    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]
    logisticReg.fit(X_train, y_train)
    y_score = logisticReg.predict_proba(X_val)[:, 1]
    precision, recall, thresholds = precision_recall_curve(y_val, y_score)
    f1_scores = 2 * (precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-6)
    best_idx = f1_scores.argmax()
    tau = thresholds[best_idx]
    y_pred = (y_score >= tau).astype(int)
```
`precision_recall_curve()` restituisce precisione e recall per ogni soglia possibile, con un punto in più rispetto all'elenco delle soglie stesse (il punto finale, recall=0, non ha una soglia associata) — da cui il taglio `[:-1]` su precisione e recall prima di calcolare l'F1 per ciascuna soglia candidata. Il termine `+ 1e-6` al denominatore evita una divisione per zero se sia precisione sia recall fossero nulle per una soglia candidata. `best_idx = f1_scores.argmax()` sceglie la soglia che avrebbe massimizzato l'F1 su **questo stesso fold di validazione**.

> **ATTENZIONE —** questo è il punto esatto già anticipato al capitolo 2.3 e al capitolo 33: la soglia `tau` è scelta guardando `y_val` — le etichette vere del fold di validazione — e poi la stessa soglia viene usata per calcolare `y_pred` su cui, poche righe sotto, si misurano accuratezza e F1 riportati come prestazione del modello **su quello stesso fold**. Non è data leakage nel senso di informazione che raggiunge l'addestramento del modello (`logisticReg.fit()` vede solo `X_train`/`y_train`, mai il fold di validazione) — è un ottimismo più sottile, limitato alla sola scelta della soglia, che gonfia leggermente F1 e accuratezza rispetto a una soglia fissata a priori o scelta su un fold separato di calibrazione. Il capitolo 51 lo tratta con tutto il rigore critico che merita.

## 23.3 Cosa viene salvato e a cosa serve dopo

**[Fatto]** Oltre alle metriche medie sui 5 fold (righe 47-56, salvate nel dizionario globale `results`, capitolo 8.3 e capitolo 19.2), il codice concatena le predizioni di *tutti* i fold in quattro array (righe 61-68):
```python
all_val_idx = np.concatenate(all_val_idx)
np.save(os.path.join(dirs["results"], f"{model['model_name']}_y_true.npy"), all_y_true)
np.save(os.path.join(dirs["results"], f"{model['model_name']}_y_score.npy"), all_y_scores)
np.save(os.path.join(dirs["results"], f"{model['model_name']}_y_pred.npy"), all_y_preds)
np.save(os.path.join(dirs["results"], f"{model['model_name']}_val_idx.npy"), all_val_idx)
```
`all_val_idx` — gli indici di riga usati come validazione in ciascun fold, concatenati nell'ordine in cui i fold sono stati processati — è il file più importante per il capitolo 25: è il ponte che permette di ricondurre ogni previsione (giusta o sbagliata) al record originale in `X_train_raw.csv` (capitolo 21.3). Senza questo file, l'analisi degli errori del capitolo 25 non avrebbe modo di sapere *quale riga* del dataset originale corrisponde a ciascuna predizione salvata.

**[Fatto]** Perché questa concatenazione produca un risultato coerente — cioè perché l'elemento *i*-esimo di `all_y_true`, `all_y_score`, `all_y_pred` e `all_val_idx` si riferiscano davvero allo stesso record — è necessario che i quattro array vengano popolati nello stesso ordine, fold per fold, dentro lo stesso ciclo: **[Fatto]** verificato leggendo le righe 43-46, è esattamente così che il codice li costruisce, con un `append` per lista corrispondente ad ogni iterazione del ciclo prima della concatenazione finale.

## Interfaccia pubblica

| Funzione | Parametri | Effetti |
|---|---|---|
| `training_classifier(dataset="heart_disease")` | Nome dataset | Popola `results` (side-effect globale, capitolo 19.2); salva 4 file `.npy` per modello + `model_performance.csv`; genera il grafico di confronto metriche |

**[Fatto]** È l'unica funzione pubblica del file: le sette variabili locali del ciclo (`X`, `y`, `kf`, `logisticReg`, `tmp_results`, ecc.) esistono solo dentro `training_classifier()`, non sono richiamabili da altri moduli.

## Errori tipici

Un `IndexError` o una forma inattesa in `X[train_idx]` segnala quasi sempre un disallineamento fra il numero di righe di `X` (embedding) e di `y` (etichette) — capiterebbe se, per esempio, la generazione degli embedding (capitolo 22) fosse stata interrotta a metà per un modello e ripresa con un numero diverso di frasi. Un `f1_scores` interamente `NaN` o `0` per un intero fold segnalerebbe un fold senza esempi di una delle due classi — lo scenario che `StratifiedKFold` è pensato per evitare, e la cui comparsa indicherebbe un problema a monte nella stratificazione o nei dati stessi.

## Riepilogo

`classification.py` allena una regressione logistica separata per ciascuno dei sette modelli, con validazione a 5 fold stratificati sugli embedding già bilanciati da SMOTENC. La soglia di decisione è scelta, fold per fold, massimizzando F1 sulle etichette dello stesso fold di validazione su cui viene poi misurata la prestazione — un punto di attenzione metodologica reale. Gli indici di validazione salvati da questo file sono il collegamento indispensabile fra ogni previsione e il record clinico che l'ha generata.

## Domande di autoverifica

**1. Perché `StratifiedKFold`, e non un k-fold ordinario, è la scelta giusta per Diabetes130 in particolare?**
Perché Diabetes130 ha una classe positiva minoritaria (11.16%, capitolo 4.2): un k-fold ordinario rischierebbe di produrre fold con proporzioni di classe molto diverse dal dataset intero, o addirittura fold senza esempi della classe minoritaria — la stratificazione lo previene per costruzione.

**2. In che senso la scelta della soglia `tau` non è "data leakage" nel senso classico, ma resta comunque un problema?**
Perché il modello (`logisticReg.fit()`) non vede mai le etichette del fold di validazione durante l'addestramento — l'addestramento è pulito. Il problema riguarda solo la soglia: viene scelta massimizzando F1 sulle stesse etichette di validazione su cui poi si riporta la metrica, un ottimismo più contenuto ma reale.

**3. Perché `all_val_idx` è indispensabile per il capitolo 25 (analisi degli errori)?**
Perché è l'unico collegamento salvato fra una previsione (giusta o sbagliata) e la riga originale del dataset da cui proviene: senza questi indici, non ci sarebbe modo di sapere quale record clinico corrisponde a un falso positivo o falso negativo specifico.

> **MATERIALE PER LA TESI**
> 1. La spiegazione formale della soglia F1-ottima per fold, con l'osservazione critica sull'ottimismo che introduce — riusabile parola per parola nella sezione "Discussione e limiti", capitolo di riferimento 51.
> 2. La spiegazione di `StratifiedKFold` applicato dopo SMOTENC, con la precisazione che opera su un pool già bilanciato — riusabile in "Materiali e metodi" per descrivere con precisione il protocollo di validazione.
> 3. Lo schema del collegamento `val_idx` → record originale, con i quattro file salvati per modello — riusabile come base tecnica per la sezione che descrive la tracciabilità degli errori nella tesi.

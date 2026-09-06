# Capitolo 25 — `error_analysis.py`: dall'errore statistico al caso clinico

**Obiettivi del capitolo**

- Vedere come un indice numerico salvato da `classification.py` diventa un record clinico leggibile.
- Capire cosa significa, esattamente, un caso "più difficile" quando sette modelli diversi lo valutano.
- Leggere la formula della deviazione di feature e sapere cosa NON dice.

**[Fatto]** `error_analysis.py` (81 righe) è la fase 5 (`main.py:46`): l'unico file, oltre a `generatereport.py`, il cui scopo esplicito è tradurre risultati statistici in qualcosa di direttamente interpretabile su un caso clinico reale, non solo su un numero aggregato.

## 25.1 Ricostruire il record dall'indice di validazione

**[Fatto]** `analyze_errors()` (righe 6-81) inizia ricaricando `X_train_raw.csv` (capitolo 21.3) — la versione leggibile delle feature, salvata da `preprocessing.py` — e per ciascun modello usa `val_idx` (salvato da `classification.py`, capitolo 23.3) per riallineare le predizioni ai record originali:
```python
records = X_raw.iloc[val_idx].reset_index(drop=True).copy()
records["y_score"] = y_score
records[fp_mask].to_csv(os.path.join(dirs["results"], f"{name}_false_positives.csv"), index=False)
records[fn_mask].to_csv(os.path.join(dirs["results"], f"{name}_false_negatives.csv"), index=False)
```
`X_raw.iloc[val_idx]` seleziona, nell'ordine esatto in cui `classification.py` li aveva concatenati (capitolo 23.3), esattamente i record che sono stati usati come validazione in uno dei 5 fold di quel modello — non un campione casuale, ma la ricostruzione precisa e verificabile di quali righe hanno prodotto quale previsione. `fp_mask` e `fn_mask` (già visti al capitolo 4.3) selezionano poi, fra questi, rispettivamente i falsi positivi e i falsi negativi, salvati in due CSV separati per modello — 14 file in tutto, due per ciascuno dei sette modelli.

> **RIFERIMENTO AL CODICE —** questo meccanismo funziona solo perché `val_idx` è stato costruito, in `classification.py`, concatenando gli indici di validazione **nello stesso ordine** in cui `y_true`, `y_score` e `y_pred` sono stati concatenati (capitolo 23.3). Se uno solo di questi quattro array fosse stato costruito con un ordine diverso, `error_analysis.py` assocerebbe silenziosamente ogni previsione al record sbagliato — senza sollevare alcun errore, perché le dimensioni degli array rimarrebbero comunque compatibili.

## 25.2 "Hardest cases": cosa significa essere sbagliato da tutti i modelli

**[Fatto]** Il file accumula, per ciascun record del dataset originale, quante volte è stato valutato e quante volte è stato classificato male, sommando su tutti e sette i modelli (righe 12-13, 47-48):
```python
error_counts = np.zeros(n_records, dtype=int)
eval_counts = np.zeros(n_records, dtype=int)
...
eval_counts[val_idx] += 1
error_counts[val_idx] += error_mask.astype(int)
```
`error_counts[val_idx] += ...` è un'assegnazione con indicizzazione avanzata di NumPy: incrementa, in un solo passaggio, tutte le posizioni indicate da `val_idx` — non un ciclo esplicito su ogni indice, un'operazione vettoriale che in Java richiederebbe scrivere a mano un ciclo `for` sull'array. Dopo aver ripetuto questo accumulo per tutti e sette i modelli, `hardest_idx = np.argsort(-error_counts)[:20]` (riga 58) individua i 20 record con il maggior numero di errori totali — `-error_counts` inverte il segno per ottenere un ordinamento decrescente da una funzione, `argsort`, che di norma ordina in modo crescente.

**[Interpretazione]** Un record che compare fra gli "hardest cases" con, per esempio, 7 su 7 modelli sbagliati (il valore massimo possibile, dato che ogni record compare in validazione una sola volta per modello, nei fold della cross-validation) non è necessariamente un caso "ambiguo" nel senso clinico del termine: potrebbe esserlo, ma potrebbe anche essere un record sintetico generato da SMOTENC (capitolo 21.2) che si trova in una zona dello spazio delle feature poco rappresentata, o un errore di imputazione che ha reso il record atipico. Il file non distingue queste possibilità — le tabella soltanto, e resta a chi legge il report interpretarle correttamente, un punto che il capitolo 46 riprende con lo sguardo critico che merita.

## 25.3 Deviazione di feature: una standardizzazione con un'interpretazione clinica

**[Fatto]** L'ultima analisi del file confronta, per ciascuna feature numerica, la sua media nei casi sbagliati contro la sua media nei casi corretti, aggregando su tutti i modelli (righe 65-75):
```python
for feature in num_cols_used:
    pooled_std = pd.concat([df_error[feature], df_correct[feature]]).std()
    deviation = (df_error[feature].mean() - df_correct[feature].mean()) / pooled_std if pooled_std else 0.0
```

$$
d_{\text{feature}} = \frac{\bar{x}_{\text{errore}} - \bar{x}_{\text{corretto}}}{s_{\text{pooled}}} \tag{25.1}
$$

dove $\bar{x}_{\text{errore}}$ e $\bar{x}_{\text{corretto}}$ sono le medie della feature nei due gruppi (record classificati male, record classificati bene, aggregati su tutti i modelli), e $s_{\text{pooled}}$ è la deviazione standard calcolata sull'unione dei due gruppi (riga 71, `pd.concat([...]).std()`). **[Livello: teoria consolidata del settore]** Questa quantità è concettualmente imparentata alla *d* di Cohen, una misura standard di dimensione dell'effetto: divide la differenza fra due medie per una deviazione standard comune, così da poter confrontare fra loro feature misurate su scale del tutto diverse (anni di età contro mg/dl di colesterolo) — senza questa standardizzazione, una differenza di "5" per il colesterolo (scala di centinaia) e una differenza di "5" per l'età (scala di decine) non sarebbero minimamente comparabili.

> **ATTENZIONE —** questa deviazione descrive una differenza aggregata *su tutti i modelli insieme*, non su un modello specifico, e riguarda solo le feature **numeriche** (`num_cols_used`, capitolo 6.1) — le feature categoriali (sesso, tipo di dolore toracico, razza) non compaiono in questa analisi, anche se potrebbero essere altrettanto informative su cosa caratterizza un caso difficile. È un limite di copertura reale, non solo una scelta di semplicità: il capitolo 46 lo nota esplicitamente.

## Interfaccia pubblica

| Funzione | Parametri | Effetti |
|---|---|---|
| `analyze_errors(dataset="heart_disease")` | Nome dataset | Salva `error_summary.csv`, `hardest_cases.csv`, `feature_deviation.csv`, 14 CSV di FP/FN, 2 grafici |

## Errori tipici

Un `KeyError` su una colonna di `X_raw` in questa fase indica quasi sempre che `num_cols_used` (scelto in base al dataset, riga 8) non corrisponde alle colonne effettivamente presenti in `X_train_raw.csv` — capiterebbe se `preprocessing.py` fosse stato modificato senza aggiornare di conseguenza gli elenchi di `function.py`. Un `hardest_cases.csv` vuoto o con meno di 20 righe (riga 59, `error_counts[hardest_idx] > 0`) significherebbe che meno di 20 record sono mai stati classificati male da almeno un modello — un segnale, non un errore, di un problema insolitamente facile.

## Riepilogo

`error_analysis.py` usa gli indici di validazione salvati da `classification.py` per ricondurre ogni previsione al record clinico originale, aggregando su tutti e sette i modelli per individuare i casi più difficili e per misurare, con una statistica standardizzata simile alla *d* di Cohen, quali feature numeriche caratterizzano i casi sbagliati rispetto a quelli corretti — senza però coprire le feature categoriali, e senza distinguere un record realmente ambiguo da un artefatto del bilanciamento sintetico.

## Domande di autoverifica

**1. Perché `X_raw.iloc[val_idx]` funziona solo se `val_idx` è stato costruito nello stesso ordine di `y_true`/`y_score`/`y_pred` in `classification.py`?**
Perché l'associazione fra un record e la sua previsione si basa esclusivamente sulla posizione corrispondente nei quattro array: se l'ordine di costruzione divergesse anche per un solo array, ogni record verrebbe associato silenziosamente alla previsione sbagliata, senza che le dimensioni compatibili degli array segnalino nulla.

**2. Un record compare fra gli "hardest cases" con 7 errori su 7 modelli: cosa NON puoi concludere automaticamente da questo dato?**
Non puoi concludere che sia un caso clinicamente ambiguo in senso stretto: potrebbe essere un record sintetico generato da SMOTENC in una zona poco rappresentata dello spazio delle feature, o un artefatto di imputazione — il file registra la frequenza dell'errore, non ne diagnostica la causa.

**3. Perché la deviazione di feature (§25.3) permette di confrontare l'età e il colesterolo sulla stessa scala, pur avendo unità di misura diverse?**
Perché la differenza di medie viene divisa per una deviazione standard comune (pooled), calcolata sull'unione dei casi sbagliati e corretti — una standardizzazione concettualmente simile alla *d* di Cohen, che rende la quantità risultante adimensionale e quindi confrontabile fra feature diverse.

> **MATERIALE PER LA TESI**
> 1. La Formula 25.1 con la spiegazione di ogni simbolo e il collegamento alla *d* di Cohen — riusabile in "Materiali e metodi" per la sezione sull'analisi degli errori.
> 2. Il meccanismo di ricostruzione del record originale tramite `val_idx`, con l'avvertenza sulla sua fragilità silenziosa — riusabile come nota tecnica sulla tracciabilità, o come punto di attenzione nella sezione critica.
> 3. Il limite di copertura sulle sole feature numeriche, esplicitamente dichiarato — riusabile come voce autonoma nella sezione "Discussione e limiti" o come proposta di estensione nella Parte XII.

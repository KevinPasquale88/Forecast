# Capitolo 40 — Caso d'uso 1: `python main.py --dataset heart_disease` dall'inizio alla fine

**Obiettivi del capitolo**

- Seguire, con numeri reali verificati, come 920 righe di dati grezzi diventano un report finale.
- Vedere in una sola tabella come cambia la forma dei dati a ogni passaggio della pipeline.
- Sapere esattamente cosa trovare su disco al termine di un'esecuzione completa, e dove guardare per primo.

Questo capitolo non introduce concetti nuovi: mette in sequenza, con numeri concreti, tutto ciò che le Parti IV-VII hanno già spiegato separatamente.

## 40.1 Cosa succede fase per fase

**[Fatto]** Il comando `python main.py --dataset heart_disease` (o semplicemente `python main.py`, dato il default, capitolo 28.2) attraversa le otto fasi già viste al capitolo 17-18, in questo ordine, con questi numeri reali per questo dataset specifico:

1. **Pulizia** (`main.py:33-36`): i file di una precedente esecuzione su questo dataset vengono cancellati.
2. **Preprocessing** (`preprocessing.py`, capitolo 21): le 920 righe concatenate (capitolo 29.1) vengono divise 80/20 (736 righe di training, 184 di test), imputate con statistiche del solo training (con indicatori `ca_missing`/`slope_missing`/`thal_missing` per le colonne oltre il 30% di mancanza nel training), e il training bilanciato con SMOTENC; il test set è salvato su disco senza bilanciamento.
3. **Embedding** (`embedding.py`, capitolo 22): ciascuna delle righe bilanciate diventa una frase, poi un vettore, per ciascuno dei sette modelli — e lo stesso accade, separatamente, alle 184 righe del test set (file `*_test.npy`).
4. **Classificazione** (`classification.py`, capitolo 23): sette regressioni logistiche indipendenti, ciascuna validata con 5-fold stratificato e soglia calibrata su una fetta separata.
5. **Valutazione** (`evaluation.py`, capitolo 24): bootstrap a 10.000 iterazioni per ciascun modello, sei grafici comparativi.
6. **Analisi errori** (`error_analysis.py`, capitolo 25): ogni falso positivo e falso negativo ricondotto al record clinico originale.
7. **Test statistici** (`statisticaltest.py`, capitolo 26): 21 confronti a coppie per ciascuna delle tre metriche, più 21 confronti DeLong sull'AUC, con p-value grezzi e corretti Benjamini-Hochberg.
8. **Valutazione holdout** (`holdout_evaluation.py`, capitolo 43): un classificatore fresco per modello, valutato una sola volta sulle 184 righe di test mai viste.
9. **Report** (`generatereport.py`, capitolo 27): tutto assemblato in `report.md`.

## 40.2 Come cambiano i dati

**[Fatto]** Questa tabella traccia la forma esatta dei dati a ogni passaggio, con numeri verificati nelle Parti IV-VII di questo libro:

| Passaggio | Forma dei dati | Fonte del numero |
|---|---|---|
| Dati grezzi concatenati | 920 righe × 14 colonne (13 feature + target) | Capitolo 29.1 |
| Dopo split feature/target | `X`: 920×13, `y`: 920 | `preprocessing.py:48-50` |
| Dopo split 80/20 | `X_train`: 736×13, `X_test`: 184×13 (persistito per la fase holdout) | Capitolo 21.1, capitolo 33.1 |
| Dopo indicatori + imputazione | 736×16 (13 feature + `ca_missing`, `slope_missing`, `thal_missing`), nessun valore mancante | Capitolo 21.2, capitolo 31.1; header di `X_train_raw.csv` |
| Dopo SMOTENC | `X_train_bal`: **814×16** (classe minoritaria pareggiata) | Capitolo 4.2, verificato su `X_train_raw.csv` |
| Dopo conversione a testo | 814 stringhe (più 184 per il test set) | Capitolo 22.1 |
| Dopo embedding, per modello | 814×768 (5 modelli) o 814×1024 (2 modelli), più 184×768/1024 di test | Capitolo 32.3, tabella dimensioni |
| Per fold di classificazione | ~651 training (di cui ~130 di calibrazione), ~163 validazione | $814 \times \frac{4}{5}$ e $814 \times \frac{1}{5}$, capitolo 23.2 |
| Risultati concatenati, per modello | `y_true`/`y_score`/`y_pred`/`val_idx`: 814 ciascuno | Capitolo 23.3 |
| Bootstrap, per modello e metrica | 10.000 valori | Capitolo 36.1 |
| Confronti statistici | $\binom{7}{2}=21$ per metrica × 3 metriche + 21 DeLong | Capitolo 26.1, capitolo 37 |
| Valutazione holdout, per modello | 1 riga di metriche su 184 casi di test | `holdout_evaluation.csv`, capitolo 43 |

## 40.3 Cosa trovi su disco

**[Fatto]** Al termine, `datas/heart_disease/reports/report.md` (già presente nel repository, generato in un'esecuzione precedente al momento della scrittura di questo libro — capitolo 43 chiarisce la provenienza esatta di questi numeri) riporta, fra le altre cose, questa tabella riassuntiva:

| Modello | Accuracy | Macro-F1 | ROC-AUC |
|---|---|---|---|
| pubmedbert | **0.7936** | **0.7916** | **0.8909** |
| sentence-biobert | 0.7900 | 0.7874 | 0.8748 |
| gte-large | 0.7752 | 0.7727 | 0.8543 |
| gte-base | 0.7727 | 0.7718 | 0.8458 |
| bioclinicalbert | 0.7703 | 0.7669 | 0.8829 |
| e5-base | 0.7702 | 0.7679 | 0.8476 |
| e5-large | 0.7629 | 0.7594 | 0.8554 |

**[Fatto]** `pubmedbert` — un modello biomedico, non generalista — ha il valore medio più alto in tutte e tre le metriche di cross-validation, coerentemente con la seconda domanda di ricerca del progetto (capitolo 6.3). **[Fatto]** La sezione "Held-Out Test Set Evaluation" dello stesso report aggiunge la controprova sul 20% mai visto: sui 184 casi di test, il migliore è `bioclinicalbert` (accuracy 0.8424, macro-F1 0.8399, AUC 0.9193), e tutti e tre i biomedici superano tutti i generalisti in AUC. **[Attenzione]** Il capitolo 44 tratta questi stessi numeri con tutto il rigore statistico necessario (quali differenze sono davvero significative secondo i tre test, non solo quale valore è numericamente più alto): qui li vedi solo come tappa finale del percorso appena tracciato.

Oltre al report, cinque cartelle sotto `datas/heart_disease/` contengono ciascuna l'output di una o più fasi (capitolo 17.2): `preprocessing/` (5 file, inclusi `X_test_raw.csv` e `y_test.npy`), `embeddings/` (28 file, quattro per modello: embedding ed etichette per training e test), `results/` (oltre 80 file fra predizioni, bootstrap, CSV di confronto e `holdout_evaluation.csv`), `graphics/` (grafici UMAP, ROC, matrici di confusione), `reports/` (il solo `report.md`).

## Riepilogo

Un'esecuzione completa per Heart Disease trasforma 920 righe grezze in un report finale attraversando passaggi tracciabili con numeri precisi: 736 righe di training e 184 di test trattenute per la valutazione holdout, 814 righe dopo il bilanciamento sintetico, sette insiemi di embedding per il training più sette per il test, sette classificatori validati a 5 fold con soglia calibrata, 10.000 ricampionamenti bootstrap per metrica e modello, 21 confronti a coppie per tre test statistici diversi, e una valutazione finale sul test set mai visto. I modelli con le prestazioni migliori — `pubmedbert` in cross-validation, `bioclinicalbert` sull'holdout — sono entrambi biomedici, non generalisti: un primo indizio, da trattare con rigore statistico al capitolo 44, sulla seconda domanda di ricerca del progetto.

## Domande di autoverifica

**1. Delle 920 righe grezze di Heart Disease, quante contribuiscono agli embedding di training e quante alla valutazione holdout?**
814 righe (le 736 di training dopo il bilanciamento SMOTENC) alimentano gli embedding di training; le 184 righe del test set vengono embeddate separatamente (file `*_test.npy`) e usate una sola volta, dalla fase holdout, per la stima di generalizzazione. In una versione precedente del codice quelle 184 righe venivano calcolate e scartate.

**2. Perché il numero di righe usate per l'addestramento aumenta (da 736 a 814) invece di diminuire, nonostante nessun dato venga aggiunto dall'esterno?**
Perché SMOTENC genera record sintetici della classe minoritaria per pareggiarla alla classe maggioritaria (capitolo 21.2, capitolo 31.2): l'aumento di 78 righe (736→814) corrisponde esattamente alla differenza fra le due classi nel training set prima del bilanciamento.

**3. I modelli con le prestazioni migliori nel report per Heart Disease appartengono alla stessa famiglia?**
Sì, sono tutti biomedici: `pubmedbert` (famiglia `biomedical`) guida tutte e tre le metriche in cross-validation, e `bioclinicalbert` (stessa famiglia) è il migliore sulla valutazione holdout — nessuno dei quattro modelli generalisti compare al primo posto in nessuna metrica, né in validazione né sul test set.

> **MATERIALE PER LA TESI**
> 1. La tabella di trasformazione dei dati (§40.2), con ogni numero verificato e la fonte esatta — riusabile come diagramma di flusso quantitativo in "Materiali e metodi".
> 2. La tabella riassuntiva delle prestazioni reali per Heart Disease (§40.3) — riusabile direttamente nella sezione "Risultati", con il rimando al capitolo 44 per l'analisi statistica completa.
> 3. L'osservazione che i due modelli migliori sono entrambi biomedici — riusabile come prima evidenza descrittiva a supporto della seconda domanda di ricerca, da confermare statisticamente con i test del capitolo 44.

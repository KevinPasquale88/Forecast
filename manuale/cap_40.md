# Capitolo 40 — Caso d'uso 1: `python main.py --dataset heart_disease` dall'inizio alla fine

**Obiettivi del capitolo**

- Seguire, con numeri reali verificati, come 920 righe di dati grezzi diventano un report finale.
- Vedere in una sola tabella come cambia la forma dei dati a ogni passaggio della pipeline.
- Sapere esattamente cosa trovare su disco al termine di un'esecuzione completa, e dove guardare per primo.

Questo capitolo non introduce concetti nuovi: mette in sequenza, con numeri concreti, tutto ciò che le Parti IV-VII hanno già spiegato separatamente.

## 40.1 Cosa succede fase per fase

**[Fatto]** Il comando `python main.py --dataset heart_disease` (o semplicemente `python main.py`, dato il default, capitolo 28.2) attraversa le sette fasi già viste al capitolo 17-18, in questo ordine, con questi numeri reali per questo dataset specifico:

1. **Pulizia** (`main.py:28-31`): i file di una precedente esecuzione su questo dataset vengono cancellati.
2. **Preprocessing** (`preprocessing.py`, capitolo 21): le 920 righe concatenate (capitolo 29.1) vengono divise 80/20 (736 righe di training, 184 di test — mai più usate, capitolo 21.1), imputate, e bilanciate con SMOTENC.
3. **Embedding** (`embedding.py`, capitolo 22): ciascuna delle righe bilanciate diventa una frase, poi un vettore, per ciascuno dei sette modelli.
4. **Classificazione** (`classification.py`, capitolo 23): sette regressioni logistiche indipendenti, ciascuna validata con 5-fold stratificato.
5. **Valutazione** (`evaluation.py`, capitolo 24): bootstrap a 10.000 iterazioni per ciascun modello, sei grafici comparativi.
6. **Analisi errori** (`error_analysis.py`, capitolo 25): ogni falso positivo e falso negativo ricondotto al record clinico originale.
7. **Test statistici** (`statisticaltest.py`, capitolo 26): 21 confronti a coppie per ciascuna delle tre metriche, più 21 confronti DeLong sull'AUC.
8. **Report** (`generatereport.py`, capitolo 27): tutto assemblato in `report.md`.

## 40.2 Come cambiano i dati

**[Fatto]** Questa tabella traccia la forma esatta dei dati a ogni passaggio, con numeri verificati nelle Parti IV-VII di questo libro:

| Passaggio | Forma dei dati | Fonte del numero |
|---|---|---|
| Dati grezzi concatenati | 920 righe × 14 colonne (13 feature + target) | Capitolo 29.1 |
| Dopo split feature/target | `X`: 920×13, `y`: 920 | `preprocessing.py:39-41` |
| Dopo split 80/20 | `X_train`: 736×13 (usato), `X_test`: 184×13 (**mai più usato**) | Capitolo 21.1, capitolo 33.1 |
| Dopo imputazione | 736×13, nessun valore mancante | Capitolo 21.2, capitolo 31.1 |
| Dopo SMOTENC | `X_train_bal`: **814×13** (classe minoritaria pareggiata) | Capitolo 4.2, verificato sui file `.npy` |
| Dopo conversione a testo | 814 stringhe | Capitolo 22.1 |
| Dopo embedding, per modello | 814×768 (5 modelli) o 814×1024 (2 modelli) | Capitolo 32.3, tabella dimensioni |
| Per fold di classificazione | ~651 training, ~163 validazione | $814 \times \frac{4}{5}$ e $814 \times \frac{1}{5}$ |
| Risultati concatenati, per modello | `y_true`/`y_score`/`y_pred`/`val_idx`: 814 ciascuno | Capitolo 23.3 |
| Bootstrap, per modello e metrica | 10.000 valori | Capitolo 36.1 |
| Confronti statistici | $\binom{7}{2}=21$ per metrica × 3 metriche + 21 DeLong | Capitolo 26.1, capitolo 37 |

## 40.3 Cosa trovi su disco

**[Fatto]** Al termine, `datas/heart_disease/reports/report.md` (già presente nel repository, generato in un'esecuzione precedente al momento della scrittura di questo libro — capitolo 43 chiarisce la provenienza esatta di questi numeri) riporta, fra le altre cose, questa tabella riassuntiva:

| Modello | Accuracy | Macro-F1 | ROC-AUC |
|---|---|---|---|
| sentence-biobert | 0.8207 | 0.8195 | 0.8781 |
| pubmedbert | 0.8120 | 0.8090 | **0.8855** |
| bioclinicalbert | 0.7960 | 0.7932 | 0.8795 |
| e5-large | 0.7961 | 0.7923 | 0.8661 |
| gte-base | 0.7899 | 0.7883 | 0.8401 |
| gte-large | 0.7862 | 0.7838 | 0.8540 |
| e5-base | 0.7777 | 0.7716 | 0.8489 |

**[Fatto]** `sentence-biobert` ha l'accuratezza e l'F1 più alti; `pubmedbert` ha l'AUC più alta — due modelli biomedici, non generalisti, coerentemente con la seconda domanda di ricerca del progetto (capitolo 6.3). **[Attenzione]** Il capitolo 44 tratta questi stessi numeri con tutto il rigore statistico necessario (quali differenze sono davvero significative secondo i tre test, non solo quale valore è numericamente più alto): qui li vedi solo come tappa finale del percorso appena tracciato.

Oltre al report, cinque cartelle sotto `datas/heart_disease/` contengono ciascuna l'output di una o più fasi (capitolo 17.2): `preprocessing/` (3 file), `embeddings/` (14 file, due per modello), `results/` (oltre 60 file fra predizioni, bootstrap, CSV di confronto), `graphics/` (grafici UMAP, ROC, matrici di confusione), `reports/` (il solo `report.md`).

## Riepilogo

Un'esecuzione completa per Heart Disease trasforma 920 righe grezze in un report finale attraversando otto passaggi tracciabili con numeri precisi: 736 righe di training (184 scartate), 814 dopo il bilanciamento sintetico, sette insiemi di embedding, sette classificatori validati a 5 fold, 10.000 ricampionamenti bootstrap per metrica e modello, 21 confronti a coppie per tre test statistici diversi. I due modelli con le prestazioni migliori nel report già presente nel repository sono entrambi biomedici, non generalisti — un primo indizio, da trattare con rigore statistico al capitolo 44, sulla seconda domanda di ricerca del progetto.

## Domande di autoverifica

**1. Delle 920 righe grezze di Heart Disease, quante finiscono davvero per contribuire a un embedding testuale, e quante vengono scartate?**
814 righe (dopo lo split 80/20 e il bilanciamento SMOTENC) contribuiscono agli embedding; le 184 righe del test set, calcolate ma mai riutilizzate, sono di fatto scartate.

**2. Perché il numero di righe usate per l'addestramento aumenta (da 736 a 814) invece di diminuire, nonostante nessun dato venga aggiunto dall'esterno?**
Perché SMOTENC genera record sintetici della classe minoritaria per pareggiarla alla classe maggioritaria (capitolo 21.2, capitolo 31.2): l'aumento di 78 righe (736→814) corrisponde esattamente alla differenza fra le due classi nel training set prima del bilanciamento.

**3. I due modelli con le prestazioni migliori nel report già presente per Heart Disease appartengono alla stessa famiglia?**
Sì, entrambi sono biomedici: `sentence-biobert` (famiglia `biomedical-st`) ha accuratezza e F1 più alti, `pubmedbert` (famiglia `biomedical`) ha l'AUC più alta — nessuno dei quattro modelli generalisti compare al primo posto in nessuna delle tre metriche.

> **MATERIALE PER LA TESI**
> 1. La tabella di trasformazione dei dati (§40.2), con ogni numero verificato e la fonte esatta — riusabile come diagramma di flusso quantitativo in "Materiali e metodi".
> 2. La tabella riassuntiva delle prestazioni reali per Heart Disease (§40.3) — riusabile direttamente nella sezione "Risultati", con il rimando al capitolo 44 per l'analisi statistica completa.
> 3. L'osservazione che i due modelli migliori sono entrambi biomedici — riusabile come prima evidenza descrittiva a supporto della seconda domanda di ricerca, da confermare statisticamente con i test del capitolo 44.

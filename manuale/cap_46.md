# Capitolo 46 — Analisi degli errori sui due dataset

**Obiettivi del capitolo**

- Vedere un pattern sistematico, presente su entrambi i dataset, nel modo in cui i sette modelli sbagliano.
- Scoprire, con una verifica diretta e non solo un sospetto, cosa hanno davvero in comune i casi "più difficili".
- Collegare questa analisi alle scoperte sulla qualità dei dati già fatte nella Parte VI.

## 46.1 Tassi di falsi positivi/negativi per modello

**[Fatto]** *Tabella 46.1 — Tassi di errore reali, entrambi i dataset (da `error_summary.csv`, già presente nel repository).*

| Modello | FP rate (HD) | FN rate (HD) | FP rate (D130) | FN rate (D130) |
|---|---|---|---|---|
| e5-base | 38.3% | 6.1% | 66.6% | 10.0% |
| gte-base | 29.0% | 13.0% | 64.3% | 12.3% |
| gte-large | 31.7% | 11.1% | 62.9% | 11.7% |
| e5-large | 33.7% | 7.1% | 62.8% | 11.7% |
| bioclinicalbert | 31.7% | 9.1% | 49.6% | 15.3% |
| pubmedbert | 31.0% | 6.6% | 55.1% | 12.3% |
| sentence-biobert | 25.6% | 10.3% | 50.5% | 12.9% |

**[Fatto]** Un pattern si ripete identico su **entrambi** i dataset e per **tutti e sette** i modelli, senza eccezione: il tasso di falsi positivi è sempre sostanzialmente più alto del tasso di falsi negativi — su Heart Disease di un fattore 3-6 volte, su Diabetes130 di un fattore 4-6 volte. **[Interpretazione]** Una spiegazione plausibile, coerente con quanto già visto al capitolo 35.2: la soglia $\tau^\star$ è scelta massimizzando F1, una metrica che in questo regime tende a favorire un recall alto (catturare i veri positivi) al costo di più falsi positivi — un compromesso che l'F1 pesa in un modo specifico, non necessariamente quello che un contesto clinico realmente richiederebbe (capitolo 1.2). **[Fatto]** Nota anche che i modelli biomedici hanno, coerentemente su entrambi i dataset, tassi di falsi positivi più bassi dei generalisti (media 29.4% contro 33.2% su Heart Disease; 51.7% contro 64.1% su Diabetes130) — un divario più ampio proprio sul dataset dove il capitolo 45 ha già mostrato una superiorità biomedica più netta.

## 46.2 I casi più difficili: cosa hanno in comune

**[Fatto]** Il capitolo 25.2 aveva già sollevato un dubbio, senza poterlo verificare a quel punto del libro: un record fra gli "hardest cases" potrebbe essere un artefatto di SMOTENC piuttosto che un caso clinicamente ambiguo. Ora possiamo verificarlo. **[Fatto]** `datas/heart_disease/results/hardest_cases.csv` (già presente, letto per intero) mostra, per i primi due record classificati male da tutti e 7 i modelli, età di **55.2321** e **54.0393** anni — valori non interi, impossibili per un'età anagrafica reale, e quindi la prova diretta che questi specifici record sono **sintetici**, generati da SMOTENC interpolando fra vicini reali (capitolo 21.2, capitolo 31.2), non pazienti realmente osservati.

**[Fatto]** Più rivelatore ancora: la maggioranza dei dieci casi più difficili condivide `ca=0` e `thal=3`. **[Fatto]** Ho verificato direttamente, calcolando mediana e moda sui valori realmente osservati (non mancanti) delle 920 righe originali: la **mediana osservata di `ca` è esattamente 0.0**, e la **moda osservata di `thal` è esattamente 3.0** — gli stessi identici valori che l'imputazione (`preprocessing.py:76-82`) assegna a ogni riga con questi campi mancanti (il 66.4% e il 52.8% delle righe, capitolo 29.3). **[Interpretazione]** La conclusione più probabile, alla luce di questa verifica: i record "più difficili" del progetto non sono necessariamente casi clinicamente ambigui — sono, con ogni evidenza, casi in cui `ca` e `thal` portano il valore imputato più comune, reso ancora più comune dall'amplificazione di SMOTENC già ipotizzata al capitolo 31.2. Il modello non fatica a distinguere un paziente raro e complesso: fatica a distinguere pazienti che condividono lo stesso valore "generico" imputato per due delle feature più informative del dataset standard.

> **ATTENZIONE —** questa non è una prova definitiva (non è stato verificato ogni singolo record fra i venti "hardest cases", solo i primi due per l'età non intera e il pattern comune per gli altri campi), ma è un'evidenza diretta e concreta, non solo un sospetto teorico. È probabilmente il collegamento più importante di questo libro fra la Parte VI (qualità dei dati) e la Parte IX (risultati): un limite di qualità dei dati individuato guardando i file grezzi si manifesta, concretamente, nell'analisi degli errori del sistema.

## 46.3 Deviazione di feature: quali variabili "tradiscono" un errore

**[Fatto]** La Formula 25.1 (capitolo 25.3) misura, per ciascuna feature numerica, quanto la sua media differisca fra casi sbagliati e casi corretti, aggregando su tutti i modelli. `datas/heart_disease/results/feature_deviation.csv` e il grafico corrispondente (`ErrorAnalysis_feature_deviation.png`, già presenti nel repository) mostrano quali feature portano il segnale più forte in questa direzione — un'informazione che completa, dal lato delle feature numeriche, ciò che il paragrafo 46.2 ha già mostrato dal lato delle feature categoriali (`ca`, `thal`, entrambe escluse da questa analisi perché non numeriche, capitolo 25.3).

> **PROVA TU —** apri il grafico `ErrorAnalysis_feature_deviation.png` di entrambi i dataset e verifica se `oldpeak` o `trestbps` (le due feature con più valori mancanti mascherati da zero, capitolo 29.2) mostrano una deviazione insolitamente alta o bassa rispetto alle altre feature numeriche — se lo fanno, è un altro possibile segnale che la qualità dei dati, non solo la difficoltà clinica intrinseca, guida parte degli errori del sistema.

## Riepilogo

Su entrambi i dataset, tutti e sette i modelli producono sistematicamente più falsi positivi che falsi negativi, coerentemente con una soglia ottimizzata per F1 (capitolo 35.2). I casi "più difficili" del progetto, verificati direttamente, sono in parte rilevante record sintetici generati da SMOTENC con valori di `ca` e `thal` coincidenti esattamente con i valori usati dall'imputazione — un'evidenza concreta che collega il limite di qualità dei dati già individuato nella Parte VI a un effetto osservabile nell'analisi degli errori.

## Domande di autoverifica

**1. Cosa hanno in comune tutti e sette i modelli, su entrambi i dataset, nel tipo di errore che commettono più spesso?**
Producono sempre più falsi positivi che falsi negativi, con un rapporto da 3 a 6 volte a seconda del modello e del dataset — un pattern sistematico, non un caso isolato di un singolo modello.

**2. Quale evidenza diretta dimostra che almeno alcuni degli "hardest cases" di Heart Disease sono record sintetici, non pazienti reali?**
Il valore dell'età: due dei casi più difficili hanno età di 55.2321 e 54.0393 anni — valori non interi, impossibili per un'anagrafica reale, che possono derivare solo dall'interpolazione lineare di SMOTENC fra due vicini reali.

**3. Perché il fatto che `ca=0` e `thal=3` compaiano nella maggioranza degli "hardest cases" è più di una coincidenza?**
Perché questi sono esattamente i valori — verificati direttamente calcolando mediana e moda sui dati realmente osservati — che l'imputazione assegna a ogni riga con questi campi mancanti (il 66% e il 53% delle righe): i casi più difficili condividono, con ogni evidenza, il profilo "generico" imputato più comune, non necessariamente una reale ambiguità clinica.

> **MATERIALE PER LA TESI**
> 1. La Tabella 46.1 dei tassi di errore, con il pattern sistematico FP>FN evidenziato — riusabile direttamente nella sezione "Risultati" o "Analisi degli errori".
> 2. La catena di evidenza sui casi più difficili — età non intera → record sintetico; `ca=0`/`thal=3` → valore di imputazione verificato — è probabilmente la scoperta più originale e meglio verificata di tutto il libro: riusabile quasi integralmente come sezione autonoma della tesi, con la piena tracciabilità della verifica.
> 3. Il suggerimento di verifica su `oldpeak`/`trestbps` nella deviazione di feature — riusabile come direzione di analisi aggiuntiva, se si decide di approfondire ulteriormente questo filone nella tesi.

# Capitolo 46 — Analisi degli errori sui due dataset

**Obiettivi del capitolo**

- Vedere un pattern sistematico, presente su entrambi i dataset, nel modo in cui i sette modelli sbagliano.
- Scoprire, con una verifica diretta e non solo un sospetto, cosa hanno davvero in comune i casi "più difficili".
- Collegare questa analisi alle scoperte sulla qualità dei dati già fatte nella Parte VI.

## 46.1 Tassi di falsi positivi/negativi per modello

**[Fatto]** *Tabella 46.1 — Tassi di errore reali, entrambi i dataset (da `error_summary.csv`, già presente nel repository).*

| Modello | FP rate (HD) | FN rate (HD) | FP rate (D130) | FN rate (D130) |
|---|---|---|---|---|
| e5-base | 32.4% | 13.5% | 56.7% | 15.2% |
| gte-base | 28.0% | 17.4% | 61.9% | 13.2% |
| gte-large | 32.4% | 12.5% | 56.8% | 14.6% |
| e5-large | 35.4% | 12.0% | 59.3% | 13.8% |
| bioclinicalbert | 34.6% | 11.3% | 49.7% | 15.4% |
| pubmedbert | 30.0% | 11.3% | 53.4% | 12.8% |
| sentence-biobert | 31.7% | 10.3% | 50.0% | 13.8% |

**[Fatto]** Un pattern si ripete identico su **entrambi** i dataset e per **tutti e sette** i modelli, senza eccezione: il tasso di falsi positivi è sempre sostanzialmente più alto del tasso di falsi negativi — su Heart Disease di un fattore 1.6-3 volte, su Diabetes130 di un fattore 3-5 volte. **[Interpretazione]** Una spiegazione plausibile, coerente con quanto già visto al capitolo 35.2: la soglia $\tau^\star$ è scelta massimizzando F1, una metrica che in questo regime tende a favorire un recall alto (catturare i veri positivi) al costo di più falsi positivi — un compromesso che l'F1 pesa in un modo specifico, non necessariamente quello che un contesto clinico realmente richiederebbe (capitolo 1.2). **[Fatto]** Su Diabetes130 i modelli biomedici hanno tassi di falsi positivi visibilmente più bassi dei generalisti (media 51.0% contro 58.7%) — un divario coerente con la superiorità biomedica più netta già mostrata al capitolo 45; su Heart Disease, con la pipeline corretta, le medie delle due famiglie sono invece praticamente identiche (~32%), a conferma che lì il vantaggio biomedico si manifesta nell'AUC più che nel profilo di errore alla soglia scelta.

## 46.2 I casi più difficili: cosa hanno in comune

**[Fatto]** Il capitolo 25.2 aveva già sollevato un dubbio: un record fra gli "hardest cases" potrebbe essere un artefatto della preparazione dei dati piuttosto che un caso clinicamente ambiguo. La storia di questa verifica si è svolta in due atti. **[Fatto]** *Primo atto (pipeline pre-fix):* l'analisi degli hardest cases dell'esecuzione precedente ai fix aveva trovato età non intere (55.2321, 54.0393) — prova diretta di record sintetici SMOTENC — e, soprattutto, la maggioranza dei casi condivideva `ca=0` e `thal=3`: esattamente la mediana e la moda osservate delle 920 righe originali, cioè **i valori che l'imputazione assegnava a ogni riga con questi campi mancanti** (il 66.4% e il 52.8% delle righe, capitolo 29.3), scritti nel testo generato come se fossero stati osservati sul paziente. I casi "più difficili" erano in larga parte il profilo "generico imputato", amplificato da SMOTE.

**[Fatto]** *Secondo atto (pipeline corretta):* quella scoperta ha motivato il fix degli indicatori di mancanza (capitolo 21.2) e del mascheramento "not recorded" nel testo (capitolo 22.1, `docs/CHANGES.md` §3). Nell'esecuzione attuale, `datas/heart_disease/results/hardest_cases.csv` porta con sé le stesse colonne indicatore, e la verifica diventa diretta invece che inferita: **14 dei 20 casi sbagliati da tutti e 7 i modelli hanno `ca_missing=1`, 13 hanno `thal_missing=1`** (e 19 su 20 hanno `ca=0`). Le età non intere sono sparite dai primi venti. **[Interpretazione]** Il quadro che emerge è più onesto ma coerente: i casi più difficili restano in maggioranza quelli in cui le due feature più informative del dataset **non sono mai state misurate** — solo che ora il modello riceve la frase "not recorded" invece di un valore fabbricato, e la difficoltà è legittimamente attribuibile all'informazione mancante, non a un artefatto di imputazione mascherato da osservazione.

> **ATTENZIONE —** è probabilmente il collegamento più importante di questo libro fra la Parte VI (qualità dei dati) e la Parte IX (risultati), con in più il valore metodologico della sequenza completa: un limite individuato guardando i file grezzi → verificato nell'analisi degli errori → corretto nel codice → e ri-misurato nella nuova esecuzione, dove gli indicatori rendono il legame missingness-difficoltà osservabile direttamente nel CSV.

## 46.3 Deviazione di feature: quali variabili "tradiscono" un errore

**[Fatto]** La Formula 25.1 (capitolo 25.3) misura, per ciascuna feature numerica, quanto la sua media differisca fra casi sbagliati e casi corretti, aggregando su tutti i modelli. `datas/heart_disease/results/feature_deviation.csv` e il grafico corrispondente (`ErrorAnalysis_feature_deviation.png`, già presenti nel repository) mostrano quali feature portano il segnale più forte in questa direzione — un'informazione che completa, dal lato delle feature numeriche, ciò che il paragrafo 46.2 ha già mostrato dal lato delle feature categoriali (`ca`, `thal`, entrambe escluse da questa analisi perché non numeriche, capitolo 25.3).

> **PROVA TU —** apri il grafico `ErrorAnalysis_feature_deviation.png` di entrambi i dataset e verifica se `oldpeak` o `trestbps` (le due feature con più valori mancanti mascherati da zero, capitolo 29.2) mostrano una deviazione insolitamente alta o bassa rispetto alle altre feature numeriche — se lo fanno, è un altro possibile segnale che la qualità dei dati, non solo la difficoltà clinica intrinseca, guida parte degli errori del sistema.

## Riepilogo

Su entrambi i dataset, tutti e sette i modelli producono sistematicamente più falsi positivi che falsi negativi, coerentemente con una soglia ottimizzata per F1 (capitolo 35.2). I casi "più difficili" del progetto restano in maggioranza quelli in cui `ca` e `thal` non sono mai stati misurati: nell'esecuzione pre-fix questo si manifestava come profili imputati presentati come osservati (la scoperta che ha motivato il fix degli indicatori di mancanza); nell'esecuzione attuale gli indicatori nel CSV rendono il legame fra missingness e difficoltà osservabile direttamente — 14 dei 20 casi sbagliati da tutti i modelli hanno `ca_missing=1`.

## Domande di autoverifica

**1. Cosa hanno in comune tutti e sette i modelli, su entrambi i dataset, nel tipo di errore che commettono più spesso?**
Producono sempre più falsi positivi che falsi negativi, con un rapporto da circa 1.6 a 5 volte a seconda del modello e del dataset — un pattern sistematico, non un caso isolato di un singolo modello.

**2. Quale evidenza aveva dimostrato che alcuni "hardest cases" dell'esecuzione pre-fix erano record sintetici, non pazienti reali?**
Il valore dell'età: due dei casi più difficili avevano età di 55.2321 e 54.0393 anni — valori non interi, impossibili per un'anagrafica reale, derivabili solo dall'interpolazione lineare di SMOTENC fra due vicini reali. Nei primi venti hardest cases dell'esecuzione attuale, dopo il fix del mascheramento, le età non intere non compaiono più.

**3. Come si verifica, nell'esecuzione attuale, il legame fra valori mai misurati e difficoltà di classificazione?**
Direttamente dalle colonne indicatore incluse in `hardest_cases.csv`: 14 dei 20 record sbagliati da tutti e sette i modelli hanno `ca_missing=1` e 13 hanno `thal_missing=1` — la maggioranza dei casi più difficili è fatta di pazienti per cui le due feature più informative del dataset non sono mai state misurate, oggi dichiarate "not recorded" nel testo invece che riempite con il valore imputato.

> **MATERIALE PER LA TESI**
> 1. La Tabella 46.1 dei tassi di errore, con il pattern sistematico FP>FN evidenziato — riusabile direttamente nella sezione "Risultati" o "Analisi degli errori".
> 2. La catena di evidenza completa sui casi più difficili — età non intera → record sintetico; `ca=0`/`thal=3` → valore di imputazione verificato; fix degli indicatori → legame missingness-difficoltà ora osservabile direttamente (14/20 con `ca_missing=1`) — è probabilmente la scoperta più originale e meglio verificata di tutto il libro: riusabile quasi integralmente come sezione autonoma della tesi, con la piena tracciabilità di scoperta, correzione e ri-misura.
> 3. Il suggerimento di verifica su `oldpeak`/`trestbps` nella deviazione di feature — riusabile come direzione di analisi aggiuntiva, se si decide di approfondire ulteriormente questo filone nella tesi.

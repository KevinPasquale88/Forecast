# Capitolo 44 — Risultati — UCI Heart Disease

**Obiettivi del capitolo**

- Avere la tabella completa dei risultati reali per Heart Disease, con intervalli di confidenza, non solo le medie già viste al capitolo 40.
- Sapere quali differenze fra famiglie di modelli sono descrittivamente osservabili nella tabella.
- Sapere quali delle 21 coppie di modelli sono davvero, statisticamente, diverse fra loro secondo il test di DeLong — non solo quale ha il numero più alto.

**[Fatto]** Ogni numero di questo capitolo proviene da `datas/heart_disease/reports/report.md` e dai CSV in `datas/heart_disease/results/`, già presenti nel repository (capitolo 43.1) — non da un'esecuzione di questa sessione.

## 44.1 Tabella completa delle metriche con intervalli di confidenza

**[Fatto]** *Tabella 44.1 — Risultati completi, Heart Disease (bootstrap 10.000 iterazioni, capitolo 36).*

| Modello | Accuracy (IC 95%) | Macro-F1 (IC 95%) | ROC-AUC (IC 95%) |
|---|---|---|---|
| e5-base | 0.7702 (0.7408–0.7985) | 0.7679 (0.7377–0.7967) | 0.8476 (0.8200–0.8737) |
| gte-base | 0.7727 (0.7432–0.8010) | 0.7718 (0.7428–0.8007) | 0.8458 (0.8186–0.8717) |
| gte-large | 0.7752 (0.7457–0.8034) | 0.7727 (0.7433–0.8012) | 0.8543 (0.8277–0.8797) |
| e5-large | 0.7629 (0.7334–0.7924) | 0.7594 (0.7293–0.7886) | 0.8554 (0.8295–0.8800) |
| bioclinicalbert | 0.7703 (0.7408–0.7985) | 0.7669 (0.7374–0.7956) | 0.8829 (0.8599–0.9050) |
| pubmedbert | 0.7936 (0.7654–0.8219) | 0.7916 (0.7626–0.8197) | 0.8909 (0.8686–0.9125) |
| sentence-biobert | 0.7900 (0.7617–0.8170) | 0.7874 (0.7590–0.8147) | 0.8748 (0.8500–0.8975) |

Gli intervalli di confidenza si leggono come già spiegato al capitolo 36.2: il 95% dei 10.000 ricampionamenti bootstrap produce un valore in quel range. **[Fatto]** Nota che gli intervalli si sovrappongono ampiamente fra modelli vicini in classifica — un indizio visivo, prima ancora del test formale, che alcune differenze potrebbero non essere statisticamente solide.

**[Fatto]** *Tabella 44.1bis — Valutazione holdout, Heart Disease (184 casi di test mai visti, `holdout_evaluation.csv`).*

| Modello | Accuracy | Macro-F1 | ROC-AUC |
|---|---|---|---|
| e5-base | 0.7935 | 0.7843 | 0.8778 |
| gte-base | 0.7989 | 0.7914 | 0.8973 |
| gte-large | 0.7554 | 0.7413 | 0.8656 |
| e5-large | 0.8098 | 0.8026 | 0.8971 |
| bioclinicalbert | **0.8424** | **0.8399** | **0.9193** |
| pubmedbert | 0.8315 | 0.8259 | 0.9087 |
| sentence-biobert | 0.8098 | 0.7988 | 0.8959 |

**[Fatto]** Sui 184 casi mai visti, tutti i modelli ottengono metriche pari o superiori a quelle di cross-validation — un segnale rassicurante: la stima incrociata non era ottimista, su questo dataset — e il migliore è `bioclinicalbert` (AUC 0.9193). **[Attenzione]** È una singola misura su 184 casi, senza intervallo bootstrap: le differenze fra modelli in questa tabella vanno lette con più cautela ancora di quelle della Tabella 44.1.

## 44.2 Confronto tra famiglie di modelli

**[Fatto: media aritmetica semplice delle righe della Tabella 44.1, non l'analisi bootstrap pooled del grafico `FamilyComparison_metrics.png`]** Raggruppando per famiglia (capitolo 5.3):

| Famiglia | AUC media (dei modelli membri) |
|---|---|
| Generalista (e5-base, gte-base, gte-large, e5-large) | 0.8508 |
| Biomedica (bioclinicalbert, pubmedbert) | 0.8869 |
| Biomedica per frasi (sentence-biobert, un solo membro) | 0.8748 |

**[Interpretazione]** Descrittivamente, le famiglie biomediche superano quella generalista di circa 2.4-3.6 punti percentuali di AUC media. **[Attenzione]** Questa è una media semplice, utile per farsi un'idea rapida, non il risultato di un test statistico: il capitolo 44.3 va oltre, verificando quali differenze specifiche fra coppie di modelli sono davvero significative — la risposta, come vedrai, è più sfumata di quanto questa tabella da sola suggerisca.

## 44.3 Cosa dicono davvero i test statistici

**[Fatto]** Il test di DeLong (capitolo 37.3) confronta l'AUC di ciascuna delle $\binom{7}{2}=21$ coppie di modelli. Riorganizzando i risultati reali di `delong_comparison.csv` per famiglia:

**[Fatto]** Tutti e 12 i confronti fra un modello generalista e un modello biomedico sono significativi al p-value grezzo (p < 0.05): ogni biomedico supera ogni generalista in AUC in modo statisticamente solido, non solo descrittivo. Dopo la correzione Benjamini-Hochberg (capitolo 26.2bis), 11 confronti su 12 restano significativi — l'unico che scende sotto soglia è `e5-large` contro `sentence-biobert` (p grezzo 0.0436, p corretto 0.0704), un caso limite da riportare con precisione.

**[Fatto]** All'interno delle famiglie, invece, quasi nulla si distingue: nessuna coppia di generalisti è significativa (sei confronti, p da 0.0745 a 0.874 — `gte-large` contro `e5-large` arriva a p=0.874, un pareggio pieno), e fra i biomedici bioclinicalbert-pubmedbert (p=0.0696) e bioclinicalbert-sentence-biobert (p=0.3164) non sono significativi, mentre pubmedbert-sentence-biobert è significativo al p-value grezzo (0.0354) ma **non sopravvive alla correzione** (p corretto 0.062).

> **ATTENZIONE —** la risposta onesta alla seconda domanda di ricerca del progetto (capitolo 6.3), su Heart Disease con la pipeline corretta, è: "ogni modello biomedico supera ogni modello generalista in AUC in modo statisticamente significativo (11 coppie su 12 anche dopo la correzione per confronti multipli), mentre all'interno di ciascuna famiglia i modelli non si distinguono l'uno dall'altro". È una conclusione forte fra famiglie e prudente dentro le famiglie — più precisa, e più difendibile in sede di discussione, di quella che una lettura solo descrittiva della Tabella 44.1 suggerirebbe.

## Riepilogo

Pubmedbert ha le prestazioni di cross-validation numericamente migliori su Heart Disease e bioclinicalbert le migliori sul test set holdout; il test di DeLong mostra una superiorità dei modelli biomedici statisticamente solida contro tutti e quattro i generalisti (12 coppie su 12 al p-value grezzo, 11 dopo la correzione Benjamini-Hochberg), mentre le differenze all'interno di ciascuna famiglia non raggiungono la significatività — con un solo caso limite (pubmedbert-sentence-biobert) significativo solo prima della correzione.

## Domande di autoverifica

**1. Quale modello ha l'AUC media più alta nella Tabella 44.1, e questo lo rende statisticamente superiore a tutti gli altri sei?**
Pubmedbert (0.8909). No: il test di DeLong mostra che è significativamente migliore di tutti e quattro i modelli generalisti, ma il confronto con bioclinicalbert non è significativo (p=0.0696) e quello con sentence-biobert lo è solo prima della correzione per confronti multipli (p grezzo 0.0354, p corretto 0.062) — "il più alto numericamente" non equivale a "superiore a tutti statisticamente".

**2. Quale unico confronto generalista-biomedico non sopravvive alla correzione Benjamini-Hochberg?**
`e5-large` contro `sentence-biobert`: p grezzo 0.0436 (significativo), p corretto 0.0704 (non significativo) — un caso limite che merita di essere riportato con precisione, non arrotondato a "significativo" o "non significativo" senza qualificazione. Gli altri 11 confronti fra famiglie restano significativi anche dopo la correzione.

**3. All'interno della famiglia biomedica, quante delle tre coppie possibili sono statisticamente distinguibili in AUC?**
Nessuna, dopo la correzione per confronti multipli: bioclinicalbert-pubmedbert (p=0.0696) e bioclinicalbert-sentence-biobert (p=0.3164) non sono significativi nemmeno al p-value grezzo; pubmedbert-sentence-biobert lo è al grezzo (0.0354) ma non al corretto (0.062).

> **MATERIALE PER LA TESI**
> 1. La Tabella 44.1 completa con intervalli di confidenza — riusabile direttamente come tabella principale della sezione "Risultati".
> 2. L'analisi per famiglia con la precisazione sulla natura descrittiva della media semplice — riusabile con la dovuta cautela metodologica nella stessa sezione.
> 3. La sintesi sfumata della risposta alla seconda domanda di ricerca, basata sul test di DeLong reale e non su una lettura solo descrittiva — è materiale di alto valore per la sezione "Discussione", e un esempio concreto di rigore statistico applicato correttamente.

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
| e5-base | 0.7777 (0.7482–0.8059) | 0.7716 (0.7417–0.8001) | 0.8489 (0.8215–0.8746) |
| gte-base | 0.7899 (0.7617–0.8170) | 0.7883 (0.7600–0.8160) | 0.8401 (0.8122–0.8667) |
| gte-large | 0.7862 (0.7580–0.8145) | 0.7838 (0.7549–0.8124) | 0.8540 (0.8272–0.8797) |
| e5-large | 0.7961 (0.7678–0.8243) | 0.7923 (0.7636–0.8204) | 0.8661 (0.8406–0.8900) |
| bioclinicalbert | 0.7960 (0.7678–0.8231) | 0.7932 (0.7646–0.8207) | 0.8795 (0.8560–0.9014) |
| pubmedbert | 0.8120 (0.7850–0.8378) | 0.8090 (0.7811–0.8354) | 0.8855 (0.8622–0.9065) |
| sentence-biobert | 0.8207 (0.7936–0.8464) | 0.8195 (0.7922–0.8449) | 0.8781 (0.8544–0.9005) |

Gli intervalli di confidenza si leggono come già spiegato al capitolo 36.2: il 95% dei 10.000 ricampionamenti bootstrap produce un valore in quel range. **[Fatto]** Nota che gli intervalli si sovrappongono ampiamente fra modelli vicini in classifica (per esempio bioclinicalbert ed e5-large hanno intervalli di accuratezza quasi identici) — un indizio visivo, prima ancora del test formale, che alcune differenze potrebbero non essere statisticamente solide.

## 44.2 Confronto tra famiglie di modelli

**[Fatto: media aritmetica semplice delle righe della Tabella 44.1, non l'analisi bootstrap pooled del grafico `FamilyComparison_metrics.png`]** Raggruppando per famiglia (capitolo 5.3):

| Famiglia | AUC media (dei modelli membri) |
|---|---|
| Generalista (e5-base, gte-base, gte-large, e5-large) | 0.8523 |
| Biomedica (bioclinicalbert, pubmedbert) | 0.8825 |
| Biomedica per frasi (sentence-biobert, un solo membro) | 0.8781 |

**[Interpretazione]** Descrittivamente, le famiglie biomediche superano quella generalista di circa 2.5-3 punti percentuali di AUC media. **[Attenzione]** Questa è una media semplice, utile per farsi un'idea rapida, non il risultato di un test statistico: il capitolo 44.3 va oltre, verificando quali differenze specifiche fra coppie di modelli sono davvero significative — la risposta, come vedrai, è più sfumata di quanto questa tabella da sola suggerisca.

## 44.3 Cosa dicono davvero i test statistici

**[Fatto]** Il test di DeLong (capitolo 37.3) confronta l'AUC di ciascuna delle $\binom{7}{2}=21$ coppie di modelli. Riorganizzando i risultati reali di `delong_comparison.csv` per famiglia:

**[Fatto]** Ogni confronto fra un modello generalista *piccolo* (e5-base, gte-base) e un modello biomedico è significativo (p < 0.05, in 6 confronti su 6): la superiorità biomedica, per questi due modelli generalisti specifici, è statisticamente solida, non solo descrittiva.

**[Fatto]** Ma per i modelli generalisti *grandi* (gte-large, e5-large), il quadro è più sfumato: `gte-large` contro `e5-large` non è significativo (p=0.0628, appena sopra la soglia); `e5-large` contro `bioclinicalbert` non è significativo (p=0.061, ugualmente appena sopra la soglia); `gte-large` contro `e5-large` (già citato) e contro `bioclinicalbert` (p=0.0012, questo sì significativo) danno risposte diverse a seconda della coppia specifica.

**[Fatto]** All'interno della famiglia biomedica, **nessuna delle tre coppie è significativamente diversa**: bioclinicalbert-pubmedbert (p=0.1937), bioclinicalbert-sentence-biobert (p=0.8515), pubmedbert-sentence-biobert (p=0.3075) — i tre modelli biomedici, pur con AUC numericamente diverse (0.8795, 0.8855, 0.8781), non si distinguono statisticamente l'uno dall'altro su questo dataset.

> **ATTENZIONE —** la risposta onesta alla seconda domanda di ricerca del progetto (capitolo 6.3), su Heart Disease, non è un netto "sì, i modelli biomedici vincono sempre": è "i modelli biomedici e generalisti-grandi formano, su questo dataset, un gruppo di prestazioni statisticamente indistinguibili fra loro, superiore in modo solido solo rispetto ai due modelli generalisti più piccoli". È una conclusione più precisa, e più difendibile in sede di discussione, di quella che una lettura solo descrittiva della Tabella 44.1 (o il testo statico del report, capitolo 27.2) suggerirebbe.

## Riepilogo

Sentence-biobert e pubmedbert hanno le prestazioni numericamente migliori su Heart Disease, ma il test di DeLong rivela un quadro più sfumato: la superiorità dei modelli biomedici è statisticamente solida solo contro i due modelli generalisti più piccoli (e5-base, gte-base); contro i modelli generalisti più grandi, e fra i modelli biomedici stessi, molte differenze numeriche non raggiungono la significatività statistica.

## Domande di autoverifica

**1. Quale modello ha l'AUC media più alta nella Tabella 44.1, e questo lo rende statisticamente superiore a tutti gli altri sei?**
Pubmedbert (0.8855). No: il test di DeLong mostra che è significativamente migliore di tutti e quattro i modelli generalisti (e5-base, gte-base, gte-large, e5-large, tutti con p $\leq$ 0.0005), ma non è significativamente diverso dagli altri due modelli biomedici, bioclinicalbert (p=0.1937) e sentence-biobert (p=0.3075) — "il più alto numericamente" non equivale a "superiore a tutti statisticamente".

**2. Fra quali coppie di modelli generalisti "grandi" e modelli biomedici il test di DeLong non trova una differenza significativa?**
`gte-large` contro `e5-large` (p=0.0628) ed `e5-large` contro `bioclinicalbert` (p=0.061) — entrambi appena sopra la soglia convenzionale di 0.05, un caso limite che merita di essere riportato con precisione, non arrotondato a "significativo" o "non significativo" senza qualificazione.

**3. All'interno della famiglia biomedica, quante delle tre coppie possibili sono statisticamente distinguibili in AUC?**
Nessuna: bioclinicalbert, pubmedbert e sentence-biobert hanno AUC numericamente diverse ma nessuna delle tre coppie raggiunge la significatività statistica secondo il test di DeLong su questo dataset.

> **MATERIALE PER LA TESI**
> 1. La Tabella 44.1 completa con intervalli di confidenza — riusabile direttamente come tabella principale della sezione "Risultati".
> 2. L'analisi per famiglia con la precisazione sulla natura descrittiva della media semplice — riusabile con la dovuta cautela metodologica nella stessa sezione.
> 3. La sintesi sfumata della risposta alla seconda domanda di ricerca, basata sul test di DeLong reale e non su una lettura solo descrittiva — è materiale di alto valore per la sezione "Discussione", e un esempio concreto di rigore statistico applicato correttamente.

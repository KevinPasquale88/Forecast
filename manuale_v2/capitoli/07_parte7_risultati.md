# Parte VII — Risultati

## Capitolo 31 — Protocollo sperimentale

### 31.1 Cosa è stato eseguito

| Esperimento | Data | Codice | Output |
| --- | --- | --- | --- |
| Pipeline completa su Heart Disease, 7 encoder, protocollo standardizzato | 14/11/2026 | `python main.py --dataset heart_disease` (branch `fix/port-chatbot-corrections`) | `datas/heart_disease/` |
| Pipeline completa su Diabetes130, 7 encoder, protocollo standardizzato | 14/11/2026 | `python main.py --dataset diabetes130` | `datas/diabetes130/` |
| Baseline tabellari su entrambi i dataset; AUC per centro; modello "solo mancanza" | 14/11/2026 | `manuale_v2/analisi/analisi_aggiuntive.py` | `manuale_v2/analisi/risultati_aggiuntivi.json` |
| Analisi di sensibilità sulla scala degli embedding (quattro protocolli) e DeLong | 14/11/2026 | `manuale_v2/analisi/scala_embedding.py` | `manuale_v2/analisi/scala_embedding.json` |

### 31.2 Ambiente

Python 3.14.0 su Apple Silicon; scikit-learn 1.8.0, sentence-transformers 5.5.1, transformers 5.7.0, torch 2.11.0, numpy 2.4.4, pandas 3.0.2, scipy 1.17.1, MLstatkit 0.1.91; Ollama 0.40.15. Seme 42 ovunque.

### 31.3 Protocollo, in sintesi

1. Split stratificato 80/20 (seme 42).
2. Frase per record; embedding con 7 encoder congelati.
3. Linear probe: standardizzazione + regressione logistica L2, in CV stratificata a 5 fold. In ogni fold, sulla sola parte di training: C scelto in {0,001; 0,01; 0,1; 1; 10; 100} con una CV interna (massima ROC-AUC); soglia dal massimo F1 su punteggi out-of-fold di un'altra CV interna con quel C; classificatore finale su tutta la parte di training.
4. Bootstrap a 10.000 ricampionamenti delle predizioni out-of-fold; intervalli percentili al 95%.
5. Wilcoxon e t-test appaiato sui bootstrap; DeLong sulle predizioni out-of-fold; correzione di Benjamini-Hochberg.
6. Holdout: stesso protocollo su tutto il training, misura unica sul test.

## Capitolo 32 — Risultati su Heart Disease

### 32.1 Cross-validation

Medie bootstrap e intervalli al 95% (`encoder_comparison_summary.csv`):

| Modello | Famiglia | Accuracy | Macro-F1 | ROC-AUC |
| --- | --- | --- | --- | --- |
| pubmedbert | biomedica | 0,843 (0,815–0,870) | 0,839 (0,811–0,866) | 0,890 (0,864–0,913) |
| gte-base | generalista | 0,813 (0,784–0,841) | 0,806 (0,776–0,835) | 0,880 (0,854–0,905) |
| bioclinicalbert | biomedica | 0,813 (0,784–0,841) | 0,808 (0,779–0,837) | 0,880 (0,853–0,904) |
| e5-large | generalista | 0,810 (0,781–0,838) | 0,802 (0,772–0,831) | 0,877 (0,851–0,902) |
| sentence-biobert | biomedica | 0,819 (0,791–0,848) | 0,814 (0,785–0,843) | 0,876 (0,850–0,901) |
| e5-base | generalista | 0,806 (0,777–0,834) | 0,796 (0,767–0,826) | 0,875 (0,848–0,900) |
| gte-large | generalista | 0,780 (0,750–0,810) | 0,771 (0,740–0,802) | 0,849 (0,819–0,878) |

Medie per famiglia: biomedici accuracy 0,825, macro-F1 0,820, AUC 0,882; generalisti 0,802, 0,794, 0,870. Il divario di AUC tra famiglie è di 1,2 punti, e gli intervalli dei sei modelli migliori si sovrappongono quasi del tutto.

Metriche aggiuntive (media dei 5 fold, `model_performance.csv`):

| Modello | PR-AUC | Brier | Soglia media τ | C scelto (mediana) |
| --- | --- | --- | --- | --- |
| pubmedbert | 0,897 | 0,127 | 0,433 | 0,01 |
| gte-base | 0,894 | 0,135 | 0,404 | 0,01 |
| bioclinicalbert | 0,890 | 0,136 | 0,477 | 0,01 |
| e5-large | 0,887 | 0,136 | 0,371 | 0,01 |
| sentence-biobert | 0,881 | 0,137 | 0,447 | 0,01 |
| e5-base | 0,877 | 0,138 | 0,352 | 0,01 |
| gte-large | 0,862 | 0,153 | 0,361 | 0,01 |

Con la standardizzazione la CV interna sceglie C = 0,01 per tutti i modelli e in tutti i fold: una regolarizzazione forte, coerente con 589 record di training per fold e 768–1024 dimensioni. Il Brier score dei generalisti scende da 0,18–0,20 (protocollo originale) a 0,135–0,153: prima erano penalizzati, non poco informativi.

![Media e intervallo al 95% di accuracy, macro-F1 e ROC-AUC per modello (grafico prodotto dalla pipeline).](figure/MeanCI_metrics.png)

![Curve ROC out-of-fold dei sette encoder.](figure/ROC_comparison.png)

### 32.2 Test set

| Modello | Accuracy | Macro-F1 | ROC-AUC | PR-AUC | Precision | Recall | Brier | τ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bioclinicalbert | 0,832 | 0,825 | 0,925 | 0,934 | 0,803 | 0,922 | 0,109 | 0,388 |
| gte-base | 0,848 | 0,845 | 0,919 | 0,926 | 0,843 | 0,892 | 0,111 | 0,480 |
| pubmedbert | 0,842 | 0,836 | 0,915 | 0,927 | 0,812 | 0,931 | 0,115 | 0,426 |
| e5-base | 0,826 | 0,816 | 0,913 | 0,914 | 0,778 | 0,961 | 0,113 | 0,312 |
| e5-large | 0,842 | 0,836 | 0,912 | 0,923 | 0,812 | 0,931 | 0,113 | 0,381 |
| sentence-biobert | 0,832 | 0,827 | 0,912 | 0,922 | 0,814 | 0,902 | 0,115 | 0,445 |
| gte-large | 0,804 | 0,796 | 0,889 | 0,910 | 0,775 | 0,912 | 0,134 | 0,370 |

184 record, prevalenza 55,4%; C = 0,01 per tutti. Tutti i modelli fanno un po' meglio che in CV: il classificatore finale usa tutto il training (736 record invece di 589) e il test di 184 record ha una variabilità di circa ±0,04 di AUC. Sei modelli su sette stanno tra 0,912 e 0,925: sul test set non c'è una gerarchia leggibile.

### 32.3 Test statistici

**DeLong** (21 confronti, BH): 9 significativi.

- Tra famiglie (12 confronti): 5 significativi. gte-large è inferiore a tutti e tre i biomedici; pubmedbert supera e5-base ed e5-large. gte-base non differisce da nessun biomedico.
- Tra generalisti: gte-large è inferiore agli altri tre.
- Tra biomedici: pubmedbert supera sentence-biobert (p corretto 0,031); contro bioclinicalbert la differenza non è significativa dopo la correzione (0,070).

**Wilcoxon e t-test sui bootstrap**: 62 confronti su 63 significativi con entrambi i test. L'unico non significativo è l'accuracy di gte-base contro bioclinicalbert (0,8126 contro 0,8127). La differenza più piccola dichiarata significativa è 0,0008: la potenza dei due test dipende dai 10.000 ricampionamenti (capitolo 29.4).

![Distribuzione delle 10.000 metriche bootstrap per modello.](figure/BOXPLOT_metrics.png)

![Confronto per famiglia (grafico prodotto dalla pipeline).](figure/FamilyComparison_metrics.png)

Le matrici di confusione out-of-fold mostrano la differenza in concreto: pubmedbert sbaglia 116 record su 736, e5-base 143, soprattutto per i falsi positivi (110 contro 74).

![Matrice di confusione out-of-fold di pubmedbert.](figure/CM_pubmedbert.png)

![Matrice di confusione out-of-fold di e5-base.](figure/CM_e5-base.png)

### 32.4 Analisi di sensibilità: il protocollo originale

Fino al 14 novembre 2026 la pipeline usava `LogisticRegression(C=1)` sui vettori grezzi. Gli embedding Ollama hanno norma 1, quelli Hugging Face 11–13 (capitolo 8.3): con la stessa penalità L2, i generalisti venivano regolarizzati molto di più. Lo stesso confronto in quattro varianti (`scala_embedding.py`):

| Modello | Originale (grezzi, C = 1) | Standardizzati, C = 1 | Norma 1 per tutti, C = 1 | Standardizzati, C da CV |
| --- | --- | --- | --- | --- |
| e5-base | 0,839 | 0,855 | 0,839 | 0,875 |
| gte-base | 0,841 | 0,849 | 0,841 | 0,880 |
| gte-large | 0,844 | 0,833 | 0,844 | 0,853 |
| e5-large | 0,850 | 0,849 | 0,850 | 0,878 |
| bioclinicalbert | 0,879 | 0,823 | 0,856 | 0,876 |
| pubmedbert | 0,887 | 0,864 | 0,835 | 0,889 |
| sentence-biobert | 0,880 | 0,848 | 0,854 | 0,881 |

(ROC-AUC out-of-fold. L'ultima colonna è calcolata con una griglia di 11 valori di C e coincide entro 0,004 con i risultati della pipeline, che ne usa 6.)

| | Protocollo originale | Protocollo attuale |
| --- | --- | --- |
| AUC generalisti | 0,839–0,850 | 0,849–0,880 |
| AUC biomedici | 0,879–0,887 | 0,876–0,890 |
| Divario medio tra famiglie | 3,8 punti | 1,2 punti |
| DeLong significativi tra famiglie (BH) | 12 su 12 | 5 su 12 |
| Brier generalisti | 0,178–0,197 | 0,135–0,153 |

Il vantaggio "netto" dei biomedici era in larga parte un effetto della regolarizzazione. Con un probe equo i biomedici restano in media davanti di poco più di un punto; pubmedbert è il migliore in tutte le varianti tranne quella a norma 1.

> *Per la tesi.* Riportare il protocollo attuale come risultato principale e questa tabella come analisi di sensibilità. È un esempio concreto di come un dettaglio di preprocessing (la scala degli ingressi) possa cambiare la risposta a una domanda di ricerca, e di come lo si scopre misurando.

## Capitolo 33 — Analisi degli errori e ruolo del centro

### 33.1 Errori per modello

| Modello | Errori su 736 | Falsi positivi | Falsi negativi | Tasso FP (sui sani) | Tasso FN (sui malati) |
| --- | --- | --- | --- | --- | --- |
| pubmedbert | 116 | 74 | 42 | 22,5% | 10,3% |
| sentence-biobert | 133 | 89 | 44 | 27,1% | 10,8% |
| gte-base | 138 | 96 | 42 | 29,2% | 10,3% |
| bioclinicalbert | 138 | 84 | 54 | 25,5% | 13,3% |
| e5-large | 140 | 105 | 35 | 31,9% | 8,6% |
| e5-base | 143 | 110 | 33 | 33,4% | 8,1% |
| gte-large | 162 | 113 | 49 | 34,3% | 12,0% |

La soglia F1 privilegia il recall: tutti i modelli producono più falsi positivi che falsi negativi. I generalisti hanno soglie più basse (0,35–0,40) e quindi più falsi positivi e meno falsi negativi.

![Tassi di errore per modello.](figure/ErrorAnalysis_rates.png)

### 33.2 Quali record si sbagliano

Deviazione standardizzata media (record sbagliati meno record corretti, su tutti i modelli): `ca` −0,38, `oldpeak` −0,19, `thalach` +0,13, `age` +0,08, `chol` +0,04, `trestbps` 0,00. I record sbagliati hanno meno vasi visibili in fluoroscopia, minore sottoslivellamento ST e frequenza massima più alta: pazienti con segni strumentali meno netti, cioè malati "silenziosi" (falsi negativi) o sani con qualche fattore di rischio (falsi positivi). Molti dei 20 record sbagliati da tutti i modelli hanno `ca`, `slope` o `thal` non registrati.

![Deviazione standardizzata delle variabili numeriche tra record sbagliati e corretti.](figure/ErrorAnalysis_feature_deviation.png)

### 33.3 Il centro come scorciatoia

Due esperimenti (`analisi_aggiuntive.py`) misurano quanto si può prevedere senza informazione clinica:

- **Solo il centro**: assegnando a ogni record la prevalenza del suo centro stimata sugli altri fold, la ROC-AUC è **0,70**.
- **Solo quali campi mancano**: una regressione logistica sui soli indicatori di mancanza dei 9 campi incompleti ottiene **0,74** in CV.

Per separare la componente clinica si calcola l'AUC dentro ciascun centro, dove il centro non può aiutare:

| Centro | Record (training) | Prevalenza | ROC-AUC biomedici | ROC-AUC generalisti |
| --- | --- | --- | --- | --- |
| Cleveland | 248 | 45,6% | 0,873–0,880 | 0,855–0,890 |
| Ungheria | 230 | 36,5% | 0,871–0,908 | 0,854–0,892 |
| Svizzera | 95 | 92,6% | 0,758–0,833 | 0,692–0,781 |
| Long Beach VA | 163 | 74,8% | 0,688–0,699 | 0,637–0,687 |

![ROC-AUC out-of-fold calcolata dentro ciascun centro.](figure/auc_per_centro.png)

Lettura:

- **Dentro Cleveland**, dove quasi nulla manca, gli encoder raggiungono 0,86–0,89: il segnale clinico c'è ed è forte. Qui il miglior modello è un generalista (e5-large, 0,890) e le famiglie non si distinguono.
- **Dentro Ungheria** i valori sono simili, nonostante `ca` manchi quasi sempre; pubmedbert arriva a 0,908.
- **Svizzera e Long Beach** sono molto più difficili: pochi sani (7 in Svizzera), molti dati mancanti.
- L'AUC aggregata (0,85–0,89) è vicina a quella di Cleveland e Ungheria: il centro contribuisce, ma non spiega da solo il risultato.

> *Per la tesi.* Questa analisi risponde in anticipo all'obiezione "il modello riconosce il centro, non la malattia". Riportare la tabella per centro e i due riferimenti (0,70 e 0,74).

## Capitolo 34 — Confronto con modelli tabellari

### 34.1 Perché serve

Senza un riferimento, un'AUC di 0,88 non dice se convertire in testo aiuta o danneggia. Le baseline tabellari usano le colonne originali, gli stessi split e lo stesso protocollo di soglia:

- **Regressione logistica**: numeriche imputate con la mediana del training più indicatori di mancanza, standardizzate; categoriche one-hot con la mancanza come categoria.
- **Gradient boosting** (`HistGradientBoostingClassifier`): gestisce i valori mancanti in modo nativo, iperparametri predefiniti.

### 34.2 Risultati

| Dataset | Modello | ROC-AUC CV | ROC-AUC test | PR-AUC test | Brier test | Precision test | Recall test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Heart Disease | Reg. logistica tabellare | 0,896 | 0,914 | 0,906 | 0,111 | 0,825 | 0,922 |
| Heart Disease | Gradient boosting tabellare | 0,865 | 0,892 | 0,889 | 0,133 | 0,814 | 0,902 |
| Heart Disease | Miglior encoder (pubmedbert) | 0,891 | 0,915 | 0,927 | 0,115 | 0,812 | 0,931 |
| Diabetes130 | Reg. logistica tabellare | 0,618 | 0,644 | 0,170 | 0,079 | 0,158 | 0,448 |
| Diabetes130 | Gradient boosting tabellare | 0,611 | 0,636 | 0,154 | 0,080 | 0,143 | 0,437 |
| Diabetes130 | Miglior encoder in CV (sentence-biobert) | 0,609 | 0,616 | 0,157 | 0,080 | 0,150 | 0,284 |

![Heart Disease: encoder e baseline tabellari a confronto.](figure/baseline_heart.png)

### 34.3 Lettura

- **Heart Disease**: il miglior encoder è alla pari con la regressione logistica tabellare (0,891 contro 0,896 in CV, media dei fold; 0,915 contro 0,914 sul test). La conversione in testo conserva il segnale senza aggiungerne. Con il protocollo standardizzato anche quattro generalisti si avvicinano (0,875–0,884).
- **Gradient boosting** non batte la regressione logistica su nessuno dei due dataset: con pochi dati (Heart) o segnale debole (Diabetes) un modello più flessibile non aiuta.
- Su **Diabetes130** gli encoder restano sotto entrambe le baseline (capitolo 35.4).

> *Per la tesi.* La domanda principale ha una risposta precisa: gli embedding locali supportano la classificazione clinica quanto un modello tabellare classico su un compito con segnale forte. Il vantaggio dell'approccio testuale non è la prestazione, ma l'uniformità (un formato per dataset diversi), la possibilità di accettare descrizioni testuali e l'uso in un'interfaccia conversazionale.

## Capitolo 35 — Risultati su Diabetes130

Su Diabetes130 i sette encoder sono indistinguibili: ROC-AUC tra 0,600 e 0,609 in cross-validation, nessuna differenza significativa al test di DeLong, e tutti sotto la regressione logistica tabellare. Run del 14 novembre 2026 (2 ore e 43 minuti, dominate dagli embedding di 20.000 frasi).

### 35.1 Cross-validation

16.000 record di training, prevalenza 9,0%. Medie bootstrap e intervalli al 95%:

| Modello | Famiglia | Accuracy | Macro-F1 | ROC-AUC |
| --- | --- | --- | --- | --- |
| sentence-biobert | biomedica | 0,712 (0,705–0,719) | 0,512 (0,504–0,520) | 0,608 (0,593–0,624) |
| bioclinicalbert | biomedica | 0,734 (0,727–0,740) | 0,519 (0,511–0,527) | 0,607 (0,592–0,622) |
| e5-large | generalista | 0,700 (0,693–0,707) | 0,505 (0,497–0,512) | 0,604 (0,589–0,620) |
| e5-base | generalista | 0,670 (0,662–0,677) | 0,494 (0,486–0,501) | 0,604 (0,588–0,619) |
| gte-base | generalista | 0,650 (0,643–0,658) | 0,485 (0,477–0,492) | 0,603 (0,587–0,618) |
| gte-large | generalista | 0,656 (0,649–0,663) | 0,490 (0,483–0,498) | 0,602 (0,586–0,617) |
| pubmedbert | biomedica | 0,692 (0,684–0,699) | 0,500 (0,492–0,508) | 0,600 (0,585–0,615) |

Medie per famiglia: biomedici AUC 0,605, generalisti 0,603. PR-AUC tra 0,129 e 0,139 (prevalenza 0,090); Brier 0,081 per tutti, praticamente uguale al riferimento costante π(1 − π) = 0,082. Soglia media τ tra 0,096 e 0,110. C scelto: 0,01 per sei modelli, 0,001 per bioclinicalbert.

Le accuracy variano molto (0,65–0,73) a parità di AUC: dipendono solo da dove cade la soglia, cioè da quanti "a rischio" ciascun modello dichiara. Su questo dataset l'accuracy non dice nulla sulla qualità della rappresentazione.

![Media e intervallo al 95% delle metriche su Diabetes130 (grafico prodotto dalla pipeline).](figure/diab_MeanCI_metrics.png)

![Curve ROC out-of-fold su Diabetes130: le sette curve quasi coincidono.](figure/diab_ROC_comparison.png)

### 35.2 Test set

| Modello | Accuracy | Macro-F1 | ROC-AUC | PR-AUC | Precision | Recall | Brier | τ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gte-base | 0,725 | 0,519 | 0,622 | 0,144 | 0,137 | 0,390 | 0,080 | 0,107 |
| bioclinicalbert | 0,702 | 0,516 | 0,619 | 0,151 | 0,141 | 0,457 | 0,080 | 0,102 |
| sentence-biobert | 0,791 | 0,538 | 0,616 | 0,157 | 0,150 | 0,284 | 0,080 | 0,122 |
| e5-large | 0,632 | 0,482 | 0,615 | 0,145 | 0,126 | 0,521 | 0,080 | 0,092 |
| gte-large | 0,727 | 0,519 | 0,613 | 0,147 | 0,137 | 0,384 | 0,080 | 0,106 |
| pubmedbert | 0,647 | 0,484 | 0,608 | 0,139 | 0,123 | 0,476 | 0,081 | 0,096 |
| e5-base | 0,692 | 0,502 | 0,605 | 0,138 | 0,127 | 0,412 | 0,081 | 0,104 |

4.000 record, prevalenza 9,0%. Precision tra 0,12 e 0,15: su 100 pazienti indicati "a rischio" ne vengono riammessi 12–15, contro 9 della popolazione. Il modello concentra i positivi, ma poco. `sentence-biobert` (0,616) coincide con quanto misurato nel repository `chatbot-forecast` (0,611), che usa lo stesso encoder e lo stesso split.

### 35.3 Test statistici

- **DeLong**: 0 confronti significativi su 21 dopo BH (i p corretti più bassi sono 0,52). Con 16.000 record il test ha molta potenza: se non vede differenze, le differenze tra encoder sono davvero trascurabili.
- **Wilcoxon e t-test sui bootstrap**: 63 confronti su 63 significativi, anche per differenze di AUC di 0,0008. È il caso più chiaro di quanto detto nel capitolo 29.4: con 10.000 ricampionamenti appaiati questi test rilevano qualunque differenza sistematica, per quanto piccola.

> *Per la tesi.* Riportare insieme i due risultati, che non si contraddicono: DeLong risponde a "le AUC sono diverse, tenuto conto dell'incertezza sui pazienti?" (no); Wilcoxon e t-test a "la differenza ha lo stesso segno in quasi tutti i ricampionamenti?" (sì, ma è di millesimi). La conclusione corretta è che gli encoder sono equivalenti su questo compito.

### 35.4 Confronto con i modelli tabellari

| Modello | ROC-AUC CV | ROC-AUC test | PR-AUC test | Precision test | Recall test |
| --- | --- | --- | --- | --- | --- |
| Regressione logistica tabellare | 0,618 | 0,644 | 0,170 | 0,158 | 0,448 |
| Gradient boosting tabellare | 0,611 | 0,636 | 0,154 | 0,143 | 0,437 |
| Miglior encoder in CV (sentence-biobert) | 0,609 | 0,616 | 0,157 | 0,150 | 0,284 |
| Miglior encoder sul test (gte-base) | 0,604 | 0,622 | 0,144 | 0,137 | 0,390 |

La conversione in testo perde circa 1 punto di AUC in cross-validation e 2–4 punti sul test. La causa più probabile è la rappresentazione dei codici di ricovero e dimissione come numeri senza significato per un encoder di linguaggio (capitolo 20.5).

### 35.5 Analisi degli errori

Con una soglia intorno a 0,10 ogni modello dichiara "a rischio" una larga parte dei pazienti: 3.353–4.826 falsi positivi su 14.563 negativi (tasso 23–33%) e 749–909 falsi negativi su 1.437 positivi (52–63%). Deviazione standardizzata tra record sbagliati e corretti: `time_in_hospital` +0,60, `number_inpatient` +0,45, `num_medications` +0,44, `number_diagnoses` +0,41. Gli errori sono soprattutto falsi positivi su pazienti "complessi" (degenze lunghe, molti farmaci, ricoveri precedenti) che poi non vengono riammessi: il modello ha imparato che la complessità aumenta il rischio, ma la complessità da sola non basta a prevedere chi tornerà.

![Deviazione standardizzata delle variabili tra record sbagliati e corretti su Diabetes130.](figure/diab_ErrorAnalysis_feature_deviation.png)

### 35.6 La run precedente con SMOTENC, per confronto

| Modello | AUC CV dichiarata (con SMOTENC) | AUC CV su soli record reali | AUC test (vecchia run) | AUC CV (pipeline definitiva) |
| --- | --- | --- | --- | --- |
| e5-base | 0,718 | 0,505 | 0,502 | 0,604 |
| gte-base | 0,710 | — | 0,502 | 0,603 |
| gte-large | 0,725 | 0,509 | 0,513 | 0,602 |
| e5-large | 0,712 | — | 0,482 | 0,604 |
| bioclinicalbert | 0,760 | 0,520 | 0,529 | 0,607 |
| pubmedbert | 0,759 | 0,517 | 0,533 | 0,600 |
| sentence-biobert | 0,765 | 0,558 | 0,552 | 0,608 |

La vecchia run sovrastimava la CV (0,71–0,77) e, sul test reale, rendeva meno della pipeline definitiva (0,48–0,55 contro 0,61–0,62): addestrare sui record sintetici non solo gonfiava la misura, ma peggiorava anche il modello.

### 35.7 Sintesi dei due dataset

| | Heart Disease | Diabetes130 |
| --- | --- | --- |
| ROC-AUC encoder (CV) | 0,849–0,890 | 0,600–0,609 |
| ROC-AUC encoder (test) | 0,889–0,925 | 0,605–0,622 |
| Regressione logistica tabellare (CV / test) | 0,896 / 0,914 | 0,618 / 0,644 |
| Biomedici contro generalisti (AUC media CV) | 0,882 contro 0,870 | 0,605 contro 0,603 |
| DeLong significativi | 9 su 21 (5 su 12 tra famiglie) | 0 su 21 |
| Miglior encoder | pubmedbert | nessuno distinguibile |

> *Per la tesi.* La risposta alle due domande di ricerca è ora completa. Principale: gli embedding locali conservano il segnale clinico quanto un modello tabellare quando il segnale è forte (Heart Disease) e un po' meno quando è debole (Diabetes130). Secondaria: la specializzazione biomedica dà un vantaggio piccolo su Heart Disease (circa un punto, significativo soprattutto contro il generalista più debole) e nessun vantaggio su Diabetes130, dove le variabili sono amministrative e non c'è lessico clinico da sfruttare.

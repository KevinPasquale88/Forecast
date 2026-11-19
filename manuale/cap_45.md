# Capitolo 45 — Risultati — Diabetes 130-US Hospitals

**Obiettivi del capitolo**

- Avere la tabella completa dei risultati reali per Diabetes130, con intervalli di confidenza.
- Vedere come lo stesso confronto per famiglia dia, qui, una risposta molto più netta che su Heart Disease.
- Capire perché questo dataset, nonostante (o proprio per) i punteggi assoluti più bassi, offre un banco di prova metodologicamente più solido.

**[Fatto]** Come per il capitolo precedente, ogni numero proviene da `datas/diabetes130/reports/report.md` e dai CSV in `datas/diabetes130/results/`, già presenti nel repository (capitolo 43.1).

## 45.1 Tabella completa delle metriche con intervalli di confidenza

**[Fatto]** *Tabella 45.1 — Risultati completi, Diabetes130 (bootstrap 10.000 iterazioni, n=28.428).*

| Modello | Accuracy (IC 95%) | Macro-F1 (IC 95%) | ROC-AUC (IC 95%) |
|---|---|---|---|
| e5-base | 0.6405 (0.6350–0.6461) | 0.6243 (0.6186–0.6299) | 0.7183 (0.7125–0.7243) |
| gte-base | 0.6247 (0.6191–0.6304) | 0.6011 (0.5952–0.6070) | 0.7104 (0.7045–0.7164) |
| gte-large | 0.6432 (0.6377–0.6490) | 0.6266 (0.6209–0.6325) | 0.7249 (0.7190–0.7307) |
| e5-large | 0.6346 (0.6291–0.6403) | 0.6147 (0.6089–0.6204) | 0.7117 (0.7058–0.7176) |
| bioclinicalbert | 0.6742 (0.6688–0.6798) | 0.6643 (0.6588–0.6699) | 0.7602 (0.7547–0.7658) |
| pubmedbert | 0.6693 (0.6637–0.6749) | 0.6551 (0.6493–0.6608) | 0.7590 (0.7534–0.7645) |
| sentence-biobert | 0.6811 (0.6757–0.6864) | 0.6703 (0.6648–0.6758) | 0.7648 (0.7594–0.7702) |

**[Fatto]** Gli intervalli di confidenza sono molto più stretti che su Heart Disease (per esempio, l'AUC di sentence-biobert varia solo fra 0.7594 e 0.7702, un intervallo di 0.0108, contro 0.0475 per lo stesso modello su Heart Disease) — una conseguenza diretta della dimensione del campione: con $n=28.428$ invece di $n=814$, ogni ricampionamento bootstrap (capitolo 36.1) è molto più simile agli altri, e la variabilità stimata si riduce di conseguenza.

**[Fatto]** *Tabella 45.1bis — Valutazione holdout, Diabetes130 (4.000 casi di test mai visti, distribuzione di classe reale, `holdout_evaluation.csv`).*

| Modello | Accuracy | Macro-F1 | ROC-AUC |
|---|---|---|---|
| e5-base | 0.4540 | 0.3840 | 0.5020 |
| gte-base | 0.3975 | 0.3549 | 0.5022 |
| gte-large | 0.4513 | 0.3857 | 0.5133 |
| e5-large | 0.4628 | 0.3905 | 0.4825 |
| bioclinicalbert | 0.4525 | 0.3916 | 0.5288 |
| pubmedbert | 0.4823 | 0.4091 | 0.5327 |
| sentence-biobert | **0.4973** | **0.4208** | **0.5517** |

**[Fatto]** Questa tabella è il risultato singolo più importante — e più scomodo — dell'intero progetto. Sui 4.000 casi mai visti, con la distribuzione di classe reale (11.16% di positivi), ogni modello crolla: l'AUC migliore è 0.5517 (`sentence-biobert`), quella di `e5-large` scende addirittura sotto 0.5 (0.4825, peggio del caso), e ogni accuratezza è lontanissima sia dai valori di cross-validation sia dal baseline banale a maggioranza sulla popolazione reale (88.84%, capitolo 47.3). **[Interpretazione]** Le metriche di cross-validation della Tabella 45.1, misurate ruotando fette dello stesso pool riequilibrato da SMOTE, descrivono un compito molto più facile di quello reale: sul vero problema — individuare l'11% di riammessi precoci nella popolazione così com'è, con soglie e classificatori congelati prima di vedere quei dati — questi embedding, con questa testa lineare, sono quasi al livello del caso. È la dimostrazione concreta del perché un test set indipendente non è un ornamento metodologico: senza questa tabella, il progetto avrebbe raccontato una storia molto più ottimista di quella vera.

## 45.2 Confronto tra famiglie di modelli

**[Fatto: media aritmetica semplice, stessa cautela metodologica del capitolo 44.2]**

| Famiglia | AUC media (dei modelli membri) |
|---|---|
| Generalista (4 modelli) | 0.7163 |
| Biomedica (2 modelli) | 0.7596 |
| Biomedica per frasi (1 modello) | 0.7648 |

**[Fatto]** Il divario descrittivo fra generalisti e biomedici è qui di circa **4.3-4.9 punti percentuali** di AUC — più ampio del 2.4-3.6 già visto su Heart Disease (capitolo 44.2). **[Fatto]** Il test di DeLong conferma questo divario con una nettezza che colpisce: **19 delle 21 coppie possibili sono statisticamente significative** (identiche anche dopo la correzione Benjamini-Hochberg), con due sole eccezioni: gte-base contro e5-large (p=0.4614) e bioclinicalbert contro pubmedbert (p=0.1439, AUC quasi identiche: 0.7602 contro 0.7590, capitolo 41.1). Tutti e 12 i confronti generalista-biomedico sono significativi, senza eccezioni.

> **ATTENZIONE —** su Diabetes130 la risposta alla seconda domanda di ricerca, misurata in cross-validation, è netta: i modelli biomedici (tutti e tre) superano tutti e quattro i modelli generalisti in modo statisticamente solido, senza eccezioni ambigue, coerentemente con una dimensione campionaria che dà al test di DeLong molta potenza. Ma la Tabella 45.1bis impone la qualificazione decisiva: questa superiorità relativa è misurata su un pool bilanciato e **non si traduce in prestazioni utilizzabili sulla distribuzione reale** — i biomedici restano i migliori anche sull'holdout (le tre AUC più alte), ma "migliori" lì significa 0.53-0.55 di AUC, non un sistema clinicamente utile.

## 45.3 Perché questo dataset è metodologicamente più interessante

**[Interpretazione]** Tre ragioni, prese insieme, rendono Diabetes130 un banco di prova più solido di Heart Disease per rispondere alle domande di ricerca del progetto, nonostante (o proprio a causa di) i punteggi assoluti più bassi:

1. **Potenza statistica.** Con $n=28.428$ contro $n=814$, il test di DeLong ha molta più capacità di distinguere differenze reali da variazione casuale (capitolo 45.2) — la conclusione sulla superiorità biomedica poggia qui su basi statistiche molto più solide.
2. **Sbilanciamento reale più marcato.** L'11.16% di classe positiva originale (capitolo 4.2) rende la scelta delle metriche (capitolo 34) e il ruolo di SMOTENC (capitolo 21.2) tutt'altro che un dettaglio tecnico: su un dataset quasi bilanciato come Heart Disease, alcune di queste scelte avrebbero cambiato poco; qui contano davvero.
3. **Regime statistico sicuro per tutti i modelli.** Il capitolo 32.3 ha già mostrato che il rapporto dimensione-embedding/dimensione-training-set è ampiamente favorevole per tutti i modelli su questo dataset (0.045 anche per i 1024 dimensioni) — nessuno dei limiti di overfitting potenziale discussi per Heart Disease si applica qui.

**[Attenzione]** Questo non significa che Diabetes130 sia esente da limiti: il campionamento a 20.000 righe (capitolo 30.1, capitolo 51) e l'esclusione da git degli embedding di training a 1024 dimensioni (capitolo 32.3, rigenerabili ma non scaricabili) restano punti di attenzione specifici — e la Tabella 45.1bis aggiunge il limite più sostanziale di tutti: la distanza fra le prestazioni sul pool bilanciato e quelle sulla popolazione reale.

## Riepilogo

Su Diabetes130, il divario descrittivo fra famiglie biomediche e generaliste (4.3-4.9 punti di AUC) è confermato dal test di DeLong in modo netto: 19 delle 21 coppie di modelli sono statisticamente distinguibili, e tutti i 12 confronti fra famiglie lo sono. Ma la valutazione holdout sulla distribuzione reale ribalta la prospettiva: AUC fra 0.48 e 0.55 per tutti i modelli, quasi al livello del caso — il confronto relativo fra encoder resta valido, la trasferibilità assoluta del sistema no. La dimensione campionaria ampia, lo sbilanciamento reale marcato e il regime statistico sicuro rendono questo dataset il banco di prova più istruttivo del progetto, proprio perché espone questo divario.

## Domande di autoverifica

**1. Perché gli intervalli di confidenza su Diabetes130 sono sensibilmente più stretti che su Heart Disease, a parità di numero di ricampionamenti bootstrap (10.000)?**
Perché l'ampiezza dell'intervallo di confidenza bootstrap dipende dalla dimensione del campione sottostante, non dal numero di ricampionamenti: con $n=28.428$ invece di $n=814$, ogni ricampionamento è statisticamente più simile agli altri, riducendo la variabilità osservata.

**2. Su quante delle 21 coppie di modelli il test di DeLong trova una differenza di AUC statisticamente significativa su Diabetes130, e quali sono le eccezioni?**
19 su 21 (anche dopo la correzione Benjamini-Hochberg). Le eccezioni sono gte-base contro e5-large (p=0.4614) e bioclinicalbert contro pubmedbert (p=0.1439), le cui AUC (0.7602 e 0.7590) sono così vicine da non essere distinguibili nemmeno con questa potenza statistica elevata.

**3. Perché la risposta alla seconda domanda di ricerca è più netta su Diabetes130 che su Heart Disease, pur riguardando lo stesso confronto concettuale?**
Perché la dimensione campionaria molto più grande dà al test di DeLong più potenza statistica per rilevare differenze reali anche quando numericamente contenute — lo stesso tipo di divario descrittivo, su un campione più piccolo come Heart Disease, produce più spesso confronti che non raggiungono la soglia di significatività.

> **MATERIALE PER LA TESI**
> 1. La Tabella 45.1 completa, affiancabile alla Tabella 44.1 del capitolo precedente — riusabile come tabella comparativa nella sezione "Risultati".
> 2. Il conteggio "19 su 21 coppie significative, 12 su 12 fra famiglie", con le eccezioni motivate numericamente, affiancato alla Tabella 45.1bis dell'holdout — la coppia di risultati più citabile della tesi: la superiorità relativa dei biomedici è solida, la trasferibilità assoluta alla popolazione reale no.
> 3. Le tre ragioni per cui Diabetes130 è metodologicamente più solido, con i limiti specifici comunque dichiarati — riusabile per una discussione bilanciata e onesta sulla scelta di quale dataset enfatizzare nelle conclusioni della tesi.

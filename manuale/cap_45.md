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
| e5-base | 0.6170 (0.6114–0.6226) | 0.5838 (0.5780–0.5896) | 0.7051 (0.6991–0.7112) |
| gte-base | 0.6169 (0.6113–0.6226) | 0.5891 (0.5834–0.5949) | 0.6989 (0.6929–0.7049) |
| gte-large | 0.6269 (0.6214–0.6326) | 0.6008 (0.5950–0.6067) | 0.7220 (0.7162–0.7279) |
| e5-large | 0.6273 (0.6216–0.6330) | 0.6013 (0.5955–0.6070) | 0.7131 (0.7071–0.7192) |
| bioclinicalbert | 0.6753 (0.6699–0.6809) | 0.6655 (0.6599–0.6711) | 0.7575 (0.7520–0.7631) |
| pubmedbert | 0.6628 (0.6573–0.6683) | 0.6466 (0.6409–0.6522) | 0.7579 (0.7523–0.7635) |
| sentence-biobert | 0.6832 (0.6778–0.6885) | 0.6715 (0.6660–0.6770) | 0.7678 (0.7625–0.7732) |

**[Fatto]** Gli intervalli di confidenza sono molto più stretti che su Heart Disease (per esempio, l'AUC di sentence-biobert varia solo fra 0.7625 e 0.7732, un intervallo di 0.0107, contro 0.0461 su Heart Disease) — una conseguenza diretta della dimensione del campione: con $n=28.428$ invece di $n=814$, ogni ricampionamento bootstrap (capitolo 36.1) è molto più simile agli altri, e la variabilità stimata si riduce di conseguenza.

## 45.2 Confronto tra famiglie di modelli

**[Fatto: media aritmetica semplice, stessa cautela metodologica del capitolo 44.2]**

| Famiglia | AUC media (dei modelli membri) |
|---|---|
| Generalista (4 modelli) | 0.7098 |
| Biomedica (2 modelli) | 0.7577 |
| Biomedica per frasi (1 modello) | 0.7678 |

**[Fatto]** Il divario descrittivo fra generalisti e biomedici è qui di circa **4.8-5.8 punti percentuali** di AUC — sensibilmente più ampio del 2.5-3 già visto su Heart Disease (capitolo 44.2). **[Fatto]** Il test di DeLong conferma questo divario con una nettezza che Heart Disease non aveva: **20 delle 21 coppie possibili sono statisticamente significative**, l'unica eccezione essendo bioclinicalbert contro pubmedbert (p=0.6793, AUC praticamente identiche: 0.7575 contro 0.7579, capitolo 41.1) — l'unico caso in cui due modelli sono davvero, numericamente, quasi indistinguibili. Ogni altro confronto, incluso quello fra i due modelli generalisti più grandi (gte-large contro e5-large, p<0.0001), raggiunge la significatività statistica.

> **ATTENZIONE —** su Diabetes130, a differenza di Heart Disease, la risposta alla seconda domanda di ricerca è netta: i modelli biomedici (tutti e tre) superano tutti e quattro i modelli generalisti in modo statisticamente solido, senza eccezioni ambigue. La differenza rispetto al quadro più sfumato di Heart Disease (capitolo 44.3) non è una contraddizione: è coerente con una dimensione campionaria molto più grande, che dà al test di DeLong più potenza per rilevare differenze reali anche quando sono numericamente contenute.

## 45.3 Perché questo dataset è metodologicamente più interessante

**[Interpretazione]** Tre ragioni, prese insieme, rendono Diabetes130 un banco di prova più solido di Heart Disease per rispondere alle domande di ricerca del progetto, nonostante (o proprio a causa di) i punteggi assoluti più bassi:

1. **Potenza statistica.** Con $n=28.428$ contro $n=814$, il test di DeLong ha molta più capacità di distinguere differenze reali da variazione casuale (capitolo 45.2) — la conclusione sulla superiorità biomedica poggia qui su basi statistiche molto più solide.
2. **Sbilanciamento reale più marcato.** L'11.16% di classe positiva originale (capitolo 4.2) rende la scelta delle metriche (capitolo 34) e il ruolo di SMOTENC (capitolo 21.2) tutt'altro che un dettaglio tecnico: su un dataset quasi bilanciato come Heart Disease, alcune di queste scelte avrebbero cambiato poco; qui contano davvero.
3. **Regime statistico sicuro per tutti i modelli.** Il capitolo 32.3 ha già mostrato che il rapporto dimensione-embedding/dimensione-training-set è ampiamente favorevole per tutti i modelli su questo dataset (0.045 anche per i 1024 dimensioni) — nessuno dei limiti di overfitting potenziale discussi per Heart Disease si applica qui.

**[Attenzione]** Questo non significa che Diabetes130 sia esente da limiti: il campionamento a 20.000 righe (capitolo 30.1, capitolo 51), l'assenza di un test set finale indipendente (capitolo 33.1, valida per entrambi i dataset) e la mancanza degli embedding a 1024 dimensioni oggi non più recuperabili (capitolo 32.3) restano punti di attenzione specifici di questo dataset.

## Riepilogo

Su Diabetes130, il divario descrittivo fra famiglie biomediche e generaliste (4.8-5.8 punti di AUC) è confermato dal test di DeLong in modo netto: 20 delle 21 coppie di modelli sono statisticamente distinguibili, l'unica eccezione essendo la coppia con AUC praticamente identiche. La dimensione campionaria molto più ampia, l'sbilanciamento reale più marcato, e un regime statistico sicuro per tutti i modelli rendono questo dataset un test più solido delle domande di ricerca del progetto rispetto a Heart Disease — pur con i propri limiti specifici, distinti da quelli già discussi per l'altro dataset.

## Domande di autoverifica

**1. Perché gli intervalli di confidenza su Diabetes130 sono sensibilmente più stretti che su Heart Disease, a parità di numero di ricampionamenti bootstrap (10.000)?**
Perché l'ampiezza dell'intervallo di confidenza bootstrap dipende dalla dimensione del campione sottostante, non dal numero di ricampionamenti: con $n=28.428$ invece di $n=814$, ogni ricampionamento è statisticamente più simile agli altri, riducendo la variabilità osservata.

**2. Su quante delle 21 coppie di modelli il test di DeLong trova una differenza di AUC statisticamente significativa su Diabetes130, e qual è l'unica eccezione?**
20 su 21. L'unica eccezione è la coppia bioclinicalbert-pubmedbert (p=0.6793), le cui AUC (0.7575 e 0.7579) sono così vicine da non essere distinguibili nemmeno con questa potenza statistica elevata.

**3. Perché la risposta alla seconda domanda di ricerca è più netta su Diabetes130 che su Heart Disease, pur riguardando lo stesso confronto concettuale?**
Perché la dimensione campionaria molto più grande dà al test di DeLong più potenza statistica per rilevare differenze reali anche quando numericamente contenute — lo stesso tipo di divario descrittivo, su un campione più piccolo come Heart Disease, produce più spesso confronti che non raggiungono la soglia di significatività.

> **MATERIALE PER LA TESI**
> 1. La Tabella 45.1 completa, affiancabile alla Tabella 44.1 del capitolo precedente — riusabile come tabella comparativa nella sezione "Risultati".
> 2. Il conteggio "20 su 21 coppie significative", con l'unica eccezione motivata numericamente — un risultato pulito e citabile quasi testualmente nella sezione "Risultati" o "Discussione".
> 3. Le tre ragioni per cui Diabetes130 è metodologicamente più solido, con i limiti specifici comunque dichiarati — riusabile per una discussione bilanciata e onesta sulla scelta di quale dataset enfatizzare nelle conclusioni della tesi.

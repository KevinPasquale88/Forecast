# Capitolo 37 — I tre test di significatività

**Obiettivi del capitolo**

- Avere la formula (o la struttura formale) di ciascuno dei tre test usati dal progetto per confrontare due modelli.
- Sapere sotto quale ipotesi nulla ciascun test opera, e cosa significa esattamente rifiutarla.
- Collegare ogni test alla riga di codice esatta che lo esegue, già letta al capitolo 26.

## 37.1 Wilcoxon signed-rank

**[Livello: teoria consolidata del settore]** Dati $n$ coppie di osservazioni accoppiate — qui, i valori bootstrap corrispondenti di due modelli, `scores_a[i]` e `scores_b[i]` per lo stesso indice $i$ di ricampionamento (capitolo 26.1) — il test di Wilcoxon calcola le differenze $d_i = a_i - b_i$, scarta le differenze nulle, assegna un **rango** al valore assoluto $|d_i|$ di ciascuna differenza rimanente (rango 1 alla più piccola, e così via), poi somma i ranghi delle differenze positive ($W^+$) e negative ($W^-$) separatamente:

$$
W = \min(W^+, W^-), \qquad W^+ = \sum_{i:\, d_i > 0} R_i, \quad W^- = \sum_{i:\, d_i < 0} R_i \tag{37.1}
$$

dove $R_i$ è il rango di $|d_i|$. **[Livello: teoria consolidata del settore]** Sotto l'ipotesi nulla $H_0$ ("nessuna differenza sistematica fra le distribuzioni dei due modelli"), $W^+$ e $W^-$ dovrebbero essere approssimativamente uguali; un valore di $W$ molto più piccolo di quanto atteso per caso porta a rifiutare $H_0$. Il test non assume che le differenze $d_i$ seguano una distribuzione normale — si basa solo sui loro ranghi, non sui valori esatti — il che lo rende più robusto quando questa assunzione è dubbia, un caso comune per dati clinici (`docs/STATISTICAL_TESTS.md:26`).

**[Fatto]** `wilcoxon(scores_a, scores_b)` (`statisticaltest.py:35`, da `scipy.stats`) implementa esattamente questo test sulle $B=10.000$ coppie di valori bootstrap di ciascuna coppia di modelli, per ciascuna delle tre metriche.

## 37.2 t-test appaiato

**[Livello: teoria consolidata del settore]** Con le stesse differenze accoppiate $d_i = a_i - b_i$ della Formula 37.1, il t-test appaiato calcola:

$$
t = \frac{\bar{d}}{s_d / \sqrt{n}}, \qquad \bar{d} = \frac{1}{n}\sum_{i=1}^n d_i, \qquad s_d = \sqrt{\frac{1}{n-1}\sum_{i=1}^n (d_i - \bar{d})^2} \tag{37.2}
$$

dove $\bar{d}$ è la media delle differenze e $s_d$ la loro deviazione standard campionaria. Sotto $H_0: \mu_d = 0$ (le medie dei due modelli sono uguali), $t$ segue (approssimativamente, sotto l'assunzione di normalità delle differenze) una distribuzione $t$ di Student con $n-1$ gradi di libertà. **[Livello: teoria consolidata del settore]** Se questa assunzione di normalità regge, il t-test ha più potenza statistica di Wilcoxon — rileva come significative differenze più piccole a parità di dimensione campionaria — ma la sua validità dipende da un'assunzione che Wilcoxon non richiede.

**[Fatto]** `ttest_rel(scores_a, scores_b)` (`statisticaltest.py:48`, da `scipy.stats`) implementa esattamente la Formula 37.2. **[Interpretazione]** Con $n=10.000$ (il numero di ricampionamenti bootstrap, non il numero di pazienti), anche differenze di media minuscole fra due modelli tendono a risultare "statisticamente significative" a entrambi i test — un punto di attenzione già anticipato dal capitolo 1.3 sulla distinzione fra significatività statistica e clinica, che `docs/STATISTICAL_TESTS.md:78-82` discute esplicitamente: una differenza di accuratezza dello 0.5%, con un campione bootstrap così grande, risulterà quasi sempre significativa, ma potrebbe non avere alcuna rilevanza per una decisione clinica reale.

## 37.3 Il test di DeLong

**[Livello: teoria consolidata del settore]** Il test di DeLong confronta due AUC calcolate sugli **stessi** casi (stesse etichette vere), tenendo conto della correlazione che nasce da questa condivisione. La forma generale della statistica di test è uno z-score:

$$
Z = \frac{\widehat{\text{AUC}}_A - \widehat{\text{AUC}}_B}{\sqrt{\widehat{\text{Var}}(\widehat{\text{AUC}}_A) + \widehat{\text{Var}}(\widehat{\text{AUC}}_B) - 2\,\widehat{\text{Cov}}(\widehat{\text{AUC}}_A, \widehat{\text{AUC}}_B)}} \tag{37.3}
$$

**[Livello: teoria consolidata del settore, dettaglio da verificare]** dove le varianze e la covarianza non sono stimate con un ricampionamento, ma con una formula analitica basata sui cosiddetti *componenti strutturali* (o *placement values*) legati alla rappresentazione dell'AUC come statistica di Mann-Whitney — il metodo originale è descritto in DeLong, E.R., DeLong, D.M., & Clarke-Pearson, D.L. (1988), *Comparing the areas under two or more correlated receiver operating characteristic curves: a nonparametric approach*, Biometrics `[DA VERIFICARE — volume, numero di pagina e DOI esatti da confermare prima di citarlo in bibliografia]`. **[Fatto]** In questo progetto, l'intera formula è delegata alla libreria esterna `MLstatkit` (`statisticaltest.py:3,95-102`, capitolo 26.2), non reimplementata: `Delong_test(y_true_a, scores[a]["y_score"], scores[b]["y_score"], return_ci=False, return_auc=True, verbose=0)` restituisce direttamente $Z$, il p-value, e le due AUC.

**[Fatto]** A differenza di Wilcoxon e t-test (applicati alle $B=10.000$ osservazioni bootstrap), il test di DeLong lavora direttamente su `y_score` — i punteggi di probabilità originali del fold di validazione (concatenati su tutti i 5 fold, capitolo 23.3), non su una distribuzione ricampionata. **[Fatto]** Per questo motivo, il codice verifica esplicitamente che `y_true_a` e `y_true_b` coincidano prima di procedere (`statisticaltest.py:91-93`, capitolo 26.2): il test richiede che i due modelli siano valutati esattamente sugli stessi record, una precondizione che Wilcoxon e t-test — applicati a distribuzioni bootstrap generate con lo stesso seme, non a dati originali — non necessitano di verificare esplicitamente.

## Riepilogo

I tre test confrontano coppie di modelli sotto assunzioni diverse: Wilcoxon (Formula 37.1) non assume normalità e si basa sui ranghi delle differenze; il t-test appaiato (Formula 37.2) assume normalità delle differenze e ha più potenza se l'assunzione regge; DeLong (Formula 37.3) è specifico per l'AUC, lavora sui punteggi originali anziché su una distribuzione bootstrap, e tiene conto esplicitamente della correlazione fra modelli valutati sugli stessi casi. Con $B=10.000$ ricampionamenti bootstrap, anche differenze minuscole tendono a risultare statisticamente significative: la distinzione fra significatività statistica e clinica, già introdotta al capitolo 1, qui trova la sua giustificazione tecnica precisa.

## Domande di autoverifica

**1. Perché il test di Wilcoxon si basa sui ranghi delle differenze $|d_i|$ invece che sui loro valori esatti?**
Perché questo lo rende non parametrico: non richiede assumere che le differenze seguano una distribuzione normale, un'assunzione spesso dubbia per dati clinici, a differenza del t-test appaiato che quell'assunzione la richiede per la validità formale della sua distribuzione di riferimento.

**2. Con $n=10.000$ osservazioni bootstrap, perché una differenza di accuratezza dello 0.5% fra due modelli risulta quasi sempre "statisticamente significativa"?**
Perché la potenza statistica di un test cresce con la dimensione campionaria: con un campione così grande, anche differenze di media molto piccole diventano rilevabili come significative, indipendentemente dal fatto che quella differenza abbia un'importanza pratica o clinica.

**3. Perché il test di DeLong, a differenza di Wilcoxon e t-test in questo progetto, richiede una verifica esplicita che le etichette vere dei due modelli coincidano?**
Perché lavora direttamente sui punteggi originali del fold di validazione, non su una distribuzione bootstrap generata con lo stesso seme: la sua validità dipende dal fatto che i due modelli siano stati valutati esattamente sugli stessi record, una condizione che va verificata sui dati reali, non garantita per costruzione come lo è per il ricampionamento bootstrap.

> **MATERIALE PER LA TESI**
> 1. Le Formule 37.1-37.3 con le rispettive ipotesi nulle esplicitate — riusabili integralmente in "Materiali e metodi" per una descrizione rigorosa del protocollo di confronto statistico.
> 2. La distinzione formale fra significatività statistica (garantita quasi sempre da $n=10.000$) e rilevanza clinica — riusabile come argomento metodologico centrale nella sezione "Discussione".
> 3. Il riferimento bibliografico al test di DeLong, marcato esplicitamente da verificare prima della citazione finale — da confermare con WebSearch/WebFetch in Appendice D, poi riusabile come citazione verificata nella tesi.

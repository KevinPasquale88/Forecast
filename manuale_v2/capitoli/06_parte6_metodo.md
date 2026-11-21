# Parte VI — Metodo

## Capitolo 22 — La regressione logistica

### 22.1 Il modello

La regressione logistica stima la probabilità della classe positiva come funzione sigmoide di una combinazione lineare delle variabili:

```latex
p(y = 1 \mid \mathbf{x}) = \sigma(\mathbf{w}^{\top}\mathbf{x} + b) = \frac{1}{1 + e^{-(\mathbf{w}^{\top}\mathbf{x} + b)}}
```

Nel progetto **x** è l'embedding (768 o 1024 numeri), **w** un vettore di pesi della stessa dimensione, b un termine costante. Il confine di decisione (dove p = τ) è un iperpiano nello spazio degli embedding: per questo si parla di classificatore lineare.

Il logaritmo del rapporto di probabilità (log-odds) è lineare: log(p / (1 − p)) = **w**ᵀ**x** + b. Ogni peso dice di quanto cambia il log-odds se la corrispondente dimensione dell'embedding aumenta di 1. Con gli embedding le singole dimensioni non hanno un significato clinico, quindi i pesi non sono interpretabili come in un modello tabellare.

### 22.2 Addestramento

I parametri minimizzano la log-loss (entropia incrociata) più una penalità sulla norma dei pesi:

```latex
\min_{\mathbf{w}, b} \; \frac{1}{2}\lVert\mathbf{w}\rVert^{2} + C \sum_{i=1}^{n} \log\left(1 + e^{-y_i^{\pm}(\mathbf{w}^{\top}\mathbf{x}_i + b)}\right)
```

con y± ∈ {−1, +1}. È la formulazione di scikit-learn: C è l'inverso della forza di regolarizzazione (C piccolo = penalità forte). Il problema è convesso e scikit-learn lo risolve con L-BFGS, un metodo quasi-Newton; `max_iter=2000` dà al risolutore abbastanza iterazioni per convergere.

### 22.3 Regolarizzazione e scala degli ingressi

La penalità L2 riduce i pesi verso zero e controlla l'overfitting quando le dimensioni sono molte rispetto agli esempi (768–1024 dimensioni, 589 record di training per fold su Heart Disease).

La penalità agisce sui pesi, e la grandezza necessaria dei pesi dipende dalla scala degli ingressi: se una dimensione varia di 0,005, serve un peso 20 volte più grande che se varia di 0,1 per ottenere lo stesso effetto, e la penalità su quel peso è 400 volte maggiore. Per questo di solito si standardizzano le variabili prima di una regressione regolarizzata, e si sceglie C con una cross-validation interna. Fino al 14 novembre 2026 la pipeline non faceva né l'una né l'altra cosa: usava C = 1 su vettori grezzi. Il capitolo 8.3 mostra che i vettori delle due famiglie hanno scale molto diverse; il capitolo 32.4 misura l'effetto. Ora ogni encoder viene standardizzato e riceve il suo C, scelto in {0,001; 0,01; 0,1; 1; 10; 100} con una CV interna (`fit_classifier`).

### 22.4 Perché un modello lineare

- È il *linear probe* standard per valutare rappresentazioni (capitolo 3.3).
- Ha pochi iperparametri e si addestra in meno di un secondo.
- Con pochi dati (Heart Disease) un modello più flessibile rischierebbe di più l'overfitting.
- Produce probabilità ragionevolmente calibrate, utili per Brier score e per un chatbot che mostra una percentuale.

Un classificatore non lineare (per esempio gradient boosting sugli embedding, o una piccola rete) potrebbe estrarre più informazione: è un lavoro futuro (capitolo 40).

## Capitolo 23 — Validazione

### 23.1 Hold-out

Una sola divisione in training e test. Semplice, ma con pochi dati la stima dipende molto da quali record finiscono nel test: su 184 record, l'intervallo al 95% di una AUC intorno a 0,9 è largo circa ±0,04.

### 23.2 Cross-validation k-fold

I dati si dividono in k parti (fold); a turno ciascuna fa da validazione e le altre da training. Ogni record viene previsto una volta da un modello che non l'ha visto (predizione *out-of-fold*). La media delle k misure ha meno varianza di un singolo hold-out. Con k = 5 ogni modello si addestra sull'80% dei dati: la stima è leggermente pessimistica rispetto a un modello addestrato su tutto.

### 23.3 Stratificazione

`StratifiedKFold` mantiene in ogni fold la stessa proporzione di positivi del totale. È importante su Diabetes130 (9% positivi): senza stratificazione un fold potrebbe avere sensibilmente meno positivi e la sua AUC sarebbe meno stabile.

### 23.4 Cross-validation annidata

Quando una scelta (iperparametro, soglia) si fa guardando i dati, la scelta va ripetuta dentro ogni fold usando solo il training di quel fold, con una seconda cross-validation interna. Altrimenti la scelta "vede" il fold di validazione e la stima risulta ottimistica (Varma e Simon, 2006; Cawley e Talbot, 2010).

Nel progetto le scelte da annidare sono due, C e la soglia: dentro ogni fold esterno, `choose_C` esegue una CV interna per la regolarizzazione e `out_of_fold_threshold` un'altra per la soglia, entrambe solo sulla parte di training del fold.

### 23.5 Il test set finale

Il 20% di test non entra in nessuna scelta: serve a una misura unica del procedimento completo (soglia out-of-fold + classificatore addestrato su tutto il training). È la stima più vicina a ciò che succede in uso reale, ad esempio nel chatbot.

> *Per la tesi.* Riportare sempre sia la cross-validation (con intervalli, più stabile, base dei test statistici) sia il test set (misura indipendente). Se divergono molto, c'è un problema: è così che è emerso il leakage da SMOTENC su Diabetes130.

## Capitolo 24 — Data leakage

### 24.1 Definizione

C'è *leakage* quando durante addestramento o selezione del modello entra informazione che in uso reale non sarebbe disponibile, o che appartiene ai dati usati per valutare. Il risultato è una stima ottimistica, a volte di molto. Kaufman et al. (2012) ne danno una definizione formale; Kapoor e Narayanan (2023) mostrano che è una delle cause più diffuse di risultati non riproducibili nella ricerca basata su machine learning, e propongono una tassonomia.

### 24.2 Le forme incontrate nel progetto

| Forma | Dove era | Effetto | Correzione |
| --- | --- | --- | --- |
| Preprocessing prima della divisione (oversampling) | SMOTENC sull'intero training, poi CV | Diabetes: AUC CV 0,76 contro 0,55 reale | Nessun oversampling |
| Scelta sui dati di valutazione (soglia) | τ scelta sulle etichette del fold di validazione | Accuracy e F1 ottimistiche | τ da CV interna |
| Statistiche stimate sul test (imputazione) | Rischio potenziale se si imputava il test con le sue statistiche | Test non indipendente | Statistiche dal solo training, poi nessuna imputazione |
| Stessa unità in training e test (paziente) | Più ricoveri dello stesso paziente in Diabetes130 | Il modello riconosce il paziente | Un ricovero per paziente |
| Scorciatoia nei dati (centro, mancanza) | Heart Disease: "not recorded" legato al centro e alla prevalenza | Parte del segnale non è clinico | Dichiarata e misurata (capitolo 33) |

### 24.3 Il caso SMOTENC in dettaglio

SMOTENC crea un record sintetico prendendo un record della classe minoritaria, uno dei suoi k vicini (k = 5) della stessa classe, e interpolando le variabili numeriche tra i due; per le categoriche usa il valore più frequente tra i vicini (capitolo 25).

Applicato prima della cross-validation, ogni record sintetico finisce in un fold, mentre i record reali da cui è stato generato sono, quasi sempre, in altri fold. Il classificatore vede nel training record molto simili a quelli che deve prevedere in validazione. In più, i record sintetici hanno caratteristiche proprie (combinazioni di valori "medie") che li rendono riconoscibili come gruppo, e tutti appartengono alla classe positiva.

I numeri su Diabetes130, ricalcolati dalle predizioni out-of-fold della run con SMOTENC (sentence-biobert):

| Insieme | ROC-AUC |
| --- | --- |
| CV dichiarata (reali + sintetici) | 0,765 |
| CV, solo record reali | 0,558 |
| Negativi reali contro positivi sintetici | 0,794 |
| Test set reale | 0,552 |

La terza riga è la prova: il modello distingueva bene i positivi sintetici dai negativi reali, ma non i positivi reali.

> *Per la tesi.* Questo esempio vale un paragrafo nella discussione: mostra un errore comune, spiega il meccanismo, lo quantifica e lo corregge. Una commissione lo apprezzerà più di un risultato apparentemente migliore.

## Capitolo 25 — Sbilanciamento delle classi

### 25.1 Il problema

Con il 9% di positivi, un modello che predice sempre "no" ha accuratezza 91%. Il problema non è il classificatore (la regressione logistica stima comunque probabilità sensate), ma la regola di decisione e le metriche: a soglia 0,5 quasi nessuno supera la soglia, e l'accuratezza premia l'inerzia.

### 25.2 Rimedi

| Rimedio | Come | Effetto sulle probabilità |
| --- | --- | --- |
| Oversampling (copie o SMOTE) | Più esempi della classe rara nel training | Distorce: il modello crede che la classe rara sia più frequente |
| Undersampling | Meno esempi della classe frequente | Distorce e butta dati |
| Pesi di classe (`class_weight="balanced"`) | Errori sulla classe rara pesano di più nella log-loss | Distorce in modo simile all'oversampling |
| Spostamento della soglia | Si addestra sui dati reali e si sceglie τ sotto 0,5 | Nessuna distorsione: le probabilità restano calibrate |

### 25.3 SMOTE e SMOTENC

SMOTE (Chawla et al., 2002) genera un punto sintetico x_new = x_i + λ(x_j − x_i), con x_j uno dei k vicini di x_i nella classe minoritaria e λ uniforme in [0, 1]. SMOTENC estende il metodo a dati misti: le distanze tra vicini includono le categoriche, e il valore categorico del sintetico è il più frequente tra i vicini. Se usato, va applicato solo al training di ogni fold, dopo la divisione (in scikit-learn con una `Pipeline` di imbalanced-learn).

### 25.4 La scelta del progetto

Il progetto addestra sui dati reali e sposta la soglia. Le probabilità restano interpretabili (la probabilità media predetta su Diabetes130 è vicina alla prevalenza del 9%), il che è importante per un chatbot che le mostra all'utente.

## Capitolo 26 — La soglia di decisione

### 26.1 Criteri

| Criterio | Definizione | Quando ha senso |
| --- | --- | --- |
| 0,5 | Positivo se p ≥ 0,5 | Classi bilanciate, costi uguali, probabilità calibrate |
| Massimo F1 | τ che massimizza l'F1 della classe positiva | Classe positiva rara e interesse a trovarla senza troppi falsi allarmi |
| Indice di Youden | τ che massimizza sensibilità + specificità − 1 | Dare uguale peso alle due classi |
| Costi espliciti | τ = C_FP / (C_FP + C_FN) con probabilità calibrate | Quando si conoscono i costi clinici degli errori |
| Vincolo clinico | τ che garantisce una sensibilità minima (es. 90%) | Screening: non perdere i malati |

Il progetto usa il massimo F1. È una scelta statistica: F1 ignora i veri negativi e dà uguale peso a precision e recall. In clinica la soglia andrebbe concordata con i medici in base ai costi degli errori; va dichiarato.

### 26.2 Dipendenza dalla prevalenza

La soglia F1-ottima scende con la prevalenza: 0,42–0,53 su Heart Disease (55% positivi), circa 0,10–0,12 su Diabetes130 (9%). Una soglia di 0,12 non significa che il modello sia "insicuro": significa che, con il 9% di base, un paziente al 12% è già più a rischio della media.

### 26.3 Perché out-of-fold

Scegliere τ sugli stessi dati su cui si valuta gonfia accuracy e F1 (la soglia si adatta al rumore di quel fold). Scegliere τ sulle predizioni del training su sé stesso è ancora peggio: il modello è troppo sicuro sui dati che ha visto. I punteggi out-of-fold sono la via corretta: ogni punteggio viene da un modello che non ha visto quel record, come succederà in uso reale.

## Capitolo 27 — Metriche

### 27.1 Matrice di confusione

| | Predetto positivo | Predetto negativo |
| --- | --- | --- |
| **Realmente positivo** | Veri positivi (TP) | Falsi negativi (FN) |
| **Realmente negativo** | Falsi positivi (FP) | Veri negativi (TN) |

Da qui:

- **Sensibilità (recall)** = TP / (TP + FN): quota di malati trovati.
- **Specificità** = TN / (TN + FP): quota di sani riconosciuti.
- **Precisione (PPV)** = TP / (TP + FP): quota di allarmi giusti.
- **NPV** = TN / (TN + FN): quota di "tranquilli" giusti.
- **Accuracy** = (TP + TN) / totale.

### 27.2 F1 e macro-F1

```latex
F_1 = \frac{2 \cdot \mathrm{precision} \cdot \mathrm{recall}}{\mathrm{precision} + \mathrm{recall}}
```

La media armonica penalizza lo squilibrio: con precision 0,15 e recall 0,30 l'F1 è 0,20. Il **macro-F1** è la media degli F1 delle due classi: dà peso anche alla classe negativa. Su Diabetes130 un macro-F1 di 0,53 combina un F1 alto sui negativi (circa 0,87) e uno basso sui positivi (circa 0,20).

### 27.3 Curva ROC e AUC

La curva ROC traccia la sensibilità contro 1 − specificità al variare della soglia. L'area sotto la curva (AUC) è la probabilità che un positivo scelto a caso abbia un punteggio più alto di un negativo scelto a caso: equivale alla statistica U di Mann-Whitney normalizzata (Hanley e McNeil, 1982).

```latex
\mathrm{AUC} = \frac{1}{n_{+} n_{-}} \sum_{i \in +} \sum_{j \in -} \left[ \mathbb{1}(s_i > s_j) + \tfrac{1}{2}\mathbb{1}(s_i = s_j) \right]
```

È indipendente dalla soglia e dalla prevalenza: per questo è la metrica principale del confronto. Riferimenti indicativi in ambito clinico: 0,5 nessuna discriminazione, 0,7–0,8 accettabile, 0,8–0,9 buona, oltre 0,9 eccellente.

### 27.4 Curva precision-recall e average precision

Con classi rare l'AUC può apparire buona anche quando, in pratica, quasi tutti gli allarmi sono falsi. La curva precision-recall e la sua area (calcolata come *average precision*) misurano la qualità sulla classe positiva; il riferimento casuale è la prevalenza, non 0,5 (Saito e Rehmsmeier, 2015). Su Diabetes130 una PR-AUC di 0,15 contro una prevalenza di 0,09 significa che il modello concentra i positivi, ma poco.

### 27.5 Brier score e calibrazione

```latex
\mathrm{BS} = \frac{1}{n}\sum_{i=1}^{n} (p_i - y_i)^2
```

Il Brier score (Brier, 1950) è l'errore quadratico medio tra probabilità ed esito: 0 è perfetto, e un modello che predice sempre la prevalenza π ottiene π(1 − π) (0,247 su Heart Disease, 0,082 su Diabetes130). Combina discriminazione e calibrazione: un modello calibrato è quello per cui, tra i pazienti a cui assegna il 30%, circa il 30% ha l'esito. Su Diabetes130 un Brier di 0,080 è appena sotto il riferimento costante 0,082: altra conferma che il segnale è debole. La calibrazione si studia meglio con curve di calibrazione (Van Calster et al., 2019), non ancora prodotte dal progetto.

## Capitolo 28 — Bootstrap e intervalli di confidenza

### 28.1 L'idea

Il bootstrap (Efron, 1979) stima la variabilità di una statistica ricampionando i dati con reinserimento: si estraggono n record dagli n disponibili (alcuni più volte, altri mai), si ricalcola la statistica, e si ripete B volte. La distribuzione dei B valori approssima quella che si otterrebbe con campioni nuovi dalla stessa popolazione.

### 28.2 Intervalli percentili

L'intervallo al 95% è dato dal 2,5° e dal 97,5° percentile dei valori bootstrap. È il metodo più semplice; esistono varianti più accurate (BCa) che correggono distorsione e asimmetria (Efron e Tibshirani, 1993). Con B = 10.000 l'errore dovuto al numero finito di ricampionamenti è trascurabile.

### 28.3 Cosa misura e cosa no

Nel progetto si ricampionano le predizioni out-of-fold già calcolate: l'intervallo cattura la variabilità dovuta a **quali pazienti** si osservano, non quella dovuta all'**addestramento** (un modello addestrato su un altro campione darebbe punteggi diversi). È quindi un intervallo un po' stretto rispetto all'incertezza totale. Una CV ripetuta con semi diversi stimerebbe anche la seconda componente.

### 28.4 Bootstrap appaiato

Con lo stesso seme (42) per tutti i modelli, il campione bootstrap k contiene gli stessi pazienti per ogni modello. Le differenze tra modelli si possono allora studiare campione per campione: è il presupposto dei test della sezione seguente.

## Capitolo 29 — Test statistici

### 29.1 Il quadro

Un test statistico valuta se una differenza osservata è compatibile con l'ipotesi nulla di "nessuna differenza". Il p-value è la probabilità di osservare una differenza almeno così grande se l'ipotesi nulla fosse vera. Sotto 0,05 la differenza si dice significativa. Significatività non è rilevanza: con campioni grandi anche differenze trascurabili risultano significative, quindi va sempre riportata anche la dimensione dell'effetto.

### 29.2 Wilcoxon signed-rank

Test non parametrico per dati appaiati (Wilcoxon, 1945). Procedura: si calcolano le differenze d_k tra i due modelli su ogni campione bootstrap, si ordinano i loro valori assoluti, si sommano i ranghi delle differenze positive (W⁺) e negative (W⁻). Sotto l'ipotesi nulla (differenze simmetriche attorno a zero) W⁺ e W⁻ hanno la stessa distribuzione; con molte coppie la statistica è approssimata da una normale. Non assume che le differenze siano normali.

### 29.3 t-test appaiato

```latex
t = \frac{\bar{d}}{s_d / \sqrt{n}}
```

dove d̄ e s_d sono media e deviazione standard delle differenze, n il numero di coppie. Sotto l'ipotesi nulla (differenza media zero) e con differenze circa normali, t segue una distribuzione t di Student con n − 1 gradi di libertà. Con n = 10.000 la normalità delle medie è garantita dal teorema del limite centrale.

### 29.4 Come leggere Wilcoxon e t-test sui bootstrap

Con n = 10.000, s_d / √n è minuscolo: anche una differenza media di 0,001 produce t enormi e p-value prossimi a zero. Su Heart Disease tutte le 63 comparazioni sono significative con entrambi i test, compresa la più piccola (0,0012). I test rispondono correttamente alla domanda "la differenza ha lo stesso segno nella grande maggioranza dei ricampionamenti?", ma la loro potenza dipende da B, che si sceglie arbitrariamente.

In tesi vanno quindi presentati come conferma della stabilità di una differenza, sempre accanto alla differenza media e agli intervalli, e completati da DeLong per l'AUC. Per un confronto tra modelli basato sulle ripetizioni di addestramento esistono anche il t-test corretto di Nadeau e Bengio (2003) e il 5×2 cv test di Dietterich (1998).

### 29.5 DeLong

DeLong, DeLong e Clarke-Pearson (1988) propongono un test per confrontare due AUC calcolate sugli stessi pazienti. L'AUC è una statistica U; per ogni positivo i e negativo j si definiscono le "componenti strutturali":

```latex
V_{10}(i) = \frac{1}{n_{-}}\sum_{j} \psi(s_i, s_j), \qquad V_{01}(j) = \frac{1}{n_{+}}\sum_{i} \psi(s_i, s_j)
```

con ψ = 1 se s_i > s_j, 1/2 in caso di parità, 0 altrimenti. Dalle loro varianze e covarianze tra i due modelli si stima la varianza della differenza delle AUC, e si costruisce z = (AUC_A − AUC_B) / √Var, confrontata con una normale standard. Il test tiene conto della correlazione tra i due modelli (stessi pazienti) ed è lo standard per confrontare AUC in letteratura clinica.

### 29.6 Confronti multipli: Benjamini-Hochberg

Con m test e soglia 0,05, ci si aspettano in media 0,05·m falsi positivi se nessuna differenza fosse reale. Bonferroni controlla la probabilità di anche un solo falso positivo (soglia 0,05/m), ma è molto conservativo. Benjamini e Hochberg (1995) controllano invece il *false discovery rate*, la quota attesa di falsi positivi tra i risultati dichiarati significativi:

```latex
p^{BH}_{(k)} = \min_{j \ge k} \min\left(1, \frac{m}{j}\, p_{(j)}\right)
```

con i p-value ordinati p₍₁₎ ≤ … ≤ p₍ₘ₎. Il progetto riporta sia i p-value grezzi sia quelli corretti.

## Capitolo 30 — UMAP

UMAP (McInnes, Healy, Melville, 2018) proietta dati ad alta dimensione in 2D conservando soprattutto la struttura locale: costruisce un grafo dei vicini nello spazio originale e cerca un disegno 2D con un grafo simile. Nel progetto proietta i dati tabellari standardizzati del training, colorati per classe.

Cosa può dire: se i due gruppi sono visibilmente separati, il problema ha struttura semplice. Cosa non può dire: distanze tra gruppi lontani, densità e forma globale non sono affidabili; un grafico UMAP non misura l'accuratezza di un classificatore. Va usato come illustrazione, non come prova.

![UMAP dei dati tabellari standardizzati del training di Heart Disease (colore: classe).](figure/UMAP_Preprocessed_Data.png)

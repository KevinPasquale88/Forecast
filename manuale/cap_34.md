# Capitolo 34 — Le tre metriche del progetto

**Obiettivi del capitolo**

- Avere la formula esatta di accuratezza, F1 macro e ROC-AUC, con il rimando alla riga di codice che le calcola.
- Sapere, per ciascuna, in quale caso concreto di questo progetto potrebbe ingannare.
- Interpretare correttamente il valore di soglia $\tau$ che compare accanto a queste tre metriche nei risultati.

**[Fatto]** `classification.py:39-41` calcola, per ogni fold e ogni modello, esattamente tre metriche — nessuna quarta, nessuna metrica di regressione come MAE o RMSE, perché questo è un problema di classificazione, non di previsione di un valore continuo (capitolo 1).

## 34.1 Accuracy

**[Livello: teoria consolidata del settore]** L'accuratezza è la proporzione di previsioni corrette sul totale:

$$
\text{Accuracy} = \frac{VP + VN}{VP + VN + FP + FN} \tag{34.1}
$$

dove $VP$, $VN$, $FP$, $FN$ sono i quattro esiti della matrice di confusione già definiti al capitolo 4.3. **[Fatto]** `accuracy_score(y_val, y_pred)` (`classification.py:39`, da `sklearn.metrics`) implementa esattamente questa formula.

> **ATTENZIONE —** l'accuratezza inganna precisamente quando le classi sono sbilanciate (capitolo 4.2): su Diabetes130 (11.16% di classe positiva), un classificatore che rispondesse *sempre* "non riammesso" otterrebbe un'accuratezza dell'88.84% — un numero che sembra ottimo ma che non ha imparato assolutamente nulla di utile. È precisamente per questo che il capitolo 47 costruisce un modello di riferimento banale: senza un termine di paragone esplicito, un'accuratezza dell'85% su Diabetes130 potrebbe sembrare un successo quando è, in realtà, appena sopra la soglia della cosa più ovvia possibile.

## 34.2 Macro-F1

**[Livello: teoria consolidata del settore]** L'F1 è la media armonica di precisione e recall:

$$
F1 = 2 \cdot \frac{\text{precisione} \cdot \text{recall}}{\text{precisione} + \text{recall}}, \qquad \text{precisione} = \frac{VP}{VP+FP}, \qquad \text{recall} = \frac{VP}{VP+FN} \tag{34.2}
$$

**[Fatto]** `f1_score(y_val, y_pred, average='macro')` (`classification.py:40`) non calcola una singola F1: calcola l'F1 separatamente per la classe 0 e per la classe 1, poi ne fa la **media aritmetica semplice**, non pesata per il numero di esempi di ciascuna classe (`average='macro'`, in contrasto con `average='weighted'`, che pesare per frequenza, o `average='binary'`, che riporta solo l'F1 della classe positiva).

> **ATTENZIONE —** su un dataset sbilanciato come Diabetes130, la media macro dà lo **stesso peso** alla F1 della classe minoritaria (11.16% dei casi) e alla F1 della classe maggioritaria, anche se quest'ultima è calcolata su quasi nove volte più esempi. Questo è, nella maggior parte dei contesti clinici, un pregio della scelta `macro` fatta dal progetto: impedisce che un modello bravo solo sulla classe maggioritaria (facile, per definizione, su un dataset sbilanciato) ottenga un punteggio alto ignorando la classe minoritaria — spesso quella clinicamente più rilevante (i pazienti a rischio di riammissione). Ma inganna in senso opposto se letta distrattamente come "F1 della classe positiva": non lo è, è una media fra le due.

## 34.3 ROC-AUC

**[Livello: teoria consolidata del settore]** La curva ROC (Receiver Operating Characteristic) traccia, al variare della soglia di decisione da 0 a 1, la coppia (tasso di falsi positivi, tasso di veri positivi):

$$
\text{TPR}(\tau) = \frac{VP(\tau)}{VP(\tau)+FN(\tau)}, \qquad \text{FPR}(\tau) = \frac{FP(\tau)}{FP(\tau)+VN(\tau)} \tag{34.3}
$$

**[Fatto]** `plot_roc_comparison()` (`function.py:257-277`, capitolo 24.3) disegna esattamente questa curva per ciascun modello. L'AUC (Area Under the Curve) è l'area sotto quella curva — un numero fra 0.5 (nessuna capacità discriminante, equivalente a indovinare a caso) e 1 (separazione perfetta fra le due classi). **[Livello: teoria consolidata del settore]** L'interpretazione più utile dell'AUC è probabilistica: è la probabilità che il modello assegni un punteggio più alto a un caso positivo scelto a caso rispetto a un caso negativo scelto a caso — una proprietà che dipende solo dall'**ordinamento** relativo dei punteggi, non da una soglia specifica.

**[Fatto]** `roc_auc_score(y_val, y_score)` (`classification.py:41`) riceve `y_score` — il punteggio di probabilità continuo, non `y_pred` — a differenza di accuratezza e F1, che invece dipendono da `y_pred`, cioè da una soglia già applicata. **[Interpretazione]** Questo rende l'AUC l'unica delle tre metriche del progetto **indipendente dalla soglia $\tau$** (capitolo 35): non importa quale soglia venga scelta, l'AUC resta la stessa, perché misura la qualità dell'ordinamento dei punteggi, non una singola classificazione binaria specifica. È anche il motivo per cui il capitolo 26 usa il test di DeLong — specifico per l'AUC — come confronto indipendente dalla scelta (per fold, e potenzialmente ottimistica, capitolo 23.2) della soglia.

> **ATTENZIONE —** l'AUC inganna quando la si legge come "quanto è bravo il modello nella pratica clinica": un'AUC alta dice che il modello *ordina bene* i casi, ma non dice se la soglia effettivamente usata in produzione (capitolo 35) sia quella giusta per il costo relativo di falsi positivi e falsi negativi discusso al capitolo 1.2. Due modelli con la stessa identica AUC possono avere prestazioni molto diverse a una soglia fissata, se la forma delle rispettive curve ROC differisce.

## Riepilogo

Le tre metriche del progetto misurano aspetti diversi e non intercambiabili: l'accuratezza (Formula 34.1) è ingannevole su dati sbilanciati; l'F1 macro (Formula 34.2) pesa equamente le due classi indipendentemente dalla loro frequenza, correggendo parzialmente quel problema; l'AUC (Formula 34.3) è l'unica indipendente dalla soglia di decisione, e misura la qualità dell'ordinamento dei punteggi piuttosto che di una singola classificazione. Nessuna delle tre, da sola, basta a giudicare un sistema di supporto clinico: vanno lette insieme, con la consapevolezza specifica di cosa ciascuna può nascondere.

## Domande di autoverifica

**1. Quale accuratezza otterrebbe, su Diabetes130, un classificatore che prevedesse sempre "non riammesso", e perché questo numero da solo non dice nulla di utile?**
Circa l'88.84%, la proporzione della classe maggioritaria (capitolo 4.2) — un numero alto ottenuto senza che il classificatore abbia imparato a distinguere alcunché fra le due classi, il motivo esatto per cui serve un modello di riferimento banale (capitolo 47) come termine di paragone.

**2. Perché l'F1 macro non va letta come "l'F1 della classe positiva"?**
Perché `average='macro'` calcola l'F1 separatamente per entrambe le classi e ne fa la media aritmetica semplice, non pesata per frequenza: il numero risultante riflette il comportamento del modello su entrambe le classi in egual misura, non solo sulla classe di interesse clinico.

**3. Perché l'AUC è l'unica delle tre metriche del progetto a non dipendere dalla soglia di decisione $\tau$?**
Perché `roc_auc_score()` riceve `y_score` (il punteggio continuo di probabilità), non `y_pred` (l'etichetta binaria già ottenuta applicando una soglia): l'AUC misura la qualità dell'ordinamento relativo dei punteggi fra le due classi, una proprietà indipendente da dove si scelga di tagliare quella scala continua in due.

> **MATERIALE PER LA TESI**
> 1. Le Formule 34.1-34.3 con la traduzione completa dei simboli e il rimando esatto alla riga di codice — riusabili integralmente nella sezione "Materiali e metodi" dedicata alle metriche di valutazione.
> 2. La spiegazione di quando ciascuna metrica inganna, applicata specificamente ai due dataset di questo progetto — riusabile nella sezione "Discussione", per qualificare correttamente ogni numero riportato nei risultati.
> 3. La precisazione sull'indipendenza dell'AUC dalla soglia di decisione, con il collegamento al test di DeLong — riusabile per motivare, in "Materiali e metodi", la scelta di un test specifico per l'AUC oltre a Wilcoxon e t-test.

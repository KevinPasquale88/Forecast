# Capitolo 35 — Soglie di decisione

**Obiettivi del capitolo**

- Capire perché 0.5 è una soglia arbitraria, non una scelta neutra o "di default corretta".
- Avere la formula esatta di ciò che `classification.py` ottimizza quando cerca la soglia migliore.
- Mettere a fuoco, con precisione matematica, il costo nascosto già anticipato ai capitoli 23.2 e 33.3.

## 35.1 Perché 0.5 non basta sempre

**[Livello: teoria consolidata del settore]** Un classificatore binario produce una probabilità continua (Formula 32.1); trasformarla in un'etichetta richiede scegliere un punto di taglio $\tau \in [0,1]$: se $P(y=1\mid\mathbf{x}) \geq \tau$, l'etichetta prevista è 1, altrimenti 0. **[Fatto]** `y_pred = (y_score >= tau).astype(int)` (`classification.py:37`) implementa esattamente questo confronto. Scegliere $\tau = 0.5$ è la convenzione più comune, ma non ha nulla di matematicamente privilegiato: è ottimale solo se i due tipi di errore (falso positivo, falso negativo) hanno lo stesso costo e le due classi sono bilanciate — nessuna delle due condizioni è garantita in generale, e il capitolo 1.2 ha già mostrato che, per entrambi i dataset di questo progetto, i due tipi di errore hanno conseguenze cliniche diverse.

**[Interpretazione]** Abbassare $\tau$ sotto 0.5 rende il modello più "allarmista": più veri positivi catturati (meno falsi negativi), ma anche più falsi positivi. Alzarlo fa l'opposto. La scelta corretta di $\tau$, in un contesto clinico reale, dovrebbe dipendere esplicitamente dal costo relativo dei due errori (capitolo 1.2) — un'informazione che questo progetto non incorpora mai: la soglia scelta ottimizza F1 (capitolo 35.2), una metrica che pesa implicitamente falsi positivi e falsi negativi allo stesso modo, non il costo clinico specifico di questo dominio.

## 35.2 La soglia F1-ottima: formula e codice

**[Fatto]** `classification.py:30-35` cerca, fra tutte le soglie candidate generate da `precision_recall_curve()`, quella che massimizza l'F1 (Formula 34.2) sul fold di validazione:

$$
\tau^\star = \operatorname*{arg\,max}_{\tau \in T} \; F1\big(y_{\text{val}},\, \mathbb{1}[y_{\text{score}} \geq \tau]\big) \tag{35.1}
$$

dove $T$ è l'insieme finito di soglie candidate restituito da `precision_recall_curve(y_val, y_score)` (ogni punto di discontinuità della curva precisione-recall, non un campionamento uniforme di $[0,1]$), e $\mathbb{1}[\cdot]$ è la funzione indicatrice (1 se la condizione è vera, 0 altrimenti) — la stessa operazione di `(y_score >= tau).astype(int)`. **[Fatto]** Il codice calcola l'F1 per ogni soglia candidata con la formula esplicita, non richiamando `f1_score()` in un ciclo (più costoso):
```python
f1_scores = 2 * (precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-6)
best_idx = f1_scores.argmax()
tau = thresholds[best_idx]
```
`argmax()` implementa esattamente l'operatore $\arg\max$ della Formula 35.1: restituisce l'*indice* del valore massimo, non il valore stesso — da cui `thresholds[best_idx]`, non `f1_scores[best_idx]`, per recuperare la soglia corrispondente.

## 35.3 Il costo nascosto della sua ottimizzazione

**[Fatto]** La Formula 35.1 usa $y_{\text{val}}$ — le etichette vere del fold di validazione — sia per calcolare $\tau^\star$ sia, immediatamente dopo, per misurare accuratezza e F1 con quella stessa soglia sullo stesso $y_{\text{val}}$ (già segnalato ai capitoli 23.2 e 33.3, qui reso preciso in una formula). **[Interpretazione]** Il problema, in termini formali, è che $\tau^\star$ non è una costante fissata a priori: è essa stessa una **funzione di $y_{\text{val}}$**, esattamente il campione su cui la prestazione finale viene poi riportata. Confrontala con un'alternativa più rigorosa — mai implementata in questo progetto — in cui la soglia venga scelta su un fold di *calibrazione* separato, distinto sia dal training sia dal fold su cui si riporta la metrica:

$$
\tau^\star_{\text{rigoroso}} = \operatorname*{arg\,max}_{\tau \in T} \; F1\big(y_{\text{calib}},\, \mathbb{1}[y_{\text{score,calib}} \geq \tau]\big), \qquad \text{poi valutato su } y_{\text{val}} \neq y_{\text{calib}} \tag{35.2}
$$

**[Interpretazione]** La differenza fra la Formula 35.1 (usata dal progetto) e la Formula 35.2 (l'alternativa più rigorosa, non implementata) è la fonte esatta dell'ottimismo statistico già discusso: nella Formula 35.1, la soglia è "cucita su misura" per massimizzare la metrica proprio sui dati su cui quella metrica viene poi riportata, un vantaggio che una soglia scelta su dati indipendenti (Formula 35.2) non avrebbe.

> **PROVA TU —** stima tu stesso l'entità di questo ottimismo, senza rieseguire l'intera pipeline: per uno dei modelli già presenti in `datas/heart_disease/results/`, calcola l'F1 che si otterrebbe con la soglia fissa $\tau=0.5$ invece della soglia F1-ottima salvata, usando i file `{model}_y_true.npy` e `{model}_y_score.npy` già presenti. La differenza fra i due numeri è una stima diretta, per quel modello specifico, di quanto la Formula 35.1 abbia effettivamente gonfiato l'F1 riportato rispetto a una soglia scelta senza guardare le etichette di validazione.

## Riepilogo

La soglia di decisione di 0.5 non ha alcun privilegio matematico: è ottimale solo sotto assunzioni di costo ed equilibrio fra classi che questo progetto non verifica mai esplicitamente. La soglia F1-ottima (Formula 35.1) è scelta e valutata sullo stesso fold di validazione — una funzione delle stesse etichette su cui la prestazione viene poi misurata, distinta con precisione formale da un'alternativa più rigorosa (Formula 35.2) che userebbe un fold di calibrazione separato, mai implementata in questo progetto.

## Domande di autoverifica

**1. Sotto quali due condizioni la soglia $\tau=0.5$ sarebbe effettivamente ottimale?**
Se i due tipi di errore (falso positivo, falso negativo) avessero lo stesso costo, e se le due classi fossero bilanciate nella popolazione. Nessuna delle due condizioni è verificata esplicitamente in questo progetto per nessuno dei due dataset.

**2. Cosa restituisce esattamente `f1_scores.argmax()` in `classification.py:34`, e perché il codice usa poi `thresholds[best_idx]` e non `f1_scores[best_idx]`?**
`argmax()` restituisce l'indice della posizione con il valore F1 massimo, non il valore stesso. `thresholds[best_idx]` usa quell'indice per recuperare la soglia corrispondente, che è ciò che serve per classificare nuovi punteggi — il valore massimo di F1 in sé non è più necessario a questo punto del codice.

**3. Qual è la differenza formale precisa fra la Formula 35.1 (usata dal progetto) e la Formula 35.2 (l'alternativa più rigorosa)?**
Nella Formula 35.1 la soglia è scelta e poi valutata sullo stesso insieme $y_{\text{val}}$; nella Formula 35.2 è scelta su un insieme di calibrazione $y_{\text{calib}}$ distinto dall'insieme $y_{\text{val}}$ su cui viene poi valutata — quest'ultima non introduce lo stesso ottimismo statistico perché la soglia non è "cucita su misura" per i dati su cui la prestazione finale viene riportata.

> **MATERIALE PER LA TESI**
> 1. La Formula 35.1 con la spiegazione precisa dell'operatore $\arg\max$ e il rimando al codice — riusabile in "Materiali e metodi" per descrivere con rigore la procedura di scelta della soglia.
> 2. Il confronto formale fra Formula 35.1 e Formula 35.2, con la fonte esatta dell'ottimismo statistico resa esplicita — probabilmente la formalizzazione più utile per la tesi di un limite già discusso più volte nel libro: riusabile integralmente nella sezione "Discussione e limiti".
> 3. L'esercizio pratico per stimare l'entità dell'ottimismo con i dati già presenti nel repository (§35.3) — riusabile come base per una misura quantitativa originale da includere nei risultati o nella discussione della tesi.

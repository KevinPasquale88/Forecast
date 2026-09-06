# Capitolo 32 — La regressione logistica, dalle basi alla riga di codice

**Obiettivi del capitolo**

- Avere la formula completa della regressione logistica, con ogni simbolo tradotto in ciò che rappresenta in questo progetto.
- Sapere cosa minimizza `LogisticRegression.fit()` quando viene chiamato, incluso il ruolo esatto del parametro `C`.
- Capire perché un classificatore lineare su un embedding congelato è una scelta metodologica precisa, non una semplificazione di comodo.

## 32.1 Funzione logistica come probabilità

**[Livello: teoria consolidata del settore]** La regressione logistica calcola prima una combinazione lineare dell'input, poi la comprime in un numero fra 0 e 1 con la funzione logistica (sigmoide):

$$
P(y=1 \mid \mathbf{x}) = \sigma(\mathbf{w}^\top \mathbf{x} + b) = \frac{1}{1 + e^{-(\mathbf{w}^\top \mathbf{x} + b)}} \tag{32.1}
$$

**[Fatto]** In questo progetto, $\mathbf{x}$ è l'embedding di un record clinico (un vettore di 768 o 1024 numeri, capitolo 5.1); $\mathbf{w}$ è un vettore di pesi della stessa dimensione, appreso durante l'addestramento; $b$ è un singolo numero (l'intercetta); $P(y=1 \mid \mathbf{x})$ è ciò che il codice chiama `y_score` (`classification.py:28`, capitolo 23.1). Ogni componente di $\mathbf{w}$ pesa una delle 768 (o 1024) direzioni dello spazio di embedding: la regressione logistica impara, in sostanza, *quali direzioni* di quello spazio sono associate alla classe positiva.

> **SE VIENI DA JAVA —** non esiste, in questo progetto, un solo vettore $\mathbf{w}$ condiviso: `training_classifier()` (capitolo 23) istanzia un `LogisticRegression` nuovo per ciascuno dei sette modelli (`classification.py:16`, dentro il ciclo `for model in models_all`), quindi $\mathbf{w}$ ha una dimensione diversa (768 o 1024, a seconda del modello di embedding) e valori completamente indipendenti per ciascuno — sette problemi di ottimizzazione separati, non uno condiviso.

## 32.2 Funzione di costo e ottimizzazione

**[Livello: teoria consolidata del settore]** `LogisticRegression.fit()` (`classification.py:26`) non sceglie $\mathbf{w}$ e $b$ arbitrariamente: li trova risolvendo un problema di minimizzazione. **[Fatto]** Con la penalizzazione di default di scikit-learn (L2, mai cambiata in questo progetto — verificato: `classification.py:16` chiama `LogisticRegression(max_iter=2000)` senza specificare `penalty`), la funzione minimizzata è, nella notazione della documentazione ufficiale di scikit-learn (con le etichette codificate come $y_i \in \{-1, +1\}$, non $\{0,1\}$ come nei dati salvati su disco — una convenzione puramente interna al solutore):

$$
\min_{\mathbf{w}, b} \;\; \frac{1}{2}\mathbf{w}^\top \mathbf{w} + C \sum_{i=1}^{n} \log\Big(1 + e^{-y_i (\mathbf{w}^\top \mathbf{x}_i + b)}\Big) \tag{32.2}
$$

**[Fatto]** Il primo termine, $\frac{1}{2}\mathbf{w}^\top \mathbf{w}$, è la **penalizzazione L2** (o *ridge*): più grandi sono i pesi, più alto è il costo, il che scoraggia il modello dall'affidarsi in modo estremo a poche direzioni dell'embedding. Il secondo termine è la somma, su tutti gli $n$ esempi di addestramento, della **log-loss** (o *cross-entropy* binaria): penalizza il modello tanto più quanto la sua probabilità prevista si discosta dall'etichetta vera. Il parametro $C$ bilancia i due termini: **[Fatto]** `classification.py:16` non lo specifica mai, quindi resta al default di scikit-learn, $C=1.0$, per tutti e sette i modelli e per entrambi i dataset — un iperparametro reale del progetto, mai reso esplicito né validato, che il capitolo 39 riprende per intero.

**[Fatto]** `max_iter=2000` (l'unico parametro esplicitamente impostato) non è parte della formula: è un limite al numero di iterazioni che l'algoritmo di ottimizzazione (il *solver*, di default `lbfgs` in scikit-learn, non cambiato in questo progetto) può compiere prima di fermarsi comunque, anche se non ha ancora raggiunto una soluzione stabile — un valore più alto del default di libreria (100), presumibilmente scelto perché con dati ad alta dimensionalità (768-1024 colonne) l'ottimizzazione può richiedere più iterazioni per convergere.

## 32.3 Perché lineare su embedding, non una rete profonda

**[Interpretazione]** Un embedding pre-addestrato e mai riaddestrato (capitolo 5, capitolo 22) più un classificatore lineare addestrato sopra è un pattern con un nome riconosciuto in letteratura sulla rappresentazione: **linear probing** — "sondare" con un modello semplicissimo se una rappresentazione già pronta contiene abbastanza segnale per il compito, senza modificare la rappresentazione stessa. È l'opposto del *fine-tuning* (riaddestrare anche l'embedding) o di impilare una rete neurale profonda sopra l'embedding congelato.

**[Fatto]** Per Heart Disease, questa scelta non è solo prudente: è quasi necessaria. Il pool di addestramento dopo SMOTENC è di **814 righe** (capitolo 21.3), circa **651 per fold** di training con 5-fold cross-validation (capitolo 23.1) — verificato caricando i file di embedding con NumPy. Per i due modelli a 1024 dimensioni (gte-large, e5-large), questo significa che il classificatore ha **più pesi da stimare (1024) che esempi su cui stimarli (~651) in ciascun fold**: un rapporto di 1.57, un regime statisticamente delicato in cui un modello con ancora più parametri (una rete neurale profonda) sarebbe quasi certamente destinato all'overfitting (capitolo 2.3) su un dataset di questa scala.

**[Fatto]** Per Diabetes130, la situazione è opposta: il pool post-SMOTENC ha **28.428 righe** (verificato caricando `bioclinicalbert_embeddings.npy`), circa **22.743 per fold** — il rapporto dimensione/esempi per un modello a 1024 dimensioni scende a **0.045**, un regime ben più sicuro. **[Da verificare]** Curiosamente, gli embedding a 1024 dimensioni (e5-large, gte-large) **non esistono più** su disco per questo dataset — né in git (`.gitignore:12-13` li esclude esplicitamente per nome) né in questo ambiente locale (verificato). **[Inferenza]** Alle dimensioni di questo dataset, ciascuno di quei due file peserebbe circa 111 MB, sopra il limite di 100 MB per file imposto da GitHub — una spiegazione plausibile, coerente con la dimensione osservata (87.3 MB) del file analogo a 768 dimensioni nello stesso commit storico. I risultati per questi due modelli su Diabetes130 esistono comunque (`datas/diabetes130/results/`, capitolo 45): sono stati calcolati in un momento in cui gli embedding erano presenti, prima di essere rimossi dal repository.

> **ATTENZIONE —** questa asimmetria — regime $p > n$ per Heart Disease, $p \ll n$ per Diabetes130 — non è mai discussa nella documentazione esistente del progetto, ma cambia sostanzialmente quanto ci si può fidare delle prestazioni dei modelli più grandi sul dataset più piccolo. Il capitolo 51 lo riprende come limite metodologico specifico, distinto da quelli già discussi.

## Riepilogo

La regressione logistica di questo progetto stima, per ciascuno dei sette modelli separatamente, un vettore di pesi che pondera le direzioni dello spazio di embedding, minimizzando una combinazione di penalizzazione L2 e log-loss regolata dal parametro `C` — mai esplicitato, quindi sempre al default `C=1.0`. La scelta di un classificatore lineare su embedding congelati (linear probing) è particolarmente giustificata per Heart Disease, dove il rapporto fra dimensione dell'embedding e dimensione del training set per fold rende un modello più complesso rischioso; per Diabetes130 la stessa scelta è più prudente che necessaria, dato il pool molto più ampio.

## Domande di autoverifica

**1. Cosa rappresentano, in questo progetto, i simboli $\mathbf{w}$ e $b$ della Formula 32.1?**
$\mathbf{w}$ è il vettore di pesi appreso durante l'addestramento, della stessa dimensione dell'embedding (768 o 1024); $b$ è l'intercetta, un singolo numero. Insieme definiscono la combinazione lineare dell'embedding che, passata attraverso la funzione logistica, produce la probabilità stimata della classe positiva.

**2. Perché `C=1.0` è un iperparametro reale del progetto, anche se non compare mai esplicitamente nel codice?**
Perché è il valore di default di scikit-learn per la forza della regolarizzazione L2, applicato automaticamente ogni volta che `LogisticRegression(max_iter=2000)` viene istanziato senza specificare `C` — una scelta implicita quanto una esplicita, semplicemente mai dichiarata né validata.

**3. Perché il rapporto fra dimensione dell'embedding e dimensione del training set per fold è un problema per Heart Disease ma non per Diabetes130?**
Perché Heart Disease ha solo ~651 esempi di training per fold contro le 1024 dimensioni di alcuni embedding (rapporto 1.57, più parametri che esempi), mentre Diabetes130 ne ha ~22.743 (rapporto 0.045) — lo stesso classificatore lineare si trova in un regime statisticamente molto più sicuro su un dataset che in origine, prima del campionamento, era comunque molto più grande.

> **MATERIALE PER LA TESI**
> 1. La Formula 32.1 e la Formula 32.2 con la traduzione completa di ogni simbolo nei termini del progetto — riusabili integralmente in "Materiali e metodi", sezione sul modello.
> 2. L'analisi del rapporto dimensione-embedding/dimensione-training-set per entrambi i dataset, con i numeri esatti verificati — è un'osservazione metodologica originale e ben quantificata: riusabile nella sezione "Discussione e limiti".
> 3. La spiegazione della scomparsa dei file di embedding a 1024 dimensioni per Diabetes130, con l'ipotesi motivata sul limite di dimensione di GitHub — riusabile come nota tecnica sulla riproducibilità, o in Appendice E come domanda da confermare con chi ha scritto il codice.

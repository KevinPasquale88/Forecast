# Capitolo 33 — Come si valida correttamente un modello di classificazione

**Obiettivi del capitolo**

- Sapere a cosa serve, in linea di principio, dividere i dati in training, validazione e test — tre ruoli distinti, non intercambiabili.
- Avere la formula precisa del k-fold stratificato, e sapere perché "stratificato" non è un dettaglio opzionale.
- Riconoscere le forme più comuni di data leakage, e collocarci con precisione i due punti di questo progetto già individuati nei capitoli precedenti.

Questo capitolo tratta la validazione come argomento a sé, indipendente da questo progetto specifico — il tuo prompt originale la chiedeva esplicitamente come argomento di base, e diluirla solo dentro i capitoli sui singoli moduli (Parte V) avrebbe reso più difficile vederne il quadro generale prima dei dettagli.

## 33.1 Train/validation/test: a cosa serve ciascuno

**[Livello: teoria consolidata del settore]** Una pipeline di apprendimento supervisionato (capitolo 2.2) ha, in linea di principio, bisogno di **tre** porzioni di dati distinte, non due:

- Il **training set** addestra il modello: i suoi parametri (i pesi $\mathbf{w}$ e l'intercetta $b$ della Formula 32.1) sono scelti per adattarsi a questi dati.
- Il **validation set** guida le decisioni che un umano (o una procedura automatica) prende *durante* lo sviluppo: quale soglia di decisione usare, quale valore di un iperparametro, quale fra due modelli preferire. Il modello non viene mai addestrato su questi dati, ma le sue prestazioni su di essi influenzano scelte a valle.
- Il **test set** stima, una volta sola e alla fine, quanto il modello — con tutte le decisioni già prese sul validation set — generalizzerà su dati mai visti in nessuna fase precedente. Se il test set viene consultato più di una volta per aggiustare qualcosa, smette di essere un test set: diventa, di fatto, un secondo validation set, e la stima di generalizzazione che fornisce torna a essere ottimista.

**[Fatto]** `preprocessing.py:52` crea esplicitamente tutte e tre le porzioni concettuali: `train_test_split(X, y, test_size=0.2, ...)` produce un `X_test`/`y_test` che gioca il terzo ruolo. **[Fatto]** Non è sempre stato così: per gran parte della storia del progetto quella porzione veniva calcolata e **mai più usata** — il progetto aveva, di fatto, solo due porzioni funzionanti, e ogni cifra riportata derivava dalla sola validazione incrociata. La revisione documentata in `docs/CHANGES.md` §1 ha chiuso il cerchio: oggi il test set è imputato con statistiche del solo training, salvato su disco, embeddato separatamente, e valutato da un modulo dedicato — `holdout_evaluation.py`, fase 7 della pipeline — che addestra un classificatore fresco per modello sul pool di training e riporta accuracy/macro-F1/AUC sul solo test split, dati che né l'addestramento, né la scelta della soglia, né la validazione incrociata hanno mai visto. **[Interpretazione]** I capitoli 44-45 riportano quindi due famiglie di numeri con garanzie diverse: le metriche di cross-validation (medie su 5 fold del pool bilanciato da SMOTE) e le metriche holdout (una sola stima, ma su dati genuinamente mai consultati e con la distribuzione di classe reale) — ed è il confronto fra le due, specialmente su Diabetes130, a essere istruttivo.

## 33.2 K-fold e k-fold stratificato: formula e procedura

**[Livello: teoria consolidata del settore]** Un k-fold suddivide i dati disponibili in $k$ parti (*fold*) di uguale dimensione. Per ciascuna delle $k$ iterazioni, una parte diversa gioca il ruolo di validazione, mentre le restanti $k-1$ parti giocano il ruolo di training:

$$
\text{per } i = 1, \dots, k: \quad \text{addestra su } \bigcup_{j \neq i} D_j, \quad \text{valuta su } D_i \tag{33.1}
$$

dove $D_1, \dots, D_k$ sono le $k$ parti disjunte in cui il dataset $D$ è stato suddiviso. Il risultato finale è tipicamente la media delle $k$ metriche di validazione — esattamente ciò che `classification.py:54-57` calcola (`acc_mean = np.mean([r[0] for r in tmp_results])`, capitolo 23.1). Ogni singolo esempio del dataset finisce, in questo schema, esattamente una volta nel ruolo di validazione e $k-1$ volte nel ruolo di training, mai in entrambi i ruoli nella stessa iterazione.

**[Livello: teoria consolidata del settore]** Un k-fold **stratificato** aggiunge un vincolo alla suddivisione: ogni $D_i$ deve mantenere, il più possibile, la stessa proporzione fra le classi presente nel dataset intero. Senza questo vincolo, con un dataset sbilanciato (capitolo 4.2), una suddivisione puramente casuale potrebbe produrre un fold con una proporzione di classe molto diversa dalle altre — nel caso estremo, un fold senza alcun esempio della classe minoritaria, rendendo impossibile persino calcolare una metrica come l'AUC su quel fold. **[Fatto]** `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` (`classification.py:15`) applica esattamente questo vincolo, con $k=5$.

## 33.3 Data leakage: tassonomia generale e perché è la minaccia più insidiosa

**[Livello: teoria consolidata del settore]** Il **data leakage** (fuga di informazione) è, in generale, qualunque situazione in cui informazione che non dovrebbe essere disponibile al momento della previsione influenza, in modo diretto o indiretto, il processo di addestramento o di valutazione — gonfiando artificialmente le prestazioni misurate rispetto a quelle che il sistema avrebbe davvero su dati nuovi. Si distinguono comunemente alcune forme:

- **Leakage diretto (target leakage):** una feature usata per l'addestramento contiene, di fatto, informazione derivata dall'etichetta stessa (per esempio, una colonna calcolata *dopo* aver già osservato l'esito). Il capitolo 22.1 ha già verificato che questo progetto non lo presenta: nessuna delle funzioni `record_to_text_*()` menziona mai l'etichetta target.
- **Leakage fra train e test (contaminazione dello split):** una trasformazione (scaling, imputazione, bilanciamento) viene calcolata sull'intero dataset *prima* di dividerlo in training e test, così che il training set "vede" indirettamente informazione statistica (medie, varianze) che include anche i dati di test. Il capitolo 21.2 ha già mostrato che questo progetto evita questa forma: imputazione e SMOTENC operano solo su `X_train`, e il test set è imputato riapplicando i valori calcolati sul solo training (`fit_imputation_values`/`apply_imputation`) — una separazione introdotta proprio per non creare questa forma di leakage nel momento in cui il test set è entrato in uso.
- **Leakage nella selezione di iperparametri o soglie:** una decisione (una soglia, un iperparametro) viene scelta guardando le etichette dello stesso insieme di dati su cui poi si riporta la metrica finale. **[Fatto]** Questo progetto **presentava** questa forma, in un punto preciso individuato al capitolo 23.2: la soglia $\tau$ era scelta massimizzando F1 su `y_val`, poi la prestazione (accuratezza, F1) veniva misurata usando quella stessa soglia sullo stesso `y_val`. Non era leakage verso l'addestramento del modello (che restava pulito), ma era esattamente questa terza forma, limitata alla sola soglia. Il codice attuale la elimina scegliendo $\tau$ su una fetta di calibrazione disgiunta (capitolo 23.2, `docs/CHANGES.md` §4); resta qui come esempio concreto — realmente accaduto in questo progetto — di quanto questa forma di leakage sia facile da introdurre senza accorgersene.
- **Leakage temporale:** per dati con una componente temporale, usare informazione futura per prevedere il passato. Non applicabile a questo progetto (nessuna delle due variabili target ha una dimensione temporale nella formulazione usata qui, capitolo 1).

> **ATTENZIONE —** fra le quattro forme elencate, questo progetto ne ha mostrata storicamente una sola, e nella sua variante più lieve: non il leakage diretto (assente, verificato), non la contaminazione train/test (evitata correttamente per SMOTENC e imputazione), ma la fuga di informazione limitata alla scelta della soglia di decisione — oggi corretta nel codice. È importante essere precisi su questo punto quando si scrive la tesi: sopravvalutare la gravità del problema storico (dicendo, per esempio, che "il modello soffriva di data leakage" senza qualificare quale forma) sarebbe impreciso quanto sottovalutarlo, e la storia della sua individuazione e correzione è essa stessa materiale metodologicamente prezioso.

## Riepilogo

Un sistema supervisionato ha bisogno, in linea di principio, di tre porzioni di dati con ruoli distinti; questo progetto oggi le usa tutte e tre — dopo una lunga fase in cui il test set veniva calcolato e sprecato, corretta con l'introduzione di `holdout_evaluation.py`. Il k-fold stratificato garantisce che ogni fold di validazione mantenga la proporzione di classe del dataset intero, un vincolo non opzionale su dati sbilanciati come Diabetes130. Fra le forme comuni di data leakage, questo progetto ne ha presentata storicamente solo la più lieve — la scelta della soglia di decisione sullo stesso fold su cui veniva misurata la prestazione — poi eliminata con la fetta di calibrazione; le forme più gravi (leakage diretto, contaminazione train/test) sono sempre state assenti.

## Domande di autoverifica

**1. Perché un test set consultato più volte durante lo sviluppo smette, di fatto, di essere un test set?**
Perché il suo ruolo distintivo è fornire una stima di generalizzazione mai influenzata da decisioni di sviluppo. Se lo si consulta ripetutamente per aggiustare qualcosa (una soglia, un iperparametro), quelle decisioni cominciano a essere calibrate su di esso, esattamente come farebbero su un validation set — la stima che fornisce torna quindi a essere ottimista.

**2. Perché la stratificazione è particolarmente importante per Diabetes130 rispetto a Heart Disease?**
Perché Diabetes130 ha una classe positiva minoritaria marcata (11.16%, capitolo 4.2): senza stratificazione, un fold generato casualmente potrebbe avere una proporzione di classe molto diversa dal dataset intero, nel caso estremo pochissimi o nessun esempio della classe minoritaria — un problema molto meno probabile su Heart Disease, quasi bilanciato.

**3. Quale delle quattro forme di data leakage elencate in questo capitolo è stata presente in questo progetto, e qual è lo stato attuale?**
Solo la fuga di informazione nella scelta della soglia di decisione, in una versione precedente del codice (capitolo 23.2), oggi corretta con una fetta di calibrazione disgiunta. Sono sempre stati assenti il leakage diretto (nessuna frase generata include mai l'etichetta target, capitolo 22.1) e la contaminazione train/test (imputazione e SMOTENC operano solo sul training set, con valori riapplicati identici al test set, capitolo 21.2); il leakage temporale non è applicabile a questo progetto.

> **MATERIALE PER LA TESI**
> 1. La distinzione fra i tre ruoli training/validation/test, applicata esplicitamente a questo progetto — inclusa la storia del test set prima sprecato e poi recuperato con `holdout_evaluation.py` — riusabile in "Materiali e metodi" per una descrizione precisa e onesta del protocollo sperimentale.
> 2. La Formula 33.1 del k-fold, con la spiegazione della stratificazione — riusabile per la sezione metodologica sulla validazione.
> 3. La tassonomia completa delle forme di data leakage, con la collocazione precisa di questo progetto in una sola di esse — riusabile quasi integralmente nella sezione "Discussione e limiti", per una valutazione critica calibrata e non generica.

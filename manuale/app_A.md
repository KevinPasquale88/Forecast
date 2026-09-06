# Appendice A — Glossario generale

> Solo termini di dominio e di statistica/machine learning. I termini di programmazione generale (variabile, ciclo, eccezione...) non compaiono per costruzione: il libro presuppone che tu li conosca già da Java (capitolo 0).

**Accuratezza (accuracy)** — Proporzione di previsioni corrette sul totale (Formula 34.1). Ingannevole su classi sbilanciate. → capitolo 34.1

**Addestramento (training)** — Fase in cui i parametri di un modello vengono adattati a dati etichettati. → capitolo 2.2

**Baseline** — Modello di riferimento banale usato per stabilire un pavimento minimo di prestazione. → capitolo 47.1

**Bootstrap** — Tecnica di ricampionamento con reinserimento per stimare l'incertezza di una metrica senza assunzioni distributive. → capitolo 36

**Classificazione binaria** — Compito di assegnare un'osservazione a una fra due categorie. → capitolo 4.1

**Curva ROC** — Grafico del tasso di veri positivi contro il tasso di falsi positivi al variare della soglia di decisione. → capitolo 34.3

**Data leakage** — Fuga di informazione che non dovrebbe essere disponibile al momento della previsione, che gonfia artificialmente le prestazioni misurate. Tassonomia: diretto, contaminazione train/test, selezione di soglie/iperparametri, temporale. → capitolo 33.3

**DeLong, test di** — Test statistico per confrontare due AUC correlate, calcolate sugli stessi casi. → capitolo 37.3

**Deviazione standard bootstrap** — Dispersione della distribuzione empirica bootstrap di una metrica (Formula 36.4). → capitolo 36.2

**Duck typing** — (Nota: è un idioma Python, non un termine di dominio, ma incluso perché ricorrente) Verificare la presenza di un comportamento (un metodo) invece del tipo dichiarato di un oggetto. → capitolo 7.2

**Embedding** — Rappresentazione di un testo come vettore numerico di lunghezza fissa, costruita in modo che testi semanticamente simili producano vettori vicini. → capitolo 5.1

**F1 (macro)** — Media aritmetica dell'F1 calcolato separatamente per ciascuna classe (Formula 34.2). → capitolo 34.2

**Falso positivo / falso negativo** — Un caso negativo classificato come positivo / un caso positivo classificato come negativo. → capitolo 4.3

**Famiglia di modelli** — Categoria di un modello di embedding: generalista, biomedico, biomedico per frasi. → capitolo 5.3

**Generalizzazione** — Capacità di un modello di comportarsi bene su dati mai visti durante l'addestramento. → capitolo 2.3

**Imputazione** — Sostituzione di un valore mancante con una stima (mediana per variabili numeriche, moda per categoriali in questo progetto). → capitolo 21.2

**Inferenza** — Applicazione di un modello già addestrato e validato a un input nuovo, di etichetta ignota. → capitolo 2.2

**Intervallo di confidenza (percentile)** — Intervallo costruito dai percentili di una distribuzione bootstrap (Formula 36.3). → capitolo 36.2

**K-fold / k-fold stratificato** — Procedura di validazione che suddivide i dati in k parti, usando ciascuna a turno come validazione; la variante stratificata preserva la proporzione di classe in ogni parte. → capitolo 33.2

**Linear probing** — Addestrare solo un classificatore lineare sopra un embedding pre-addestrato e mai modificato. → capitolo 32.3

**Overfitting / underfitting** — Sovradattamento (basso errore in addestramento, alto su dati nuovi) / sottoadattamento (alto errore su entrambi). → capitolo 2.3

**Pooling (mean pooling)** — Combinazione dei vettori di più token in un unico vettore di frase, tipicamente per media. → capitolo 5.2

**Regolarizzazione L2** — Penalizzazione sulla norma dei pesi di un modello, che scoraggia valori estremi (Formula 32.2). → capitolo 32.2

**ROC-AUC** — Area sotto la curva ROC; probabilità che un caso positivo scelto a caso riceva un punteggio più alto di un caso negativo scelto a caso. → capitolo 34.3

**SMOTE / SMOTENC** — Tecnica di bilanciamento delle classi che genera record sintetici della classe minoritaria; SMOTENC ne è la variante per feature miste numeriche/categoriali. → capitolo 21.2

**Soglia di decisione ($\tau$)** — Valore che separa un punteggio di probabilità in etichetta positiva o negativa. → capitolo 35.1

**Sovrapposizione (overlap) delle famiglie / minacce alla validità** — Interna, esterna, di costrutto, statistica: quattro categorie classiche di limite di uno studio empirico. → capitolo 53.3

**Tokenizzazione** — Suddivisione di un testo in unità più piccole (sotto-parole) prima dell'elaborazione da parte di un modello linguistico. → capitolo 5.2

**Triangolazione metodologica** — Uso di più metodi/test con assunzioni diverse per rafforzare la fiducia in una conclusione quando concordano. → capitolo 26.3

**UMAP** — Tecnica non supervisionata di riduzione di dimensionalità, usata in questo progetto solo per visualizzazione. → capitolo 38

**Validazione** — Fase in cui le prestazioni di un modello già addestrato vengono misurate su dati non usati per l'addestramento, per guidare decisioni di sviluppo. → capitolo 2.2, capitolo 33.1

**Wilcoxon signed-rank, test di** — Test non parametrico per confrontare due campioni accoppiati basato sui ranghi delle differenze. → capitolo 37.1

# Capitolo 53 — Posizionamento rispetto allo stato dell'arte

**Obiettivi del capitolo**
- Collocare con precisione questo progetto nel panorama dei metodi possibili per lo stesso tipo di problema.
- Sapere esattamente cosa questo progetto NON dimostra, per evitare di sovra-generalizzare i suoi risultati in tesi.
- Applicare la tassonomia classica delle minacce alla validità a questo caso specifico, punto per punto.

## 53.1 Tabellare→testo→embedding vs. classificazione tabellare diretta, "linear probing" su embedding congelati

**[Fatto]** Il capitolo 3.3 ha già collocato questo progetto rispetto a tre famiglie di approccio: classificazione tabellare diretta, reti neurali per dati tabellari, testo clinico autentico. Il capitolo 32.3 ha introdotto il termine tecnico per la scelta specifica del progetto — **linear probing**: un embedding pre-addestrato e mai riaddestrato, con solo un classificatore lineare stimato sopra. **[Livello: teoria consolidata del settore]** Questo pattern è diffuso in letteratura sulla rappresentazione come metodo per *valutare* la qualità di un embedding già pronto — non necessariamente come la scelta di massima prestazione assoluta, ma come un modo controllato di isolare "quanto segnale utile è già presente nella rappresentazione", separato dalla capacità di un classificatore complesso di compensare una rappresentazione mediocre con più parametri.

**[Interpretazione]** In questi termini, il progetto risponde a una domanda più ristretta e più precisa di quanto "questo sistema prevede la malattia cardiaca" suggerisca: non "qual è il miglior sistema possibile per diagnosticare la malattia coronarica da dati tabellari", ma "quanto segnale utile per questo compito è già catturato da un embedding testuale pre-addestrato, generalista o biomedico, senza alcun adattamento successivo al dominio specifico". È una domanda scientificamente più modesta e più onesta — e più difendibile in sede di discussione, se presentata come tale.

## 53.2 Cosa NON prova questo progetto

**[Interpretazione]** Alla luce di tutto il libro, un elenco esplicito di ciò che i risultati **non** dimostrano, utile da avere a portata di mano prima di una discussione:

- **Non dimostra che l'approccio tabellare→testo→embedding sia migliore della classificazione tabellare diretta.** Nessun classificatore tabellare diretto è mai stato addestrato in questo progetto (capitolo 1.3, capitolo 47) — solo un baseline banale, non un vero competitor come una regressione logistica diretta sulle 14/19 feature originali o un gradient boosting.
- **Non dimostra che questi risultati generalizzino a testo clinico autentico.** Il testo usato è sintetico, generato da un template fisso (capitolo 3.3, capitolo 22.1), non prosa scritta da un medico.
- **Non dimostra le prestazioni sulla popolazione reale e sbilanciata di origine.** Ogni numero riportato nei capitoli 44-45 riguarda il pool riequilibrato da SMOTENC, non la distribuzione reale (capitolo 47.3, capitolo 51.1).
- **Non dimostra che la superiorità biomedica sia dovuta al dominio del pre-addestramento, e non ad altre differenze fra i modelli** (dimensione, architettura, obiettivo di addestramento) confuse con l'appartenenza a una famiglia — il progetto confronta modelli che differiscono per più di una sola variabile alla volta, un limite di validità interna trattato nel prossimo paragrafo.
- **Non dimostra la robustezza fuori dai due dataset usati.** Due dataset, entrambi statunitensi/europei, entrambi storici (capitolo 29.3, capitolo 30.3): non c'è alcuna base per generalizzare oltre questi due contesti specifici.

## 53.3 Minacce alla validità: interna, esterna, di costrutto, statistica

**[Livello: teoria consolidata del settore]** Una tassonomia diffusa nella ricerca empirica distingue quattro tipi di minaccia alla validità di uno studio. Applicata punto per punto a questo progetto:

**Validità interna** (il confronto misura davvero ciò che dice di misurare, senza spiegazioni alternative?): **[Interpretazione]** il confronto fra famiglie di modelli (capitolo 6.3, capitolo 44-45) confonde il dominio del pre-addestramento con altre variabili — dimensione del modello, architettura esatta, obiettivo di addestramento specifico — che differiscono simultaneamente fra i sette modelli. Non è possibile, con il disegno sperimentale di questo progetto, isolare l'effetto del solo dominio biomedico da questi altri fattori.

**Validità esterna** (i risultati generalizzano oltre questo studio specifico?): **[Fatto]** limitata a due dataset, entrambi storici e di provenienza occidentale (capitolo 29.3, capitolo 30.3), con un campionamento parziale per Diabetes130 (capitolo 30.1). Non generalizzabile ad altri domini clinici, altre popolazioni, o testo clinico autentico invece che sintetico.

**Validità di costrutto** (le metriche misurano davvero il costrutto di interesse — "supporto efficace alla decisione clinica"?): **[Interpretazione]** accuratezza, F1 e AUC (capitolo 34) misurano la capacità discriminante statistica, non l'utilità clinica reale, che dipenderebbe dal costo relativo di falsi positivi e falsi negativi (capitolo 1.2) mai incorporato esplicitamente in nessuna fase della pipeline.

**Validità statistica** (le conclusioni statistiche sono supportate correttamente dai dati?): **[Fatto]** parzialmente minacciata dall'assenza di correzione per confronti multipli (capitolo 39.2, 21 confronti per metrica) e dalla soglia ottimizzata sullo stesso fold di validazione (capitolo 35.3, 51.2) — entrambi limiti già quantificati in questo libro, non solo ipotizzati.

> **ATTENZIONE —** applicare questa tassonomia non è un esercizio distruttivo: ogni studio empirico, in qualunque campo, ha minacce alla validità di qualche tipo. Il punto di una buona sezione critica in tesi non è "dimostrare che il progetto è invalido" — è mostrare che *sai riconoscere* dove sono i limiti, con la stessa precisione con cui hai presentato i risultati positivi.

## Riepilogo

Il progetto si colloca nella tradizione del linear probing su embedding congelati, una domanda di ricerca più modesta e più difendibile di "il miglior sistema possibile per questo compito clinico". Non dimostra la superiorità sulla classificazione tabellare diretta, la generalizzazione a testo clinico autentico, le prestazioni sulla popolazione reale sbilanciata, l'attribuzione causale della superiorità biomedica al solo dominio di pre-addestramento, o la robustezza oltre i due dataset usati. Applicando la tassonomia delle quattro validità, ogni tipo — interna, esterna, di costrutto, statistica — presenta almeno una minaccia concreta e già documentata in questo libro.

## Domande di autoverifica

**1. Perché descrivere questo progetto come "linear probing" invece di "un classificatore di malattia cardiaca" è più preciso e più difendibile in sede di discussione?**
Perché la domanda di ricerca effettivamente testata è più ristretta: quanto segnale utile è già presente in un embedding pre-addestrato e mai adattato al dominio specifico, non quale sia il miglior sistema diagnostico possibile in assoluto — una domanda che richiederebbe confrontarsi anche con approcci non testati qui, come la classificazione tabellare diretta.

**2. Perché il confronto fra famiglie di modelli ha una minaccia alla validità interna, anche assumendo che tutti i calcoli siano corretti?**
Perché i modelli confrontati differiscono per più di una variabile insieme al dominio di pre-addestramento (dimensione, architettura, obiettivo di addestramento specifico): un risultato migliore per la famiglia biomedica non può essere attribuito con certezza al solo dominio, dato che altre differenze fra i modelli potrebbero contribuire.

**3. In quale delle quattro categorie di validità rientra il problema dell'assenza di correzione per confronti multipli?**
Validità statistica: riguarda se le conclusioni statistiche (quali differenze sono "significative") sono supportate correttamente dai dati, dato il numero di test eseguiti simultaneamente — un problema distinto dalla validità interna, esterna o di costrutto.

> **MATERIALE PER LA TESI**
> 1. La riformulazione della domanda di ricerca in termini di "linear probing", con il rimando alla letteratura sulla valutazione delle rappresentazioni — riusabile nell'introduzione o nello stato dell'arte della tesi per calibrare correttamente l'ambizione delle conclusioni.
> 2. L'elenco esplicito di cosa il progetto NON dimostra — riusabile quasi integralmente come premessa alla sezione "Conclusioni", per prevenire sovra-generalizzazioni in sede di discussione.
> 3. L'applicazione punto per punto delle quattro minacce alla validità — riusabile come struttura portante dell'intera sezione "Discussione e limiti" della tesi.

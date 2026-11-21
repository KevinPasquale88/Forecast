# Parte I — Contesto

## Capitolo 1 — Il problema clinico

Il progetto affronta due compiti clinici diversi per natura: riconoscere una malattia già presente (diagnosi di coronaropatia) e prevedere un evento futuro (riammissione ospedaliera entro 30 giorni). La differenza spiega gran parte dei risultati: la diagnosi parte da misure dirette della malattia, la prognosi da informazioni amministrative che descrivono il ricovero solo indirettamente.

### 1.1 La malattia coronarica e come si diagnostica

La malattia coronarica (*coronary artery disease*, CAD) è il restringimento delle arterie che portano sangue al muscolo cardiaco, quasi sempre per aterosclerosi. Quando il restringimento è importante, durante uno sforzo il cuore riceve meno ossigeno di quanto ne serve (ischemia), e il paziente può avvertire dolore toracico (angina).

Lo standard di riferimento per la diagnosi è l'angiografia coronarica: un mezzo di contrasto iniettato nelle coronarie mostra ai raggi X dove le arterie sono ristrette. Nel dataset UCI Heart Disease l'esito dell'angiografia è la variabile `num`: 0 se nessun vaso principale ha un restringimento oltre il 50% del diametro, da 1 a 4 altrimenti. Il progetto lo riduce a una classe binaria (malattia presente o assente).

L'angiografia è invasiva e costosa, quindi prima si usano esami non invasivi. Le variabili del dataset li rappresentano quasi tutti:

| Variabile | Esame o dato | Cosa indica |
| --- | --- | --- |
| `age`, `sex` | Anamnesi | Il rischio cresce con l'età ed è più alto negli uomini che nelle donne prima della menopausa |
| `cp` | Anamnesi del dolore toracico | Angina tipica, atipica, dolore non anginoso, assenza di sintomi |
| `trestbps` | Pressione arteriosa a riposo | Ipertensione, fattore di rischio |
| `chol` | Esame del sangue | Colesterolo sierico, fattore di rischio |
| `fbs` | Esame del sangue | Glicemia a digiuno sopra 120 mg/dl (diabete) |
| `restecg` | Elettrocardiogramma a riposo | Normale, anomalie del tratto ST-T, ipertrofia ventricolare sinistra |
| `thalach`, `exang`, `oldpeak`, `slope` | Test da sforzo (ECG durante esercizio) | Frequenza massima raggiunta, angina indotta, sottoslivellamento del tratto ST, sua pendenza |
| `thal` | Scintigrafia miocardica con tallio | Perfusione normale, difetto fisso (cicatrice), difetto reversibile (ischemia da sforzo) |
| `ca` | Fluoroscopia | Numero di vasi principali (0–3) visibili, cioè con calcificazioni |

Alcune osservazioni utili per la discussione:

- Il **sottoslivellamento del tratto ST** durante lo sforzo (`oldpeak`) è il segno elettrocardiografico classico di ischemia. Una pendenza piatta o discendente (`slope` 2 o 3) è più sospetta di una ascendente.
- Il **dolore "asintomatico"** (`cp = 4`) è, in questo dataset, fortemente associato alla malattia. Sembra controintuitivo, ma riflette chi veniva inviato all'angiografia: pazienti senza dolore tipico ma con altri esami positivi.
- `ca` e `thal` sono tra le variabili più predittive, ma sono anche quelle che mancano più spesso (capitolo 19): richiedono esami che non tutti i centri eseguivano.

### 1.2 La riammissione ospedaliera a 30 giorni

Una riammissione è un nuovo ricovero dello stesso paziente poco dopo la dimissione. Entro 30 giorni viene spesso letta come segno di una dimissione prematura, di una terapia inadeguata o di un follow-up mancato. Negli Stati Uniti il *Hospital Readmissions Reduction Program*, introdotto dall'Affordable Care Act del 2010 e in vigore dal 2012, riduce i rimborsi agli ospedali con tassi di riammissione a 30 giorni superiori all'atteso per alcune condizioni. Da qui l'interesse per modelli che identifichino i pazienti a rischio prima della dimissione.

Il dataset Diabetes 130-US Hospitals raccoglie ricoveri di pazienti diabetici. Il diabete è rilevante perché è frequente tra i ricoverati e perché la sua gestione durante il ricovero (misura dell'emoglobina glicata, aggiustamento della terapia) può influire sull'esito. Lo studio che ha pubblicato il dataset (Strack et al., 2014) trovò che la misura dell'HbA1c durante il ricovero era associata a un tasso di riammissione più basso.

Prevedere la riammissione è difficile per ragioni note in letteratura: dipende da fattori che i dati amministrativi non contengono, come l'aderenza alla terapia, il supporto a domicilio, le condizioni socioeconomiche, l'accesso alle cure dopo la dimissione. Modelli pubblicati su dataset di questo tipo raggiungono di solito ROC-AUC tra 0,6 e 0,7. Il risultato del progetto (circa 0,61–0,64) è in linea.

> *Per la tesi.* La differenza tra i due compiti è un buon filo conduttore: Heart Disease misura quanto bene gli embedding conservano un segnale clinico forte; Diabetes130 misura cosa succede quando il segnale è debole e le variabili sono amministrative.

### 1.3 Supporto alle decisioni cliniche

Un modello che stima un rischio non sostituisce il medico: è uno strumento di supporto alle decisioni (*clinical decision support*). Perché sia utile servono tre proprietà, che torneranno nei capitoli di metodo:

1. **Discriminazione**: distinguere chi avrà l'esito da chi non lo avrà (misurata da ROC-AUC e PR-AUC, capitolo 27).
2. **Calibrazione**: una probabilità del 30% deve corrispondere a circa 30 casi su 100 (misurata in parte dal Brier score).
3. **Utilità decisionale**: la soglia oltre cui si agisce deve riflettere il costo di falsi positivi e falsi negativi (capitolo 26).

Il progetto misura bene la prima, in parte la seconda, e sceglie la soglia con un criterio statistico (massimo F1) e non clinico. È un limite da dichiarare (capitolo 39).

## Capitolo 2 — Machine learning supervisionato: i concetti che servono

### 2.1 Il compito

Nell'apprendimento supervisionato si dispone di esempi già etichettati: coppie (x, y) dove x descrive un caso (qui un record clinico, poi il suo embedding) e y è l'esito noto. L'obiettivo è una funzione f che, dato un nuovo x, predica y. Quando y ha due valori il compito è una **classificazione binaria**; il modello di solito restituisce una probabilità p = P(y = 1 | x), e una **soglia** τ la trasforma in decisione (positivo se p ≥ τ).

### 2.2 Generalizzazione, overfitting, underfitting

Un modello serve se funziona su casi nuovi, non su quelli visti in addestramento. La differenza tra l'errore sui dati di addestramento e quello su dati nuovi misura quanto il modello ha "imparato a memoria" (**overfitting**). L'opposto è l'**underfitting**: un modello troppo semplice per cogliere il segnale.

Il compromesso si descrive con la decomposizione **bias-varianza**: un modello semplice sbaglia in modo sistematico (bias alto) ma stabile; uno complesso si adatta ai dati (bias basso) ma cambia molto da un campione all'altro (varianza alta). La regolarizzazione (capitolo 22) è lo strumento per controllare la varianza.

Nel progetto il rischio di overfitting è concreto su Heart Disease: 736 record di training e vettori da 768 o 1024 dimensioni. Con più dimensioni che esempi, un classificatore lineare non regolarizzato può separare perfettamente il training anche con etichette casuali. La regolarizzazione L2, con intensità scelta per ogni encoder da una cross-validation interna (capitolo 22), è ciò che rende sensato il linear probe.

### 2.3 Training, validazione, test

Per stimare la generalizzazione si separano i dati:

- **training**: per stimare i parametri del modello;
- **validazione**: per le scelte fatte guardando i risultati (iperparametri, soglia, quale modello tenere);
- **test**: per una sola misura finale, su dati mai usati per alcuna scelta.

Ogni volta che un dato influenza una scelta, perde la capacità di misurarne l'effetto senza distorsione. È il principio da cui derivano tutte le correzioni del capitolo 36. La cross-validation (capitolo 23) usa la stessa porzione di dati, a turno, per addestrare e validare.

### 2.4 Rappresentazione

Un classificatore lavora su vettori numerici. Come si costruisce il vettore (la **rappresentazione**) conta quanto il classificatore. Nel progetto la rappresentazione è l'idea centrale: invece di dare al classificatore le colonne del dataset, gli si dà l'embedding di una frase che descrive il record. Il classificatore è volutamente semplice (lineare), così le differenze di prestazione si possono attribuire alla rappresentazione.

## Capitolo 3 — Dalla tabella al testo: stato dell'arte

### 3.1 Perché convertire una tabella in testo

I dati clinici strutturati (tabelle di variabili) si analizzano tradizionalmente con modelli tabellari: regressione logistica, alberi di decisione, foreste casuali, gradient boosting. Su dati tabellari di dimensione media i modelli ad alberi restano spesso i più forti; Grinsztajn, Oyallon e Varoquaux (2022) lo hanno mostrato in modo sistematico su decine di benchmark.

La conversione in testo nasce da un'altra prospettiva. I modelli di linguaggio pre-addestrati contengono conoscenza sul significato delle parole: sanno, per esempio, che "asymptomatic chest pain" e "typical angina" sono descrizioni di sintomi, o che un colesterolo di 300 mg/dl è alto. Trasformando un record in frase si può sfruttare quella conoscenza senza progettare a mano le variabili. In più, il testo è un formato comune: la stessa pipeline può accettare dataset diversi senza modifiche al modello.

### 3.2 Approcci esistenti

La letteratura si divide in tre famiglie.

1. **Serializzazione e modello generativo.** Il record viene scritto come testo e un grande modello di linguaggio produce direttamente la risposta, con pochi esempi nel prompt o dopo un fine-tuning. TabLLM (Hegselmann et al., 2023) ha confrontato diversi modi di serializzare una riga (lista "colonna: valore", frasi scritte a mano, frasi generate da un LLM) e ha mostrato che con pochissimi esempi etichettati questo approccio può competere con i modelli tabellari; con molti dati i modelli tabellari tornano in vantaggio.
2. **Serializzazione ed embedding.** Il testo viene trasformato in un vettore da un encoder e il vettore viene dato a un classificatore. È l'approccio di Forecast. Il vantaggio è il costo: un encoder piccolo gira in locale su un portatile, senza GPU.
3. **Modelli tabellari pre-addestrati.** Reti progettate per tabelle e pre-addestrate su molti dataset; sono un filone recente, non usato qui.

Il formato di serializzazione di Forecast è del tipo "campo: valore" con nomi espansi in inglese clinico ("chest pain type: typical angina"), cioè una via di mezzo tra la lista grezza e la frase scritta a mano.

### 3.3 Linear probing

Valutare una rappresentazione addestrando sopra di essa solo un classificatore lineare, con l'encoder congelato, si chiama *linear probing* (Alain e Bengio, 2016). È lo schema standard per confrontare rappresentazioni: se le classi sono separabili linearmente nello spazio degli embedding, l'informazione è "accessibile" senza ulteriore addestramento. Il risultato dice quanto è buona la rappresentazione, non quanto è buono il miglior modello possibile.

### 3.4 Cosa aggiunge Forecast

- Un confronto controllato tra sette encoder di tre famiglie, con lo stesso protocollo e test statistici appaiati.
- Due compiti clinici con caratteristiche opposte.
- Un'esecuzione interamente locale, rilevante per dati sanitari (capitolo 38).
- Un confronto con baseline tabellari sullo stesso split (capitolo 34), che colloca il risultato rispetto all'approccio tradizionale.
- Un caso documentato di leakage da oversampling e la sua correzione (capitoli 24 e 36), utile come contributo metodologico.

## Capitolo 4 — Domande di ricerca e ipotesi

### 4.1 Le domande

**Domanda principale.** Gli embedding semantici generati localmente da modelli di linguaggio supportano efficacemente un compito di classificazione clinica, partendo da dati strutturati convertiti in linguaggio naturale?

**Domanda secondaria.** Gli encoder specializzati nel dominio biomedico producono rappresentazioni più efficaci di quelli generalisti, per un compito clinico basato su dati tabellari trasformati in testo?

### 4.2 Come renderle verificabili

"Efficacemente" va tradotto in criteri misurabili. Una formulazione difendibile:

- **H1 (principale).** Per ciascun dataset, la ROC-AUC del linear probe è significativamente superiore a 0,5 (classificatore casuale) e confrontabile con quella di un modello tabellare sullo stesso split. Il primo criterio dice che c'è segnale; il secondo dice se la conversione in testo lo conserva.
- **H2 (secondaria).** La ROC-AUC media degli encoder biomedici è superiore a quella dei generalisti, e le differenze tra coppie biomedico/generalista sono significative al test di DeLong dopo correzione di Benjamini-Hochberg.

### 4.3 Cosa rispondono i dati

| Ipotesi | Heart Disease | Diabetes130 |
| --- | --- | --- |
| H1, segnale | Sì: AUC 0,85–0,89 in CV, 0,89–0,93 sul test | Debole: AUC 0,600–0,609 in CV, 0,605–0,622 sul test |
| H1, confronto con tabellare | Equivalente: miglior encoder 0,891 in CV e 0,915 sul test, regressione logistica tabellare 0,896 e 0,914 | Inferiore: tabellare 0,618 in CV e 0,644 sul test, miglior encoder 0,609 e 0,622 |
| H2 | Vantaggio piccolo: biomedici 0,882 contro generalisti 0,870 in media; 5 confronti DeLong su 12 significativi; pubmedbert il migliore | No: 0,605 contro 0,603; nessun confronto DeLong significativo |

Il capitolo 34 discute il confronto con il tabellare e il capitolo 33 un fattore che complica la lettura di H1 su Heart Disease: una parte del segnale viene dal centro di provenienza dei pazienti.

> *Per la tesi.* Conviene dichiarare le ipotesi nel capitolo introduttivo nella forma di 4.2, e riprenderle una per una nelle conclusioni con i numeri di 4.3.

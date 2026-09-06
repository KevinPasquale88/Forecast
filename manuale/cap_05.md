# Capitolo 5 — Rappresentazioni testuali ed embedding

**Obiettivi del capitolo**

- Avere un'intuizione di cos'è un embedding prima di vedere una sola formula o una sola riga di codice.
- Capire, a livello concettuale, come un modello linguistico trasforma una frase in un vettore di numeri.
- Sapere perché il progetto distingue esplicitamente modelli "generalisti" da modelli "biomedici", e da dove viene questa distinzione nel codice.

## 5.1 Cos'è un embedding, in una frase, prima di ogni formula

Un **embedding** è la rappresentazione di un testo — una parola, una frase, un intero documento — come un elenco fisso di numeri, un vettore. Non è una codifica arbitraria: due frasi che un lettore umano giudicherebbe simili nel significato producono, con un buon modello di embedding, vettori numericamente vicini fra loro; due frasi di significato lontano producono vettori numericamente lontani. La "vicinanza" fra vettori si misura di solito con una distanza geometrica ordinaria (o con una quantità strettamente imparentata, la similarità coseno), lo stesso tipo di distanza che useresti fra due punti su una mappa.

**[Fatto]** In questo progetto, ogni frase generata da `record_to_text_*()` (capitolo 22.1) diventa, dopo l'embedding, un vettore di 768 o 1024 numeri in virgola mobile a seconda del modello (verificato caricando i file `.npy` con NumPy — la tabella completa è al capitolo 39.1). Quel vettore, non la frase originale, è ciò che il classificatore vede.

> **SE VIENI DA JAVA —** non c'è una `class Embedding` da qualche parte con campi nominati. Un embedding, in questo progetto come nella maggior parte del codice di questo tipo, è semplicemente un array NumPy di numeri in virgola mobile — un `float[]` di lunghezza fissa, se preferisci pensarlo in termini Java, ma senza alcun nome per le singole posizioni: la posizione 347 del vettore non "significa" nulla di dichiarabile a parole, è solo una delle centinaia di coordinate che insieme codificano il significato della frase.

## 5.2 Da testo a vettore: tokenizzazione, encoder transformer, pooling

**[Livello: teoria consolidata del settore]** Tutti i sette modelli usati in questo progetto — sia quelli generalisti serviti da Ollama sia quelli biomedici serviti da Hugging Face — condividono la stessa famiglia architetturale di fondo, quella dei modelli **transformer** basati su encoder (la stessa famiglia architetturale di BERT). Il percorso da frase a vettore attraversa tre passaggi concettuali:

1. **Tokenizzazione.** La frase viene spezzata in unità più piccole di una parola intera — sotto-parole, spesso — ciascuna delle quali corrisponde a un identificativo numerico in un vocabolario fisso che il modello ha imparato durante il proprio pre-addestramento. "Asymptomatic" potrebbe diventare due o tre token, non uno solo.
2. **Passaggio attraverso l'encoder.** Ogni token, inizialmente rappresentato da un vettore che dipende solo da se stesso, attraversa più strati della rete neurale che ricalcolano la sua rappresentazione tenendo conto di *tutti gli altri token della frase* — è questo il meccanismo che permette al modello di rappresentare, per esempio, che "non" prima di "diabetico" ne inverte il significato clinico.
3. **Pooling.** A questo punto hai un vettore per ogni token della frase, non un vettore per l'intera frase. Il pooling li combina in un unico vettore di lunghezza fissa — tipicamente calcolandone la media (*mean pooling*), talvolta prendendo solo il vettore associato a un token speciale di inizio-frase.

**[Fatto]** Il codice del progetto conferma esplicitamente che questo è il meccanismo in gioco per i modelli biomedici: un commento in `embedding.py:170` dichiara che "SentenceTransformer applicherà automaticamente il 'mean pooling' ai token di Bio_ClinicalBERT" — la libreria `sentence-transformers` (capitolo 22.3) si occupa dei tre passaggi per te, e la riga di codice che li innesca è una sola: `model.encode(texts, ...)` (`embedding.py:178`).

> **APPROFONDIMENTO FACOLTATIVO —** i modelli generalisti di questo progetto (E5, GTE) sono addestrati con un obiettivo specifico chiamato apprendimento contrastivo: durante il pre-addestramento, il modello vede coppie di testi che dovrebbero essere semanticamente vicini (per esempio una domanda e la sua risposta corretta) insieme a testi che non dovrebbero esserlo, e viene aggiustato in modo che le prime coppie producano vettori vicini e le seconde vettori lontani. I paper originali di questi modelli — Wang et al. per E5, Li et al. per GTE `[DA VERIFICARE — non citare prima del controllo: titoli, sedi e anni esatti da confermare]` — dettagliano la procedura; non è necessaria per seguire il resto del libro.

## 5.3 Perché esistono modelli generalisti e modelli biomedici

**[Fatto]** Il progetto distingue esplicitamente tre famiglie di modelli, con un campo `family` nella configurazione di ciascuno (`function.py:39-51`):

| Famiglia | Modelli nel progetto | Pre-addestrati principalmente su |
|---|---|---|
| `general-purpose` | e5-base, e5-large, gte-base, gte-large | Testo generico, multilingue, di larga scala |
| `biomedical` | bioclinicalbert, pubmedbert | Letteratura biomedica e/o note cliniche |
| `biomedical-st` | sentence-biobert | Variante biomedica adattata specificamente per produrre embedding di frase |

**[Livello: teoria consolidata del settore]** Un modello pre-addestrato su un corpus generico apprende relazioni semantiche valide per il linguaggio comune, ma può non aver mai incontrato abbastanza testo specialistico da rappresentare bene termini come "discharge disposition" o "A1C" con la stessa finezza con cui un modello addestrato specificamente su letteratura medica li rappresenterebbe. È esattamente l'ipotesi che il progetto vuole mettere alla prova, non darla per scontata: da qui la seconda domanda di ricerca dichiarata in `README.md:60-61` ("i modelli specializzati nel dominio biomedico producono rappresentazioni semantiche più efficaci di quelli generalisti, per un compito di classificazione clinica basato su dati tabellari trasformati in testo?"). Il capitolo 6.3 mostra esattamente come questa domanda si traduce in codice eseguibile; i capitoli 44 e 45 ne riportano la risposta empirica sui due dataset.

> **ATTENZIONE —** "biomedico" qui non significa "addestrato sugli stessi due dataset di questo progetto", né su dati simili a quelli in `record_to_text_*()`. Significa addestrato su corpora biomedici in generale — letteratura scientifica, per esempio, per PubMedBERT. È un dominio linguistico affine a quello del progetto, non identico: un punto da non dare per scontato quando si interpretano i risultati del capitolo 44.

## Riepilogo

Un embedding rappresenta un testo come un vettore numerico di lunghezza fissa, costruito in modo che testi semanticamente simili producano vettori vicini. Il percorso da frase a vettore, per tutti i modelli di questo progetto, attraversa tokenizzazione, un encoder transformer che contestualizza ogni token rispetto agli altri, e un pooling finale che produce un unico vettore per l'intera frase. Il progetto distingue esplicitamente tre famiglie di modelli — generalisti, biomedici, biomedici per frasi — proprio per poter confrontare, in modo controllato, se la specializzazione di dominio migliora la rappresentazione di testo clinico sintetico.

## Domande di autoverifica

**1. Perché due frasi "simili" dovrebbero produrre vettori "vicini", e come si misura questa vicinanza?**
Perché un buon modello di embedding è costruito e addestrato apposta perché la vicinanza geometrica fra vettori rispecchi la vicinanza semantica fra i testi corrispondenti. Si misura tipicamente con una distanza geometrica o con la similarità coseno fra i due vettori.

**2. A cosa serve il passaggio di pooling, e perché non basta l'output dell'encoder da solo?**
L'encoder produce un vettore per ciascun token della frase, non un vettore per l'intera frase. Il pooling (per esempio la media dei vettori di tutti i token) li riduce a un unico vettore di lunghezza fissa, indipendente da quante parole aveva la frase originale — necessario perché il classificatore successivo si aspetta un input di dimensione costante.

**3. In che senso la distinzione "generalista/biomedico" non è solo un'etichetta descrittiva, ma il cuore della domanda di ricerca del progetto?**
Perché il progetto è costruito apposta per confrontare, a parità di tutto il resto della pipeline, le prestazioni dei modelli delle due famiglie sullo stesso compito — non per usarne uno solo. La domanda "il dominio specialistico aiuta?" ha una risposta solo se il confronto è esplicito e controllato, come qui.

> **MATERIALE PER LA TESI**
> 1. La tabella delle tre famiglie di modello con i relativi membri e la fonte del pre-addestramento (§5.3) — riusabile come tabella descrittiva in "Materiali e metodi".
> 2. Lo schema in tre passaggi tokenizzazione→encoder→pooling, con il riferimento al commento originale del codice (`embedding.py:170`) — riusabile come spiegazione tecnica sintetica nello stato dell'arte.
> 3. La citazione letterale della seconda domanda di ricerca da `README.md:60-61`, con l'avvertenza sul significato di "biomedico" (§5.3, riquadro Attenzione) — riusabile nell'introduzione della tesi per formulare l'ipotesi in modo preciso, evitando affermazioni più forti di quelle che i dati possono sostenere.

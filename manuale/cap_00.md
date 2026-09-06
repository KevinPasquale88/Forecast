# Parte 0 — Come usare questo libro

**Obiettivi del capitolo**

- Sapere quale percorso di lettura seguire, in base a cosa già sai e a cosa ti serve.
- Riconoscere le convenzioni tipografiche usate in ogni capitolo, prima di incontrarle nel merito.
- Capire come questo manuale si collega alla tesi che dovrai scrivere, e cosa questo libro deliberatamente non fa.

Questo libro documenta un progetto reale: una pipeline Python che confronta modelli di embedding testuale per la classificazione clinica. Non è la tua tesi. È il materiale — verificato, citato, misurato — da cui la tesi si scrive. Le due cose hanno regole diverse, e questo capitolo te le mostra prima di cominciare.

## 0.1 Percorsi di lettura e a chi serve questo libro

Il libro presuppone una cosa sola con certezza: sai già programmare, in un linguaggio a oggetti staticamente tipizzato, e conosci il mestiere — HTTP, SQL, test automatici, gestione delle dipendenze, concorrenza in astratto. Il libro è scritto assumendo che tu venga da Java in particolare, perché è il riferimento più utile per marcare le differenze che contano. Non presuppone nulla sul dominio clinico, su Python, o su questo progetto specifico. Tre profili di lettura, con percorsi diversi:

### 0.1.1 Se vieni da Java e non conosci Python

Leggi in ordine dalla Parte I alla Parte VIII senza saltare la Parte II. È tentante saltarla — "conosco già la programmazione" — ma la Parte II non insegna a programmare: insegna dove Python *si comporta diversamente* da Java pur sembrando uguale, che è esattamente il tipo di differenza che morde a metà di un debugging, non mentre leggi con calma. Un esempio su tutti, anticipato qui e spiegato per intero nel capitolo 8: in Python un valore di default mutabile in una firma di funzione viene creato *una sola volta*, non ad ogni chiamata. In Java questo problema semplicemente non esiste nella stessa forma. Se lo scopri leggendo un capitolo, costa un paragrafo. Se lo scopri in produzione, costa una sera.

### 0.1.2 Se conosci già Python e vuoi solo il progetto

Salta la Parte II. Puoi anche scorrere rapidamente la Parte III (ambiente) se il tuo ambiente locale è già configurato. Comincia dalla Parte IV (architettura) e prosegui linearmente: Parte V (codice modulo per modulo), Parte VI (dati), Parte VII (matematica del modello), Parte VIII (casi d'uso end-to-end). Le Parti I, IX, X, XI, XII, XIII restano utili quanto per chiunque altro: coprono il dominio, i risultati, la qualità e la messa in prospettiva critica, argomenti indipendenti dalla lingua di programmazione.

### 0.1.3 Se stai preparando la tesi

Leggi il libro nell'ordine in cui è scritto almeno una prima volta — la Parte XIII da sola, senza il resto, è materiale senza fondamenta. Poi usa la Parte XIII come indice di ritorno: ogni sua sezione ti rimanda ai capitoli con il materiale grezzo (dati, formule, tabelle, figure, criticità) per quella parte specifica della tesi. La sezione 0.3.2 di questo capitolo ti dà un'anteprima immediata di quella mappa.

> **ATTENZIONE —** questo libro non usa prosa da incollare in una tesi. È scritto come manuale tecnico: schemi, tabelle, definizioni, dati verificati. La tesi la scrivi tu, con le tue parole, usando questo materiale come fondamenta verificate. Copiare paragrafi da qui alla tesi senza riscriverli è un rischio che riguarda te, non un problema di questo libro — ma è bene dirlo chiaramente da subito.

## 0.2 Convenzioni tipografiche e riquadri ricorrenti

### 0.2.1 Le etichette Fatto / Inferenza / Da verificare

Ogni affermazione tecnica in questo libro porta una di tre etichette, in grassetto, all'inizio della frase o del paragrafo a cui si applica.

**[Fatto]** significa: verificato leggendo il codice sorgente reale del progetto, o eseguendo un comando reale e osservandone l'output. Ogni "Fatto" porta con sé un riferimento nella forma `percorso/file.py:riga` (spiegata in 0.2.3) oppure il comando esatto eseguito. Esempio reale, che rincontrerai nel capitolo 28: **[Fatto]** `main.py` accetta un solo argomento da riga di comando, `--dataset`, con default `heart_disease` (`main.py:14-18`).

**[Inferenza]** significa: una deduzione ragionevole, non direttamente scritta nel codice ma costruita a partire da ciò che il codice fa, con la motivazione resa esplicita subito dopo. Esempio reale, dal capitolo 35: **[Inferenza]** scegliere la soglia di decisione che massimizza F1 sullo stesso fold di validazione su cui poi si misura la metrica introduce un ottimismo statistico lieve — motivazione: il modello non vede le etichette di validazione per allenarsi, ma la soglia sì, quindi il numero riportato è calibrato sui dati su cui viene anche giudicato.

**[Da verificare]** significa: una domanda aperta, un'ipotesi non controllata, qualcosa che richiederebbe una fonte esterna, un esperimento, o una conversazione con chi ha scritto il codice per essere chiusa. Esempio reale, dal capitolo 6: **[Da verificare]** la libreria `ucimlrepo` compare in `requirements.txt` ma non risulta importata in nessuno dei nove file Python del progetto letti per questo libro — probabilmente un residuo di una fase esplorativa precedente, ma non verificato.

Tutte le voci "Da verificare" del libro confluiscono anche nell'Appendice E, in un elenco unico, pensato per essere portato così com'è a chi supervisiona la tesi.

> **ATTENZIONE —** le tre etichette non sono intercambiabili, e la differenza conta più in una tesi che in questo manuale. Presentare in tesi un "Da verificare" come se fosse un "Fatto" significa dichiarare come risultato verificato qualcosa che non lo è. Chi la legge — un relatore, un membro di commissione — verifica le fonti. Trovarne una che non regge mina la credibilità di tutto il resto, anche della parte solida.

### 0.2.2 I sei riquadri ricorrenti

Oltre alle etichette puntuali, il libro usa sei riquadri più estesi, sempre nella stessa forma tipografica — una citazione (blockquote) con un'etichetta in maiuscolo in grassetto, senza icone o decorazioni:

> **SE VIENI DA JAVA —** una differenza specifica tra Python e Java, sul punto preciso che il capitolo sta trattando. Non spiega cos'è una variabile: spiega, per esempio, perché in Python una funzione può restituire tipi diversi a seconda del ramo eseguito, e cosa significa per te che vieni da un linguaggio dove la firma del metodo lo vieta a priori.

> **ATTENZIONE —** un punto dove un'assunzione ragionevole ti porterebbe fuori strada. Il libro ne apre uno, per esempio, sul fatto che eseguire `python main.py` senza argomenti esegue silenziosamente il dataset Heart Disease, non entrambi i dataset e non un dataset scelto a caso: un flag con un default è comodo finché non te ne accorgi mentre confronti risultati che pensavi appartenessero a un altro dataset.

> **APPROFONDIMENTO FACOLTATIVO —** un contenuto che arricchisce ma non è necessario per seguire il filo del capitolo. Puoi saltarlo alla prima lettura e tornarci se ti serve per la tesi. Il libro lo usa, per esempio, per il funzionamento interno di UMAP nel capitolo 38: capire cosa succede nella pipeline non richiede sapere come UMAP costruisce il suo grafo di vicinanza, ma la tesi potrebbe trarne beneficio.

> **PROVA TU —** un piccolo esercizio pratico, quasi sempre eseguibile in pochi minuti sull'ambiente che avrai configurato nella Parte III. Non ha una soluzione nascosta altrove nel libro: è pensato perché tu lo faccia, non perché tu legga cosa succederebbe.

> **RIFERIMENTO AL CODICE —** un rimando puntuale a un file e a una riga (o intervallo di righe) del progetto, quando serve isolarlo dal flusso del paragrafo — per esempio quando la stessa riga è rilevante per due argomenti diversi in due capitoli diversi, e conviene poterla ritrovare rapidamente in entrambi.

> **MATERIALE PER LA TESI —** presente alla fine di ogni capitolo, indica tre elementi di quel capitolo — una tabella, una formula, un dato, un grafico, un'osservazione critica — pensati per essere ripresi, con le tue parole, in una sezione specifica della tesi.

### 0.2.3 Come leggere i riferimenti file:riga

Ogni volta che il libro scrive qualcosa come `classification.py:16`, significa: riga 16 del file `classification.py`, che si trova nella radice del repository del progetto. Un intervallo si scrive `preprocessing.py:43-70` e significa dalla riga 43 alla riga 70 comprese. Questi riferimenti sono verificabili da chiunque abbia il repository aperto: aprilo, vai a quella riga, e troverai esattamente ciò che il libro descrive. Se un giorno il codice cambia e la riga non corrisponde più, il riferimento è invecchiato — non inventato: era corretto al momento della scrittura, verificato leggendo il commit `41bf90e` del branch `master` (l'ultimo al momento in cui questo libro è stato scritto).

> **RIFERIMENTO AL CODICE —** quando un riferimento riguarda un file su un branch diverso da `master` — capita una sola volta in questo libro, per il chatbot del capitolo 54 — il libro lo dice esplicitamente: `chatbot_core.py:12 (branch chatbot)`. In assenza di questa precisazione, il riferimento è sempre su `master`.

## 0.3 Mappa manuale → tesi

### 0.3.1 Struttura tipica di una tesi triennale in informatica

Una tesi triennale in informatica, nell'ambito di ingegneria del software, segue tipicamente uno schema semplice: un'introduzione che motiva il problema, una rassegna dello stato dell'arte che lo colloca rispetto a ciò che già esiste, una descrizione di materiali e metodi che spiega cosa hai costruito e come, una presentazione dei risultati, una discussione che ne pesa la portata e i limiti, e delle conclusioni che indicano cosa si potrebbe fare dopo. Questo libro non ha quella struttura — ha la struttura di un manuale tecnico, pensata per l'apprendimento e la consultazione, non per la difesa di una tesi — ma ogni sua parte alimenta uno o più di quei momenti.

### 0.3.2 Tabella di corrispondenza capitoli-sezioni (anteprima)

La Parte XIII (capitoli 56-58) tratta questa corrispondenza capitolo per capitolo, con il dettaglio di quali figure, tabelle e misure sono già pronte e quali vanno ancora prodotte. Questa è solo l'anteprima, utile da subito per orientarti.

| Sezione tipica di tesi | Parti del manuale a cui attingere |
|---|---|
| Introduzione e motivazione | Parte I |
| Stato dell'arte | Parte I, Parte XI (cap. 53), Appendice D |
| Materiali e metodi | Parte IV, Parte V, Parte VI, Parte VII |
| Risultati | Parte IX |
| Discussione e limiti | Parte XI |
| Conclusioni e lavori futuri | Parte XII |

### 0.3.3 Cosa non troverai in questo libro

Non troverai paragrafi già scritti nello stile di una tesi, pronti per un copia-incolla. Non troverai una bibliografia che accetta un riferimento perché "suona giusto": ogni voce in Appendice D è verificabile con un identificativo reale (DOI, ISBN o URL), oppure è marcata esplicitamente come da controllare prima di essere citata. Non troverai concetti di programmazione generale spiegati da zero — se compare una spiegazione di cos'è un ciclo o un'eccezione, è un errore di calibrazione di questo libro, non una scelta. E non troverai, nella parte di dominio, alcun accenno a serie storiche, stagionalità o trend: nonostante il nome storico del progetto, il codice non fa previsioni temporali — fa classificazione clinica binaria a partire da embedding testuali, come stabilito leggendo `main.py`, `preprocessing.py` ed `embedding.py`, non deducendolo dal nome della cartella. Il capitolo 1 lo spiega per intero.

## Riepilogo

Questo libro ha tre percorsi di lettura a seconda di cosa sai già; usa tre etichette (Fatto, Inferenza, Da verificare) per dichiarare quanto è solida ogni affermazione tecnica, e sei riquadri ricorrenti per isolare contenuti di natura diversa dal corpo del testo. Non è la tesi: è il materiale verificato da cui la tesi si scrive, e la Parte XIII è la mappa esplicita che collega l'uno all'altra.

## Domande di autoverifica

**1. Perché un'affermazione marcata "Da verificare" non va citata in tesi come se fosse un fatto assodato?**
Perché "Da verificare" segnala un'ipotesi non ancora controllata. Presentarla come "Fatto" significa dichiarare come risultato verificato qualcosa che non lo è — un errore che chiunque verifichi la fonte scopre subito, con un costo di credibilità che si estende al resto del lavoro.

**2. In quale parte del manuale trovi le formule matematiche del progetto, con il rimando alla riga di codice che le implementa?**
Parte VII — Il modello: matematica e implementazione (capitoli 32-39).

**3. Il tuo relatore ti chiede quali sono i limiti di questo lavoro. Dove guardi per primo?**
Parte XI — Analisi critica (capitoli 51-53), con supporto dal capitolo 47 (confronto con un baseline) e dall'Appendice E (zone d'ombra), che raccoglie in un solo elenco tutte le domande aperte del libro.

> **MATERIALE PER LA TESI**
> 1. La tabella di corrispondenza sezione-di-tesi → parte-del-manuale (§0.3.2): riusabile per motivare, nell'introduzione della tesi, come è organizzato il lavoro.
> 2. La convenzione Fatto/Inferenza/Da verificare (§0.2.1): riusabile come nota metodologica esplicita nel capitolo "Materiali e metodi", per dichiarare il grado di certezza di ogni affermazione empirica.
> 3. L'elenco dei sei riquadri ricorrenti (§0.2.2): riusabile come schema per organizzare, in un'appendice della tesi, le osservazioni critiche raccolte durante l'analisi del progetto.

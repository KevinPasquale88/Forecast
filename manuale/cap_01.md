# Capitolo 1 — Perché questo progetto esiste

**Obiettivi del capitolo**

- Capire quali sono, in concreto, i due problemi clinici che il progetto affronta.
- Capire chi userebbe una previsione di questo tipo, e cosa cambia per un paziente reale a seconda che il sistema sbagli in un verso o nell'altro.
- Sapere cosa si intende, in questo campo, per approccio "tradizionale", e in cosa il progetto se ne discosta.

## 1.1 Il problema clinico reale: diagnosi vs. rischio di riammissione

**[Fatto]** Il progetto affronta due problemi distinti, uno per dataset, entrambi di classificazione binaria su dati clinici strutturati:

Il primo problema — dataset **UCI Heart Disease** — è un problema di supporto alla diagnosi: dato il profilo clinico di un paziente (età, pressione a riposo, colesterolo, risultati di un elettrocardiogramma, e altre nove misure), il sistema deve produrre una stima della presenza di malattia coronarica. Non sostituisce una diagnosi medica — restituisce una probabilità, calcolata su dati storici, che può informare una decisione umana successiva. È il problema classico di *classificazione diagnostica*: la variabile che il progetto chiama `num` nel codice (`function.py:12`) diventa, dopo la binarizzazione `(num > 0)` (`preprocessing.py:41`), la risposta a una domanda semplice: malattia presente, sì o no.

Il secondo problema — dataset **Diabetes 130-US Hospitals** — è un problema diverso nella sostanza, anche se identico nella forma matematica: dato un ricovero ospedaliero già avvenuto per un paziente diabetico (quanti giorni è rimasto ricoverato, quanti farmaci ha ricevuto, quante visite di pronto soccorso ha avuto nell'anno precedente, e altre quindici misure), il sistema deve stimare se quel paziente tornerà ricoverato entro 30 giorni dalla dimissione. Non è una diagnosi: è una previsione di utilizzo futuro del sistema sanitario, il tipo di previsione che serve a decidere l'intensità del follow-up post-dimissione. **[Fatto]** La colonna `readmitted` viene binarizzata in `load_diabetes130()` con la regola `(readmitted == "<30")` (`function.py:124`): 1 se il paziente è tornato entro 30 giorni, 0 altrimenti (anche se non è mai tornato, o è tornato dopo più di 30 giorni — una scelta di framing di cui riparliamo al capitolo 30.3).

Due problemi diversi, la stessa struttura: una tabella di feature cliniche in ingresso, un'etichetta binaria in uscita. È esattamente questa uniformità di struttura, al di là del contenuto clinico specifico, che rende sensato trattarli con la stessa pipeline — il tema di cui parla il capitolo 3.

## 1.2 Chi decide, e con quali conseguenze

Un sistema come questo non prende decisioni cliniche: le informa. Ma è utile, fin da subito, chiedersi chi guarderebbe questo numero e cosa ne farebbe, perché la risposta anticipa un concetto tecnico — l'asimmetria fra i due tipi di errore — che il capitolo 4.3 formalizza.

Per Heart Disease, il numero informerebbe un clinico durante una valutazione di rischio cardiovascolare. Se il sistema dice "malattia probabile" per un paziente sano (un **falso positivo**), la conseguenza tipica è un esame diagnostico in più — invasivo o costoso, ma raramente pericoloso di per sé. Se il sistema dice "nessuna malattia" per un paziente che invece ce l'ha (un **falso negativo**), la conseguenza è la mancata individuazione di una condizione che può aggravarsi. I due errori non pesano allo stesso modo, e nessuna delle metriche che il progetto calcola — le vedremo al capitolo 34 — lo sa già da sola: lo sai tu, quando le interpreti.

Per Diabetes130, il ragionamento è simmetrico ma le conseguenze pratiche sono diverse. Un falso positivo (il sistema segnala rischio di riammissione per un paziente che non tornerà) costa una telefonata di follow-up in più, forse non necessaria. Un falso negativo (il sistema non segnala un paziente che invece tornerà entro 30 giorni) costa l'assenza di un intervento — educazione del paziente, controllo ravvicinato, aggiustamento della terapia — che avrebbe potuto prevenire il ricovero.

> **ATTENZIONE —** in nessuno dei due casi il progetto stesso discute esplicitamente questa asimmetria nel codice: le metriche calcolate (accuratezza, F1, AUC — capitolo 34) trattano i due tipi di errore in modo sostanzialmente simmetrico. È un limite reale, non un dettaglio implementativo: lo riprendiamo con la dovuta attenzione critica nel capitolo 51.

## 1.3 Cosa si faceva prima: classificazione diretta su dati tabellari

**[Livello: teoria consolidata del settore]** L'approccio più diffuso per problemi di questo tipo — dati clinici strutturati, etichetta binaria — è addestrare un classificatore direttamente sulle feature tabellari originali: un modello lineare (come la regressione logistica che il progetto stesso usa più avanti nella pipeline, capitolo 32), oppure un modello ad albero o un insieme di alberi (random forest, gradient boosting). Questi approcci non richiedono alcuna conversione a testo: la tabella con le sue colonne numeriche e categoriali entra direttamente nel modello. È un approccio maturo, ben studiato, spesso difficile da battere su dati genuinamente tabellari con poche migliaia di righe — esattamente la scala dei due dataset di questo progetto.

**[Fatto]** `docs/DATASET.md:59-64` e `docs/DATASET.md:109-110` sono espliciti su questo punto: il contributo di questo progetto **non è** un classificatore tabellare diretto. È qualcos'altro — una trasformazione del problema, prima ancora che una soluzione — che il capitolo 3 introduce da zero.

**[Interpretazione]** Vale la pena notare, con lo sguardo critico che questo libro adotta ovunque, che scegliere di non fare ciò che la letteratura consolidata farebbe per primo non è né giusto né sbagliato in astratto: è una scelta di ricerca che sposta la domanda da "qual è il modello più accurato" a "cosa succede se rappresenti i dati in un modo diverso". È una domanda legittima. Ma significa anche che il confronto onesto richiederebbe, idealmente, anche un classificatore tabellare diretto come termine di paragone — cosa che il progetto non include, e che il capitolo 47 costruisce da zero come esercizio di validazione.

## Riepilogo

Il progetto affronta due problemi di classificazione binaria su dati clinici strutturati — diagnosi di malattia coronarica e rischio di riammissione ospedaliera — con la stessa struttura tecnica ma conseguenze pratiche diverse per i due tipi di errore possibile. L'approccio consolidato in letteratura per questo genere di problema è la classificazione tabellare diretta; il progetto sceglie invece una strada diversa, che introduciamo dal capitolo 3 in poi.

## Domande di autoverifica

**1. Le due variabili target, `num` per Heart Disease e `readmitted` per Diabetes130, come diventano etichette binarie nel codice?**
`num` diventa binaria con la regola `(num > 0)` in `preprocessing.py:41` (qualunque grado di malattia rilevato conta come "presente"). `readmitted` diventa binaria con la regola `(readmitted == "<30")` in `function.py:124` (solo la riammissione entro 30 giorni conta come "positiva"; una riammissione più tardiva conta come "negativa", esattamente come nessuna riammissione).

**2. Perché l'asimmetria tra falsi positivi e falsi negativi non è già incorporata nelle metriche che il progetto calcola?**
Perché accuratezza, F1 e AUC (capitolo 34) sono metriche generiche, pensate per riassumere le prestazioni di un classificatore senza assumere nulla sul costo relativo dei due tipi di errore in un dominio specifico. Incorporare quell'asimmetria richiederebbe una scelta esplicita — per esempio una soglia di decisione calibrata sul costo clinico, non solo sull'F1 — che il progetto, come vedremo al capitolo 35, non fa.

**3. In che senso il progetto "non fa" ciò che la letteratura consolidata farebbe per primo?**
Non addestra un classificatore direttamente sulle feature tabellari originali. Trasforma prima ogni record in una frase di linguaggio naturale, poi calcola un embedding di quella frase, e allena il classificatore sull'embedding — una scelta metodologica di per sé, discussa dal capitolo 3 in poi, non un'omissione.

> **MATERIALE PER LA TESI**
> 1. La formulazione precisa dei due task (diagnosi binaria; riammissione a 30 giorni binarizzata da una variabile originariamente non binaria) con i relativi riferimenti `file:riga` — riusabile parola per parola nell'introduzione della tesi per definire il problema.
> 2. Il ragionamento sull'asimmetria costo-FP/costo-FN, differenziato per i due dataset — riusabile nella discussione (capitolo 51) come base per una critica motivata alla scelta delle metriche.
> 3. L'osservazione che il progetto omette il confronto con un classificatore tabellare diretto — riusabile come motivazione esplicita per l'esperimento di baseline che costruiamo al capitolo 47, e che rafforza la sezione "materiali e metodi" della tesi.

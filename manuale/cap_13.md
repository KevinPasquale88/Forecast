# Capitolo 13 — Tabella di traduzione Java→Python e trappole finali

**Obiettivi del capitolo**

- Avere un unico punto di riferimento che riassuma, costrutto per costrutto, tutta la Parte II.
- Vedere in un solo elenco le cinque differenze più insidiose fra Python e Java, ciascuna con la propria conseguenza pratica.
- Leggere un traceback Python reale, prodotto da questo stesso progetto, riconoscendone la struttura.

## 13.1 Tabella sistematica

| Concetto | In Java | In Python | Capitolo |
|---|---|---|---|
| Blocco di codice | `{ }` | Indentazione | 7.1 |
| Fine istruzione | `;` | Fine riga | 7.1 |
| Tipizzazione | Statica, verificata a compile time | Dinamica, verificata solo a runtime | 7.2 |
| Riferimento all'oggetto corrente | `this` implicito | `self` esplicito, primo parametro di ogni metodo | 7.3 |
| Lista dinamica | `ArrayList<T>` | `list` | 8.1 |
| Mappa chiave-valore | `HashMap<K,V>` | `dict` | 8.1 |
| Ritorno multiplo da una funzione | Oggetto o array dedicato | Tupla, destrutturata per posizione | 8.1 |
| Trasformare una collezione | `stream().map().collect(...)` | List/dict comprehension | 8.2 |
| Modificatori di accesso | `private`/`protected`/`public`, imposti dal compilatore | Nessuno; convenzione dell'underscore, non imposta | 10.3 |
| Struttura a package | Cartelle + dichiarazione `package` | Nessuna dichiarazione; un file è già un modulo | 10.1 |
| Overload di funzione | Stesso nome, firme diverse, risolto a compile time | Non esiste; nomi diversi o logica a runtime | 9.3 |
| Funzione come valore | Lambda/riferimenti a metodo, tipizzati su un'interfaccia funzionale | Qualunque funzione, sempre, nessuna interfaccia richiesta | 9.2 |
| Gestione di una risorsa | try-with-resources (`AutoCloseable`) | `with` (context manager) | 11.2 |
| Eccezioni | Controllate/non controllate, dichiarate con `throws` | Nessuna distinzione, nessuna dichiarazione in firma | 11.1 |
| Concatenare un'eccezione alla sua causa | `new X(msg, cause)` | `raise X(...) from cause` | 11.1 |
| Comportamento aggiunto a una funzione | Nessun equivalente integrato nel linguaggio | Decoratori (`@nome`) | 11.3 |
| Parallelismo reale fra thread | Sì, su core diversi | No a livello di bytecode puro (GIL); sì durante attesa I/O o codice nativo | 12.1 |
| Pool di thread | `ExecutorService` | `ThreadPoolExecutor` | 12.2 |
| Ambiente delle dipendenze | Classpath assemblato da Maven/Gradle | Ambiente virtuale + `pip`/`requirements.txt` | 14 |

## 13.2 Le cinque trappole più insidiose per chi arriva da un linguaggio tipizzato staticamente

1. **Un default mutabile in una firma di funzione viene creato una volta sola**, non a ogni chiamata (capitolo 9.1). Non presente in questo progetto, ma è la trappola più citata dell'intero linguaggio: la prima volta che la incontri altrove, riconoscerai il sintomo (una lista di default che "ricorda" chiamate precedenti) prima ancora di ricordarti il nome del problema.
2. **Nessuna rete di sicurezza a compile time sui tipi** (capitolo 7.2): zero annotazioni di tipo in tutto questo progetto significano che un errore come passare un `DataFrame` dove il codice si aspetta un `ndarray` (o viceversa) emerge solo eseguendo quella riga specifica, non prima.
3. **Importare un modulo esegue il suo codice**, non solo lo dichiara disponibile (capitolo 10.2): `function.py:154` configura lo stile globale dei grafici nel momento dell'import, non quando qualcuno lo richiede esplicitamente — un side-effect facile da non notare leggendo solo le firme delle funzioni.
4. **Il GIL non impedisce il threading, ma ne limita il beneficio a un caso specifico** (capitolo 12.1): aspettarsi che tre thread Python diano una velocità tripla su calcolo puro, come ci si aspetterebbe in Java su una macchina multi-core, è un'aspettativa sbagliata — il beneficio reale, in questo progetto, viene dall'attesa di rete e dal codice nativo che rilascia il GIL, non dal bytecode Python in sé.
5. **Mutare un oggetto condiviso non richiede alcuna dichiarazione speciale** (capitolo 8.3): `results[chiave] = valore` in `classification.py:51` modifica silenziosamente il dizionario definito in `function.py`, senza `global`, senza alcun segnale sintattico che indichi "questa riga ha un effetto che sopravvive a questa funzione".

> **PROVA TU —** prendi le cinque trappole e, per ciascuna, prova a scrivere in una frase quale bug produrrebbe in un contesto *diverso* da quello attuale del progetto (per esempio: "cosa succederebbe se qualcuno chiamasse `training_classifier()` due volte nello stesso processo Python, per due dataset diversi, senza riavviare l'interprete?"). Non è un esercizio retorico: è esattamente il tipo di domanda che un buon code review, in qualunque linguaggio, dovrebbe porsi prima di riusare del codice scritto assumendo un solo utilizzo per processo.

## 13.3 Prova tu: leggere un traceback

Un traceback Python si legge **dal basso verso l'alto** per capire cosa è andato storto per primo nel tempo, ma la riga più in basso è quella più vicina al punto in cui l'errore è stato effettivamente sollevato — l'opposto, a prima vista, di uno stack trace Java, che invece elenca per prima la riga più vicina all'eccezione e scende verso il chiamante originale. In realtà l'ordine logico è lo stesso in entrambi i casi (dal punto dell'errore verso il punto di avvio); cambia solo la direzione grafica in cui viene stampato.

> **PROVA TU —** dopo aver completato l'installazione del capitolo 15, dalla cartella del progetto con l'ambiente virtuale attivato, esegui:
> ```bash
> python3 -c "from function import get_output_dirs; get_output_dirs('nope')"
> ```
> Otterrai un traceback reale, generato da questo stesso progetto. In fondo troverai `ValueError: Invalid dataset 'nope'. Valid options are: ['heart_disease', 'diabetes130']` — il messaggio scritto esplicitamente in `function.py:81`. Risalendo, troverai la riga esatta di `function.py` che ha sollevato l'eccezione, e sopra ancora la riga del tuo comando che ha chiamato `get_output_dirs`. Con due sole righe di codice hai già davanti la struttura completa di un traceback: fonte dell'errore in fondo, catena delle chiamate che ci sono arrivate risalendo.

## Riepilogo

Questo capitolo chiude la Parte II con una tabella di riferimento sistematica e cinque trappole reali (una delle quali, gli argomenti mutabili di default, non presente in questo progetto ma troppo diffusa nel linguaggio per non conoscerla comunque). Da qui in avanti il libro smette di confrontare Python con Java a ogni costrutto, e comincia a occuparsi dell'ambiente (Parte III), dell'architettura (Parte IV) e infine del codice del progetto nel dettaglio (Parte V) — dando per acquisito tutto ciò che hai visto in questi sette capitoli.

## Domande di autoverifica

**1. Perché "nessun parallelismo reale a livello di bytecode Python" e "il threading in questo progetto è comunque utile" non sono affermazioni in contraddizione?**
Perché il beneficio del threading, in questo progetto, viene dal tempo speso in attesa di rete (verso Ollama) o dentro codice nativo che rilascia il GIL (PyTorch), non dall'esecuzione parallela di bytecode Python puro — l'unica cosa che il GIL effettivamente impedisce.

**2. In un traceback Python, dove si trova il messaggio dell'errore effettivamente sollevato, e dove si trova la chiamata che lo ha originato?**
Il messaggio dell'errore si trova in fondo al traceback; risalendo verso l'alto si trova la catena delle chiamate, fino alla riga che ha avviato tutto — l'opposto grafico, ma non logico, di uno stack trace Java.

**3. Quale delle cinque trappole di questo capitolo è l'unica a non avere un esempio reale in questo progetto, e perché la si tratta comunque?**
Gli argomenti mutabili di default (capitolo 9.1): non compaiono in nessuna firma di questo progetto, ma sono fra le trappole più diffuse e citate dell'intero linguaggio Python, e conoscerle prima di incontrarle altrove evita un debugging altrimenti sorprendente.

> **MATERIALE PER LA TESI**
> 1. La tabella di traduzione sistematica Java→Python (§13.1) — riusabile in appendice alla tesi come riferimento rapido, o citata parzialmente per giustificare scelte di lettura del codice in "Materiali e metodi".
> 2. L'elenco delle cinque trappole con la loro conseguenza pratica specifica a questo progetto — riusabile come base per la sezione "Discussione e limiti", distinguendo quali rischi sono già materializzati nel codice e quali restano solo potenziali.
> 3. L'esercizio del traceback reale (§13.3), con il comando esatto e l'output atteso — riusabile come esempio riproducibile in un'eventuale sezione della tesi dedicata alla gestione degli errori.

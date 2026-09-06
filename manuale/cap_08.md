# Capitolo 8 — Strutture dati e comprehension

**Obiettivi del capitolo**

- Sapere quali strutture dati Python il progetto usa davvero, e a cosa corrispondono nel mondo Java.
- Leggere una list comprehension o una dict comprehension come faresti con uno stream Java, riconoscendone la forma.
- Capire perché il dizionario globale `results` di `function.py` è un punto di attenzione, in termini di stato condiviso.

## 8.1 Liste, dizionari, tuple vs. `List`/`Map`/nessun equivalente diretto per le tuple

Python ha quattro strutture dati integrate nel linguaggio stesso — non in una libreria a parte — che ricorrono in ogni file di questo progetto: la **lista** (`[1, 2, 3]`, mutabile, ordinata, equivalente più vicino a `ArrayList<T>`), il **dizionario** (`{"a": 1}`, mutabile, chiavi-valori, equivalente più vicino a `HashMap<K,V>`), la **tupla** (`(1, 2)`, ordinata come una lista ma immutabile), e l'**insieme** (`{1, 2, 3}`, non ordinato, senza duplicati, equivalente più vicino a `HashSet<T>` — usato una sola volta nel progetto, implicitamente, da `.unique()` di pandas, non come `set` letterale).

La tupla merita attenzione perché non ha un equivalente diretto e altrettanto naturale in Java. **[Fatto]** `preprocessing.py:43`:
```python
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
```
`train_test_split` restituisce **quattro valori in una volta sola**, impacchettati in una tupla, e la riga li assegna a quattro variabili in un solo passaggio — una forma di destrutturazione posizionale. In Java, un metodo può restituire un solo valore: per ottenerne quattro dovresti restituire un array, un oggetto dedicato con quattro campi, oppure quattro chiamate separate. Qui non serve dichiarare nulla in anticipo: la tupla di ritorno esiste solo per la durata di quella riga, e le quattro variabili a sinistra la "spacchettano" in base alla posizione, non al nome.

> **SE VIENI DA JAVA —** questa destrutturazione posizionale ricorre in tutto il progetto ogni volta che una funzione ha più di un risultato logico da restituire: `X_train_bal, y_train_bal = balance_classes(...)` (`preprocessing.py:53`), `acc_mean, acc_ci = ci(bootstrap_metrics_dict['acc'])` (`evaluation.py:29`). Non esiste, in nessuno di questi casi, una classe che rappresenti "il risultato di questa funzione": è sempre e solo una tupla anonima, letta per posizione.

## 8.2 List comprehension, dict comprehension ed espressioni generatore

Una **list comprehension** costruisce una nuova lista applicando un'espressione a ogni elemento di una sequenza esistente, in un'unica riga: `[espressione for elemento in sequenza]`, opzionalmente con un filtro (`if condizione`) alla fine. È l'equivalente concettuale di uno stream Java con `.map()` (ed eventualmente `.filter()`) seguito da `.collect(Collectors.toList())` — ma senza bisogno di alcuna chiamata esplicita a `collect`: la lista è il risultato diretto dell'espressione fra parentesi quadre.

**[Fatto]** Il progetto ne fa un uso pervasivo. Alcuni esempi reali, in ordine di complessità crescente:
```python
model_order = [name for name, _, _ in roc_data]                                   # function.py:258
dfs = [pd.read_csv(f, header=None, na_values="?") for f in files]                  # function.py:103
colors = ["#e34948" if v > 0 else "#2a78d6" for v in df_sorted["deviation"]]       # function.py:378
texts = [record_to_text(r) for _, r in X.iterrows()]                               # embedding.py:17
```
L'ultimo esempio merita un momento: `X.iterrows()` restituisce, per ogni riga di un DataFrame pandas, una coppia (indice, riga) — la comprehension usa `_` per l'indice, segnalando con la convenzione del trattino basso "questo valore esiste ma non mi interessa", e applica `record_to_text` (che sia la versione per Heart Disease o per Diabetes130, scelta alla riga precedente) a ogni riga, producendo una lista di frasi.

**[Fatto]** Esiste anche l'equivalente per i dizionari, usato una sola volta nel progetto: `MODEL_FAMILY = {m["model_name"]: m["family"] for m in models_all}` (`function.py:54`) costruisce un dizionario che associa a ogni nome breve di modello la sua famiglia, iterando sulla lista di configurazione e producendo, per ogni elemento, una coppia chiave-valore.

> **APPROFONDIMENTO FACOLTATIVO —** cambiando le parentesi quadre `[...]` in parentesi tonde `(...)`, la stessa sintassi produce non una lista ma un **generatore**: un oggetto che produce i valori uno alla volta, su richiesta, invece di costruire subito l'intera lista in memoria. Questo progetto non usa mai questa forma (né la forma più esplicita con la parola chiave `yield` in una funzione, anch'essa assente — verificato con una ricerca sistematica su tutti i file). Vale comunque la pena saperlo riconoscere, perché la differenza sintattica è minima — una parentesi al posto di un'altra — mentre la differenza di comportamento (tutto subito in memoria contro un valore alla volta) può essere rilevante su dataset molto più grandi di quelli usati qui.

## 8.3 Il dizionario globale mutabile di `function.py`

**[Fatto]** `function.py:67-72` definisce, a livello di modulo — non dentro nessuna funzione — questo dizionario:
```python
results = {
    "e5-base":    {"acc": [], "f1": [], "auc": [], "tau": []},
    "e5-large":   {"acc": [], "f1": [], "auc": [], "tau": []},
    "gte-large":  {"acc": [], "f1": [], "auc": [], "tau": []},
    "gte-base":  {"acc": [], "f1": [], "auc": [], "tau": []}
}
```
Nota subito una cosa: contiene solo 4 delle 7 chiavi che il progetto userà davvero (mancano `bioclinicalbert`, `pubmedbert`, `sentence-biobert`). **[Fatto]** `classification.py:51` scrive `results[model['model_name']] = {...}` per ognuno dei 7 modelli in `models_all`: per le prime 4 chiavi questo *sovrascrive* il valore iniziale, per le altre 3 lo *crea da zero*. In Python un dizionario non ha uno schema fisso: assegnare a una chiave che non esiste ancora la crea silenziosamente, senza errori, che tu l'avessi prevista o no in fase di inizializzazione. In Java, l'equivalente più vicino — una `Map<String, Metriche>` — si comporterebbe allo stesso modo con `.put()`, quindi qui la differenza non è nel comportamento della mappa in sé, ma nel fatto che l'inizializzazione di `results` sembra dichiarare uno schema (4 chiavi specifiche) che poi il codice ignora completamente.

Il punto più delicato non è questo, però: `results` è un dizionario **a livello di modulo**, importato con `from function import ... results` in `classification.py:7` e mutato lì con `results[...] = ...`. Nessuna riga usa la parola chiave `global` — verificato, non ce n'è traccia in tutto il progetto — e non ne serve una: `global` servirebbe solo per *riassegnare* interamente il nome `results` a un nuovo oggetto dentro una funzione (`results = {}`), non per modificare il contenuto dell'oggetto a cui `results` punta già. Scrivere `results[chiave] = valore` è una mutazione dell'oggetto esistente, permessa da qualunque funzione che abbia un riferimento a quell'oggetto, senza bisogno di dichiarazioni particolari.

> **ATTENZIONE —** è precisamente questo comportamento — mutare senza riassegnare — a rendere `results` uno stato globale mutabile silenzioso: qualunque funzione che importi `results` da `function` può modificarlo, e ogni altra parte del programma che lo importi vede quella modifica, perché tutte condividono lo stesso oggetto dizionario in memoria, non una copia. Nell'uso attuale del progetto (un processo per dataset, `classification.py` chiamato una sola volta da `main.py`) questo non causa un bug osservabile. Se qualcuno riusasse queste funzioni in un contesto diverso — un notebook, un test che chiama `training_classifier()` due volte nello stesso processo — troverebbe `results` già popolato dalla chiamata precedente, un comportamento sorprendente per chi si aspetta che ogni chiamata di funzione parta "pulita". Ne riparliamo, con l'inquadramento architetturale completo, al capitolo 19.2.

## Riepilogo

Liste, dizionari e insiemi in Python corrispondono abbastanza direttamente a `List`, `Map` e `Set` in Java; la tupla, usata ovunque nel progetto per restituire più valori da una funzione in un colpo solo, non ha un equivalente altrettanto naturale. Le comprehension — usate in modo pervasivo nel progetto per liste, una sola volta per un dizionario — costruiscono una nuova collezione in un'unica espressione, senza bisogno di un ciclo esplicito o di `.collect()`. Il dizionario `results` di `function.py` è uno stato globale mutabile: funziona nell'uso attuale del progetto, ma è un punto di attenzione se il codice venisse riusato in un contesto diverso da un singolo processo per dataset.

## Domande di autoverifica

**1. Perché `train_test_split(...)` può restituire quattro valori con un'unica istruzione, mentre un metodo Java tipicamente ne restituisce uno solo?**
Perché in Python i quattro valori vengono impacchettati in una tupla anonima, e l'istruzione di assegnazione la spacchetta per posizione in quattro variabili nello stesso momento. Java richiederebbe un array, un oggetto con quattro campi dichiarato appositamente, o quattro chiamate separate.

**2. Cosa succede, in Python, se assegni a una chiave di dizionario che non esiste ancora?**
Il dizionario la crea silenziosamente, senza sollevare un errore — è esattamente ciò che fa `classification.py:51` per le tre chiavi di `results` non presenti nell'inizializzazione di `function.py:67-72`.

**3. Perché mutare `results` da `classification.py` non richiede la parola chiave `global`?**
Perché `global` serve solo quando una funzione deve *riassegnare* interamente un nome di variabile di modulo a un nuovo oggetto. Qui il codice modifica il contenuto dell'oggetto dizionario esistente (`results[chiave] = valore`), un'operazione permessa a chiunque abbia un riferimento a quell'oggetto, senza bisogno di dichiarazioni aggiuntive.

> **MATERIALE PER LA TESI**
> 1. L'esempio della destrutturazione di tupla in `preprocessing.py:43`, con il confronto esplicito rispetto alla necessità di un oggetto multi-campo in Java — riusabile come illustrazione di una differenza idiomatica concreta in "Materiali e metodi".
> 2. La sequenza di comprehension reali con relativa spiegazione (§8.2) — riusabile come esempio di stile idiomatico Python, utile per motivare la leggibilità (o meno) del codice analizzato.
> 3. L'analisi del dizionario globale `results` come stato mutabile condiviso, con la precisazione sul perché non serve `global` — riusabile nella discussione critica (capitolo 19.2) sulla robustezza del codice a un riuso diverso da quello attuale.

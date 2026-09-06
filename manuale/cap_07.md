# Capitolo 7 — Sintassi minima e idiomi core

**Obiettivi del capitolo**

- Leggere un blocco di codice Python senza cercare parentesi graffe o punti e virgola che non ci sono.
- Capire cosa significa "tipizzazione dinamica" concretamente, con un esempio reale del progetto.
- Sapere cosa fa `self` in Python, anche se — fatto notevole — non lo vedrai mai *definito* in questo progetto.

## 7.1 Indentazione come sintassi, niente `{}` né `;`

In Java, i blocchi di codice sono delimitati da `{` e `}`; l'indentazione è una convenzione stilistica, non richiesta dal compilatore. In Python, l'indentazione **è** la sintassi: due righe indentate allo stesso livello, subito dopo i due punti che chiudono un `if`, un `for`, o una definizione di funzione, appartengono allo stesso blocco. Non c'è modo di "sbagliare le graffe" in Python, perché non ce ne sono — ma c'è modo di sbagliare l'indentazione, ed è un errore che Java non ti lascerebbe mai commettere in questa forma, perché per lui l'indentazione è invisibile.

**[Fatto]** Un esempio qualunque del progetto, `main.py:20-24`:
```python
def main():
    args = parse_args()
    dirs = get_output_dirs(args.dataset)
    delete_files_embeddings(dirs["embeddings"])
```
Le tre righe dopo `def main():` appartengono al corpo della funzione perché sono indentate di quattro spazi rispetto a `def`. Non c'è un `}` che segnali dove il corpo finisce: finisce quando l'indentazione torna al livello precedente.

> **SE VIENI DA JAVA —** non esiste il punto e virgola come terminatore di istruzione: la fine della riga è la fine dell'istruzione (salvo pochi casi espliciti, come le espressioni fra parentesi che continuano su più righe, molto comuni in questo progetto — vedi la definizione multi-riga di `parse_args()` in `main.py:12-18`, tenuta insieme dalle parentesi tonde di `add_argument`, non da alcun carattere di continuazione).

## 7.2 Tipizzazione dinamica e duck typing vs. tipizzazione statica di Java

**[Fatto]** In tutti e nove i file Python di questo progetto, non compare **una sola** annotazione di tipo — né sui parametri di funzione (`def foo(x: int)`), né sui valori di ritorno (`-> bool`), verificato con una ricerca sistematica su tutti i file. Ogni parametro, ogni variabile, ogni valore di ritorno ha un tipo — Python è dinamicamente tipizzato, non "senza tipi" — ma quel tipo si scopre solo eseguendo il codice, non leggendo una firma dichiarata. `def preprocessing_data(dataset="heart_disease")` (`preprocessing.py:19`) ti dice che esiste un parametro `dataset` con un valore di default: non ti dice, e non può dirti staticamente, che deve essere una stringa fra `"heart_disease"` e `"diabetes130"` — lo scopri leggendo `get_output_dirs()` (`function.py:79-81`), che solleva un errore *a runtime* se il valore non è tra quelli attesi.

Questa non è un'assenza casuale: Python offre da tempo una sintassi di annotazioni di tipo opzionali (proprio come quella che ti aspetteresti, `def foo(x: int) -> bool:`), ma restano **decorative** senza uno strumento esterno che le controlli (come `mypy`) — l'interprete le ignora a runtime. Il fatto che questo progetto non le usi affatto è una scelta (o un'assenza di scelta) reale e verificabile, non un limite del linguaggio.

**[Fatto]** Il *duck typing* — "se si comporta come un'anatra, trattalo come un'anatra, senza chiederti se è davvero della classe Anatra" — compare esplicitamente in `preprocessing.py:109`:
```python
if hasattr(X_train_emb, "toarray"):
    X_train_emb = X_train_emb.toarray()
```
Questo codice non controlla *il tipo* di `X_train_emb` con un `isinstance()`: controlla se l'oggetto *possiede il metodo* `toarray` — tipico di una matrice sparsa prodotta da `OneHotEncoder` quando ci sono molte categorie. Se l'oggetto ce l'ha, lo chiama; se non ce l'ha (perché `ColumnTransformer` ha già restituito un array denso), salta il passaggio. In Java, un controllo equivalente richiederebbe che `X_train_emb` implementasse un'interfaccia comune con un metodo dichiarato — qui basta che l'oggetto, qualunque cosa sia, risponda a quel nome di metodo.

> **ATTENZIONE —** la stessa lettera, `X`, denota in questo progetto oggetti di tipo concreto diverso a seconda del file: in `preprocessing.py` è quasi sempre un `pandas.DataFrame`; in `classification.py:13`, dopo `np.load(...)`, è un `numpy.ndarray`. Nessuna riga di codice lo dichiara: lo capisci solo seguendo da dove viene il valore. È il prezzo della tipizzazione dinamica — flessibilità immediata, nessuna rete di sicurezza del compilatore.

## 7.3 `self` esplicito, niente `this` implicito

**[Fatto]** Nessuno dei nove file del progetto definisce una singola classe propria — zero occorrenze della parola chiave `class`, verificato con una ricerca sistematica. Il progetto è scritto interamente in stile procedurale: funzioni che si chiamano a vicenda, nessun oggetto con stato incapsulato definito dal progetto stesso. Questo significa che non troverai, nel codice di questo progetto, un solo posto dove `self` viene *dichiarato* in una firma di metodo.

Lo vedi però, indirettamente, ogni volta che il codice chiama un metodo su un oggetto di libreria. Quando scrivi `logisticReg.fit(X_train, y_train)` (`classification.py:26`), da qualche parte dentro scikit-learn esiste una definizione simile a `def fit(self, X, y):` — `self` è il parametro che riceve, esplicitamente, l'oggetto `logisticReg` su cui il metodo è stato chiamato. In Java, il riferimento all'oggetto corrente (`this`) è sempre disponibile implicitamente dentro un metodo di istanza: non lo dichiari nella firma, il compilatore lo aggiunge per te. In Python, quel primo parametro va scritto a mano in ogni definizione di metodo — non è un'eccezione stilistica, è una regola del linguaggio.

> **SE VIENI DA JAVA —** la differenza pratica più immediata: se un giorno definisci tu una classe in Python e ti scordi `self` come primo parametro di un metodo, il codice fallisce a runtime con un errore sul numero di argomenti — non a compile time, perché niente in Python controlla staticamente le firme dei metodi. Non è un problema che affronti leggendo questo progetto (non definisce classi), ma è tra i primi errori che chiunque incontra scrivendo Python per la prima volta.

**[Interpretazione]** Il fatto che l'intero progetto non usi mai una classe propria non è casuale rispetto al suo dominio: la pipeline è una sequenza di trasformazioni di dati (tabella → testo → embedding → previsione → grafico), non un sistema con entità che mantengono stato nel tempo. Uno stile procedurale, con funzioni pure per quanto possibile, è una scelta comune e ragionevole per questo tipo di codice — lo stesso lavoro, in un contesto enterprise Java, verrebbe probabilmente organizzato in classi di servizio con metodi statici, non troppo diverse concettualmente da queste funzioni a livello di modulo.

## Riepilogo

L'indentazione in Python sostituisce le parentesi graffe come delimitatore di blocco, e il punto e virgola non serve. Il progetto non usa mai annotazioni di tipo: ogni tipo si scopre a runtime, e il duck typing (`hasattr` invece di `isinstance`, capitolo 7.2) è la norma, non l'eccezione. Nessuna classe è definita nel codice del progetto: `self` lo incontri solo quando chiami metodi di libreria, mai in una definizione propria.

## Domande di autoverifica

**1. Perché l'assenza di annotazioni di tipo in questo progetto non significa che le variabili non abbiano un tipo?**
Perché Python è dinamicamente tipizzato, non privo di tipi: ogni valore ha un tipo concreto in ogni momento, ma quel tipo si stabilisce solo eseguendo il codice, non dichiarandolo in anticipo in una firma che il compilatore controlla.

**2. Cosa controlla `hasattr(X_train_emb, "toarray")` in `preprocessing.py:109`, e cosa NON controlla?**
Controlla se l'oggetto possiede un metodo chiamato `toarray`, indipendentemente dalla sua classe esatta. Non controlla se l'oggetto è un'istanza di un tipo specifico (non usa `isinstance`) — è duck typing puro.

**3. Perché non troverai mai, in questo progetto, una definizione di metodo con `self` come primo parametro?**
Perché il progetto non definisce alcuna classe propria — è scritto interamente in stile procedurale, con funzioni a livello di modulo che si richiamano a vicenda.

> **MATERIALE PER LA TESI**
> 1. Il dato verificato "zero annotazioni di tipo in nove file, zero classi definite" — riusabile come caratterizzazione oggettiva dello stile di programmazione del progetto in "Materiali e metodi".
> 2. L'esempio di duck typing con `hasattr` (`preprocessing.py:109`), confrontato esplicitamente con l'equivalente concettuale in un linguaggio a tipizzazione statica — riusabile come illustrazione tecnica in un capitolo che discuta le scelte implementative.
> 3. L'osservazione che lo stile puramente procedurale è coerente con la natura del progetto (una pipeline di trasformazioni, non un sistema stateful) — riusabile come argomento a favore di una scelta progettuale, utile in una sezione di giustificazione metodologica.

# Capitolo 9 — Funzioni, argomenti, trappole

**Obiettivi del capitolo**

- Distinguere argomenti posizionali e keyword, e riconoscere i valori di default nel codice del progetto.
- Conoscere la trappola degli argomenti mutabili di default — non presente in questo progetto, ma fra le più citate del linguaggio, e per questo da sapere comunque.
- Capire come Python gestisce funzioni con lo stesso nome ma scopi diversi, in assenza di overloading.

## 9.1 Argomenti posizionali, keyword, default — e il pericolo dei default mutabili

Una funzione Python può ricevere argomenti in due modi, spesso mescolati nella stessa chiamata: **posizionali** (l'ordine conta, come in Java) e **keyword** (il nome del parametro è scritto esplicitamente nella chiamata, l'ordine non conta più). **[Fatto]** `function.py:103`:
```python
dfs = [pd.read_csv(f, header=None, na_values="?") for f in files]
```
`f` è posizionale (il primo argomento di `read_csv`); `header=None` e `na_values="?"` sono keyword. In Java, l'equivalente più vicino sarebbe un overload di metodo con quella combinazione specifica di parametri, oppure un builder — qui è semplicemente la stessa funzione, chiamata specificando solo i parametri che vuoi cambiare rispetto al loro default.

**[Fatto]** I default stessi compaiono ovunque nelle firme del progetto: `def preprocessing_data(dataset="heart_disease")` (`preprocessing.py:19`), `def bootstrap_metrics(y_true, y_score, y_pred, n_iter=10000, seed=42)` (`evaluation.py:62`), `def load_diabetes130(sample_size=20000, random_state=42)` (`function.py:116`). In tutti questi casi il default è un valore immutabile — una stringa, un intero — e non c'è alcun problema.

> **ATTENZIONE —** se il default fosse invece una lista o un dizionario, ci sarebbe un problema, e non un problema ipotetico: è una delle trappole più conosciute e più citate dell'intero linguaggio, e vale la pena saperla riconoscere anche se — verificato — non compare in nessuna firma di questo progetto. Considera una funzione scritta così, in un progetto diverso da questo:
> ```python
> def aggiungi_errore(lista_errori=[]):
>     lista_errori.append("errore")
>     return lista_errori
> ```
> Ti aspetteresti che ogni chiamata a `aggiungi_errore()` senza argomenti parta da una lista vuota. Non è così: il valore di default `[]` viene creato **una sola volta**, nel momento in cui Python legge la definizione della funzione — non a ogni chiamata. Tutte le chiamate che non passano `lista_errori` esplicitamente condividono *lo stesso oggetto lista*, che quindi cresce a ogni chiamata: la seconda chiamata restituisce `["errore", "errore"]`, non `["errore"]`. In Java questo problema non si presenta nella stessa forma, perché ogni invocazione di metodo che crea un nuovo `ArrayList<>()` nel corpo del metodo ne crea davvero uno nuovo ogni volta — l'inizializzazione è parte del corpo eseguito a ogni chiamata, non della firma valutata una sola volta.

## 9.2 Funzioni come cittadini di prima classe

In Python, una funzione è un valore come un altro: puoi assegnarla a una variabile, passarla come argomento, restituirla da un'altra funzione, senza alcuna sintassi speciale o interfaccia da implementare. **[Fatto]** `function.py:246`:
```python
model_order = sorted(results_dict.keys(), key=lambda m: (MODEL_FAMILY.get(m, ""), m))
```
`lambda m: (MODEL_FAMILY.get(m, ""), m)` è una funzione anonima di una riga, passata a `sorted()` tramite il parametro keyword `key`: per ogni elemento `m` da ordinare, restituisce una tupla (famiglia, nome), e `sorted()` ordina usando quella tupla come chiave di confronto — prima per famiglia, poi per nome, entrambi in ordine alfabetico. La stessa identica riga ricorre altre due volte nel progetto (`function.py:292,363`), sempre per ordinare i modelli in modo coerente nei grafici.

**[Fatto]** Un esempio più esplicito ancora, `embedding.py:206`:
```python
futures.append(executor.submit(process_model, m, texts, labels, embeddings_dir))
```
`process_model` — il *nome della funzione stessa*, senza parentesi che la invochino — è passato come primo argomento a `executor.submit()`, che la eseguirà più tardi, in un thread del pool, con gli argomenti successivi. Non è invocata qui: è passata come valore, per essere invocata altrove.

> **SE VIENI DA JAVA —** da Java 8 in poi, lambda e riferimenti a metodo (`ClassName::methodName`) rendono questo pattern familiare, quindi la differenza è meno estranea di quanto sembri a prima vista. Ciò che resta diverso: in Python qualunque funzione è già un valore di prima classe, sempre, senza bisogno che il tipo del parametro che la riceve dichiari un'interfaccia funzionale compatibile (l'equivalente di `Runnable`, `Function<T,R>`, o un'interfaccia personalizzata con `@FunctionalInterface`). `executor.submit()` accetta letteralmente "una funzione, qualunque essa sia, più i suoi argomenti" — non esiste un tipo dichiarato a cui `process_model` deve conformarsi.

## 9.3 Assenza di overloading: come Python distingue le firme

In Java puoi definire due metodi con lo stesso nome e parametri di tipo diverso, e il compilatore sceglie quale invocare in base ai tipi degli argomenti nella chiamata. Python non ha questo meccanismo: due funzioni con lo stesso nome nello stesso modulo, la seconda sovrascrive semplicemente la prima — non c'è "risoluzione di overload" perché non ci sono tipi dichiarati su cui basarla.

**[Fatto]** Il progetto risolve lo stesso tipo di problema — comportamento diverso a seconda dei dati — con funzioni dal **nome esplicitamente diverso**, scelte a runtime con un `if`/`else` ordinario: `record_to_text_heart_disease()` e `record_to_text_diabetes130()` (`embedding.py:43,64`), selezionate in `embedding.py:16`:
```python
record_to_text = record_to_text_diabetes130 if dataset == "diabetes130" else record_to_text_heart_disease
```
Nota la seconda cosa interessante di questa riga, oltre alla scelta fra le due funzioni: `record_to_text` diventa qui una variabile che *contiene una funzione* (di nuovo, funzioni come valori — capitolo 9.2), poi chiamata più sotto come `record_to_text(r)` senza sapere, in quel punto del codice, quale delle due implementazioni sia stata effettivamente scelta.

> **ATTENZIONE —** questo pattern — un `if`/`else` che sceglie fra due funzioni con nomi diversi — è l'equivalente funzionale di un overload, ma è responsabilità di chi scrive il codice mantenerlo coerente: non c'è alcun controllo che garantisca che `record_to_text_heart_disease` e `record_to_text_diabetes130` abbiano una firma compatibile (nel senso di "prendono entrambe una riga e restituiscono entrambe una stringa"). Lo sono, verificato leggendo entrambe (`embedding.py:43-59` e `embedding.py:64-85`), ma nessuna riga di codice lo impone: è una convenzione, rispettata da chi ha scritto le due funzioni, non verificata da nessuno strumento in questo progetto.

## Riepilogo

Il progetto usa ampiamente argomenti keyword e default immutabili, ma mai un default mutabile — una trappola reale del linguaggio che vale la pena conoscere anche senza un esempio diretto nel codice. Le funzioni sono valori di prima classe: vengono passate come dati a `sorted()` e a `ThreadPoolExecutor.submit()`, senza bisogno di implementare un'interfaccia. In assenza di overloading, la stessa esigenza — comportamento diverso per dataset diverso — è risolta con funzioni dal nome esplicitamente diverso, scelte a runtime con un `if`/`else` ordinario, senza alcuna garanzia automatica di compatibilità fra le firme.

## Domande di autoverifica

**1. Perché una funzione con un parametro di default `lista=[]` è pericolosa, mentre `n_iter=10000` non lo è?**
Perché il valore di default viene creato una sola volta, quando Python legge la definizione della funzione. Un intero è immutabile, quindi non importa se è "condiviso" fra le chiamate. Una lista è mutabile: se una chiamata la modifica, la modifica persiste per tutte le chiamate successive che non forniscono l'argomento esplicitamente.

**2. In che senso `process_model`, passato a `executor.submit()` in `embedding.py:206`, non viene "chiamato" in quel punto del codice?**
Perché compare senza parentesi: è il valore-funzione stesso, non il risultato della sua esecuzione. Verrà effettivamente invocato più tardi, dentro un thread del pool, con gli argomenti passati subito dopo.

**3. Come risolve il progetto l'esigenza di un comportamento diverso per Heart Disease e per Diabetes130, in assenza di overloading di funzione?**
Definendo due funzioni con nomi diversi (`record_to_text_heart_disease`, `record_to_text_diabetes130`) e scegliendo quale delle due usare con un'espressione condizionale a runtime (`embedding.py:16`), non con una risoluzione di tipo a compile time.

> **MATERIALE PER LA TESI**
> 1. L'esempio codificato della trappola degli argomenti mutabili di default, chiaramente distinto dal codice reale del progetto (che non la presenta) — riusabile come nota metodologica su un rischio evitato, utile in una sezione che discuta la qualità del codice.
> 2. L'esempio di `executor.submit(process_model, ...)` con la spiegazione di "funzione come valore" — riusabile per illustrare, in "Materiali e metodi", il meccanismo di concorrenza della generazione degli embedding.
> 3. Il pattern "funzioni con nome diverso invece di overload", con l'osservazione sulla mancanza di garanzie automatiche di compatibilità di firma — riusabile come punto di discussione sulla manutenibilità del codice, in una sezione critica.

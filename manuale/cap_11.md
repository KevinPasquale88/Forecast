# Capitolo 11 — Eccezioni, context manager, decoratori

**Obiettivi del capitolo**

- Leggere `try`/`except`/`raise ... from` riconoscendo le differenze rispetto a `try`/`catch`/`throws`.
- Riconoscere un context manager (`with`) come l'equivalente concettuale del try-with-resources di Java, con tre esempi reali diversi.
- Sapere cosa sono i decoratori, anche se — verificato — non ne troverai uno in questo progetto.

## 11.1 `try`/`except`/`raise ... from`: differenze da `throws`/`catch`

Python non distingue eccezioni "controllate" da eccezioni "non controllate": ogni funzione può sollevare qualunque eccezione in qualunque momento, e non esiste una clausola equivalente a `throws` nella firma che dichiari quali. Chi chiama una funzione non ha modo di sapere, dalla sola firma, cosa può sollevare — solo leggendo il corpo, o la documentazione, se esiste.

**[Fatto]** `embedding.py:115-131` mostra un ciclo di retry con gestione dell'eccezione:
```python
for attempt in range(1, max_retries + 1):
    try:
        with _ollama_semaphore:
            result = client.embed(model=model_name, input=batch)
        all_embeddings.extend(result.embeddings)
        break
    except Exception as e:
        if attempt == max_retries:
            raise RuntimeError(
                f"[Batch] {model_name}: batch {batch_idx + 1}/{num_batches} "
                f"failed after {max_retries} attempts: {e}"
            ) from e
        wait = retry_delay * attempt
        ...
        time.sleep(wait)
```
`except Exception as e` cattura qualunque eccezione (una scelta volutamente ampia: qualunque problema di rete o del server Ollama viene trattato allo stesso modo), la nomina `e`, e la usa per decidere cosa fare: se è l'ultimo tentativo, rilancia un errore più specifico; altrimenti, aspetta e riprova. `break` esce dal ciclo `for` solo se il blocco `try` è andato a buon fine senza sollevare eccezioni.

**[Fatto]** La clausola `from e` alla fine del `raise` (`embedding.py:199` in un punto analogo) è la forma esplicita di **concatenamento di eccezioni**: dichiara che questo nuovo errore (`RuntimeError`) è stato causato da quello originale (`e`), e Python preserva entrambi nel traceback finale — vedrai sia il messaggio del `RuntimeError` sia, più sotto, il messaggio dell'eccezione originale che lo ha scatenato. In Java, l'equivalente è passare la causa al costruttore di una nuova eccezione (`throw new RuntimeException("...", e)`); la differenza sintattica è che in Python questo si esprime con una parola chiave dedicata (`from`), non passando un parametro extra al costruttore.

> **ATTENZIONE —** `except Exception as e` cattura *quasi* tutto — non le eccezioni che derivano da `BaseException` ma non da `Exception` (come l'interruzione da tastiera), una distinzione che in questo progetto non ha conseguenze pratiche, ma che vale la pena sapere che esiste: `Exception` non è, in Python, la radice assoluta della gerarchia di errori, a differenza di come spesso si pensa arrivando da Java dove `Throwable` gioca quel ruolo e `Exception` ne è già una sottoclasse specifica.

## 11.2 Context manager (`with`): il "try-with-resources" di Python

Un **context manager** è un oggetto che sa cosa fare all'inizio e alla fine di un blocco `with`, garantendo che la parte di "fine" (rilascio di una risorsa, ad esempio) avvenga sempre — anche se dentro il blocco viene sollevata un'eccezione. È l'equivalente concettuale del try-with-resources introdotto in Java 7, con una differenza pratica: in Python qualunque oggetto può diventare un context manager implementando due metodi (`__enter__` e `__exit__`), non serve un'interfaccia dichiarata come `AutoCloseable`.

**[Fatto]** Il progetto usa `with` in tre punti, con tre scopi diversi:
```python
with _ollama_semaphore:                                    # embedding.py:117 — un lock
    result = client.embed(model=model_name, input=batch)

with ThreadPoolExecutor(max_workers=max_workers) as executor:   # embedding.py:203 — un pool di thread
    futures = [executor.submit(process_model, m, texts, labels, embeddings_dir) for m in models_all]

with open(md_path, "w") as f:                                # generatereport.py:245 — un file
    f.write(md_content)
```
Nel primo caso, `_ollama_semaphore` (un `threading.Semaphore(1)`, capitolo 12.2) usato come context manager acquisisce il semaforo all'ingresso del blocco e lo rilascia all'uscita — anche se `client.embed(...)` sollevasse un'eccezione, il semaforo verrebbe comunque rilasciato, evitando un blocco permanente. Nel secondo, `ThreadPoolExecutor` come context manager garantisce che tutti i thread del pool vengano chiusi correttamente all'uscita dal blocco, qualunque cosa succeda dentro. Nel terzo — il più vicino a ciò che probabilmente hai già visto in Java — il file viene chiuso automaticamente all'uscita dal blocco, che il blocco sia andato a buon fine o abbia sollevato un'eccezione.

> **SE VIENI DA JAVA —** la keyword `as` dopo `with` (`as executor`, `as f`) assegna a una variabile il valore restituito da `__enter__()` — non necessariamente l'oggetto originale: `open(...)` come context manager restituisce infatti l'oggetto file stesso, ma non è garantito in generale che sia così per ogni context manager. Non serve dichiarare il tipo di `f` da nessuna parte: lo scopri, di nuovo, solo leggendo cosa fa `__enter__()` di quell'oggetto specifico.

## 11.3 Decoratori: cosa sono, dove NON compaiono in questo progetto

Un **decoratore** è una sintassi (`@nome_decoratore` scritta subito sopra una definizione di funzione o di classe) che permette di avvolgere quella funzione con un comportamento aggiuntivo, senza modificarne il corpo. È uno degli idiomi più riconoscibili di Python — lo incontrerai quasi certamente in altri progetti, per esempio nelle route di un framework web come Flask (`@app.route("/utenti")`) o nei test parametrizzati di pytest (`@pytest.fixture`) — ma **[Fatto]** non ne compare uno solo in questo progetto: una ricerca sistematica su tutti e nove i file non trova alcuna riga che cominci con `@` seguito da un nome, al di fuori di eventuali commenti.

**[Interpretazione]** Non è sorprendente, dato quanto visto al capitolo 7.3: i decoratori sono usati più spesso per aggiungere comportamento a metodi di classi o a funzioni che fanno da punto di ingresso per un framework esterno (una rotta HTTP, un test). Questo progetto non definisce classi proprie e non si appoggia a un framework che si aspetti funzioni decorate: è normale che l'idioma non compaia, non è un'omissione da segnalare come criticità.

> **APPROFONDIMENTO FACOLTATIVO —** se un giorno scrivessi tu un decoratore per, per esempio, aggiungere automaticamente il retry-con-attesa che `embedding.py:103-137` implementa oggi a mano dentro `generate_embeddings_batch`, la forma sarebbe all'incirca `@retry(max_tentativi=5)` scritta sopra la definizione della funzione, con tutta la logica di ciclo, attesa e rilancio spostata una volta sola dentro il decoratore invece che ripetuta in ogni funzione che ne ha bisogno. Il progetto non lo fa: la logica di retry vive solo dentro `generate_embeddings_batch`, e non è riusata altrove — un punto a cui torniamo, in chiave di possibile miglioramento, al capitolo 55.

## Riepilogo

Python non distingue eccezioni controllate da non controllate, e `raise ... from` concatena esplicitamente un nuovo errore alla sua causa originale, preservando entrambi nel traceback. Un context manager (`with`) garantisce che un'azione di chiusura avvenga sempre, e questo progetto ne usa tre tipi concettualmente diversi: un lock, un pool di thread, un file. I decoratori esistono come idioma del linguaggio ma non compaiono in questo progetto, verificato sistematicamente — un'assenza coerente con uno stile procedurale senza framework esterni che li richiedano.

## Domande di autoverifica

**1. Cosa aggiunge `from e` a un `raise`, rispetto a un `raise RuntimeError(...)` senza quella clausola?**
Concatena esplicitamente la nuova eccezione a quella originale che l'ha causata: il traceback finale mostra entrambe, rendendo visibile non solo cosa è fallito per ultimo ma anche cosa lo ha scatenato.

**2. Perché i tre usi di `with` in questo progetto non fanno tutti la stessa cosa, pur usando la stessa sintassi?**
Perché ciascun oggetto usato come context manager (`_ollama_semaphore`, `ThreadPoolExecutor`, il file aperto con `open`) definisce autonomamente cosa succede all'ingresso e all'uscita del blocco: un semaforo acquisisce/rilascia un lock, un pool di thread garantisce la chiusura dei thread, un file garantisce la propria chiusura. La sintassi `with` è la stessa; il comportamento dipende dall'oggetto.

**3. Perché l'assenza di decoratori in questo progetto non è, di per sé, un difetto?**
Perché i decoratori sono utili soprattutto per aggiungere comportamento a metodi di classi o a funzioni che si integrano con un framework esterno (rotte web, test parametrizzati) — nessuno dei due casi si applica a un progetto scritto in stile procedurale senza framework di questo tipo.

> **MATERIALE PER LA TESI**
> 1. L'esempio del ciclo di retry con `try`/`except`/`raise ... from` (`embedding.py:115-131,199`) — riusabile come illustrazione della gestione degli errori nella sezione "Materiali e metodi", in particolare per la fase di generazione degli embedding.
> 2. I tre usi distinti di `with` nel progetto, con la spiegazione di cosa garantiscono in ciascun caso — riusabile per motivare la robustezza (o i suoi limiti) della gestione delle risorse nella pipeline.
> 3. L'osservazione sulla logica di retry non incapsulata in un decoratore riusabile — riusabile come spunto concreto per la sezione "Lavori futuri" (capitolo 55), con una proposta di refactoring motivata.

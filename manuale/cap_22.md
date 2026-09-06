# Capitolo 22 — `embedding.py`: tabellare → testo → vettore

**Obiettivi del capitolo**

- Leggere per intero le due funzioni che convertono un record clinico in una frase.
- Capire come il file coordina, in parallelo, quattro chiamate a Ollama e tre a Hugging Face.
- Sapere quali variabili d'ambiente legge questo file, e con quale effetto esatto sul suo comportamento.

**[Fatto]** `embedding.py` (209 righe) è la fase 2 (`main.py:37`), il secondo file più lungo del progetto dopo `function.py`, e l'unico che dialoga con servizi esterni al processo Python (Ollama via rete locale, Hugging Face via download di modelli).

## 22.1 `record_to_text_*()` riga per riga

**[Fatto]** `embedding.py:14-19` è il punto di ingresso del file, chiamato da `main.py:37`:
```python
def embeddings(X, y, dataset="heart_disease"):
    dirs = get_output_dirs(dataset)
    record_to_text = record_to_text_diabetes130 if dataset == "diabetes130" else record_to_text_heart_disease
    texts = [record_to_text(r) for _, r in X.iterrows()]
    generate_all_embeddings(texts, np.asarray(y), dirs["embeddings"])
```
Già vista al capitolo 9.3 (scelta a runtime fra due funzioni con nome diverso, non overload) e al capitolo 8.2 (list comprehension su `X.iterrows()`): quattro righe che, insieme, trasformano l'intero DataFrame in una lista di frasi, pronta per l'embedding.

**[Fatto]** `record_to_text_heart_disease()` (righe 43-59) costruisce la frase concatenando una parte fissa di testo con un valore preso dal record, per ciascuna delle 12 feature (età e sesso condivise in una singola parte iniziale):
```python
def record_to_text_heart_disease(row):
    sex = _fmt_bool(row["sex"], "Male", "Female")
    parts = [
        f"{sex} patient, {_fmt_num(row['age'], ndigits=0)} years old",
        f"chest pain type: {_fmt_cat(row['cp'], CP_LABELS)}",
        f"resting blood pressure: {_fmt_num(row['trestbps'], ' mm Hg', ndigits=0)}",
        ...
    ]
    return ", ".join(parts)
```
Tre funzioni ausiliarie con prefisso underscore (capitolo 10.3) fanno il lavoro di formattazione: `_fmt_num()` (righe 28-31) arrotonda un numero e vi accoda un'unità di misura opzionale; `_fmt_cat()` (righe 33-36) traduce un codice numerico in un'etichetta leggibile usando un dizionario come `CP_LABELS` (riga 23: `{1: "typical angina", 2: "atypical angina", ...}` — gli stessi codici standard del dataset UCI, capitolo 27); `_fmt_bool()` (righe 38-41) traduce un flag binario in due parole a scelta. **[Fatto]** Tutte e tre condividono lo stesso primo controllo, `if pd.isna(value): return "not recorded"` — un valore mancante, a questo punto della pipeline, non dovrebbe più esistere (è stato imputato al capitolo 21.2), ma la funzione lo gestisce comunque esplicitamente, un margine di sicurezza che non costa nulla e previene un `NaN` che finirebbe altrimenti scritto letteralmente nella frase.

**[Fatto]** `record_to_text_diabetes130()` (righe 64-85) è strutturalmente più semplice: usa una sola funzione ausiliaria, `_fmt_raw()` (riga 61-62, `"not recorded" if pd.isna(value) else str(value)`), che non traduce alcun codice — i valori di Diabetes130 (`"Caucasian"`, `"[40-50)"`, `"Norm"`) sono già stringhe leggibili nel file sorgente, a differenza dei codici numerici di Heart Disease.

> **ATTENZIONE —** nessuna delle due funzioni di conversione menziona mai esplicitamente il *target* (`num` o `readmitted`): la frase descrive solo le feature, mai l'etichetta che il classificatore dovrà prevedere. È corretto che sia così — includere l'etichetta nel testo sarebbe una forma di leakage grossolana, praticamente equivalente a scrivere la risposta dentro la domanda — ma vale la pena verificarlo esplicitamente leggendo entrambe le funzioni, non darlo per scontato.

## 22.2 Generazione batch verso Ollama: retry, semaforo

**[Fatto]** `generate_embeddings_batch()` (righe 103-137) invia le frasi a Ollama a gruppi di 16 (`batch_size=16`, default), non tutte insieme: 
```python
def generate_embeddings_batch(model_name, texts, batch_size=16, max_retries=5,
                               retry_delay=2.0, inter_batch_delay=0.3):
    client = Client()
    num_batches = (len(texts) + batch_size - 1) // batch_size
    ...
```
`(len(texts) + batch_size - 1) // batch_size` è un idioma comune per calcolare "quanti gruppi da `batch_size` servono per coprire `len(texts)` elementi, arrotondando per eccesso" usando solo divisione intera — evita di dover importare `math.ceil` per un calcolo così semplice. Il ciclo di retry con `_ollama_semaphore` e `raise ... from` è già stato letto per intero al capitolo 11.1 e al capitolo 12.2: qui vale la pena solo notare `time.sleep(inter_batch_delay)` alla fine di ogni batch riuscito (riga 135) — una pausa fissa di 0.3 secondi, aggiuntiva rispetto al backoff del retry, per non sovraccaricare comunque il server anche quando tutto funziona al primo tentativo.

## 22.3 Generazione verso Hugging Face: autenticazione, modalità offline

**[Fatto]** `generate_embeddings_hf()` (righe 139-180) gestisce i tre modelli biomedici, con una struttura in tre passaggi commentati in italiano direttamente nel codice sorgente (`embedding.py:142,145,153` — una delle poche tracce di commenti non in inglese in tutto il progetto):
```python
hf_token = os.getenv("HF_READ_TOKEN")
if hf_token:
    login(token=hf_token)
...
is_offline = os.getenv("OFFLINE_MODE", "0") == "1"
if is_offline:
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["HF_HUB_OFFLINE"] = "1"
```
`os.getenv("HF_READ_TOKEN")` restituisce `None` se la variabile non è impostata, non solleva un errore — l'`if hf_token:` successivo tratta `None` come falso (capitolo 7.2: nessun tipo dichiarato garantisce che `hf_token` sia una stringa o `None`, lo si scopre solo a runtime). Se `OFFLINE_MODE=1`, il codice imposta **tre variabili d'ambiente diverse** (non solo il flag letto), ciascuna riconosciuta da una parte diversa dell'ecosistema Hugging Face (`transformers`, `datasets`, `huggingface_hub`) — un dettaglio che rivela quanto la modalità offline non sia un singolo interruttore, ma tre interruttori paralleli, storicamente introdotti in momenti diversi della libreria.

**[Fatto]** Il caricamento del modello vero e proprio è una sola riga, `model = SentenceTransformer(model_name, local_files_only=is_offline)` (riga 171), e la generazione degli embedding un'altra, `model.encode(texts, show_progress_bar=True, convert_to_numpy=True)` (riga 178) — già anticipata al capitolo 5.2 per il meccanismo di tokenizzazione/encoder/pooling che nasconde.

## Interfaccia pubblica

| Funzione | Parametri principali | Ritorna |
|---|---|---|
| `embeddings(X, y, dataset="heart_disease")` | Feature, target, dataset | Nessuno (salva su disco) |
| `record_to_text_heart_disease(row)` | Una riga di DataFrame | Stringa |
| `record_to_text_diabetes130(row)` | Una riga di DataFrame | Stringa |
| `generate_embeddings_batch(model_name, texts, batch_size=16, max_retries=5, ...)` | Nome modello Ollama, lista di frasi | Lista di embedding |
| `generate_embeddings_hf(texts, model_name)` | Lista di frasi, nome modello HF | Array NumPy di embedding |
| `process_model(model, texts, labels, embeddings_dir)` | Config di un modello, frasi, etichette, percorso | Nessuno (salva su disco) |
| `generate_all_embeddings(texts, labels, embeddings_dir, max_workers=3)` | Frasi, etichette, percorso | Nessuno (orchestra i 7 modelli) |

## Errori tipici

Un `RuntimeError` con "batch N/M failed after 5 attempts" indica che Ollama non ha risposto correttamente per cinque tentativi consecutivi — quasi sempre perché il server non è in esecuzione o il modello richiesto non è stato scaricato (capitolo 16.1, incluso il caso specifico del nome sbagliato per e5-base). Un errore di autenticazione Hugging Face durante `generate_embeddings_hf()` segnala un `HF_READ_TOKEN` mancante o non valido in `.env` — ma solo se il modello richiede autenticazione; per modelli pubblici il codice procede comunque, stampando solo un avviso (riga 151).

## Riepilogo

`embedding.py` traduce ogni record clinico in una frase con un template fisso specifico per dataset, poi genera i vettori corrispondenti coordinando quattro chiamate Ollama (serializzate da un semaforo, con retry) e tre chiamate Hugging Face (con autenticazione opzionale e tre variabili d'ambiente per la modalità offline) in un pool di tre thread. Nessuna delle due funzioni di conversione a testo include mai l'etichetta target nella frase generata.

## Domande di autoverifica

**1. Perché `record_to_text_heart_disease()` ha bisogno di tre funzioni ausiliarie di formattazione, mentre `record_to_text_diabetes130()` ne usa una sola?**
Perché le feature di Heart Disease sono codificate come numeri che richiedono una traduzione esplicita in etichette leggibili (`_fmt_cat`, `_fmt_bool`), mentre le feature usate di Diabetes130 sono già stringhe leggibili nel file sorgente, e richiedono solo la gestione dei valori mancanti (`_fmt_raw`).

**2. Cosa calcola esattamente `(len(texts) + batch_size - 1) // batch_size`, e perché non un più semplice `len(texts) // batch_size`?**
Il numero di batch necessari per coprire tutti i testi, arrotondato per eccesso: `len(texts) // batch_size` da solo scarterebbe l'ultimo batch parziale se `len(texts)` non fosse un multiplo esatto di `batch_size`.

**3. Perché impostare `OFFLINE_MODE=1` modifica tre variabili d'ambiente diverse invece di una sola?**
Perché l'ecosistema Hugging Face è composto da più librerie distinte (`transformers`, `datasets`, `huggingface_hub`), ciascuna delle quali riconosce una propria variabile d'ambiente per forzare la modalità offline — non esiste un singolo interruttore condiviso fra tutte.

> **MATERIALE PER LA TESI**
> 1. Il template di conversione tabellare→testo per entrambi i dataset, con le funzioni di formattazione — riusabile in "Materiali e metodi" per documentare esattamente come i record diventano testo.
> 2. L'osservazione verificata che nessuna frase include mai l'etichetta target — riusabile come argomento esplicito contro un possibile sospetto di data leakage nella conversione testuale.
> 3. Lo schema di gestione della modalità offline con le tre variabili d'ambiente — riusabile come nota tecnica per chi debba riprodurre l'ambiente sperimentale senza connessione di rete continua.

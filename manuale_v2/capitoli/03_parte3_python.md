# Parte III — Python per chi viene da Java

## Capitolo 9 — Il linguaggio

Python e Java risolvono gli stessi problemi con filosofie diverse: Java dichiara tutto e controlla in compilazione, Python dichiara poco e controlla durante l'esecuzione. Questo capitolo mostra solo ciò che serve per leggere il codice di Forecast, con esempi presi dal progetto.

### 9.1 Tabella di traduzione

| Java | Python | Esempio nel progetto |
| --- | --- | --- |
| `{ ... }` per i blocchi | indentazione (4 spazi) | ogni `def`, `for`, `if` |
| `int x = 5;` | `x = 5` (tipo dinamico) | `sample_size = 20000` |
| `final` / `static final` | convenzione: MAIUSCOLE | `HF_MAX_SEQ_LENGTH = 512` |
| `List<String>` | `list` (`[...]`) | `columns = ["age", "sex", ...]` |
| `Map<K,V>` | `dict` (`{k: v}`) | `CP_LABELS = {1: "typical angina", ...}` |
| record / tupla | `tuple` (`(a, b)`) | `return X_train, X_test, y_train, y_test` |
| `null` | `None` | `sample_size=None` |
| `String.format` | f-string | `f"{model_name}_y_score.npy"` |
| interfaccia + implementazioni | duck typing | ogni modello scikit-learn ha `fit`/`predict_proba` |
| `try/catch/finally` | `try/except/finally` | `process_model()` in `embedding.py` |
| `throw new X(msg, cause)` | `raise X(msg) from e` | `raise RuntimeError(...) from e` |
| try-with-resources | `with` | `with open(...) as f`, `with _ollama_semaphore:` |
| lambda `x -> x * 2` | `lambda x: x * 2` | `lambda v: _fmt_num(v, ndigits=0)` |
| `public static void main` | `if __name__ == "__main__":` | in fondo a `main.py` e `inference.py` |
| `ExecutorService` | `ThreadPoolExecutor` | `generate_all_embeddings()` |
| Maven / Gradle | `pip` + `requirements.txt` | installazione |
| JUnit | pytest | cartella `tests/` |

### 9.2 Tipizzazione dinamica e duck typing

Una variabile non ha tipo: lo ha il valore. `y` in `preprocessing_data()` è prima una `pandas.Series` di interi, poi una Series di 0/1; nessuna dichiarazione cambia. Il vantaggio è la brevità; il prezzo è che gli errori di tipo emergono solo quando la riga viene eseguita.

Il duck typing ("se cammina come un'anatra...") sostituisce le interfacce: una funzione accetta qualunque oggetto che abbia i metodi che usa. `evaluate()` nello script delle baseline accetta sia una regressione logistica sia un gradient boosting perché entrambi hanno `fit()` e `predict_proba()`.

### 9.3 Funzioni e argomenti

```python
def preprocessing_data(dataset="heart_disease"):
    ...
X_train, X_test, y_train, y_test = preprocessing_data(dataset="diabetes130")
```

- **Argomenti con default** (`dataset="heart_disease"`) e **per nome** (`dataset=...`) sostituiscono l'overloading, che in Python non esiste.
- **Più valori di ritorno**: in realtà una tupla, "spacchettata" in quattro variabili.
- **Trappola dei default mutabili**: un default come `def f(x=[])` è creato una volta sola e condiviso tra le chiamate. Il progetto non lo usa; va ricordato.
- **Funzioni come valori**: `RECORD_TO_TEXT = {"heart_disease": record_to_text_heart_disease, ...}` in `inference.py` è un dizionario di funzioni, l'equivalente di una mappa di strategie.

### 9.4 Comprehension

Una comprehension costruisce una lista o un dizionario in una riga:

```python
results = {m["model_name"]: {"acc": [], "f1": [], "auc": [], "tau": []} for m in models_all}
texts = [record_to_text(r) for _, r in X.iterrows()]
```

La prima, in `function.py`, crea un dizionario con una voce per modello configurato; la seconda, in `embedding.py`, trasforma ogni riga in frase. In Java servirebbero un ciclo e una collezione mutabile, oppure uno stream con `collect`.

### 9.5 Moduli e import

Ogni file `.py` è un modulo. `from function import models_all, get_output_dirs` importa nomi specifici. Non esiste `private`: per convenzione un nome che inizia con `_` (`_fmt_num`, `_benjamini_hochberg`) è interno al modulo, ma resta accessibile (i test lo importano). Il progetto è "piatto": tutti i moduli stanno nella radice e si importano tra loro; `pytest.ini` con `pythonpath = .` serve perché i test li trovino.

### 9.6 Eccezioni e context manager

```python
try:
    ...
except Exception as e:
    raise RuntimeError(f"Embedding generation failed for model '{name}' ({split}): {e}") from e
```

`from e` conserva l'eccezione originale come causa, come il secondo argomento dei costruttori di eccezione in Java.

`with` garantisce il rilascio di una risorsa anche in caso di errore: `with open(path) as f` chiude il file, `with _ollama_semaphore:` rilascia il semaforo che serializza le richieste a Ollama.

### 9.7 Concorrenza: GIL e thread

L'interprete CPython ha un *Global Interpreter Lock*: un solo thread alla volta esegue bytecode Python. I thread servono comunque quando il lavoro è attesa di I/O o calcolo in librerie native che rilasciano il lock. `generate_all_embeddings()` usa un `ThreadPoolExecutor` con tre thread: mentre un thread aspetta Ollama, un altro può far girare PyTorch per un modello Hugging Face. Il semaforo `_ollama_semaphore = threading.Semaphore(1)` impedisce che due thread interroghino Ollama contemporaneamente, cosa che in passato esauriva le porte locali (errore "can't assign requested address").

## Capitolo 10 — L'ecosistema scientifico

### 10.1 NumPy

Array n-dimensionali omogenei e operazioni vettoriali. Gli embedding sono array `float32` di forma (record, dimensioni), salvati con `np.save` in file `.npy`. Le **maschere booleane** sono l'idioma più usato nel progetto:

```python
fp_mask = (y_true == 0) & (y_pred == 1)   # falsi positivi
records[fp_mask]                          # solo quelle righe
```

`&` è l'AND elemento per elemento; le parentesi sono obbligatorie per la precedenza degli operatori.

### 10.2 pandas

Tabelle (`DataFrame`) e colonne (`Series`) con etichette. Funzioni usate nel progetto: `read_csv` (con `na_values="?"` e `keep_default_na=False`), `drop`, `isna`, `fillna`, `replace`, `iterrows` (itera sulle righe: lento ma leggibile, accettabile per 20.000 record), `groupby`, `to_csv`.

> *Attenzione.* `pd.read_csv` tratta per default come mancanti molte stringhe, tra cui `"None"`, `"NA"`, `"null"`. In Diabetes130 `"None"` è una categoria ("test non eseguito"). Per questo il progetto usa `keep_default_na=False`, e passa il test set in memoria invece di rileggerlo dal CSV.

### 10.3 scikit-learn

Tutti i modelli seguono la stessa interfaccia: `fit(X, y)` addestra, `predict_proba(X)` restituisce le probabilità per classe (colonna 1 = classe positiva), `predict(X)` usa una soglia di 0,5. Il progetto non usa `predict`: confronta `predict_proba(X)[:, 1]` con la propria soglia.

Altri componenti usati: `StratifiedKFold` e `train_test_split` (divisioni), `cross_val_predict` (predizioni out-of-fold), `precision_recall_curve`, `roc_auc_score`, `average_precision_score`, `brier_score_loss`, `f1_score`, `accuracy_score`, `StandardScaler`, `OneHotEncoder`, `ColumnTransformer`, `make_pipeline` (una sequenza di trasformazioni e un modello che si comporta come un unico modello, così la standardizzazione viene stimata solo sui dati di addestramento), `GridSearchCV` (prova una griglia di iperparametri con una cross-validation).

### 10.4 sentence-transformers, Transformers, PyTorch

`SentenceTransformer(nome)` scarica (la prima volta) e carica un modello dalla cache di Hugging Face (`~/.cache/huggingface/hub`); `encode(lista_di_frasi)` restituisce un array NumPy. Sotto, Transformers fornisce tokenizer e rete, PyTorch esegue i calcoli (su CPU nel progetto).

### 10.5 Ollama

Ollama è un server locale che esegue modelli in formato GGUF. Si installa come applicazione, si avvia con `ollama serve`, si scaricano i modelli con `ollama pull <nome>`. Il client Python (`ollama.Client().embed(model=..., input=[...])`) chiama l'API HTTP locale sulla porta 11434.

### 10.6 Statistica e grafici

SciPy fornisce `wilcoxon` e `ttest_rel`; MLstatkit fornisce `Delong_test`; UMAP (`umap-learn`) la proiezione 2D; Matplotlib e seaborn i grafici.

### 10.7 pytest

Un test è una funzione il cui nome inizia per `test_`; le asserzioni sono semplici `assert`. Strumenti usati nei test del progetto:

- `tmp_path`: una cartella temporanea per scrivere file finti (per esempio un `X_train_raw.csv`);
- `pytest.raises(ValueError, match="age")`: verifica che venga sollevata un'eccezione con un certo messaggio;
- `@pytest.mark.parametrize`: lo stesso test su più input;
- fixture `autouse`: codice eseguito prima e dopo ogni test (svuotare le cache di `inference.py`).

Si eseguono con `python -m pytest` dalla radice; oggi sono 31 test e girano in pochi secondi senza rete.

## Capitolo 11 — Ambiente, installazione e problemi tipici

### 11.1 Ambiente virtuale

Un ambiente virtuale (`python3 -m venv env`) è una cartella con un interprete e le sue librerie, separata dal sistema: l'equivalente di un classpath dedicato al progetto. Si attiva con `source env/bin/activate`; `pip install -r requirements.txt` installa le versioni fissate. La cartella `env/` non va nel repository.

### 11.2 Installazione completa (macOS, Apple Silicon)

1. Python 3.14 nativo arm64 (verificare con `python3 -c "import platform; print(platform.machine())"`, deve stampare `arm64`).
2. `python3 -m venv env && source env/bin/activate && pip install -r requirements.txt`.
3. Ollama dall'applicazione ufficiale; `ollama serve`; poi i quattro `ollama pull` (`jeffh/intfloat-e5-base-v2:q8_0`, `twwch/m3e-base`, `zyw0605688/gte-large-zh`, `jeffh/intfloat-multilingual-e5-large-instruct:q8_0`).
4. File `.env` con `HF_READ_TOKEN=<token>` e `OFFLINE_MODE=0`; dopo il primo download si può mettere `OFFLINE_MODE=1`.
5. `python -m pytest` (verifica rapida), poi `python main.py --dataset heart_disease`.

`run_pipeline.sh` (e le versioni `.bat`/`.ps1` per Windows) automatizza i passi 2–5.

### 11.3 Problemi tipici

| Sintomo | Causa | Soluzione |
| --- | --- | --- |
| `bad CPU type in executable` | Eseguibile per Intel (x86_64) su Apple Silicon senza Rosetta. Succede, per esempio, con il `pandoc` di Anaconda | Usare la versione arm64, oppure installare Rosetta (`softwareupdate --install-rosetta`) |
| Installazione lenta o fallita di `torch` | Python tradotto da Rosetta invece che nativo | Reinstallare Python arm64 e ricreare `env` |
| `model not found` da Ollama | Modello non scaricato | `ollama list`, poi `ollama pull` |
| Errori di connessione verso `127.0.0.1` | Ollama non avviato o sovraccarico | `ollama serve`; il codice già serializza e ritenta |
| Errore 401/403 da Hugging Face | Token mancante o modello con accesso riservato | `HF_READ_TOKEN` in `.env` |
| `FileNotFoundError` su `.npy` | Una fase precedente non è terminata | Rieseguire `main.py` e leggere l'errore della fase |
| `ModuleNotFoundError` | Ambiente attivo ma librerie non installate | `pip install -r requirements.txt` |

### 11.4 Tempi di esecuzione

Su un portatile Apple Silicon senza GPU dedicata, Heart Disease (920 frasi per 7 modelli) richiede alcuni minuti; il bootstrap a 10.000 iterazioni per 7 modelli è la parte più lenta dopo gli embedding. Diabetes130 genera 20.000 frasi per 7 modelli e richiede un tempo molto maggiore, dominato dagli encoder large via Ollama.

# Capitolo 48 — Da "nessun test automatico" alla prima suite pytest

**Obiettivi del capitolo**
- Sapere con precisione cosa significava, e cosa non significava, l'assenza di test automatici che questo progetto ha avuto per quasi tutta la sua storia.
- Vedere come la suite pytest introdotta con i fix di revisione copre esattamente le priorità che questa analisi aveva indicato.
- Confrontare pytest, lo strumento usato, con JUnit, quello che già conosci.

## 48.1 Cosa significava, onestamente, per l'affidabilità del progetto

**[Fatto]** Al momento della ricognizione iniziale di questo libro, nessuno dei file del progetto aveva un corrispettivo `test_*.py`; non esisteva una cartella `tests/`; `pytest` e `unittest` non comparivano in `requirements.txt` né in alcun import (verificato con `find`/`grep`, capitolo 0). **[Interpretazione]** Questo non significava che il codice fosse necessariamente pieno di bug — molte delle criticità di questo libro (soglia ottimizzata sullo stesso fold, test set mai usato, imputazione su maggioranza mancante) erano limiti *metodologici*, che un test unitario non avrebbe intercettato comunque, perché il codice faceva esattamente quello che doveva fare a livello di implementazione: il problema era nella scelta, non nell'esecuzione. Ma significava che ogni modifica al codice — un refactoring, un aggiornamento di libreria, l'aggiunta di un ottavo modello (capitolo 42) — non aveva alcuna rete di sicurezza automatica che confermasse che il comportamento osservabile non fosse cambiato per errore.

**[Fatto]** La situazione è cambiata proprio quando quella rete è servita: i fix di revisione (`docs/CHANGES.md`) hanno introdotto, insieme alle correzioni al codice, una cartella `tests/` con tre file (`test_function.py`, `test_preprocessing.py`, `test_embedding.py`, 20 funzioni di test per 22 test eseguiti, una è parametrizzata), `pytest` in `requirements.txt`, e un `pytest.ini` con `pythonpath = .` che risolve gli import "piatti" del progetto (nessun package, capitolo 10.1) allo stesso modo di `main.py`. La suite copre la logica pura toccata dai fix: le funzioni `record_to_text_*` con il mascheramento `_masked()`, le funzioni di imputazione fit/apply (incluso il test che i valori non vengano mai ricalcolati sul test split), gli indicatori di mancanza, `optimal_f1_threshold()`, la correzione Benjamini-Hochberg, e il vincolo che `results` abbia esattamente una voce per modello configurato. Si esegue con `python -m pytest -v`, senza rete né Ollama.

> **SE VIENI DA JAVA —** in un progetto Java enterprise, l'assenza totale di test sarebbe insolita quanto lo è qui, ma per motivi diversi da apprezzare: qui non c'è un framework (Spring, Hibernate) che incoraggi test di integrazione quasi "gratuiti" con annotazioni dedicate, e il progetto è scritto per essere eseguito una volta dall'inizio alla fine da chi lo ha scritto, non mantenuto da un team nel tempo — un contesto in cui la pressione per scrivere test è storicamente più bassa, a torto o a ragione.

## 48.2 Cosa testare per primo — e cosa la suite reale ha effettivamente scelto

**[Interpretazione]** Non tutte le funzioni del progetto sono ugualmente facili o utili da testare. Le più adatte per un primo test sono le **funzioni pure** — che ricevono un input e restituiscono un output senza toccare disco, rete, o stato globale (capitolo 8.3): `record_to_text_heart_disease()` e `record_to_text_diabetes130()` (`embedding.py:58-100`), le funzioni `_fmt_*` e `_masked()` di supporto, e il calcolo della soglia F1-ottima (`function.py:177-191`). Le meno adatte, almeno per cominciare, sono quelle che chiamano Ollama o Hugging Face (`embedding.py`) o che leggono/scrivono file (quasi ogni altra funzione, capitolo 17.1): richiedono tecniche di isolamento (mocking, capitolo 49.3) più impegnative da scrivere per prime.

**[Fatto]** La suite reale conferma questa analisi punto per punto: i 22 test coprono esclusivamente logica pura — nessun test tocca rete o modelli — e il primo file della suite è proprio `test_embedding.py` sulle funzioni di conversione a testo: `record_to_text_heart_disease()` è una funzione pura, il suo output è facile da verificare (una stringa), e un errore lì si propagherebbe silenziosamente fino al report finale senza che nessun'altra parte del sistema lo segnali — esattamente il tipo di funzione dove un test automatico dà il massimo valore per il minimo sforzo.

## 48.3 pytest confrontato con JUnit

**[Livello: teoria consolidata del settore]** `pytest` gioca, nell'ecosistema Python, un ruolo concettualmente equivalente a JUnit: un framework di test con scoperta automatica dei test (file `test_*.py`, funzioni `test_*`), asserzioni, fixture per la configurazione condivisa, e un runner da riga di comando. Le differenze principali che noteresti subito: **[Livello: teoria consolidata del settore]** pytest non richiede una classe che estenda una classe base (`TestCase` in `unittest`, l'equivalente più diretto di JUnit) — una funzione `def test_qualcosa():` con dentro un'asserzione `assert` ordinaria è già un test valido, riconosciuto automaticamente dal runner. Le *fixture* di pytest (funzioni decorate con `@pytest.fixture`, capitolo 11.3 sui decoratori) sostituiscono sia `@Before`/`@After` di JUnit sia, in parte, l'iniezione di dipendenze — una fixture può essere richiesta da un test semplicemente nominandola come parametro della funzione di test, senza bisogno di un contenitore di inversione del controllo.

## Riepilogo

Per quasi tutta la sua storia questo progetto non ha avuto alcun test automatico — un fatto verificato sistematicamente, non un sospetto — con le conseguenze che l'assenza di una rete di sicurezza comporta per ogni modifica. I fix di revisione hanno introdotto una prima suite pytest di 22 test (con `pytest.ini` per gli import piatti del progetto), concentrata esattamente dove questa analisi indicava il massimo valore: le funzioni pure di conversione a testo, l'imputazione fit/apply, la soglia condivisa e la correzione Benjamini-Hochberg. pytest è concettualmente vicino a JUnit, ma senza il bisogno di ereditare da una classe base.

## Domande di autoverifica

**1. L'assenza storica di test automatici implicava che tutte le criticità di questo libro fossero bug di implementazione?**
No: la maggior parte (soglia ottimizzata sullo stesso fold, test set mai usato, imputazione su maggioranza mancante) erano scelte metodologiche che un test unitario non avrebbe intercettato comunque, perché il codice implementava correttamente ciò che faceva — il problema era nella scelta, non nell'esecuzione. Coerentemente, la suite introdotta con i fix testa la logica *nuova o corretta*, non "cerca bug" nel vecchio comportamento.

**2. Perché `record_to_text_heart_disease()` era il candidato migliore per un primo test rispetto a una funzione di `embedding.py` che chiama Ollama — e cosa fa oggi la suite reale?**
Perché è una funzione pura: riceve un input, restituisce un output, senza toccare rete o disco. Testarla non richiede tecniche di isolamento (mocking). La suite reale (`tests/test_embedding.py`) la testa infatti per prima cosa: traduzione dei codici, gestione dei valori mancanti, e mascheramento dei valori imputati via `_masked()`.

**3. In cosa una fixture di pytest si avvicina, concettualmente, sia a `@Before` di JUnit sia all'iniezione di dipendenze?**
Prepara uno stato condiviso prima dell'esecuzione di un test (come `@Before`), ma un test la richiede semplicemente nominandola come proprio parametro, un meccanismo più vicino, nello spirito, all'iniezione automatica di una dipendenza che a una chiamata esplicita di setup.

> **MATERIALE PER LA TESI**
> 1. La distinzione fra criticità metodologiche e bug di implementazione, applicata esplicitamente alla storia dei test di questo progetto — riusabile nella sezione "Discussione" per calibrare correttamente la portata di questo limite.
> 2. La corrispondenza fra le priorità di test individuate dall'analisi e la suite reale poi introdotta (22 test su logica pura, `pytest.ini` per gli import piatti) — riusabile come contributo concreto discusso in tesi, con la sequenza analisi → implementazione documentata.
> 3. Il confronto pytest/JUnit — riusabile come nota tecnica per un lettore Java che debba orientarsi rapidamente nell'ecosistema di test Python.

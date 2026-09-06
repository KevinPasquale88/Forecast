# Capitolo 48 — Lo stato attuale: nessun test automatico

**Obiettivi del capitolo**
- Sapere con precisione cosa significa, e cosa non significa, l'assenza di test automatici in questo progetto.
- Avere una priorità chiara su cosa testare per primo, se dovessi cominciare oggi.
- Confrontare pytest, lo strumento che useresti, con JUnit, quello che già conosci.

## 48.1 Cosa significa, onestamente, per l'affidabilità del progetto

**[Fatto]** Nessuno dei nove file del progetto ha un corrispettivo `test_*.py`; non esiste una cartella `tests/`; `pytest` e `unittest` non compaiono in `requirements.txt` né in alcun import (verificato con `find`/`grep` in fase di ricognizione, capitolo 0). **[Interpretazione]** Questo non significa che il codice sia necessariamente pieno di bug — molte delle criticità di questo libro (soglia ottimizzata sullo stesso fold, test set mai usato, imputazione su maggioranza mancante) sono limiti *metodologici*, che un test unitario non avrebbe intercettato comunque, perché il codice fa esattamente quello che dovrebbe fare a livello di implementazione: il problema è nella scelta, non nell'esecuzione. Ma significa che ogni modifica futura al codice — un refactoring, un aggiornamento di libreria, l'aggiunta di un ottavo modello (capitolo 42) — non ha alcuna rete di sicurezza automatica che confermi che il comportamento osservabile non sia cambiato per errore.

> **SE VIENI DA JAVA —** in un progetto Java enterprise, l'assenza totale di test sarebbe insolita quanto lo è qui, ma per motivi diversi da apprezzare: qui non c'è un framework (Spring, Hibernate) che incoraggi test di integrazione quasi "gratuiti" con annotazioni dedicate, e il progetto è scritto per essere eseguito una volta dall'inizio alla fine da chi lo ha scritto, non mantenuto da un team nel tempo — un contesto in cui la pressione per scrivere test è storicamente più bassa, a torto o a ragione.

## 48.2 Cosa testeresti per primo, e perché

**[Interpretazione]** Non tutte le funzioni del progetto sono ugualmente facili o utili da testare. Le più adatte per un primo test sono le **funzioni pure** — che ricevono un input e restituiscono un output senza toccare disco, rete, o stato globale (capitolo 8.3): `record_to_text_heart_disease()` e `record_to_text_diabetes130()` (`embedding.py:43-85`), le funzioni `_fmt_*` di supporto, e il calcolo della soglia F1-ottima (`classification.py:30-35`, isolabile dal resto della funzione). Le meno adatte, almeno per cominciare, sono quelle che chiamano Ollama o Hugging Face (`embedding.py`) o che leggono/scrivono file (quasi ogni altra funzione, capitolo 17.1): richiedono tecniche di isolamento (mocking, capitolo 49.3) più impegnative da scrivere per prime.

**[Interpretazione]** Se dovessi scrivere un solo test per questo progetto, sarebbe su `record_to_text_heart_disease()`: è una funzione pura, il suo output è facile da verificare (una stringa), e un errore in questa funzione si propagherebbe silenziosamente fino al report finale senza che nessun'altra parte del sistema lo segnali — esattamente il tipo di funzione dove un test automatico dà il massimo valore per il minimo sforzo.

## 48.3 pytest confrontato con JUnit

**[Livello: teoria consolidata del settore]** `pytest` gioca, nell'ecosistema Python, un ruolo concettualmente equivalente a JUnit: un framework di test con scoperta automatica dei test (file `test_*.py`, funzioni `test_*`), asserzioni, fixture per la configurazione condivisa, e un runner da riga di comando. Le differenze principali che noteresti subito: **[Livello: teoria consolidata del settore]** pytest non richiede una classe che estenda una classe base (`TestCase` in `unittest`, l'equivalente più diretto di JUnit) — una funzione `def test_qualcosa():` con dentro un'asserzione `assert` ordinaria è già un test valido, riconosciuto automaticamente dal runner. Le *fixture* di pytest (funzioni decorate con `@pytest.fixture`, capitolo 11.3 sui decoratori) sostituiscono sia `@Before`/`@After` di JUnit sia, in parte, l'iniezione di dipendenze — una fixture può essere richiesta da un test semplicemente nominandola come parametro della funzione di test, senza bisogno di un contenitore di inversione del controllo.

## Riepilogo

Questo progetto non ha alcun test automatico, un fatto verificato sistematicamente, non un sospetto. Non implica necessariamente bug nascosti — molte criticità di questo libro sono metodologiche, non di implementazione — ma implica l'assenza di una rete di sicurezza per modifiche future. Le funzioni pure di conversione testo sono il punto di partenza più naturale per un primo test; pytest è lo strumento naturale, concettualmente vicino a JUnit ma senza il bisogno di ereditare da una classe base.

## Domande di autoverifica

**1. L'assenza di test automatici in questo progetto implica che tutte le criticità di questo libro siano bug di implementazione?**
No: la maggior parte (soglia ottimizzata sullo stesso fold, test set mai usato, imputazione su maggioranza mancante) sono scelte metodologiche che un test unitario non intercetterebbe comunque, perché il codice implementa correttamente ciò che fa — il problema è nella scelta, non nell'esecuzione.

**2. Perché `record_to_text_heart_disease()` è un candidato migliore per un primo test rispetto a una funzione di `embedding.py` che chiama Ollama?**
Perché è una funzione pura: riceve un input, restituisce un output, senza toccare rete o disco. Testarla non richiede tecniche di isolamento (mocking); testare una funzione che chiama Ollama richiederebbe simulare quella chiamata di rete.

**3. In cosa una fixture di pytest si avvicina, concettualmente, sia a `@Before` di JUnit sia all'iniezione di dipendenze?**
Prepara uno stato condiviso prima dell'esecuzione di un test (come `@Before`), ma un test la richiede semplicemente nominandola come proprio parametro, un meccanismo più vicino, nello spirito, all'iniezione automatica di una dipendenza che a una chiamata esplicita di setup.

> **MATERIALE PER LA TESI**
> 1. La distinzione fra criticità metodologiche e bug di implementazione, applicata esplicitamente all'assenza di test — riusabile nella sezione "Discussione" per calibrare correttamente la portata di questo limite.
> 2. La priorità motivata su quale funzione testare per prima — riusabile come base per la sezione "Lavori futuri" o per un contributo di test realmente scritto e discusso in tesi.
> 3. Il confronto pytest/JUnit — riusabile come nota tecnica per un lettore Java che debba orientarsi rapidamente nell'ecosistema di test Python.

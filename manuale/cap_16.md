# Capitolo 16 — Troubleshooting e verifica dell'ambiente

**Obiettivi del capitolo**

- Riconoscere gli errori più probabili durante l'installazione e la prima esecuzione, con la loro causa reale.
- Avere una checklist di verifica da eseguire prima di lanciare l'intera pipeline, non dopo che è già fallita.
- Sapere cosa NON esiste in Python rispetto a Java in tema di portabilità: niente bytecode distribuibile, niente `.jar`.

## 16.1 Gli errori più probabili e le loro cause reali

**[Fatto]** Questa tabella integra il troubleshooting di `README.md:206-213` con la causa specifica trovata leggendo il codice, non solo il sintomo.

| Sintomo | Causa reale | Dove verificarla |
|---|---|---|
| Installazione di `torch`/`numba` lenta o fallita | Python tradotto da Rosetta invece che nativo `arm64` su Apple Silicon | `python3 -c "import platform; print(platform.machine())"` deve dare `arm64`, non `x86_64` (capitolo 15.1) |
| `ollama pull` fallisce, o "model not found" durante la generazione degli embedding per e5-base | Il comando del README (`yxchia/multilingual-e5-base`) e il nome usato da `function.py:39` (`jeffh/intfloat-e5-base-v2:q8_0`) sono due modelli diversi — capitolo 15.2 lo tratta per esteso | `ollama list` deve mostrare esattamente `jeffh/intfloat-e5-base-v2:q8_0`, non l'altro nome |
| Errore di autenticazione o modello "gated" verso Hugging Face | `HF_READ_TOKEN` mancante o non valido in `.env` | `embedding.py:146-149` stampa esplicitamente se un token è stato rilevato o meno |
| `FileNotFoundError` su un file `.npy` in `embeddings/` o `results/` | Una fase precedente della pipeline non si è completata — le fasi dipendono rigidamente dall'output della fase precedente, senza controlli di integrità intermedi | Rilancia `python main.py`, osservando l'output console per capire quale fase si è interrotta (capitolo 18.3) |
| `ModuleNotFoundError` per un pacchetto elencato in `requirements.txt` | L'ambiente virtuale è stato attivato ma `pip install -r requirements.txt` non è mai stato eseguito, o è stato interrotto a metà | `pip list` dentro l'ambiente attivato, confrontato con `requirements.txt` |
| `source env/bin/activate` non funziona | L'ambiente virtuale è corrotto o incompleto | Elimina `env/` e ricrealo da zero (capitolo 15.2, passo 2) |

## 16.2 Verificare che l'installazione sia corretta prima di lanciare l'intera pipeline

Eseguire l'intera pipeline solo per scoprire, dopo dieci minuti, che manca un token Hugging Face è un modo costoso di scoprire un problema che una verifica di trenta secondi avrebbe individuato subito. Prima di eseguire `python main.py`, vale la pena controllare, in ordine:

1. **L'interprete giusto è attivo.** `which python3` punta dentro `env/`.
2. **Le dipendenze sono installate.** `pip show sentence-transformers torch scikit-learn` non restituisce errori per nessuno dei tre.
3. **Ollama è in esecuzione e ha i modelli giusti.** `ollama list` mostra i quattro nomi esatti di `function.py:39-42`, non quelli (in un caso, diversi) del README.
4. **Il token Hugging Face è configurato**, se è la prima esecuzione dopo l'installazione. `cat .env` (mai con `git` di mezzo — è un file locale, mai tracciato) mostra `HF_READ_TOKEN` valorizzato.

> **PROVA TU —** scrivi uno script di pochissime righe che automatizzi questi quattro controlli e stampi un semplice "OK" o "MANCA: ..." per ciascuno. Non è un esercizio di programmazione avanzata: è esattamente il tipo di controllo di sanità dell'ambiente (*smoke test*) che, in un contesto Java enterprise, faresti probabilmente girare come primo step di una pipeline CI — qui non esiste (capitolo 48 lo tratta nel dettaglio), ed è un'occasione concreta per aggiungerne uno tu.

## 16.3 Cosa NON esiste in Python: niente bytecode portabile tra versioni, nessun `.jar`

**[Livello: teoria consolidata del settore]** Un `.jar` Java, una volta compilato, gira su qualunque JVM (di versione compatibile) su qualunque sistema operativo — è precisamente la promessa "compila una volta, esegui ovunque" su cui è costruito l'intero ecosistema Java. Python non ha un equivalente pratico di questa promessa.

Python compila sì il proprio codice sorgente in bytecode — lo trovi nella cartella `__pycache__`, con file `.pyc` — ma quel bytecode non è pensato per essere distribuito: è specifico della versione esatta dell'interprete che lo ha generato (un `.pyc` compilato da Python 3.14 non è garantito funzionare, e spesso semplicemente non funziona, con Python 3.11), e in pratica quasi mai portato da una macchina a un'altra. Ciò che si distribuisce, normalmente, è il codice sorgente stesso (`.py`), insieme a un ambiente virtuale (capitolo 14) ricreato da zero sulla macchina di destinazione con la stessa versione di Python — non un artefatto compilato una volta e trasportato ovunque.

**[Fatto]** Questo progetto non fa eccezione: non esiste, in nessuna parte del repository, un tentativo di "compilare" o "impacchettare" il codice in una forma distribuibile autonoma (nessun `pyproject.toml`, nessun `setup.py`, verificato nella scheda tecnica). L'unico modo di eseguirlo su una macchina diversa è ripetere l'intera procedura di installazione di questo capitolo — non copiare un artefatto già pronto.

> **SE VIENI DA JAVA —** questa è una delle differenze pratiche più rilevanti quando pensi al deployment: un servizio Java packagizzato come `.jar` (o `.war`) è un artefatto singolo, versionabile e distribuibile; un progetto Python come questo richiede, su ogni macchina di destinazione, la ricostruzione completa dell'ambiente (capitolo 14) prima di poter eseguire una sola riga. Esistono strumenti che avvicinano Python a un modello di distribuzione più simile a quello Java — contenitori Docker con l'ambiente già pronto, per esempio — ma questo progetto non li usa: nessun `Dockerfile` nel repository, verificato.

## Riepilogo

Gli errori più probabili in questo progetto hanno cause specifiche, verificabili leggendo il codice: architettura Rosetta invece di `arm64`, un nome di modello Ollama sbagliato nel README per il solo e5-base, un token Hugging Face mancante, o una fase della pipeline interrotta a metà senza controlli di integrità. Una checklist di quattro verifiche rapide, eseguita prima del lancio completo, individua la maggior parte di questi problemi in pochi secondi. A differenza di un `.jar` Java, il codice Python di questo progetto non ha una forma distribuibile compilata: ogni macchina di destinazione ricostruisce l'ambiente da zero a partire dal codice sorgente e da `requirements.txt`.

## Domande di autoverifica

**1. Se `ollama pull yxchia/multilingual-e5-base` sembra completarsi senza errori, perché la pipeline potrebbe comunque fallire più avanti per il modello e5-base?**
Perché quel comando scarica un modello con un nome diverso da quello che `function.py:39` richiede davvero (`jeffh/intfloat-e5-base-v2:q8_0`). `ollama pull` va a buon fine, ma il modello scaricato non è quello che `embedding.py` chiederà al server Ollama in fase di generazione degli embedding.

**2. Perché copiare un file `.pyc` da `__pycache__` su un'altra macchina non è un modo affidabile di distribuire questo progetto?**
Perché il bytecode Python compilato è specifico della versione esatta dell'interprete che lo ha generato, e non è garantito funzionare con una versione diversa — a differenza di un `.jar`, pensato fin dall'origine per essere portabile fra JVM diverse.

**3. Quali quattro controlli faresti, in trenta secondi, prima di lanciare l'intera pipeline per la prima volta?**
Verificare che l'interprete attivo sia quello dentro `env/`, che le dipendenze chiave siano installate, che `ollama list` mostri i nomi esatti richiesti da `function.py` (non quelli, in un caso diversi, del README), e che `.env` contenga un token Hugging Face valorizzato.

> **MATERIALE PER LA TESI**
> 1. La tabella degli errori più probabili con causa reale (§16.1) — riusabile in un'appendice della tesi dedicata alla riproducibilità dell'ambiente sperimentale.
> 2. La checklist di verifica in quattro punti (§16.2) — riusabile come base per uno script di smoke test da citare in "Materiali e metodi", anche solo come proposta metodologica.
> 3. Il confronto esplicito fra il modello di distribuzione a bytecode di Java e l'assenza di un equivalente in questo progetto Python — riusabile per motivare, nella sezione "Lavori futuri", una proposta di containerizzazione (capitolo 55).

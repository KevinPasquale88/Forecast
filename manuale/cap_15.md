# Capitolo 15 — Installazione passo passo su macOS

**Obiettivi del capitolo**

- Avere tutti i prerequisiti installati e verificati prima di eseguire una sola riga del progetto.
- Seguire la procedura di installazione comando per comando, con una verifica dopo ogni passo.
- Eseguire per la prima volta la pipeline, sapendo cosa aspettarti.

Questo capitolo descrive l'installazione così come la documenta `README.md:90-120`, riorganizzata con una verifica esplicita dopo ogni passo — utile perché, se qualcosa va storto, sai esattamente a quale passo è successo, invece di scoprirlo solo quando l'intera pipeline fallisce dieci minuti dopo.

## 15.1 Prerequisiti: Python 3.14, Ollama, token Hugging Face

**[Fatto]** Il progetto richiede tre cose, oltre a un Mac con macOS: **[Fatto]** Python 3.14 — `README.md:84` dichiara che è la versione con cui il progetto è stato sviluppato e testato, versioni precedenti della serie 3.x non sono verificate; **[Fatto]** Ollama — il server locale che serve i quattro modelli generalisti (E5, GTE), richiesto e in esecuzione, non solo installato (`README.md:86`); **[Fatto]** un token di lettura Hugging Face — necessario la prima volta che ciascuno dei tre modelli biomedici viene scaricato, o se un modello è soggetto a restrizioni di accesso (`README.md:87,109-114`).

**[Fatto]** `README.md:85` dichiara inoltre che il progetto è sviluppato e verificato su Apple Silicon (`arm64`); su Intel/Linux gli stessi passi dovrebbero funzionare ma non sono stati verificati dagli autori. **[Fatto]** In questo ambiente di scrittura, sia il Python di sistema sia quello dentro `env/` risultano `arm64` (comando `platform.machine()` eseguito in questa sessione su entrambi gli interpreti) — coerente con quanto dichiarato.

> **ATTENZIONE —** se `python3 -c "import platform; print(platform.machine())"` restituisse `x86_64` su un Mac con chip Apple Silicon, significherebbe che stai usando un'installazione di Python tradotta da Rosetta invece che nativa `arm64` — una causa comune, secondo `README.md:207`, di installazioni lente o fallite per `torch` e `numba`, entrambe dipendenze pesanti di questo progetto (capitolo 20.3, capitolo 22.3).

## 15.2 Procedura completa comando per comando

I passi seguenti corrispondono a `README.md:91-118`, con una verifica aggiunta dopo ciascuno.

**1. Clona il repository e spostati nella sua cartella.** Verifica: `ls main.py` deve mostrare il file senza errori.

**2. Crea e attiva l'ambiente virtuale** (capitolo 14.1):
```bash
python3 -m venv env
source env/bin/activate
```
Verifica: dopo l'attivazione, `which python3` deve puntare dentro `env/bin/python3`, non a un Python di sistema — il prompt della shell, di norma, mostra anche un prefisso `(env)` a conferma.

**3. Installa le dipendenze:**
```bash
pip install -r requirements.txt
```
Verifica: `pip list` deve mostrare, fra le altre, `pandas`, `scikit-learn`, `torch`, `sentence-transformers` con le versioni esatte di `requirements.txt`. Questo passo è quello che richiede più tempo e più spazio su disco — capitolo 14.2 ha già mostrato che l'ambiente completo occupa circa 1.4 GB.

**4. Installa e avvia Ollama, poi scarica i quattro modelli generalisti** (`function.py:38-43`, capitolo 20.1):
```bash
ollama serve &
ollama pull yxchia/multilingual-e5-base
ollama pull twwch/m3e-base
ollama pull zyw0605688/gte-large-zh
ollama pull jeffh/intfloat-multilingual-e5-large-instruct:q8_0
```
Verifica: `ollama list` deve elencare i quattro modelli — ma qui c'è un problema reale, non ipotetico. **[Fatto]** Il primo comando `pull` di `README.md:104` scarica `yxchia/multilingual-e5-base`. **[Fatto]** La configurazione del modello e5-base in `function.py:39` usa però il nome `jeffh/intfloat-e5-base-v2:q8_0` — un identificativo diverso sul registro dei modelli di Ollama, non un alias dello stesso modello. **[Fatto]** In questo ambiente di scrittura, `ollama list` (comando eseguito in questa sessione) mostra effettivamente `jeffh/intfloat-e5-base-v2:q8_0` installato — non `yxchia/multilingual-e5-base` — cioè il modello giusto per far funzionare `function.py`, diverso da quello che il README istruisce a scaricare. **Conseguenza pratica per chi segue il README alla lettera:** eseguendo solo i quattro comandi di `README.md:103-107`, la pipeline fallirebbe alla fase di embedding per il modello e5-base con un errore "model not found", perché il modello scaricato non è quello richiesto da `embedding.py` quando chiama `client.embed(model=name, ...)` con `name` preso da `function.py:39`. Gli altri tre comandi `pull` (gte-base, gte-large, e5-large) corrispondono invece esattamente ai nomi usati in `function.py:40-42` — la discrepanza riguarda solo il primo modello. **[Da verificare]** Se sia un refuso di battitura nel README (un nome di modello simile ma sbagliato) o il residuo di una versione precedente del progetto che usava davvero `yxchia/multilingual-e5-base`, resta una domanda per chi ha scritto il codice (Appendice E).

**5. Crea un file `.env` nella radice del progetto:**
```
HF_READ_TOKEN=il_tuo_token_qui
OFFLINE_MODE=0
```
Verifica: nessun comando di verifica diretto — il primo test reale è il passo successivo, quando `embedding.py` prova a scaricare i modelli biomedici. **[Fatto]** `.env` è escluso da `.gitignore:2` e non deve mai essere committato: contiene una credenziale personale, non un valore di configurazione condivisibile.

**6. Esegui la pipeline:**
```bash
python main.py
```
Verifica: vedi il paragrafo successivo.

> **ATTENZIONE —** `python main.py` senza argomenti esegue **solo** il dataset Heart Disease (`main.py:15`, default `heart_disease`). Per eseguire anche Diabetes130 serve `python main.py --dataset diabetes130`, come comando separato — non è un'opzione che esegue entrambi i dataset in sequenza.

## 15.3 Prima esecuzione: `python main.py --dataset heart_disease`

Alla prima esecuzione, aspettati un tempo compreso fra alcuni minuti e qualche decina di minuti (`README.md:88`), dominato da due fasi: la generazione degli embedding (capitolo 22, chiamate di rete verso Ollama e calcolo verso i modelli Hugging Face) e il bootstrap a 10.000 iterazioni per ciascuno dei sette modelli (capitolo 36). Vedrai una sequenza di messaggi di stampa — non un'interfaccia grafica, non una barra di progresso unica per l'intera pipeline, ma i `print()` sparsi in ciascun modulo (capitolo 20-28 li commenta uno per uno).

Al termine, la cartella `datas/heart_disease/` conterrà cinque sottocartelle popolate: `preprocessing/`, `embeddings/`, `results/`, `graphics/`, `reports/` — l'ultima con il file `report.md` finale (capitolo 27). Se una qualunque fase fallisce a metà, la cartella resta parzialmente popolata: il capitolo 16 tratta questo scenario nel dettaglio.

> **PROVA TU —** dopo la prima esecuzione completa, apri `datas/heart_disease/reports/report.md` in un visualizzatore Markdown qualunque. Prima ancora di leggere la Parte IX di questo libro (che lo analizza nel dettaglio), prova a individuare da solo quale dei sette modelli ha l'AUC più alta — è la prima delle domande che il capitolo 44 tratta con tutto il rigore statistico necessario.

## Riepilogo

L'installazione richiede tre prerequisiti (Python 3.14 nativo `arm64`, Ollama in esecuzione con quattro modelli scaricati, un token Hugging Face), sei passi comando-per-comando ciascuno con una propria verifica, e produce, alla prima esecuzione completa, un intero albero di output sotto `datas/heart_disease/`. `python main.py` senza argomenti esegue solo Heart Disease: Diabetes130 richiede un comando esplicito separato.

## Domande di autoverifica

**1. Come verifichi, con un solo comando, che l'ambiente virtuale sia stato attivato correttamente prima di installare le dipendenze?**
`which python3` (o l'equivalente `where` su altre shell): deve puntare a un eseguibile dentro la cartella `env/`, non al Python di sistema.

**2. Cosa succede se esegui `python main.py` senza alcun argomento, e cosa NON succede?**
Viene eseguita solo la pipeline per il dataset Heart Disease, il default di `main.py:15`. Non viene eseguito anche Diabetes130: serve un comando separato con `--dataset diabetes130` esplicito.

**3. Perché il file `.env` non va mai committato nel repository, a differenza di `requirements.txt`?**
Perché contiene una credenziale personale (`HF_READ_TOKEN`), non una configurazione condivisibile fra chiunque cloni il progetto — è per questo escluso esplicitamente in `.gitignore:2`.

> **MATERIALE PER LA TESI**
> 1. La procedura di installazione comando-per-comando con verifica esplicita ad ogni passo — riusabile in un'appendice della tesi dedicata alla riproducibilità, o in "Materiali e metodi" per descrivere l'ambiente sperimentale.
> 2. La discrepanza individuata fra il nome del modello e5-base nel README e quello effettivamente usato in `function.py` — riusabile come voce dell'appendice "zone d'ombra", con l'evidenza precisa di entrambi gli identificativi.
> 3. L'osservazione sul comportamento di default di `main.py` (solo Heart Disease) — riusabile per giustificare, nella sezione "Materiali e metodi", perché i risultati su Diabetes130 richiedano un'esecuzione esplicitamente separata e documentata come tale.

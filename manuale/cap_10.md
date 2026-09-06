# Capitolo 10 — Moduli, package e l'assenza di incapsulamento reale

**Obiettivi del capitolo**

- Capire perché un file `.py` da solo è già un modulo importabile, senza nulla di equivalente a una dichiarazione di package.
- Riconoscere come funziona `import` in questo progetto, e da cosa dipende perché funzioni.
- Sapere cosa significa davvero, in Python, un nome di funzione o variabile che comincia con `_`.

## 10.1 Un file `.py` è un modulo: cosa importa rispetto a un file `.java`

In Java, un file sorgente dichiara esplicitamente il proprio package nella prima riga, e quella dichiarazione deve corrispondere alla posizione del file nell'albero delle cartelle. In Python, un file `.py` è già, per il solo fatto di esistere, un **modulo** importabile con il proprio nome di file (senza estensione) — nessuna dichiarazione richiesta al suo interno.

**[Fatto]** Questo progetto non ha nessuna struttura a package: i nove file (`main.py`, `function.py`, `preprocessing.py`, `embedding.py`, `classification.py`, `evaluation.py`, `error_analysis.py`, `statisticaltest.py`, `generatereport.py`) vivono tutti nella cartella radice del repository, senza sottocartelle, e non esiste in nessun punto del progetto un file `__init__.py` (verificato cercandolo in tutto l'albero del repository). Un `__init__.py`, quando presente, è il segnale che una cartella deve essere trattata come un **package** — un contenitore organizzato di moduli, l'equivalente più vicino a un package Java con più classi. Qui non ce n'è motivo: un solo livello, nove file, tutti allo stesso livello.

## 10.2 `import` vs. `import` Java: risoluzione, side-effect al caricamento

**[Fatto]** `main.py:1-10` importa da sei moduli diversi del progetto:
```python
from evaluation import evaluate_results
from generatereport import generate_report
from preprocessing import preprocessing_data
from embedding import embeddings
from classification import training_classifier
from function import delete_files_embeddings, delete_files_graphics, delete_files_preprocessing, delete_files_results, get_output_dirs
```
Ogni `from <modulo> import <nome>` fa due cose insieme: prima trova ed esegue *l'intero file* `<modulo>.py` (una sola volta, anche se importato da più punti — Python tiene una cache dei moduli già caricati), poi rende disponibili nello spazio dei nomi corrente solo i nomi elencati dopo `import`. In Java, `import` è una pura dichiarazione: dice al compilatore dove trovare una classe usata più sotto, e non esegue nulla. In Python, importare un modulo *esegue* quel file da cima a fondo — comprese eventuali righe scritte a livello di modulo, non dentro nessuna funzione.

**[Fatto]** Questo ha una conseguenza concreta e verificabile in questo progetto: `function.py:154` contiene, a livello di modulo — non dentro una funzione — la chiamata `_configure_plot_style()`, che imposta lo stile globale di tutti i grafici di matplotlib/seaborn. Questa chiamata viene eseguita **nel momento in cui `function.py` viene importato per la prima volta** da qualunque altro file — `main.py`, `preprocessing.py`, o qualunque altro modulo del progetto — non quando qualcuno decide esplicitamente di "configurare lo stile". È un side-effect al caricamento, un concetto che in Java non ha un equivalente diretto: la cosa più vicina sarebbe un blocco di inizializzazione statico (`static { ... }`) in una classe, eseguito al primo caricamento della classe da parte della JVM — meno comune e più esplicito di quanto non sia, in pratica, una riga scritta a livello di modulo in Python.

**[Fatto]** Perché questi `import` funzionino, un'altra condizione deve valere, implicita e mai dichiarata da nessuna parte nel codice: `python main.py` deve essere eseguito **dalla cartella radice del repository**. Python cerca i moduli importati in un elenco di percorsi (`sys.path`), che include automaticamente la cartella in cui si trova lo script avviato per primo. Se eseguissi `python main.py` da una cartella diversa, o provassi a importare `preprocessing` da un progetto esterno, l'importazione fallirebbe con un `ModuleNotFoundError` — non perché il codice sia sbagliato, ma perché non esiste alcuna installazione del progetto come package (nessun `pyproject.toml`, nessun `setup.py`, verificato nella scheda tecnica del capitolo 14) che renda questi moduli risolvibili da un punto qualunque del filesystem.

> **SE VIENI DA JAVA —** il "classpath" qui è, in pratica, una singola cartella — quella corrente al momento dell'esecuzione — non un elenco esplicito di `.jar` o cartelle compilate assemblato da un build tool. Il capitolo 14 mostra la differenza in modo più sistematico, confrontando `pip`/`requirements.txt` con Maven/Gradle.

## 10.3 Niente `private` reale: la convenzione dell'underscore

Java ha modificatori di accesso applicati e verificati dal compilatore: `private`, `protected`, `public`. Python non ha nulla di equivalente applicato dal linguaggio — ogni nome, in un modulo Python, è raggiungibile dall'esterno se lo importi esplicitamente, indipendentemente da come è scritto. Esiste però una convenzione, rispettata (non imposta) da chi scrive codice Python: un nome che comincia con un underscore (`_nome`) segnala "pensato per uso interno a questo modulo, non parte dell'interfaccia pubblica" — un'indicazione per chi legge, non una barriera per l'interprete.

**[Fatto]** Il progetto la usa con coerenza. In `embedding.py`, le funzioni di formattazione usate internamente da `record_to_text_*()` sono tutte prefissate: `_fmt_num`, `_fmt_cat`, `_fmt_bool`, `_fmt_raw` (`embedding.py:28,33,38,61`) — nessuna di queste è pensata per essere chiamata da un altro modulo, e nessun altro file del progetto le importa infatti. Lo stesso vale per `_ollama_semaphore` (`embedding.py:101`, il semaforo che serializza le chiamate a Ollama, capitolo 12.2) e per `_configure_plot_style` (`function.py:134`, appena vista al paragrafo precedente). Nessuna di queste è protetta da un compilatore: se scrivessi, in un altro file, `from embedding import _fmt_num`, funzionerebbe — l'underscore non blocca nulla, avverte soltanto.

> **ATTENZIONE —** l'unico effetto realmente "applicato" dal linguaggio, non solo convenzionale, riguarda un'importazione con `from modulo import *` (mai usata in questo progetto, che importa sempre nomi espliciti): in quel caso specifico, i nomi con underscore iniziale vengono esclusi automaticamente. Ma un'importazione esplicita per nome, come fa sempre questo progetto, ignora completamente la convenzione: l'underscore resta un messaggio a chi legge, non un cancello.

## Riepilogo

Un file `.py` è già un modulo importabile, senza dichiarazioni di package; questo progetto non ha alcuna struttura a package (nessun `__init__.py`), solo nove file allo stesso livello. Importare un modulo in Python esegue l'intero file, incluse le righe a livello di modulo — un side-effect reale che questo progetto sfrutta per configurare lo stile dei grafici al primo import. L'assenza di `private` reale è colmata da una convenzione di nomenclatura (underscore iniziale), rispettata ovunque nel progetto ma non imposta dal linguaggio.

## Domande di autoverifica

**1. Perché l'assenza di `__init__.py` in questo progetto è coerente con la sua struttura, e non un'omissione?**
Perché tutti i moduli vivono a un solo livello, nella cartella radice: `__init__.py` serve a segnalare che una cartella è un package con struttura interna da organizzare, cosa che qui non serve, dato che non ci sono sottocartelle di codice.

**2. Cosa succede, esattamente, quando `main.py` importa `function`, e quando succede rispetto all'esecuzione di `main()`?**
L'intero file `function.py` viene eseguito da cima a fondo, incluse le righe a livello di modulo come `_configure_plot_style()` (`function.py:154`) — e questo avviene nel momento dell'importazione, prima ancora che `main()` venga chiamata.

**3. Se scrivessi `from embedding import _fmt_num` in un altro file, cosa succederebbe?**
Funzionerebbe: l'underscore iniziale è una convenzione per chi legge il codice, non una restrizione imposta dall'interprete su un'importazione esplicita per nome. Solo `from embedding import *` escluderebbe automaticamente i nomi con underscore iniziale — una forma di importazione che questo progetto non usa mai.

> **MATERIALE PER LA TESI**
> 1. L'osservazione verificata sull'assenza di `__init__.py` e di qualunque file di packaging (`pyproject.toml`, `setup.py`) — riusabile in "Materiali e metodi" per descrivere oggettivamente la struttura del progetto.
> 2. L'esempio del side-effect al caricamento (`_configure_plot_style()` eseguito all'import di `function.py`) — riusabile come illustrazione di una differenza semantica concreta fra `import` Python e Java.
> 3. La convenzione dell'underscore, con l'elenco reale dei nomi che la rispettano nel progetto — riusabile come nota di stile nella sezione che descrive la qualità e leggibilità del codice.

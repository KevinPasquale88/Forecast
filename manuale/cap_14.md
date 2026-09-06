# Capitolo 14 — L'interprete e gli ambienti virtuali

**Obiettivi del capitolo**

- Capire perché Python ha bisogno di un meccanismo di isolamento delle dipendenze concettualmente diverso dal classpath Java.
- Sapere cosa contiene davvero la cartella `env/` di questo progetto, e perché non è mai versionata.
- Confrontare `pip`/`requirements.txt` con Maven/Gradle su un punto preciso: cosa viene dichiarato e cosa viene risolto.

## 14.1 Perché Python ha bisogno di un "classpath" alternativo

In un progetto Java, le dipendenze dichiarate in `pom.xml` o `build.gradle` vengono scaricate in un repository locale condiviso (`~/.m2` o la cache di Gradle) — non una copia per progetto, ma una cache centrale a cui più progetti attingono. Il "classpath" di un'esecuzione specifica è assemblato al momento della build, combinando riferimenti a quella cache condivisa: due progetti che dipendono entrambi da Guava 32 useranno, sul disco, lo stesso file `.jar`.

Python non ha, di norma, un equivalente diretto di questo meccanismo. `pip install numpy` installa NumPy nella cartella `site-packages` dell'interprete Python attivo in quel momento — e se quell'interprete è quello di sistema, condiviso da tutti i progetti Python della macchina, installare una versione diversa di NumPy per un altro progetto sovrascriverebbe (o confliggerebbe con) quella già installata. Non esiste, nel meccanismo di base di `pip`, alcuna nozione di "questa versione di NumPy per questo progetto, quell'altra per quel progetto", a meno di isolare esplicitamente ogni progetto nel proprio interprete.

Questo è esattamente il ruolo di un **ambiente virtuale** (`venv`): una copia (o una struttura di symlink) dell'interprete Python, con una propria cartella `site-packages` indipendente da quella di sistema e da quella di ogni altro ambiente virtuale. Attivarlo (`source env/bin/activate`, capitolo 15.2) modifica temporaneamente quali eseguibili `python` e `pip` risponderanno ai comandi della tua shell, facendoli puntare a quelli dentro l'ambiente virtuale invece che a quelli di sistema.

> **SE VIENI DA JAVA —** la differenza concettuale più importante: Maven/Gradle isolano le dipendenze **per progetto, condividendo comunque i download** in una cache centrale; un ambiente virtuale Python isola le dipendenze **per progetto duplicandole fisicamente** in ogni singolo ambiente (salvo la cache di download di `pip`, che velocizza le reinstallazioni ma non elimina la duplicazione su disco di ogni `site-packages`). Dieci progetti Python con un proprio `venv` ciascuno, che dipendono tutti da NumPy, avranno dieci copie installate di NumPy sul disco — non una condivisa.

## 14.2 `env/` in questo progetto: cosa contiene, perché non è versionato

**[Fatto]** Il progetto usa un ambiente virtuale nella cartella `env/` alla radice del repository, creato con `python3 -m venv env` (`README.md:94`, capitolo 15.2 per il comando completo). **[Fatto]** In questo ambiente di scrittura, `env/` occupa 1.4 GB su disco (comando `du -sh env` eseguito in questa sessione) e contiene, fra le altre cose, `env/lib/python3.14/site-packages/` con tutte le dipendenze di `requirements.txt` già installate — compresi pacchetti pesanti come `torch` (il motore di calcolo dietro i modelli Hugging Face) e le sue stesse dipendenze transitive.

**[Fatto]** `env/` compare in `.gitignore:1` (`./env`) e non è mai stata committata nel repository — verificato con `git ls-files`, che non la elenca. **[Interpretazione]** Questo non è un dettaglio amministrativo: 1.4 GB di file binari specifici per una piattaforma (`arm64`/macOS, capitolo 15.1) e per una versione esatta di Python non hanno alcun valore versionato in git — chi clona il repository deve ricrearla da zero eseguendo `python3 -m venv env` seguito da `pip install -r requirements.txt`, esattamente come chi clona un progetto Java deve lasciare che Maven o Gradle ricreino il proprio `target/`, mai committato per lo stesso motivo (dimensione, dipendenza dalla piattaforma, rigenerabilità automatica dal file di build).

> **RIFERIMENTO AL CODICE —** l'interprete dentro `env/` è, in questo ambiente di scrittura, Python 3.14.0 per architettura `arm64` (comando `env/bin/python3 -c "import platform; print(platform.machine())"` eseguito in questa sessione, output `arm64`) — coerente con quanto dichiarato in `README.md:84-85`.

## 14.3 pip e `requirements.txt` confrontati con Maven/Gradle

**[Fatto]** `requirements.txt` (67 righe) elenca ogni dipendenza con una versione fissata esattamente (`pandas==3.0.2`, `numpy==2.4.4`, e così per tutte le altre) — nessun intervallo di versioni, nessuna gestione di conflitti dichiarativa come quella di un BOM Maven. **[Interpretazione]** La forma di questo file — piatta, con dipendenze dirette (`pandas`, `scikit-learn`, `ollama`, `sentence-transformers`) mescolate senza distinzione a dipendenze chiaramente transitive (`huggingface_hub`, `tokenizers`, `safetensors`, `sympy`, `mpmath`, `networkx`, `pydantic_core` — nessuna di queste è importata direttamente in nessuno dei nove file del progetto, verificato negli import elencati al capitolo 10.2) — è tipica di un file generato con `pip freeze`: uno snapshot di *tutto ciò che si trova installato* in un ambiente funzionante in un dato momento, non una dichiarazione a mano delle sole dipendenze dirette.

In Maven o Gradle, dichiari solo le dipendenze dirette nel file di build; lo strumento calcola da solo l'albero delle dipendenze transitive, e puoi ispezionarlo esplicitamente (`mvn dependency:tree`). `pip` con un `requirements.txt` di questo tipo non offre la stessa distinzione: leggendo il file da solo, non puoi sapere quali righe il progetto importa davvero e quali sono lì solo perché qualcos'altro ne ha bisogno — lo scopri solo incrociando il file con gli `import` effettivi nel codice, esattamente il lavoro fatto per la tabella qui sopra.

> **ATTENZIONE —** una conseguenza pratica di questo stile di file: aggiornare una sola dipendenza diretta (per esempio `scikit-learn`) a mano, modificando solo quella riga, non aggiorna né verifica la compatibilità delle dipendenze transitive collegate. Uno strumento come Maven ricalcolerebbe l'intero albero; qui, l'unico modo sicuro di aggiornare è rigenerare l'intero file con `pip freeze > requirements.txt` dentro un ambiente in cui l'aggiornamento è già stato fatto e verificato manualmente.

## Riepilogo

Un ambiente virtuale Python isola le dipendenze duplicandole fisicamente per progetto, a differenza della cache condivisa di Maven/Gradle. La cartella `env/` di questo progetto (1.4 GB, verificato) non è mai versionata, per lo stesso motivo per cui non versioneresti la cartella di build compilata di un progetto Java. Il file `requirements.txt`, con versioni fissate e dipendenze dirette e transitive mescolate senza distinzione, è tipico di uno snapshot `pip freeze`, non di una dichiarazione manuale come un `pom.xml`.

## Domande di autoverifica

**1. Perché dieci progetti Python con un proprio ambiente virtuale, tutti dipendenti da NumPy, occupano più spazio su disco di dieci progetti Maven che dipendono dalla stessa libreria?**
Perché ogni ambiente virtuale duplica fisicamente la propria copia di `site-packages`, mentre Maven/Gradle condividono un'unica cache centrale (`~/.m2` o equivalente) a cui più progetti attingono senza duplicare i file scaricati.

**2. Perché `env/` non viene mai versionata in questo progetto, e cosa fa le sue veci in un progetto Java equivalente?**
Perché contiene file binari specifici per piattaforma e versione (1.4 GB, verificato), interamente rigenerabili da `requirements.txt` con un comando. La cartella di build compilata di un progetto Java (`target/` in Maven, `build/` in Gradle) gioca lo stesso ruolo e per lo stesso motivo non viene versionata.

**3. Perché non puoi distinguere, leggendo solo `requirements.txt`, quali dipendenze il progetto importa davvero e quali sono solo transitive?**
Perché il file elenca in un'unica lista piatta sia le dipendenze dirette sia quelle transitive, senza segnalare la differenza — tipico di uno snapshot generato con `pip freeze`. La distinzione si ottiene solo incrociando il file con gli `import` effettivi nel codice sorgente.

> **MATERIALE PER LA TESI**
> 1. Il confronto esplicito fra il modello di cache condivisa di Maven/Gradle e il modello di duplicazione per ambiente virtuale di Python — riusabile in "Materiali e metodi" per descrivere l'infrastruttura di sviluppo del progetto.
> 2. Il dato verificato sulla dimensione di `env/` (1.4 GB) e sulla sua esclusione da git — riusabile come nota tecnica sulla riproducibilità dell'ambiente.
> 3. L'osservazione sulla natura "flat e mista" di `requirements.txt`, con l'elenco delle dipendenze transitive individuate — riusabile in una sezione che discuta la gestione delle dipendenze del progetto, anche in chiave critica.

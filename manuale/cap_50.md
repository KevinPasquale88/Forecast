# Capitolo 50 — Debugging e log in pratica

**Obiettivi del capitolo**
- Sapere come usare un debugger Python allo stesso modo in cui useresti quello di un IDE Java.
- Leggere i `print()` sparsi nel codice come se fossero un log strutturato, senza bisogno che lo siano davvero.
- Seguire un percorso di debugging guidato su un bug reale e già documentato di questo progetto.

## 50.1 Il debugger di un IDE Python confrontato con quello di un IDE Java

**[Livello: teoria consolidata del settore]** Un debugger Python (integrato in PyCharm, VS Code, o eseguibile da riga di comando con `pdb`, la libreria standard) offre le stesse funzionalità concettuali di un debugger Java: breakpoint, esecuzione passo-passo, ispezione delle variabili nello stack corrente, valutazione di espressioni al volo. La differenza pratica più rilevante, conseguenza diretta della tipizzazione dinamica (capitolo 7.2): quando ispezioni una variabile in un breakpoint Python, l'IDE ti mostra il suo tipo *attuale*, scoperto a runtime — non un tipo dichiarato che potresti già conoscere dalla firma della funzione. Fermarti dentro `training_classifier()` (`classification.py`, capitolo 23) e ispezionare `X` ti dice, lì per lì, che è un `numpy.ndarray` di una certa forma: un'informazione che, in Java, sapresti già dalla dichiarazione del parametro.

> **SE VIENI DA JAVA —** un breakpoint condizionale (che si attiva solo se un'espressione è vera) funziona in modo identico nei due mondi. Vale la pena ricordare, per un debugging efficace su questo progetto specifico, che molte funzioni ricevono solo un nome di dataset (capitolo 17.1) e ricostruiscono tutto il resto rileggendo file da disco: un breakpoint dentro `training_classifier()` non ti mostrerà i dati "in arrivo da preprocessing.py" — te li mostrerà già caricati da `np.load()`, un passaggio intermedio che un debugger su una pipeline con passaggio diretto di oggetti non avrebbe.

## 50.2 Leggere i `print()` del progetto come se fossero log strutturati

**[Fatto]** Nessun file del progetto usa il modulo `logging` della libreria standard — ogni traccia di esecuzione passa da semplici chiamate a `print()`, verificabile scorrendo qualunque dei nove file. **[Interpretazione]** Questo non è necessariamente un problema per un progetto eseguito interattivamente da riga di comando, come questo, ma significa che non esistono livelli di severità (`DEBUG`, `INFO`, `WARNING`, `ERROR`), non c'è modo di silenziare selettivamente l'output, e ogni messaggio va allo stesso stream (l'output standard), mescolato indistintamente.

**[Fatto]** Puoi comunque leggere questi messaggi con un metodo, riconoscendo pattern ricorrenti: `embedding.py` prefissa i propri messaggi con `[Batch]` o `[HF]` a seconda della fase (righe 107,128,140), un'abitudine che imita — senza usarlo davvero — il formato di un log strutturato con un "tag" di provenienza. `statisticaltest.py:92` stampa `[WARNING]` per un caso anomalo specifico (etichette vere diverse fra due modelli, capitolo 26.2) — l'unico punto del progetto che imita esplicitamente un livello di severità. **[Interpretazione]** Se dovessi seguire un'esecuzione reale della pipeline, cerca questi prefissi per orientarti rapidamente su quale fase e quale modello sta producendo un dato messaggio, invece di leggere l'output riga per riga.

## 50.3 Isolare un bug reale: percorso guidato su un modulo del progetto

**[Fatto]** Usiamo un bug reale già documentato in questo libro (capitolo 15.2, capitolo 16.1): seguendo il README alla lettera, `ollama pull yxchia/multilingual-e5-base` scarica un modello diverso da quello che `function.py:39` richiede (`jeffh/intfloat-e5-base-v2:q8_0`). Ecco il percorso di debugging che porteresti avanti, passo per passo, se non conoscessi già la causa:

1. **Il sintomo**: `python main.py` fallisce durante la fase di embedding (capitolo 22), con un `RuntimeError` che menziona "model not found" o simile, per il modello `e5-base`.
2. **Primo breakpoint**: dentro `process_model()` (`embedding.py:182-199`), sulla riga che chiama `generate_embeddings_batch(name, texts)` — ispeziona il valore di `name`. Se è `"jeffh/intfloat-e5-base-v2:q8_0"`, il problema non è nel codice Python: è che Ollama non ha quel modello scaricato.
3. **Verifica esterna al debugger**: da terminale, `ollama list` — se `jeffh/intfloat-e5-base-v2:q8_0` non compare nell'elenco, hai isolato la causa: il modello giusto non è mai stato scaricato.
4. **Root cause**: confrontando il comando di installazione seguito (`README.md:104`) con il valore appena ispezionato nel debugger, la discrepanza emerge — due nomi diversi per quello che dovrebbe essere lo stesso modello.

> **PROVA TU —** questo percorso ha funzionato perché conoscevi già la causa dalla lettura di questo libro. Scegli ora un altro punto del codice che non hai ancora esplorato interattivamente — per esempio `build_encoder()` in `preprocessing.py` — metti un breakpoint alla prima riga, ed esplora cosa contengono davvero `X`, `num_cols`, `cat_cols` in quel momento specifico dell'esecuzione, senza fidarti solo di quello che il libro ti ha già detto: è il modo più efficace di consolidare la lettura di un capitolo di questo libro, non un'alternativa ad essa.

## Riepilogo

Un debugger Python offre le stesse funzionalità concettuali di uno Java, con la differenza pratica che ogni tipo ispezionato è scoperto a runtime, non dichiarato in anticipo. Il progetto non usa `logging`, solo `print()` con prefissi informali ricorrenti (`[Batch]`, `[HF]`, `[WARNING]`) che aiutano a orientarsi. Il percorso di debugging del "model not found" per e5-base — dal sintomo, a un breakpoint mirato, a una verifica esterna al debugger, alla causa radice — è un esempio concreto e già verificato di come isolare un bug reale di questo progetto.

## Domande di autoverifica

**1. Perché ispezionare `X` in un breakpoint dentro `training_classifier()` non ti dice nulla che non potresti già sapere dalla firma della funzione, in Java?**
È l'opposto: in Python, la firma (`def training_classifier(dataset="heart_disease"):`) non dichiara affatto il tipo delle variabili locali come `X`; solo il breakpoint, a runtime, rivela che è un `numpy.ndarray` di una certa forma — un'informazione che una firma Java tipizzata staticamente comunicherebbe già in anticipo.

**2. A cosa serve il prefisso `[WARNING]` stampato da `statisticaltest.py:92`, dato che il progetto non usa il modulo `logging`?**
Imita, senza usarlo davvero, un livello di severità di un log strutturato: segnala visivamente, a chi legge l'output della console, che quel messaggio specifico riguarda un caso anomalo (etichette vere diverse fra due modelli), distinguendolo dagli altri messaggi informativi stampati con `print()` ordinario.

**3. Nel percorso di debugging del capitolo, qual è il passaggio che richiede uscire dal debugger e usare il terminale?**
La verifica con `ollama list`: il debugger può mostrarti quale nome di modello il codice sta effettivamente richiedendo, ma solo un comando esterno al processo Python può confermare se quel modello è davvero disponibile sul server Ollama in esecuzione.

> **MATERIALE PER LA TESI**
> 1. Il confronto fra debugger Python e Java, con l'osservazione sulla scoperta dei tipi a runtime — riusabile come nota tecnica per un lettore che debba impostare per la prima volta un ambiente di sviluppo Python.
> 2. Il percorso di debugging completo sul bug reale del modello e5-base — riusabile come caso di studio in una sezione della tesi su debugging e qualità del software, con tanto di causa radice già identificata e documentata.
> 3. L'osservazione sull'assenza del modulo `logging` e sul suo effetto pratico sull'osservabilità del sistema — riusabile come punto di discussione nella sezione critica sulla qualità del codice.

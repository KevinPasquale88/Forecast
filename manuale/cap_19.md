# Capitolo 19 — Stato, configurazione, punti di estensione

**Obiettivi del capitolo**

- Sapere che `function.py` è, di fatto, l'unico file di configurazione del progetto, e cosa questo comporta.
- Rivedere lo stato globale mutabile con lo sguardo architetturale, non solo linguistico, di questo capitolo.
- Sapere esattamente dove intervenire — e dove stare attenti — per aggiungere un ottavo modello di embedding.

## 19.1 Dove vive la configurazione: `function.py` come "file unico di config"

**[Fatto]** Non esiste, in questo progetto, un file di configurazione nel senso in cui probabilmente lo intendi arrivando da Java — nessun `.properties`, nessun `.yaml`, nessuna classe annotata `@ConfigurationProperties`. Ogni parametro che potresti aspettarti di trovare esternalizzato è invece scritto direttamente dentro `function.py`, come valore letterale nel codice: l'elenco dei sette modelli con i loro identificativi (`function.py:38-49`), la dimensione del campione per Diabetes130 (`function.py:116`, `sample_size=20000`), la palette di colori (`function.py:57-61`), le dimensioni standard delle figure (`function.py:64-65`).

**[Interpretazione]** Questo significa che "configurare" il progetto in modo diverso — per esempio cambiare quanti record campionare da Diabetes130 — richiede modificare il codice sorgente, non un file di configurazione esterno da passare come parametro. Non è necessariamente un problema per un progetto di ricerca a questa scala, dove chi esegue la pipeline e chi ne legge il codice sono, con ogni probabilità, la stessa persona — ma è un punto di attenzione se il progetto dovesse mai essere eseguito da chi non ha accesso o familiarità col codice sorgente.

## 19.2 Stato globale mutabile: dove, perché, rischi

Il capitolo 8.3 ha già mostrato il meccanismo linguistico del dizionario `results` (`function.py:72`, oggi generato per comprehension da `models_all` così che non possa più divergere dall'elenco dei modelli configurati, e mutato da `classification.py:58`). A livello architetturale, la domanda interessante è un'altra: **perché lo stato globale mutabile è un problema per l'estensibilità, non solo per la correttezza immediata?**

**[Interpretazione]** Uno stato condiviso a livello di modulo rende più difficile ragionare su una funzione guardandola in isolamento: `training_classifier()` (`classification.py:9-87`) non restituisce esplicitamente il proprio risultato principale come valore di ritorno — lo scrive in un dizionario globale importato da un altro modulo, un side-effect che non è visibile guardando solo la firma della funzione (`def training_classifier(dataset="heart_disease"):`, nessun tipo di ritorno dichiarato, capitolo 7.2). Chiunque volesse scrivere un test automatico per questa funzione (Parte X) dovrebbe sapere, in anticipo, di dover controllare `function.results` dopo la chiamata — un'informazione che nessuna firma comunica.

> **ATTENZIONE —** questo è precisamente il tipo di accoppiamento implicito che un'architettura a livelli in Java tende a evitare per costruzione: un metodo di un servizio Java che scrivesse silenziosamente in un campo statico di un'altra classe, invece di restituire un valore, verrebbe quasi certamente segnalato in un code review. Qui il linguaggio lo permette senza frizione (capitolo 8.3), e il progetto lo usa: un'osservazione critica legittima per la Parte XI, non solo una curiosità sintattica.

## 19.3 Dove aggiungeresti un ottavo modello di embedding, se dovessi farlo tu

**[Fatto]** Aggiungere un ottavo modello di embedding richiede, in linea di principio, una sola modifica: aggiungere un dizionario con la stessa struttura degli altri a `models_ollama` o a `models_medical` (`function.py:38-49`), con i campi `type`, `model_name`, `name`, `filename`, `filename_label`, `family`. Ogni altra parte della pipeline — generazione degli embedding (`embedding.py`), addestramento (`classification.py`), valutazione (`evaluation.py`), analisi degli errori (`error_analysis.py`), test statistici (`statisticaltest.py`) — itera su `models_all` (`function.py:51`, l'unione di `models_ollama` e `models_medical`) senza mai nominare esplicitamente uno dei sette modelli attuali: il codice è già scritto per generalizzare a un numero qualunque di modelli.

**[Fatto]** Con una precisazione importante, se il nuovo modello appartiene a una **famiglia già esistente** (per esempio un altro modello `"biomedical"`), tutto funziona automaticamente: `get_model_palette()` (`function.py:162-174`) genera una nuova sfumatura di colore per ogni membro della famiglia, quale che sia il loro numero.

**[Fatto]** Se invece il nuovo modello introducesse una **quarta famiglia**, mai vista finora, un punto del codice richiederebbe comunque una modifica manuale per un risultato pienamente leggibile: `FAMILY_COLORS` (`function.py:57-61`) non avrebbe una voce per quella famiglia, e sia `get_model_palette()` sia `plot_family_comparison()` userebbero il colore di ripiego `"#888888"` (grigio, `function.py:170` e `function.py:379`) invece di un colore dedicato — nessun errore, solo un grafico meno leggibile. **[Fatto]** In una versione precedente del codice il rischio era più serio: `plot_family_comparison()` costruiva l'ordine delle famiglie con una lista scritta a mano (`["general-purpose", "biomedical", "biomedical-st"]`), e una quarta famiglia non elencata veniva **esclusa in silenzio** dal grafico di confronto per famiglia — generato comunque, semplicemente senza quella famiglia, senza alcun avviso in console. Oggi `family_order` è costruito da `FAMILY_COLORS` più le famiglie effettivamente presenti nei dati (`function.py:377-378`), quindi una famiglia nuova compare comunque, anche se in grigio, invece di sparire.

> **PROVA TU —** apri `function.py` e prova, sulla carta o in un ambiente di test separato, ad aggiungere un ottavo modello che reintroduca una famiglia esistente (per esempio un secondo modello `"biomedical-st"`). Poi prova, mentalmente o davvero, ad aggiungerne uno di una famiglia nuova, per esempio `"multilingual"`. Verifica tu stesso, leggendo `function.py:162-174` e `function.py:372-379`, cosa resterebbe da fare a mano (il colore dedicato in `FAMILY_COLORS`) e cosa invece la pipeline gestisce ormai da sola.

## Riepilogo

`function.py` è, di fatto, l'unico punto di configurazione del progetto: non esistono file di configurazione esterni, ogni parametro è un valore letterale nel codice sorgente. Lo stato globale mutabile del capitolo 8.3, letto ora con sguardo architetturale, rende una funzione come `training_classifier()` più difficile da testare in isolamento, perché il suo risultato principale non è nel valore di ritorno ma in un side-effect su un dizionario di un altro modulo. Aggiungere un ottavo modello a una famiglia esistente è quasi gratuito grazie a `models_all`; aggiungerne uno di una famiglia nuova richiede oggi una sola modifica manuale (il colore dedicato in `FAMILY_COLORS`), dopo che il fix alla costruzione di `family_order` ha eliminato l'esclusione silenziosa dal grafico per famiglia.

## Domande di autoverifica

**1. Perché "configurare diversamente" questo progetto richiede modificare il codice sorgente, e non un file esterno?**
Perché non esiste alcun file di configurazione esternalizzato (`.yaml`, `.properties` o equivalente): ogni parametro — elenco dei modelli, dimensione del campione, colori, dimensioni delle figure — è scritto come valore letterale direttamente dentro `function.py`.

**2. Perché testare `training_classifier()` in isolamento è più complesso di quanto la sua firma lasci intuire?**
Perché il suo risultato principale non è il valore di ritorno della funzione (che non esiste, la funzione non restituisce nulla di esplicito) ma un side-effect sul dizionario globale `results` di un altro modulo — un'informazione non visibile guardando solo la firma `def training_classifier(dataset="heart_disease"):`.

**3. Cosa succederebbe, in concreto, se aggiungessi un ottavo modello con una famiglia mai vista prima, senza modificare `FAMILY_COLORS`?**
Il modello riceverebbe un colore di ripiego grigio invece di un colore dedicato in tutti i grafici basati sulla palette, incluso il confronto per famiglia — ma comparirebbe comunque in tutti i grafici: dopo il fix alla costruzione di `family_order` (`function.py:377-378`), una famiglia non elencata in `FAMILY_COLORS` viene aggiunta in coda all'ordine invece di essere esclusa in silenzio come accadeva in una versione precedente del codice.

> **MATERIALE PER LA TESI**
> 1. L'osservazione sull'assenza di configurazione esternalizzata, con l'elenco dei parametri codificati come valori letterali — riusabile in "Materiali e metodi" per descrivere onestamente la flessibilità operativa del progetto.
> 2. L'analisi dello stato globale mutabile come ostacolo alla testabilità, collegata esplicitamente alla Parte X — riusabile come argomento nella sezione "Discussione e limiti".
> 3. La guida passo-passo per aggiungere un ottavo modello, con la storia del punto di rottura silenziosa (`family_order` scritto a mano) individuato durante la revisione e poi corretto nel codice — riusabile come esercizio dimostrativo di comprensione del codice, o come esempio concreto di miglioramento guidato dall'analisi nella sezione "lavori futuri".

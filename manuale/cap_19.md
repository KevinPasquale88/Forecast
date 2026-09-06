# Capitolo 19 — Stato, configurazione, punti di estensione

**Obiettivi del capitolo**

- Sapere che `function.py` è, di fatto, l'unico file di configurazione del progetto, e cosa questo comporta.
- Rivedere lo stato globale mutabile con lo sguardo architetturale, non solo linguistico, di questo capitolo.
- Sapere esattamente dove intervenire — e dove stare attenti — per aggiungere un ottavo modello di embedding.

## 19.1 Dove vive la configurazione: `function.py` come "file unico di config"

**[Fatto]** Non esiste, in questo progetto, un file di configurazione nel senso in cui probabilmente lo intendi arrivando da Java — nessun `.properties`, nessun `.yaml`, nessuna classe annotata `@ConfigurationProperties`. Ogni parametro che potresti aspettarti di trovare esternalizzato è invece scritto direttamente dentro `function.py`, come valore letterale nel codice: l'elenco dei sette modelli con i loro identificativi (`function.py:38-49`), la dimensione del campione per Diabetes130 (`function.py:116`, `sample_size=20000`), la palette di colori (`function.py:57-61`), le dimensioni standard delle figure (`function.py:64-65`).

**[Interpretazione]** Questo significa che "configurare" il progetto in modo diverso — per esempio cambiare quanti record campionare da Diabetes130 — richiede modificare il codice sorgente, non un file di configurazione esterno da passare come parametro. Non è necessariamente un problema per un progetto di ricerca a questa scala, dove chi esegue la pipeline e chi ne legge il codice sono, con ogni probabilità, la stessa persona — ma è un punto di attenzione se il progetto dovesse mai essere eseguito da chi non ha accesso o familiarità col codice sorgente.

## 19.2 Stato globale mutabile: dove, perché, rischi

Il capitolo 8.3 ha già mostrato il meccanismo linguistico del dizionario `results` (`function.py:67-72`, mutato da `classification.py:51`). A livello architetturale, la domanda interessante è un'altra: **perché lo stato globale mutabile è un problema per l'estensibilità, non solo per la correttezza immediata?**

**[Interpretazione]** Uno stato condiviso a livello di modulo rende più difficile ragionare su una funzione guardandola in isolamento: `training_classifier()` (`classification.py:9-80`) non restituisce esplicitamente il proprio risultato principale come valore di ritorno — lo scrive in un dizionario globale importato da un altro modulo, un side-effect che non è visibile guardando solo la firma della funzione (`def training_classifier(dataset="heart_disease"):`, nessun tipo di ritorno dichiarato, capitolo 7.2). Chiunque volesse scrivere un test automatico per questa funzione (Parte X) dovrebbe sapere, in anticipo, di dover controllare `function.results` dopo la chiamata — un'informazione che nessuna firma comunica.

> **ATTENZIONE —** questo è precisamente il tipo di accoppiamento implicito che un'architettura a livelli in Java tende a evitare per costruzione: un metodo di un servizio Java che scrivesse silenziosamente in un campo statico di un'altra classe, invece di restituire un valore, verrebbe quasi certamente segnalato in un code review. Qui il linguaggio lo permette senza frizione (capitolo 8.3), e il progetto lo usa: un'osservazione critica legittima per la Parte XI, non solo una curiosità sintattica.

## 19.3 Dove aggiungeresti un ottavo modello di embedding, se dovessi farlo tu

**[Fatto]** Aggiungere un ottavo modello di embedding richiede, in linea di principio, una sola modifica: aggiungere un dizionario con la stessa struttura degli altri a `models_ollama` o a `models_medical` (`function.py:38-49`), con i campi `type`, `model_name`, `name`, `filename`, `filename_label`, `family`. Ogni altra parte della pipeline — generazione degli embedding (`embedding.py`), addestramento (`classification.py`), valutazione (`evaluation.py`), analisi degli errori (`error_analysis.py`), test statistici (`statisticaltest.py`) — itera su `models_all` (`function.py:51`, l'unione di `models_ollama` e `models_medical`) senza mai nominare esplicitamente uno dei sette modelli attuali: il codice è già scritto per generalizzare a un numero qualunque di modelli.

**[Fatto]** Con una precisazione importante, se il nuovo modello appartiene a una **famiglia già esistente** (per esempio un altro modello `"biomedical"`), tutto funziona automaticamente: `get_model_palette()` (`function.py:162-174`) genera una nuova sfumatura di colore per ogni membro della famiglia, quale che sia il loro numero.

**[Fatto]** Se invece il nuovo modello introducesse una **quarta famiglia**, mai vista finora, due punti del codice richiederebbero una modifica manuale, non automatica: `FAMILY_COLORS` (`function.py:57-61`) non avrebbe una voce per quella famiglia, e `get_model_palette()` userebbe silenziosamente il colore di ripiego `"#888888"` (grigio, `function.py:170`) invece di un colore dedicato — nessun errore, solo un grafico meno leggibile. Più seriamente, `plot_family_comparison()` (`function.py:349`) costruisce l'ordine delle famiglie con una lista **scritta a mano**:
```python
family_order = [f for f in ["general-purpose", "biomedical", "biomedical-st"] if f in df["Family"].unique()]
```
Una quarta famiglia non elencata qui non comparirebbe affatto nell'ordine costruito da questa riga — un'esclusione silenziosa, non un errore, e per questo più insidiosa: il grafico verrebbe generato comunque, semplicemente senza quella famiglia, e nulla nella console lo segnalerebbe.

> **PROVA TU —** apri `function.py` e prova, sulla carta o in un ambiente di test separato, ad aggiungere un ottavo modello che reintroduca una famiglia esistente (per esempio un secondo modello `"biomedical-st"`). Poi prova, mentalmente o davvero, ad aggiungerne uno di una famiglia nuova, per esempio `"multilingual"`. Verifica tu stesso, leggendo `function.py:162-174` e `function.py:349`, se la tua previsione su cosa si romperebbe silenziosamente coincide con quanto appena descritto.

## Riepilogo

`function.py` è, di fatto, l'unico punto di configurazione del progetto: non esistono file di configurazione esterni, ogni parametro è un valore letterale nel codice sorgente. Lo stato globale mutabile del capitolo 8.3, letto ora con sguardo architetturale, rende una funzione come `training_classifier()` più difficile da testare in isolamento, perché il suo risultato principale non è nel valore di ritorno ma in un side-effect su un dizionario di un altro modulo. Aggiungere un ottavo modello a una famiglia esistente è quasi gratuito grazie a `models_all`; aggiungerne uno di una famiglia nuova richiede due modifiche manuali puntuali, altrimenti silenziosamente incomplete.

## Domande di autoverifica

**1. Perché "configurare diversamente" questo progetto richiede modificare il codice sorgente, e non un file esterno?**
Perché non esiste alcun file di configurazione esternalizzato (`.yaml`, `.properties` o equivalente): ogni parametro — elenco dei modelli, dimensione del campione, colori, dimensioni delle figure — è scritto come valore letterale direttamente dentro `function.py`.

**2. Perché testare `training_classifier()` in isolamento è più complesso di quanto la sua firma lasci intuire?**
Perché il suo risultato principale non è il valore di ritorno della funzione (che non esiste, la funzione non restituisce nulla di esplicito) ma un side-effect sul dizionario globale `results` di un altro modulo — un'informazione non visibile guardando solo la firma `def training_classifier(dataset="heart_disease"):`.

**3. Cosa succederebbe, in concreto, se aggiungessi un ottavo modello con una famiglia mai vista prima, senza modificare `FAMILY_COLORS` e `plot_family_comparison()`?**
Il modello riceverebbe un colore di ripiego grigio invece di un colore dedicato in tutti i grafici basati sulla palette, e sarebbe del tutto assente dal grafico di confronto per famiglia (`FamilyComparison_metrics`), perché la sua famiglia non comparirebbe nella lista scritta a mano `family_order` — senza che alcun errore o avviso lo segnali.

> **MATERIALE PER LA TESI**
> 1. L'osservazione sull'assenza di configurazione esternalizzata, con l'elenco dei parametri codificati come valori letterali — riusabile in "Materiali e metodi" per descrivere onestamente la flessibilità operativa del progetto.
> 2. L'analisi dello stato globale mutabile come ostacolo alla testabilità, collegata esplicitamente alla Parte X — riusabile come argomento nella sezione "Discussione e limiti".
> 3. La guida passo-passo per aggiungere un ottavo modello, con i due punti di rottura silenziosa individuati (`FAMILY_COLORS`, `family_order`) — riusabile come esercizio dimostrativo di comprensione del codice, o come base per una sezione "lavori futuri" più tecnica.

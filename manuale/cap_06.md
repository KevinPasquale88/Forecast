# Capitolo 6 — Il gergo del codice: dizionario variabili → concetti

**Obiettivi del capitolo**

- Avere, prima ancora di leggere una riga di implementazione, un dizionario di riferimento fra i nomi che il codice usa e i concetti della Parte I.
- Riconoscere alcuni nomi del progetto che, letti senza contesto, portano fuori strada.
- Vedere dove, esattamente, le due domande di ricerca del progetto diventano scelte concrete nel codice.

Questo capitolo è pensato per essere consultato, non solo letto una volta. Da qui in avanti, ogni volta che il libro cita una variabile o una costante del codice, il significato è quello di questa tabella — non lo ripetiamo capitolo per capitolo.

## 6.1 Tabella di corrispondenza completa

| Nome nel codice | Dove compare | Cosa significa in linguaggio comune |
|---|---|---|
| `tau` | `classification.py:35` | La soglia di decisione: il punteggio minimo oltre il quale un caso viene classificato come positivo, scelta per massimizzare F1 su quel fold (capitolo 35) |
| `y_score` | ovunque nel progetto | Il punteggio di probabilità stimata della classe positiva, prima di applicare la soglia |
| `y_pred` | ovunque nel progetto | L'etichetta binaria prevista, dopo aver applicato `tau` a `y_score` |
| `y_true` | ovunque nel progetto | L'etichetta vera, nota dal dataset originale |
| `val_idx` | `classification.py:46`, `error_analysis.py:24` | Gli indici di riga, nel training pool bilanciato, dei record usati come validazione in quel fold — il ponte che permette di tornare dal punteggio statistico al record clinico originale (capitolo 25.1) |
| `X_train_bal`, `y_train_bal` | `preprocessing.py:53,70` | Le feature e le etichette del training set dopo il bilanciamento sintetico delle classi con SMOTENC (capitolo 31.2) |
| `X_train_raw.csv` | `preprocessing.py:66-68` | La versione leggibile (non codificata numericamente) delle feature bilanciate, salvata su disco riga-per-riga allineata agli embedding, così un embedding può sempre essere ricondotto al record clinico che lo ha generato |
| `boot_acc`, `boot_f1`, `boot_auc` | `evaluation.py:23-25` | Gli array di 10.000 valori della metrica corrispondente, uno per ogni ricampionamento bootstrap (capitolo 36) |
| `family` | `function.py:39-51` | La categoria del modello di embedding: `general-purpose`, `biomedical` o `biomedical-st` — non ha nulla a che fare con una gerarchia di classi |
| `model_name` | dizionari di configurazione in `function.py:38-51` | L'etichetta breve del modello (es. `"e5-base"`), usata nei nomi dei file e nei grafici |
| `name` (nello stesso dizionario) | idem | L'identificativo completo passato a Ollama o a Hugging Face per generare davvero l'embedding (es. `"jeffh/intfloat-e5-base-v2:q8_0"`) — **non è lo stesso campo di `model_name`**, anche se il nome della chiave non lo segnala |
| `dirs` | quasi ogni funzione della pipeline | Il dizionario delle cartelle di output specifiche per il dataset scelto: `preprocessing`, `embeddings`, `results`, `graphics`, `reports` (capitolo 20.2) |
| `results` | `function.py:67-72`, `classification.py:51` | Un dizionario globale, a livello di modulo, che accumula le metriche medie per modello — non un risultato locale a una singola chiamata di funzione (capitolo 8.3 spiega perché questo è rilevante in Python) |
| `MODEL_FAMILY` | `function.py:54` | Il dizionario di lookup che, dato il nome breve di un modello, restituisce la sua famiglia |
| `FAMILY_COLORS` | `function.py:57-61` | La palette di colori assegnata a ciascuna famiglia, usata in modo coerente in tutti i grafici del progetto |
| `models_all` | `function.py:51` | La lista dei 7 modelli, unione di `models_ollama` (i 4 generalisti) e `models_medical` (i 3 biomedici) |
| `sample_size` | `function.py:116` | La dimensione del campione stratificato estratto da Diabetes130 (20.000 su 101.766 righe originali) |
| `hardest_cases.csv` | `error_analysis.py:58-63` | I record clinici classificati in modo errato dal maggior numero di modelli diversi |
| `feature_deviation.csv` | `error_analysis.py:65-75` | Per ogni feature numerica, la differenza standardizzata fra la sua media nei casi sbagliati e nei casi corretti, aggregata su tutti i modelli |
| `encoder_comparison_summary.csv` | `evaluation.py:56` | La tabella finale: media e intervallo di confidenza al 95% di ciascuna metrica, per ciascun modello |
| `HF_READ_TOKEN`, `OFFLINE_MODE` | `.env`, letto in `embedding.py:146,155` | Le due variabili d'ambiente che autenticano verso Hugging Face e attivano/disattivano la modalità offline (capitolo 15.1) |

## 6.2 I nomi che ingannano

Tre nomi meritano un avvertimento esplicito, perché il significato più ovvio — quello che ti verrebbe naturale assumere — non è quello giusto.

**`tau`.** Se hai qualche familiarità con la statistica, `tau` potrebbe farti pensare al *tau di Kendall*, un coefficiente di correlazione per ranghi. Non c'è alcuna relazione: qui `tau` è solo il simbolo, per convenzione diffusa in letteratura sulle soglie di classificazione, di un numero fra 0 e 1 che non è una correlazione di nulla — è la soglia di decisione del capitolo 35, e basta.

**`family`.** Se vieni dal mondo enterprise, "family" potrebbe evocare una gerarchia di classi o un design pattern (una *abstract factory*, per esempio, spesso descritta in termini di "famiglie di oggetti correlati"). Qui è solo una stringa, un valore come un altro in un dizionario Python (`function.py:39` per esempio: `"family": "general-purpose"`), senza alcuna gerarchia di classi corrispondente nel codice.

**`num`.** Non è specifico del codice di questo progetto — viene dallo schema originale del dataset UCI Heart Disease — ma è ingannevole quanto gli altri due. Non significa "numero di qualcosa": è il nome storico della colonna che codifica la diagnosi (0 = assente, 1-4 = presenza e gravità), poi binarizzata in `preprocessing.py:41`. La prima volta che lo vedi in una tabella, "num" sembra un contatore; è, letteralmente, l'etichetta che l'intero progetto cerca di prevedere.

> **RIFERIMENTO AL CODICE —** questa non è una lista esaustiva di ogni nome del progetto — è una lista di ciò che ti servirà per non fermarti a chiederti "cosa significa questa variabile" mentre segui il filo di un capitolo più avanti. Se incontri un nome che non è in questa tabella, il capitolo che lo introduce lo spiega comunque al momento giusto.

## 6.3 Le due domande di ricerca del progetto, ora leggibili nel codice

**[Fatto]** `README.md:56-61` dichiara esplicitamente due domande di ricerca. La prima: gli embedding semantici generati localmente supportano efficacemente la classificazione clinica a partire da dati strutturati convertiti in linguaggio naturale? La seconda: i modelli specializzati nel dominio biomedico producono rappresentazioni più efficaci di quelli generalisti, per questo compito?

Con il vocabolario appena introdotto, puoi ora vedere esattamente dove queste due domande diventano codice eseguibile, non solo dichiarazioni nella documentazione:

- La **prima domanda** non ha una singola riga che la "risponde": la risposta emerge dal confronto fra le metriche di *tutti* i modelli in `models_all` (capitolo 44-45) rispetto a un modello di riferimento banale che non usa affatto gli embedding (capitolo 47, costruito apposta perché il codice del progetto non lo include).
- La **seconda domanda** si materializza precisamente nel campo `family` di ogni voce di `models_all` (`function.py:39-51`) e nella funzione `plot_family_comparison()` (`function.py:338-357`, capitolo 24), che raggruppa i risultati bootstrap per famiglia invece che per singolo modello — l'unico punto della pipeline in cui la distinzione generalista/biomedico produce un output diverso da un semplice elenco di 7 righe.

> **ATTENZIONE —** una domanda di ricerca dichiarata nella documentazione non garantisce, da sola, che la pipeline sia stata disegnata per rispondervi nel modo statisticamente più solido possibile. Il capitolo 53 mette in prospettiva critica quanto la seconda domanda, in particolare, riceva davvero una risposta netta dai dati — anticipazione utile da tenere a mente da qui in avanti.

## Riepilogo

Questo capitolo è un dizionario di consultazione: traduce i nomi di variabili, costanti e file del progetto nei concetti della Parte I, segnala tre nomi (`tau`, `family`, `num`) il cui significato più intuitivo è quello sbagliato, e mostra dove le due domande di ricerca dichiarate nel README diventano, letteralmente, righe di codice eseguibile.

## Domande di autoverifica

**1. Qual è la differenza fra `model_name` e `name` nei dizionari di configurazione di `function.py`?**
`model_name` è l'etichetta breve usata nei nomi di file e nei grafici (per esempio `"e5-base"`); `name` è l'identificativo completo che il codice passa davvero a Ollama o Hugging Face per generare l'embedding (per esempio `"jeffh/intfloat-e5-base-v2:q8_0"`). Sono due campi distinti dello stesso dizionario, con scopi diversi.

**2. Perché `tau` non ha nulla a che fare con una correlazione statistica, nonostante il nome?**
Perché è solo la variabile che rappresenta la soglia di decisione ottimale per un fold — un valore fra 0 e 1 scelto massimizzando F1 — non un coefficiente di correlazione. La coincidenza è solo nel simbolo usato, non nel concetto.

**3. In quale unica funzione del progetto la distinzione fra famiglie di modello produce un output visibilmente diverso da un confronto modello-per-modello?**
In `plot_family_comparison()` (`function.py:338-357`), che raggruppa i risultati bootstrap per famiglia (generalista, biomedico, biomedico per frasi) invece che per singolo modello.

> **MATERIALE PER LA TESI**
> 1. La tabella di corrispondenza completa (§6.1) — riusabile come glossario tecnico in appendice alla tesi, o come tabella di riferimento nel capitolo "Materiali e metodi".
> 2. I tre nomi ingannevoli con la spiegazione del perché (§6.2) — riusabile come nota metodologica su quanto la leggibilità del codice non garantisca, da sola, la correttezza dell'interpretazione.
> 3. La mappatura esplicita delle due domande di ricerca alle rispettive righe di codice (§6.3) — riusabile, quasi parola per parola, nella sezione che nella tesi formula le domande di ricerca, con la garanzia che ogni domanda sia ancorata a qualcosa di verificabile nel codice.

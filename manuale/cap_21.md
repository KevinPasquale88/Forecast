# Capitolo 21 — `preprocessing.py`: dalla tabella grezza al training set bilanciato

**Obiettivi del capitolo**

- Seguire, riga per riga, come un dataset grezzo diventa il training pool usato per generare gli embedding.
- Capire perché il codice bilancia le classi *prima* di codificare le feature, non dopo.
- Sapere esattamente cosa viene scartato, in questo file, e perché è rilevante per la Parte XI.

**[Fatto]** `preprocessing.py` (121 righe) è la fase 1 della pipeline (`main.py:34`), l'unica — insieme a `embedding.py` — il cui output raggiunge la fase successiva per valore in memoria, non solo su disco (capitolo 17.1).

## 21.1 Caricamento e unione sorgenti

**[Fatto]** `preprocessing_data(dataset="heart_disease")` (righe 19-70) è la funzione orchestratrice dell'intero file, l'unica chiamata direttamente da `main.py:34`. Le prime righe scelgono, in base al parametro `dataset`, quale funzione di caricamento usare (`load_heart_disease()` o `load_diabetes130()`, entrambe definite in `function.py` — non in questo file, nonostante il nome) e quali elenchi di colonne applicare:
```python
if dataset == "diabetes130":
    datasetChoosen = load_diabetes130(sample_size=sample_size)
    target_col = "readmitted"
    num_cols_used = num_cols_diabetes130
    cat_cols_used = cat_cols_diabetes130
else:
    datasetChoosen = load_heart_disease()
    target_col = "num"
    num_cols_used = num_cols
    cat_cols_used = cat_cols
```
Nota il refuso — reale, non un errore di trascrizione di questo libro — nel nome della variabile `datasetChoosen`: convenzione a cammello (*camelCase*) in un file che altrove usa sistematicamente lo *snake_case* (`num_cols_used`, `target_col`). Non ha conseguenze funzionali, ma è un'incoerenza di stile verificabile leggendo il file.

**[Fatto]** Segue lo split fra feature e target (riga 39-41) e lo split fra addestramento e test (riga 43):
```python
X = datasetChoosen.drop(target_col, axis=1)
y = datasetChoosen[target_col]
y = (y > 0).astype(int)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
```
`stratify=y` garantisce che la proporzione fra le due classi (capitolo 4.2) sia preservata sia nel training set sia nel test set — senza, uno split casuale su un dataset sbilanciato potrebbe per sfortuna concentrare quasi tutta la classe minoritaria in una sola delle due parti.

> **ATTENZIONE —** `X_test` e `y_test`, calcolati in questa riga, **non vengono mai più usati in nessuna parte di questo file, né di alcun altro file del progetto** — verificato con lettura completa di tutti i moduli. La funzione restituisce solo `X_train_bal, y_train_bal` (riga 70), derivati esclusivamente da `X_train`/`y_train`. Il 20% di dati messo da parte da questa riga è, a tutti gli effetti, calcolato e scartato. Il capitolo 33 lo inquadra nel contesto della validazione corretta, il capitolo 51 lo riprende come limite metodologico.

## 21.2 Imputazione, SMOTENC, codifica: tre trasformazioni, tre scopi diversi

**[Fatto]** `impute_raw()` (righe 76-82) sostituisce i valori mancanti con la mediana per le colonne numeriche e con la moda per le colonne categoriali:
```python
def impute_raw(X, num_cols, cat_cols):
    X = X.copy()
    for col in num_cols:
        X[col] = X[col].fillna(X[col].median())
    for col in cat_cols:
        X[col] = X[col].fillna(X[col].mode().iloc[0])
    return X
```
`X = X.copy()` alla prima riga evita di modificare il DataFrame originale passato come argomento — senza questa copia esplicita, `X[col] = ...` modificherebbe l'oggetto del chiamante, un rischio concreto della tipizzazione dinamica (capitolo 7.2): niente, a livello di firma, segnala se una funzione modifica il proprio argomento o ne restituisce una copia.

**[Fatto]** `balance_classes()` (righe 84-92) applica SMOTENC — non SMOTE ordinario — sulle feature grezze, non su una loro codifica numerica:
```python
def balance_classes(X, y, cat_cols):
    cat_idx = [X.columns.get_loc(c) for c in cat_cols]
    smote_nc = SMOTENC(categorical_features=cat_idx, random_state=42)
    X_res, y_res = smote_nc.fit_resample(X, y)
    return X_res, y_res
```
**[Livello: teoria consolidata del settore]** SMOTE (Synthetic Minority Over-sampling TEchnique) genera record sintetici della classe minoritaria interpolando fra vicini reali nello spazio delle feature. La variante SMOTENC estende l'idea alle feature *categoriali* (Nominal and Continuous): per le colonne numeriche interpola come SMOTE ordinario, per le colonne categoriali assegna il valore più frequente fra i vicini usati per l'interpolazione, invece di un valore intermedio privo di senso (un'interpolazione fra "maschio" e "femmina" non produce una categoria valida). **[Interpretazione]** Applicare SMOTENC *prima* di qualunque codifica numerica, sulle feature ancora leggibili (età in anni, non uno z-score), è precisamente ciò che rende possibile, più avanti, convertire anche i record sintetici in frasi di linguaggio naturale con `record_to_text_*()` (capitolo 22.1): un record sintetico che fosse già stato scalato e codificato non avrebbe più valori interpretabili da mettere in una frase.

## 21.3 Cosa viene salvato e perché

**[Fatto]** Dopo il bilanciamento, `preprocessing_data()` costruisce anche una versione *codificata* dei dati — scalata con `StandardScaler` e one-hot-encoded con `OneHotEncoder` (`build_encoder()`, righe 94-105) — ma **[Fatto]** questa versione codificata è usata *solo* per il grafico UMAP (`plot_umap()`, riga 58, capitolo 38) e per la heatmap di correlazione (`plot_data_heatmap()`, riga 62): non alimenta in alcun modo la generazione di embedding testuali, che lavora sempre sulle feature grezze bilanciate (`X_train_bal`), non su questa versione codificata.

**[Fatto]** Un secondo output, distinto da quello codificato, è salvato per la tracciabilità degli errori (righe 66-68):
```python
X_train_bal.reset_index(drop=True).to_csv(
    os.path.join(dirs["preprocessing"], "X_train_raw.csv"), index=False
)
```
`X_train_raw.csv` è la versione leggibile delle feature bilanciate, allineata riga per riga con l'ordine in cui verranno poi trasformate in testo ed embeddate — è il file che il capitolo 25 rilegge per ricondurre un errore di classificazione al record clinico originale (o sintetico) che lo ha causato.

## Interfaccia pubblica

| Funzione | Parametri | Ritorna | Effetti collaterali |
|---|---|---|---|
| `preprocessing_data(dataset="heart_disease")` | Nome dataset | `X_train_bal, y_train_bal` (DataFrame, Series) | Crea grafici UMAP/heatmap; salva `.npy` e `X_train_raw.csv` su disco |
| `impute_raw(X, num_cols, cat_cols)` | DataFrame, elenchi colonne | Copia di `X` con mancanti imputati | Nessuno (lavora su una copia) |
| `balance_classes(X, y, cat_cols)` | Feature, target, colonne categoriali | `X_res, y_res` bilanciati | Nessuno |
| `build_encoder(X, y, num_cols, cat_cols)` | Feature bilanciate, colonne | `ColumnTransformer` addestrato | Nessuno |
| `data_processed(X_train, y_train, preprocessor, num_cols, cat_cols)` | Feature, encoder | DataFrame codificato con colonna `target` | Nessuno |
| `save_data_processed(X_train_emb_df, preprocessing_dir)` | DataFrame codificato, percorso | Nessuno | Salva 2 file `.npy` |

## Errori tipici

Un `KeyError` sul nome di una colonna, in questa fase, indica quasi sempre un disallineamento fra `num_cols`/`cat_cols` (di `function.py`) e le colonne effettivamente presenti nel DataFrame caricato — per esempio se `load_diabetes130()` cambiasse l'elenco di colonne senza aggiornare `num_cols_diabetes130`/`cat_cols_diabetes130` di conseguenza. Un `ValueError` da `SMOTENC` segnala tipicamente che `cat_idx` (gli indici di colonna categoriali) non corrisponde più alla struttura reale di `X`, per esempio se l'ordine delle colonne fosse cambiato altrove.

## Riepilogo

`preprocessing.py` carica i dati grezzi, imputa i valori mancanti, bilancia le classi con SMOTENC sulle feature ancora leggibili — condizione necessaria perché anche i record sintetici possano diventare testo — e produce, come output visibile alla fase successiva, solo `X_train_bal`/`y_train_bal`. Una versione codificata numericamente esiste ma serve solo per i grafici di visualizzazione; il 20% di dati riservato al test non viene mai più usato in nessun punto del progetto.

## Domande di autoverifica

**1. Perché SMOTENC viene applicato sulle feature grezze e non su una loro versione già codificata numericamente?**
Perché i record sintetici generati da SMOTENC devono restare convertibili in frasi di linguaggio naturale nella fase successiva (capitolo 22): un record già scalato e one-hot-encoded non avrebbe più valori interpretabili (età in anni, categoria testuale) da inserire in una descrizione testuale.

**2. Cosa succede, di fatto, al 20% di dati messo da parte da `train_test_split` alla riga 43 di `preprocessing.py`?**
Viene calcolato ma non restituito né salvato da nessuna parte: `preprocessing_data()` restituisce solo i dati derivati dall'80% di training, e nessun altro file del progetto fa riferimento a `X_test`/`y_test`.

**3. A cosa serve la versione codificata numericamente (`data_processed()`), se non alimenta la generazione di embedding?**
Serve esclusivamente ai due grafici di visualizzazione della fase di preprocessing — la proiezione UMAP e la heatmap di correlazione — entrambi bisognosi di feature numeriche scalate, a differenza della pipeline di embedding che lavora sempre sulle feature grezze.

> **MATERIALE PER LA TESI**
> 1. La spiegazione di SMOTENC applicato pre-codifica, con la motivazione esplicita legata alla convertibilità in testo — riusabile in "Materiali e metodi" per giustificare l'ordine delle trasformazioni nella pipeline.
> 2. L'osservazione verificata sul test set calcolato e mai usato (`X_test`, `y_test`) — riusabile, con il riferimento esatto di riga, nella sezione "Discussione e limiti".
> 3. La distinzione fra la versione grezza bilanciata (usata per il testo) e quella codificata (usata solo per i grafici) — riusabile come chiarimento tecnico per prevenire un fraintendimento comune su cosa "vede" davvero il classificatore finale.

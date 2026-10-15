# Capitolo 21 — `preprocessing.py`: dalla tabella grezza al training set bilanciato

**Obiettivi del capitolo**

- Seguire, riga per riga, come un dataset grezzo diventa il training pool usato per generare gli embedding.
- Capire perché il codice bilancia le classi *prima* di codificare le feature, non dopo.
- Sapere esattamente cosa esce da questo file — incluso il test set trattenuto, che una versione precedente calcolava e scartava — e perché è rilevante per le Parti IX e XI.

**[Fatto]** `preprocessing.py` (196 righe) è la fase 1 della pipeline (`main.py:41`), l'unica — insieme a `embedding.py` — il cui output raggiunge la fase successiva per valore in memoria, non solo su disco (capitolo 17.1).

## 21.1 Caricamento e unione sorgenti

**[Fatto]** `preprocessing_data(dataset="heart_disease")` (righe 28-109) è la funzione orchestratrice dell'intero file, l'unica chiamata direttamente da `main.py:41`. Le prime righe scelgono, in base al parametro `dataset`, quale funzione di caricamento usare (`load_heart_disease()` o `load_diabetes130()`, entrambe definite in `function.py` — non in questo file, nonostante il nome) e quali elenchi di colonne applicare:
```python
if dataset == "diabetes130":
    dataset_chosen = load_diabetes130(sample_size=sample_size)
    target_col = "readmitted"
    num_cols_used = num_cols_diabetes130
    cat_cols_used = cat_cols_diabetes130
else:
    dataset_chosen = load_heart_disease()
    target_col = "num"
    num_cols_used = num_cols
    cat_cols_used = cat_cols
```
Una nota di storia del codice: fino alla revisione del 2026 questa variabile si chiamava `datasetChoosen` — convenzione a cammello (*camelCase*), oltre che con un refuso di inglese, in un file che altrove usa sistematicamente lo *snake_case* (`num_cols_used`, `target_col`). Non aveva conseguenze funzionali, ed è stata rinominata in `dataset_chosen` per coerenza di stile durante i fix di qualità documentati in `docs/CHANGES.md`.

**[Fatto]** Segue lo split fra feature e target (righe 48-50) e lo split fra addestramento e test (riga 52):
```python
X = dataset_chosen.drop(target_col, axis=1)
y = dataset_chosen[target_col]
y = (y > 0).astype(int)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
```
`stratify=y` garantisce che la proporzione fra le due classi (capitolo 4.2) sia preservata sia nel training set sia nel test set — senza, uno split casuale su un dataset sbilanciato potrebbe per sfortuna concentrare quasi tutta la classe minoritaria in una sola delle due parti.

> **ATTENZIONE —** in una versione precedente del progetto, `X_test` e `y_test` calcolati in questa riga **non venivano mai più usati in nessuna parte del codice**: il 20% di dati messo da parte era, a tutti gli effetti, calcolato e scartato — uno dei limiti metodologici più seri individuati durante la stesura di questo manuale. La revisione documentata in `docs/CHANGES.md` lo ha corretto: oggi il test set viene imputato con le sole statistiche del training (righe 74-76), salvato su disco (`X_test_raw.csv`, `y_test.npy`, righe 104-107), embeddato separatamente (`main.py:48-50`) e valutato dalla fase 7 (`holdout_evaluation.py`, capitolo 43). Non viene mai bilanciato da SMOTENC né toccato da alcuna decisione di addestramento o selezione del modello. Il capitolo 33 inquadra il perché nel contesto della validazione corretta; il capitolo 51 racconta la storia del limite e della sua correzione.

## 21.2 Imputazione, SMOTENC, codifica: tre trasformazioni, tre scopi diversi

**[Fatto]** Prima dell'imputazione, la funzione individua le colonne mancanti così spesso che imputarle significherebbe fabbricare gran parte della feature: `columns_needing_missing_indicator()` (righe 112-115) seleziona ogni colonna con più del 30% di valori mancanti **nel solo training split** (`MISSING_INDICATOR_THRESHOLD`, riga 24), e `add_missing_indicators()` (righe 118-124) aggiunge per ciascuna una colonna `<col>_missing` a 0/1 in entrambi gli split. La soglia è dataset-agnostica: nessun nome di colonna è cablato nel codice, ma sui dati reali seleziona `ca`, `slope` e `thal` per Heart Disease (verificabile nell'header di `X_train_raw.csv`: tre colonne `*_missing`) e `max_glu_serum`/`A1Cresult` per Diabetes130 — colonne la cui mancanza massiccia è documentata nei capitoli 29-31. L'indicatore è trattato come feature categoriale da lì in avanti (riga 65), così SMOTENC, l'encoder e soprattutto `record_to_text_*()` in `embedding.py` (capitolo 22.1) lo vedono: è ciò che permette al testo generato di scrivere "not recorded" per un valore imputato, invece di presentarlo come osservato.

**[Fatto]** L'imputazione vera e propria è divisa in due funzioni (righe 130-147): `fit_imputation_values()` calcola i valori di riempimento (mediana per le numeriche, moda per le categoriali) da un solo DataFrame, e `apply_imputation()` li applica a qualunque DataFrame:
```python
fill_values = fit_imputation_values(X_train, num_cols_used, cat_cols_used)
X_train_imputed = apply_imputation(X_train, fill_values)
X_test_imputed = apply_imputation(X_test, fill_values)
```
La separazione non è cosmetica: i valori di riempimento sono **calcolati sul solo training split e riapplicati identici al test split** — se il test set venisse imputato con la propria mediana/moda, statistiche del test set filtrerebbero dentro i valori usati per descriverlo, una forma di leakage (capitolo 33.3). La vecchia funzione monolitica `impute_raw()` (righe 150-156) sopravvive come scorciatoia fit-and-apply per chi ha un solo DataFrame da imputare — per esempio i test automatici. In tutte queste funzioni, `X = X.copy()` evita di modificare il DataFrame originale passato come argomento — senza questa copia esplicita, `X[col] = ...` modificherebbe l'oggetto del chiamante, un rischio concreto della tipizzazione dinamica (capitolo 7.2): niente, a livello di firma, segnala se una funzione modifica il proprio argomento o ne restituisce una copia.

**[Fatto]** `balance_classes()` (righe 158-166) applica SMOTENC — non SMOTE ordinario — sulle feature grezze, non su una loro codifica numerica:
```python
def balance_classes(X, y, cat_cols):
    cat_idx = [X.columns.get_loc(c) for c in cat_cols]
    smote_nc = SMOTENC(categorical_features=cat_idx, random_state=42)
    X_res, y_res = smote_nc.fit_resample(X, y)
    return X_res, y_res
```
**[Livello: teoria consolidata del settore]** SMOTE (Synthetic Minority Over-sampling TEchnique) genera record sintetici della classe minoritaria interpolando fra vicini reali nello spazio delle feature. La variante SMOTENC estende l'idea alle feature *categoriali* (Nominal and Continuous): per le colonne numeriche interpola come SMOTE ordinario, per le colonne categoriali assegna il valore più frequente fra i vicini usati per l'interpolazione, invece di un valore intermedio privo di senso (un'interpolazione fra "maschio" e "femmina" non produce una categoria valida). **[Interpretazione]** Applicare SMOTENC *prima* di qualunque codifica numerica, sulle feature ancora leggibili (età in anni, non uno z-score), è precisamente ciò che rende possibile, più avanti, convertire anche i record sintetici in frasi di linguaggio naturale con `record_to_text_*()` (capitolo 22.1): un record sintetico che fosse già stato scalato e codificato non avrebbe più valori interpretabili da mettere in una frase.

## 21.3 Cosa viene salvato e perché

**[Fatto]** Dopo il bilanciamento, `preprocessing_data()` costruisce anche una versione *codificata* dei dati — scalata con `StandardScaler` e one-hot-encoded con `OneHotEncoder` (`build_encoder()`, righe 168-179) — ma **[Fatto]** questa versione codificata è usata *solo* per il grafico UMAP (`plot_umap()`, riga 87, capitolo 38) e per la heatmap di correlazione (`plot_data_heatmap()`, riga 91): non alimenta in alcun modo la generazione di embedding testuali, che lavora sempre sulle feature grezze bilanciate (`X_train_bal`), non su questa versione codificata.

**[Fatto]** Un secondo output, distinto da quello codificato, è salvato per la tracciabilità degli errori (righe 95-97):
```python
X_train_bal.reset_index(drop=True).to_csv(
    os.path.join(dirs["preprocessing"], "X_train_raw.csv"), index=False
)
```
`X_train_raw.csv` è la versione leggibile delle feature bilanciate, allineata riga per riga con l'ordine in cui verranno poi trasformate in testo ed embeddate — è il file che il capitolo 25 rilegge per ricondurre un errore di classificazione al record clinico originale (o sintetico) che lo ha causato.

**[Fatto]** L'ultimo output è il test set trattenuto (righe 104-107): `X_test_raw.csv` (le feature del 20% di test, imputate con le statistiche del solo training, mai bilanciate) e `y_test.npy` (le etichette corrispondenti). Il commento nel codice alle righe 99-103 dichiara esplicitamente il motivo: questi file sostituiscono una versione della funzione che calcolava lo stesso split 80/20 e poi scartava `X_test`/`y_test` senza usarli per nulla. Saranno riletti da `main.py` per la generazione degli embedding di test e dalla fase 7 per la stima di generalizzazione.

## Interfaccia pubblica

| Funzione | Parametri | Ritorna | Effetti collaterali |
|---|---|---|---|
| `preprocessing_data(dataset="heart_disease")` | Nome dataset | `X_train_bal, y_train_bal` (DataFrame, Series) | Crea grafici UMAP/heatmap; salva `.npy`, `X_train_raw.csv`, `X_test_raw.csv`, `y_test.npy` su disco |
| `columns_needing_missing_indicator(X, columns, threshold=0.30)` | DataFrame, colonne, soglia | Nomi delle colonne oltre soglia di mancanza | Nessuno |
| `add_missing_indicators(X, columns)` | DataFrame, colonne da marcare | Copia di `X` con colonne `<col>_missing` 0/1 | Nessuno (lavora su una copia) |
| `fit_imputation_values(X, num_cols, cat_cols)` | DataFrame, elenchi colonne | Dizionario colonna → valore di riempimento | Nessuno |
| `apply_imputation(X, fill_values)` | DataFrame, valori già calcolati | Copia di `X` con mancanti imputati | Nessuno (lavora su una copia) |
| `impute_raw(X, num_cols, cat_cols)` | DataFrame, elenchi colonne | Copia di `X` con mancanti imputati (fit-and-apply) | Nessuno (lavora su una copia) |
| `balance_classes(X, y, cat_cols)` | Feature, target, colonne categoriali | `X_res, y_res` bilanciati | Nessuno |
| `build_encoder(X, y, num_cols, cat_cols)` | Feature bilanciate, colonne | `ColumnTransformer` addestrato | Nessuno |
| `data_processed(X_train, y_train, preprocessor, num_cols, cat_cols)` | Feature, encoder | DataFrame codificato con colonna `target` | Nessuno |
| `save_data_processed(X_train_emb_df, preprocessing_dir)` | DataFrame codificato, percorso | Nessuno | Salva 2 file `.npy` |

## Errori tipici

Un `KeyError` sul nome di una colonna, in questa fase, indica quasi sempre un disallineamento fra `num_cols`/`cat_cols` (di `function.py`) e le colonne effettivamente presenti nel DataFrame caricato — per esempio se `load_diabetes130()` cambiasse l'elenco di colonne senza aggiornare `num_cols_diabetes130`/`cat_cols_diabetes130` di conseguenza. Un `ValueError` da `SMOTENC` segnala tipicamente che `cat_idx` (gli indici di colonna categoriali) non corrisponde più alla struttura reale di `X`, per esempio se l'ordine delle colonne fosse cambiato altrove.

## Riepilogo

`preprocessing.py` carica i dati grezzi, marca con indicatori espliciti le colonne a mancanza massiccia, imputa i valori mancanti con statistiche calcolate sul solo training, bilancia le classi con SMOTENC sulle feature ancora leggibili — condizione necessaria perché anche i record sintetici possano diventare testo — e produce, come output in memoria per la fase successiva, `X_train_bal`/`y_train_bal`. Una versione codificata numericamente esiste ma serve solo per i grafici di visualizzazione; il 20% di dati riservato al test, che una versione precedente del codice calcolava e scartava, oggi viene salvato su disco e alimenta la valutazione holdout della fase 7.

## Domande di autoverifica

**1. Perché SMOTENC viene applicato sulle feature grezze e non su una loro versione già codificata numericamente?**
Perché i record sintetici generati da SMOTENC devono restare convertibili in frasi di linguaggio naturale nella fase successiva (capitolo 22): un record già scalato e one-hot-encoded non avrebbe più valori interpretabili (età in anni, categoria testuale) da inserire in una descrizione testuale.

**2. Cosa succede, di fatto, al 20% di dati messo da parte da `train_test_split` alla riga 52 di `preprocessing.py`?**
Viene imputato con i valori di riempimento calcolati sul solo training split, salvato su disco come `X_test_raw.csv` e `y_test.npy`, e mai toccato da SMOTENC né da alcuna decisione di addestramento: lo rileggeranno `main.py` (per generare gli embedding con suffisso `_test`) e `holdout_evaluation.py` (per la stima di generalizzazione della fase 7). In una versione precedente del codice veniva invece calcolato e scartato.

**3. A cosa serve la versione codificata numericamente (`data_processed()`), se non alimenta la generazione di embedding?**
Serve esclusivamente ai due grafici di visualizzazione della fase di preprocessing — la proiezione UMAP e la heatmap di correlazione — entrambi bisognosi di feature numeriche scalate, a differenza della pipeline di embedding che lavora sempre sulle feature grezze.

> **MATERIALE PER LA TESI**
> 1. La spiegazione di SMOTENC applicato pre-codifica, con la motivazione esplicita legata alla convertibilità in testo — riusabile in "Materiali e metodi" per giustificare l'ordine delle trasformazioni nella pipeline.
> 2. La storia del test set prima calcolato e scartato, poi recuperato con imputazione training-only e valutazione holdout dedicata — riusabile, con i riferimenti esatti di riga e a `docs/CHANGES.md`, come esempio concreto di limite individuato e corretto nella sezione "Discussione e limiti".
> 3. La distinzione fra la versione grezza bilanciata (usata per il testo) e quella codificata (usata solo per i grafici) — riusabile come chiarimento tecnico per prevenire un fraintendimento comune su cosa "vede" davvero il classificatore finale.

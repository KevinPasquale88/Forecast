# Parte IV — Architettura e codice

## Capitolo 12 — Architettura

Forecast è una pipeline batch di 1.909 righe Python distribuite in undici moduli. `main.py` esegue otto fasi in sequenza; ogni fase legge da disco i risultati della precedente e scrive i propri. Non c'è stato condiviso in memoria tra le fasi, salvo i dati restituiti dalla prima alla seconda.

![Le otto fasi di `main.py`. Il test set (in blu) segue una strada separata e rientra solo nella fase 7.](figure/schema_pipeline.png)

### 12.1 Moduli

| Modulo | Righe | Responsabilità |
| --- | --- | --- |
| `main.py` | 68 | Orchestrazione delle otto fasi, argomento `--dataset` |
| `function.py` | 444 | Configurazione (colonne, modelli, famiglie), caricamento dei dataset, cartelle, soglia, pulizia, grafici |
| `preprocessing.py` | 134 | Split 80/20, copia per i grafici, salvataggio dei dati grezzi |
| `embedding.py` | 225 | Conversione in testo, embedding via Ollama e Hugging Face |
| `classification.py` | 85 | Cross-validation, soglia, metriche per fold, predizioni out-of-fold |
| `evaluation.py` | 83 | Bootstrap, intervalli, grafici di confronto |
| `error_analysis.py` | 81 | Falsi positivi e negativi, casi difficili, deviazione delle variabili |
| `statisticaltest.py` | 153 | Wilcoxon, t-test appaiato, DeLong, Benjamini-Hochberg |
| `holdout_evaluation.py` | 87 | Classificatore finale e misura sul test set |
| `generatereport.py` | 312 | Report Markdown |
| `inference.py` | 237 | Predizione su un record nuovo (fuori dalla pipeline) |

### 12.2 Cosa scrive ogni fase

| Fase | File prodotti in `datas/<dataset>/` |
| --- | --- |
| 1 Preprocessing | `preprocessing/X_train_raw.csv`, `X_test_raw.csv`, `y_test.npy`, `preprocessed_data.npy`, `preprocessed_labels.npy`; `graphics/UMAP_*`, `heatmap_correlation` |
| 2 Embedding | `embeddings/<modello>_embeddings.npy` e `_labels.npy` (training), `_embeddings_test.npy` e `_labels_test.npy` (test) |
| 3 Classificazione | `results/model_performance.csv`, `<modello>_y_true/_y_score/_y_pred/_val_idx.npy`, `metric_comparison` |
| 4 Valutazione | `results/<modello>_boot_acc/_f1/_auc.npy`, `encoder_comparison_summary.csv`, grafici; `graphics/ROC_comparison`, `CM_<modello>` |
| 5 Analisi errori | `results/error_summary.csv`, `<modello>_false_positives.csv`, `_false_negatives.csv`, `hardest_cases.csv`, `feature_deviation.csv` |
| 6 Test statistici | `results/wilcoxon_comparison.csv`, `ttest_comparison.csv`, `delong_comparison.csv` |
| 7 Holdout | `results/holdout_evaluation.csv` |
| 8 Report | `reports/report.md` |

Ogni dataset ha la sua cartella; all'inizio di ogni run le funzioni `delete_files_*` di `function.py` cancellano solo i file del dataset in esecuzione.

### 12.3 Scelte architetturali e loro conseguenze

- **Fasi comunicanti via disco.** Ogni fase si può rieseguire o ispezionare da sola (per esempio aprire `model_performance.csv`). Il prezzo è che un file rimasto da una run precedente può essere letto per errore: per questo la pulizia iniziale copre tutti i file prodotti.
- **Configurazione centralizzata.** Aggiungere un encoder significa aggiungere una voce a `models_ollama` o `models_medical` in `function.py`: le fasi successive iterano su `models_all` e lo includono automaticamente, compresi colori e famiglia nei grafici.
- **Un solo classificatore per tutto.** `make_classifier` e `fit_classifier` in `function.py` sono usati da cross-validation, holdout e inferenza: il protocollo non può divergere tra le fasi.
- **Nessun modello salvato.** La pipeline salva embedding e predizioni, non classificatori; dove serve un classificatore (holdout, inferenza) lo riaddestra dagli embedding. È economico (una regressione logistica si addestra in meno di un secondo) e garantisce coerenza con gli embedding presenti.

## Capitolo 13 — `function.py` e `main.py`

### 13.1 Configurazione

`function.py` definisce:

- le colonne di ciascun dataset (`columns`, `num_cols`, `cat_cols`, e le versioni `_diabetes130`);
- i modelli (`models_ollama`, `models_medical`, `models_all`), ciascuno con `type`, `model_name`, `name`, nomi dei file e `family`;
- `MODEL_FAMILY` e `FAMILY_COLORS` per i grafici;
- `HF_MAX_SEQ_LENGTH = 512`;
- `hospice_or_death_discharge_ids = [11, 13, 14, 19, 20, 21]`;
- `datasets = ["heart_disease", "diabetes130"]`.

### 13.2 Caricamento dei dati

```python
def load_heart_disease():
    files = [...processed.cleveland.data, ...hungarian..., ...switzerland..., ...va.data]
    dfs = [pd.read_csv(f, header=None, na_values="?") for f in files]
    df = pd.concat(dfs, ignore_index=True)
    df.columns = columns
    df["chol"] = df["chol"].replace(0, np.nan)
    df["trestbps"] = df["trestbps"].replace(0, np.nan)
    return df
```

I quattro file non hanno intestazione; `?` indica un valore mancante; gli zeri di colesterolo e pressione, impossibili fisiologicamente, diventano mancanti.

```python
def load_diabetes130(sample_size=20000, random_state=42):
    df = pd.read_csv(".../diabetic_data.csv", na_values="?", keep_default_na=False, low_memory=False)
    df = df[~df["discharge_disposition_id"].isin(hospice_or_death_discharge_ids)]
    df = df.sort_values("encounter_id").drop_duplicates("patient_nbr")
    df = df[columns_diabetes130].copy()
    df["gender"] = df["gender"].replace("Unknown/Invalid", np.nan)
    df["readmitted"] = (df["readmitted"] == "<30").astype(int)
    if sample_size is not None and sample_size < len(df):
        df, _ = train_test_split(df, train_size=sample_size, stratify=df["readmitted"], random_state=random_state)
    return df.reset_index(drop=True)
```

L'ordine conta: prima si escludono decessi e hospice, poi si tiene il primo ricovero per paziente (ordinando per `encounter_id`, che cresce nel tempo), poi si campiona. `low_memory=False` evita un avviso di tipi misti sulla colonna `payer_code`.

### 13.3 La soglia

```python
def optimal_f1_threshold(y_true, y_score):
    precision, recall, thresholds = precision_recall_curve(y_true, y_score)
    f1_scores = 2 * (precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-6)
    return thresholds[f1_scores.argmax()]

C_GRID = np.logspace(-3, 2, 6)          # 0,001 · 0,01 · 0,1 · 1 · 10 · 100

def make_classifier(C=1.0):
    return make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=5000))

def choose_C(X, y, n_splits=5, random_state=42):
    search = GridSearchCV(make_classifier(), {"logisticregression__C": C_GRID},
                          cv=StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state),
                          scoring="roc_auc", refit=False, n_jobs=-1)
    search.fit(X, y)
    return float(search.best_params_["logisticregression__C"])

def out_of_fold_threshold(X, y, C=1.0, n_splits=5, random_state=42):
    inner_cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    scores = cross_val_predict(make_classifier(C), X, y, cv=inner_cv, method="predict_proba")[:, 1]
    return optimal_f1_threshold(y, scores)

def fit_classifier(X, y):
    C = choose_C(X, y)
    tau = out_of_fold_threshold(X, y, C=C)
    return make_classifier(C).fit(X, y), tau, C
```

`make_classifier` è il *linear probe* usato ovunque: standardizzazione (media 0, deviazione 1 per ogni dimensione, stimate sui dati di addestramento) seguita da regressione logistica L2. `choose_C` sceglie la regolarizzazione con una CV interna che massimizza la ROC-AUC; lo scaler sta dentro la pipeline, quindi viene riaddestrato in ogni fold interno senza vedere i dati di validazione. `fit_classifier` riunisce il protocollo completo: C, poi soglia con quel C, poi classificatore finale su tutti i dati.

`precision_recall_curve` restituisce un punto in più per precision e recall che per le soglie (il punto finale a recall 0): per questo si scarta l'ultimo elemento. `1e-6` evita la divisione per zero. `cross_val_predict` restituisce, per ogni record, la probabilità prodotta dal modello del fold in cui quel record era escluso.

### 13.4 Cartelle, pulizia, grafici

`get_output_dirs(dataset)` crea e restituisce le cinque cartelle del dataset e rifiuta nomi sconosciuti. Le quattro `delete_files_*` cancellano i file della run precedente cercando sottostringhe note nei nomi. Le funzioni `plot_*` producono tutti i grafici con uno stile comune (`_configure_plot_style`), una tavolozza per famiglia (`get_model_palette`) e salvataggio doppio PNG + PDF (`save_figure`).

### 13.5 `main.py`

```python
X_train, X_test, y_train, y_test = preprocessing_data(dataset=args.dataset)
embeddings(X_train, y_train, dataset=args.dataset)
embeddings(X_test, y_test, dataset=args.dataset, split="test")
training_classifier(dataset=args.dataset)
evaluate_results(dataset=args.dataset)
analyze_errors(dataset=args.dataset)
test_statistical_tests(dataset=args.dataset)
evaluate_holdout(dataset=args.dataset)
generate_report(dataset=args.dataset)
```

L'unico argomento è `--dataset` (default `heart_disease`). Il test set passa alla fase 2 in memoria: rileggerlo dal CSV trasformerebbe la categoria `"None"` di Diabetes130 in un valore mancante.

## Capitolo 14 — `preprocessing.py`

La funzione `preprocessing_data(dataset)` carica, binarizza, divide e salva. Non imputa e non bilancia (motivi nei capitoli 21, 24 e 25).

```python
X = dataset_chosen.drop(target_col, axis=1)
y = (dataset_chosen[target_col] > 0).astype(int)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
```

`stratify=y` mantiene la stessa prevalenza nelle due parti (55,3% e 55,4% su Heart Disease, 9,0% su Diabetes130).

La parte di visualizzazione lavora su una copia:

```python
fill_values = fit_imputation_values(X_train, num_cols_used, cat_cols_used)
X_train_viz = apply_imputation(X_train, fill_values)
encoder = build_encoder(X_train_viz, y_train, num_cols_used, cat_cols_used)
```

`fit_imputation_values` calcola mediana (numeriche) e moda (categoriche); `apply_imputation` le applica; `build_encoder` costruisce un `ColumnTransformer` con `StandardScaler` sulle numeriche e `OneHotEncoder` sulle categoriche. Il risultato serve solo a UMAP e alla heatmap.

Infine vengono salvati `X_train_raw.csv` e `X_test_raw.csv` (con celle vuote per i mancanti) e `y_test.npy`.

## Capitolo 15 — `embedding.py`

### 15.1 Conversione in testo

`record_to_text_heart_disease(row)` e `record_to_text_diabetes130(row)` compongono una lista di parti "campo: valore" e le uniscono con virgole. Tre funzioni di formattazione gestiscono i tipi:

```python
def _fmt_num(value, unit="", ndigits=1):
    if pd.isna(value):
        return "not recorded"
    return f"{round(float(value), ndigits):g}{unit}"
```

`:g` elimina gli zeri superflui (145.0 diventa "145"). `_fmt_cat` traduce un codice in etichetta tramite un dizionario (restituisce "unknown" per codici fuori elenco); `_fmt_bool` trasforma 0/1 in parole. Per Diabetes130 `_fmt_raw` scrive il valore così com'è.

Lunghezza in token delle frasi (tutti i record):

| Tokenizer | Heart Disease (min / mediana / max) | Diabetes130 (min / mediana / max) |
| --- | --- | --- |
| BioBERT, Bio_ClinicalBERT | 116 / 122 / 132 | 130 / 132 / 137 |
| PubMedBERT | 97 / 103 / 111 | 122 / 122 / 126 |

Con il vecchio limite di 100 token, la frase del primo record di Cleveland (129 token) si interrompeva a "slope of the peak exercise s": `slope`, `ca` e `thal` non venivano mai visti da sentence-biobert.

### 15.2 Generazione

`embeddings(X, y, dataset, split)` sceglie la funzione di conversione, produce le frasi e chiama `generate_all_embeddings`, che lancia `process_model` per ciascun modello in un pool di tre thread. `process_model` sceglie Ollama o Hugging Face in base a `type`, salva vettori ed etichette, e trasforma qualunque errore in un `RuntimeError` che indica modello e split. `_split_filename` aggiunge `_test` al nome dei file del test set.

## Capitolo 16 — `classification.py` e `holdout_evaluation.py`

### 16.1 Cross-validation

```python
kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for train_idx, val_idx in kf.split(X, y):
    X_train_full, X_val = X[train_idx], X[val_idx]
    y_train_full, y_val = y[train_idx], y[val_idx]
    logisticReg, tau, C = fit_classifier(X_train_full, y_train_full)
    y_score = logisticReg.predict_proba(X_val)[:, 1]
    y_pred = (y_score >= tau).astype(int)
    acc = accuracy_score(y_val, y_pred)
    f1 = f1_score(y_val, y_pred, average='macro')
    auc = roc_auc_score(y_val, y_score)
    pr_auc = average_precision_score(y_val, y_score)
    brier = brier_score_loss(y_val, y_score)
```

Per ciascun modello si ottengono 5 valori di ogni metrica; la media va in `model_performance.csv`, insieme alla mediana dei 5 valori di C scelti (`C_median`). Le predizioni dei 5 fold vengono concatenate e salvate con gli indici di validazione, così ogni record di training ha esattamente una predizione out-of-fold.

Con `random_state=42` e le stesse etichette, i fold sono identici per tutti i modelli: ogni record cade nello stesso fold per tutti e sette, condizione necessaria per i test appaiati.

![Schema di un fold esterno: la soglia è scelta su punteggi out-of-fold di una CV interna, il classificatore è addestrato su tutto il training del fold. Prima della soglia, una terza CV interna sceglie C.](figure/schema_cv_soglia.png)

Il costo computazionale cresce: per ogni fold esterno servono 30 addestramenti per scegliere C (6 valori × 5 fold), 5 per la soglia e 1 finale. Con una regressione logistica è accettabile anche su 16.000 record.

### 16.2 Holdout

`evaluate_holdout(dataset)` ripete lo stesso schema (`fit_classifier`) una sola volta su tutto il training set: scelta di C, soglia out-of-fold, addestramento completo, misura sul test set (accuracy, macro-F1, ROC-AUC, PR-AUC, precision, recall, Brier, prevalenza). È esattamente il procedimento con cui il chatbot costruisce il modello che usa.

## Capitolo 17 — Valutazione, errori, test, report

### 17.1 `evaluation.py`

```python
def bootstrap_metrics(y_true, y_score, y_pred, n_iter=10000, seed=42):
    rng = np.random.default_rng(seed)
    for _ in range(n_iter):
        idx = rng.integers(0, len(y_true), len(y_true))
        ...accuracy, macro-F1, ROC-AUC su (y_true[idx], y_pred[idx], y_score[idx])
```

`ci(a)` restituisce media e percentili 2,5 e 97,5. `evaluate_results` produce per ogni modello le matrici di confusione, salva le distribuzioni bootstrap, disegna boxplot, curve ROC, confronto per famiglia e media con intervalli, e scrive `encoder_comparison_summary.csv`.

### 17.2 `error_analysis.py`

Carica `X_train_raw.csv`, e per ogni modello usa `val_idx` per allineare le predizioni ai record. Calcola falsi positivi e negativi e i loro tassi, salva i record sbagliati, conta per ogni record quanti modelli lo sbagliano (`hardest_cases.csv`, i 20 peggiori) e calcola la deviazione standardizzata di ogni variabile numerica tra record sbagliati e corretti.

### 17.3 `statisticaltest.py`

Per ogni metrica (accuracy, F1, AUC) e ogni coppia di modelli: `wilcoxon(scores_a, scores_b)` e `ttest_rel(scores_a, scores_b)` sulle distribuzioni bootstrap. Poi `test_delong`: per ogni coppia `Delong_test(y_true, score_a, score_b)` sulle predizioni out-of-fold, dopo aver verificato che le etichette coincidano. `_benjamini_hochberg` aggiunge i p-value corretti. I flag di significatività sono salvati come stringhe `"1"`/`"0"`: va ricordato se si filtrano i CSV con altri strumenti.

### 17.4 `generatereport.py`

Assembla `reports/report.md`: obiettivo, modelli, tabella con intervalli, curve ROC, matrici di confusione, analisi degli errori, test statistici, holdout, discussione, conclusioni, miglioramenti. Discussione e conclusioni sono calcolate dai numeri della run (`_build_discussion`, `_build_conclusions`): migliore modello per metrica, intervallo più stretto, famiglia con AUC media più alta, numero di confronti DeLong significativi.

## Capitolo 18 — `inference.py` e i test automatici

### 18.1 Inferenza su un record

`predict_record(record, dataset, model_name=None)`:

1. sceglie il modello (default: AUC media più alta in `encoder_comparison_summary.csv`);
2. `_prepare_row` costruisce la riga, accettando valori assenti solo per i campi mancanti in almeno un record di training (letti da `X_train_raw.csv` con `keep_default_na=False, na_values=[""]`); altrimenti solleva `ValueError` con l'elenco dei campi;
3. genera la frase con la stessa `record_to_text_*` e la trasforma in vettore con lo stesso encoder;
4. `_fit_classifier` chiama `fit_classifier` (una volta per processo): standardizzazione, C scelto per CV, soglia out-of-fold;
5. restituisce frase, probabilità, soglia, predizione e campi lasciati ignoti.

### 18.2 Cosa coprono i test

| File | Test | Cosa verificano |
| --- | --- | --- |
| `test_preprocessing.py` | 4 | L'imputazione per i grafici usa solo il frame da cui è stimata e non modifica l'input |
| `test_embedding.py` | 5 | Traduzione dei codici, "not recorded" per ogni mancante, `None` resta categoria in Diabetes130, nuova etichetta di `thal` |
| `test_function.py` | 9 | Cartelle valide, dizionario `results` coerente con i modelli, soglia F1 valida anche su dati sbilanciati, Benjamini-Hochberg, pulizia di Diabetes130 su dati reali, invarianza del classificatore rispetto alla scala degli embedding |
| `test_inference.py` | 13 | Campi ammessi come ignoti, scelta del modello predefinito, rifiuto di campi obbligatori mancanti anche come NaN |

Non sono coperte le funzioni che richiedono Ollama, i modelli Hugging Face o una run completa: si verificano eseguendo la pipeline.

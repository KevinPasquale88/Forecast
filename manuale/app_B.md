# Appendice B — Riferimento completo delle funzioni pubbliche

> Firma, parametri, ritorno ed effetti collaterali per ogni funzione degli undici file di `master`. Le funzioni con prefisso underscore sono interne per convenzione (capitolo 10.3) ma elencate ugualmente per completezza. Nessuna annotazione di tipo compare nel codice originale (capitolo 7.2): i tipi indicati qui sono dedotti dalla lettura del corpo delle funzioni, non dichiarati dal codice.

## `main.py`
- `parse_args()` → `Namespace` con attributo `dataset` (str). Legge `sys.argv`.
- `main()` → `None`. Effetto: esegue l'intera pipeline per il dataset scelto (capitolo 28).

## `function.py`
- `get_output_dirs(dataset: str)` → `dict[str, str]`. Effetto: crea le cartelle se non esistono. Solleva `ValueError` se `dataset` non è valido.
- `load_heart_disease()` → `pd.DataFrame` (920 righe × 14 colonne).
- `load_diabetes130(sample_size=20000, random_state=42)` → `pd.DataFrame`.
- `save_figure(fig, path_no_ext: str)` → `None`. Effetto: salva `.png` e `.pdf`.
- `get_model_palette(model_names: list)` → `dict[str, tuple]` (colore RGB per modello).
- `optimal_f1_threshold(y_true, y_score)` → `float`. La soglia che massimizza F1 sui dati passati; condivisa da `classification.py` e `holdout_evaluation.py` (capitolo 23.2). Il chiamante non deve mai passarle le etichette su cui una metrica riportata verrà poi calcolata.
- `delete_files_embeddings/preprocessing/results/graphics(folder: str)` → `None`. Effetto: cancella file su disco per pattern di sottostringa (elenchi estesi dal fix per coprire ogni file della rispettiva fase, incluso l'output holdout).
- `plot_data_heatmap(X, num_cols=None, graphics_dir=...)` → `None`. Effetto: salva grafico.
- `plot_umap(X, y, title, graphics_dir=...)` → `None`. Effetto: salva grafico.
- `plot_boxplots(results_dict, results_dir=...)` → `None`. Effetto: salva grafico.
- `plot_roc_comparison(roc_data, filename="ROC_comparison", graphics_dir=...)` → `None`. Effetto: salva grafico.
- `plot_confusion(y_true, y_pred, name, graphics_dir=...)` → `None`. Effetto: salva grafico.
- `plot_metric_comparison(df_summary, results_dir=...)` → `None`. Effetto: salva grafico.
- `plot_mean_ci(df_summary, results_dir=...)` → `None`. Effetto: salva grafico.
- `plot_family_comparison(bootstrap_results, results_dir=...)` → `None`. Effetto: salva grafico.
- `plot_error_rates(df_error_summary, results_dir=...)` → `None`. Effetto: salva grafico.
- `plot_feature_deviation(df_deviation, results_dir=...)` → `None`. Effetto: salva grafico.
- `_configure_plot_style()` → `None`. Eseguita automaticamente all'import del modulo (capitolo 10.2).

## `preprocessing.py`
- `preprocessing_data(dataset="heart_disease")` → `(X_train_bal: pd.DataFrame, y_train_bal: pd.Series)`. Effetto: salva `.npy`/`.csv` (inclusi `X_test_raw.csv` e `y_test.npy`, il test set imputato con statistiche del solo training), genera 2 grafici.
- `columns_needing_missing_indicator(X, columns, threshold=0.30)` → `list[str]`. Nomi delle colonne oltre soglia di mancanza in `X`.
- `add_missing_indicators(X, columns)` → `pd.DataFrame` (copia con colonne `<col>_missing` 0/1).
- `fit_imputation_values(X, num_cols, cat_cols)` → `dict`. Valori di riempimento (mediana/moda) calcolati da `X` solo.
- `apply_imputation(X, fill_values)` → `pd.DataFrame` (copia con mancanti riempiti dai valori già calcolati).
- `impute_raw(X, num_cols, cat_cols)` → `pd.DataFrame` (fit-and-apply in un passo; copia, nessun side-effect sull'originale).
- `balance_classes(X, y, cat_cols)` → `(X_res, y_res)`.
- `build_encoder(X, y, num_cols, cat_cols)` → `ColumnTransformer` addestrato.
- `data_processed(X_train, y_train, preprocessor, num_cols, cat_cols)` → `pd.DataFrame` con colonna `target`.
- `save_data_processed(X_train_emb_df, preprocessing_dir)` → `None`. Effetto: salva 2 file `.npy`.

## `embedding.py`
- `embeddings(X, y, dataset="heart_disease", split="train")` → `None`. Effetto: genera e salva embedding per 7 modelli; con `split="test"` i file portano il suffisso `_test`.
- `record_to_text_heart_disease(row)` → `str`.
- `record_to_text_diabetes130(row)` → `str`.
- `_fmt_num/_fmt_cat/_fmt_bool/_fmt_raw(value, ...)` → `str`.
- `_masked(row, col, formatter)` → `str`. Restituisce "not recorded" se l'indicatore `<col>_missing` della riga vale 1, altrimenti applica `formatter` al valore (capitolo 22.1).
- `_split_filename(filename, split)` → `str`. Inserisce il suffisso `_<split>` prima dell'estensione, tranne per `split="train"`.
- `save_embeddings_to_npy(embeddings, filename)` / `save_labels_to_npy(labels, filename)` → `None`. Effetto: `np.save`.
- `generate_embeddings_batch(model_name, texts, batch_size=16, max_retries=5, retry_delay=2.0, inter_batch_delay=0.3)` → `list`. Solleva `RuntimeError` dopo `max_retries` fallimenti.
- `generate_embeddings_hf(texts, model_name)` → `np.ndarray`. Effetto: scarica un modello se non in cache.
- `process_model(model: dict, texts, labels, embeddings_dir, split="train")` → `None`. Effetto: salva embedding e etichette. Solleva `RuntimeError` con causa concatenata (`from e`).
- `generate_all_embeddings(texts, labels, embeddings_dir, max_workers=3, split="train")` → `None`. Effetto: orchestra 7 chiamate a `process_model` in un pool di thread.

## `classification.py`
- `training_classifier(dataset="heart_disease")` → `None`. Effetto: popola `function.results` (side-effect globale); salva `.npy`/`.csv` per 7 modelli; genera 1 grafico.

## `evaluation.py`
- `evaluate_results(dataset="heart_disease")` → `None`. Effetto: salva bootstrap `.npy`, CSV riassuntivo, 6 grafici.
- `bootstrap_metrics(y_true, y_score, y_pred, n_iter=10000, seed=42)` → `dict[str, np.ndarray]`.
- `ci(a, alpha=0.95)` → `(float, (float, float))`.

## `error_analysis.py`
- `analyze_errors(dataset="heart_disease")` → `None`. Effetto: salva `error_summary.csv`, `hardest_cases.csv`, `feature_deviation.csv`, 14 CSV di FP/FN, 2 grafici.

## `statisticaltest.py`
- `test_statistical_tests(dataset="heart_disease")` → `None`. Effetto: salva `wilcoxon_comparison.csv`, `ttest_comparison.csv` (con colonne `p_value_bh`/`significant_bh`); chiama `test_delong`.
- `test_delong(dirs: dict)` → `None`. Effetto: salva `delong_comparison.csv` (con colonne BH); stampa un avviso se le etichette vere di due modelli non coincidono.
- `_benjamini_hochberg(p_values)` → `np.ndarray`. P-value aggiustati per il false discovery rate, nello stesso ordine dell'input (capitolo 26.2bis).
- `_add_bh_columns(df)` → `pd.DataFrame`. Aggiunge `p_value_bh` e `significant_bh` a un DataFrame di confronti.

## `holdout_evaluation.py`
- `evaluate_holdout(dataset="heart_disease")` → `pd.DataFrame`. Effetto: salva `holdout_evaluation.csv` (accuracy/macro-F1/AUC per modello sul test set trattenuto). Solleva `FileNotFoundError` se il test set o i suoi embedding non esistono, con un messaggio che indica come generarli (capitolo 43).
- `_test_filename(train_filename)` → `str`. Nome del file di embedding di test corrispondente a quello di training.

## `generatereport.py`
- `generate_report(dataset="heart_disease")` → `None`. Effetto: salva `report.md`. Solleva `FileNotFoundError` se `encoder_comparison_summary.csv` non esiste.
- `load_summary(summary_path)` → `pd.DataFrame`. Solleva `FileNotFoundError` esplicito.
- `load_statistical_results(wilcoxon_path, ttest_path, delong_path)` → `dict[str, pd.DataFrame | None]`.
- `generate_markdown(summary, dirs)` → `str`. Include condizionalmente la sezione holdout; le sezioni Discussion/Conclusions sono calcolate dai dati della run (capitolo 27.3).
- `_build_discussion(summary)` → `str`. Osservazioni calcolate dal `summary` della run (migliore per metrica, IC più stretto, famiglia migliore in media).
- `_build_conclusions(summary, stat_results)` → `str`. Conclusioni calcolate dal `summary` e, se presente, dal conteggio dei confronti DeLong significativi.

## `inference.py`
> Undicesimo file di `master`, aggiunto dopo gli altri dieci (capitolo 2.2, capitolo 54.4, `docs/INFERENCE.md`). Non è una fase: nessuna delle sue funzioni è chiamata da `main.py`.
- `predict_record(record: dict, dataset="heart_disease", model_name=None)` → `dict` (`dataset`, `model`, `text`, `probability`, `threshold`, `prediction`, `missing_fields`). Effetto: nessuno su disco; fitta un classificatore in cache di processo. Solleva `ValueError` per un dataset/modello non valido o un campo obbligatorio mancante; `FileNotFoundError` se il run del dataset non è mai stato completato.
- `_missing_eligible_columns(dataset, dirs)` → `list[str]`. Nomi delle colonne `<col>_missing` lette dall'header di `X_train_raw.csv`.
- `_best_model_name(dataset, dirs)` → `str`. Il modello con l'AUC media più alta in `encoder_comparison_summary.csv`.
- `_model_config(model_name)` → `dict`. La voce di `models_all` corrispondente. Solleva `ValueError` se il nome non è configurato.
- `_prepare_row(record, dataset, dirs)` → `(pd.Series, list[str])`. Il record pronto per `record_to_text_*()`, più i nomi delle colonne effettivamente lasciate mancanti.
- `_fit_classifier(model, dataset, dirs)` → `(LogisticRegression, float)`. Classificatore e soglia, in cache per `(dataset, model_name)`.
- `_embed_one(text, model)` → `np.ndarray`. Un embedding, via Ollama o Hugging Face a seconda di `model["type"]`.

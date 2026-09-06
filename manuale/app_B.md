# Appendice B — Riferimento completo delle funzioni pubbliche

> Firma, parametri, ritorno ed effetti collaterali per ogni funzione dei nove file di `master`. Le funzioni con prefisso underscore sono interne per convenzione (capitolo 10.3) ma elencate ugualmente per completezza. Nessuna annotazione di tipo compare nel codice originale (capitolo 7.2): i tipi indicati qui sono dedotti dalla lettura del corpo delle funzioni, non dichiarati dal codice.

## `main.py`
- `parse_args()` → `Namespace` con attributo `dataset` (str). Legge `sys.argv`.
- `main()` → `None`. Effetto: esegue l'intera pipeline per il dataset scelto (capitolo 28).

## `function.py`
- `get_output_dirs(dataset: str)` → `dict[str, str]`. Effetto: crea le cartelle se non esistono. Solleva `ValueError` se `dataset` non è valido.
- `load_heart_disease()` → `pd.DataFrame` (920 righe × 14 colonne).
- `load_diabetes130(sample_size=20000, random_state=42)` → `pd.DataFrame`.
- `save_figure(fig, path_no_ext: str)` → `None`. Effetto: salva `.png` e `.pdf`.
- `get_model_palette(model_names: list)` → `dict[str, tuple]` (colore RGB per modello).
- `delete_files_embeddings/preprocessing/results/graphics(folder: str)` → `None`. Effetto: cancella file su disco per pattern di sottostringa.
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
- `preprocessing_data(dataset="heart_disease")` → `(X_train_bal: pd.DataFrame, y_train_bal: pd.Series)`. Effetto: salva `.npy`/`.csv`, genera 2 grafici.
- `impute_raw(X, num_cols, cat_cols)` → `pd.DataFrame` (copia, nessun side-effect sull'originale).
- `balance_classes(X, y, cat_cols)` → `(X_res, y_res)`.
- `build_encoder(X, y, num_cols, cat_cols)` → `ColumnTransformer` addestrato.
- `data_processed(X_train, y_train, preprocessor, num_cols, cat_cols)` → `pd.DataFrame` con colonna `target`.
- `save_data_processed(X_train_emb_df, preprocessing_dir)` → `None`. Effetto: salva 2 file `.npy`.

## `embedding.py`
- `embeddings(X, y, dataset="heart_disease")` → `None`. Effetto: genera e salva embedding per 7 modelli.
- `record_to_text_heart_disease(row)` → `str`.
- `record_to_text_diabetes130(row)` → `str`.
- `_fmt_num/_fmt_cat/_fmt_bool/_fmt_raw(value, ...)` → `str`.
- `save_embeddings_to_npy(embeddings, filename)` / `save_labels_to_npy(labels, filename)` → `None`. Effetto: `np.save`.
- `generate_embeddings_batch(model_name, texts, batch_size=16, max_retries=5, retry_delay=2.0, inter_batch_delay=0.3)` → `list`. Solleva `RuntimeError` dopo `max_retries` fallimenti.
- `generate_embeddings_hf(texts, model_name)` → `np.ndarray`. Effetto: scarica un modello se non in cache.
- `process_model(model: dict, texts, labels, embeddings_dir)` → `None`. Effetto: salva embedding e etichette. Solleva `RuntimeError` con causa concatenata (`from e`).
- `generate_all_embeddings(texts, labels, embeddings_dir, max_workers=3)` → `None`. Effetto: orchestra 7 chiamate a `process_model` in un pool di thread.

## `classification.py`
- `training_classifier(dataset="heart_disease")` → `None`. Effetto: popola `function.results` (side-effect globale); salva `.npy`/`.csv` per 7 modelli; genera 1 grafico.

## `evaluation.py`
- `evaluate_results(dataset="heart_disease")` → `None`. Effetto: salva bootstrap `.npy`, CSV riassuntivo, 6 grafici.
- `bootstrap_metrics(y_true, y_score, y_pred, n_iter=10000, seed=42)` → `dict[str, np.ndarray]`.
- `ci(a, alpha=0.95)` → `(float, (float, float))`.

## `error_analysis.py`
- `analyze_errors(dataset="heart_disease")` → `None`. Effetto: salva `error_summary.csv`, `hardest_cases.csv`, `feature_deviation.csv`, 14 CSV di FP/FN, 2 grafici.

## `statisticaltest.py`
- `test_statistical_tests(dataset="heart_disease")` → `None`. Effetto: salva `wilcoxon_comparison.csv`, `ttest_comparison.csv`; chiama `test_delong`.
- `test_delong(dirs: dict)` → `None`. Effetto: salva `delong_comparison.csv`; stampa un avviso se le etichette vere di due modelli non coincidono.

## `generatereport.py`
- `generate_report(dataset="heart_disease")` → `None`. Effetto: salva `report.md`. Solleva `FileNotFoundError` se `encoder_comparison_summary.csv` non esiste.
- `load_summary(summary_path)` → `pd.DataFrame`. Solleva `FileNotFoundError` esplicito.
- `load_statistical_results(wilcoxon_path, ttest_path, delong_path)` → `dict[str, pd.DataFrame | None]`.
- `generate_markdown(summary, dirs)` → `str`. Contiene testo narrativo statico (capitolo 27.2, 52) per le sezioni Discussion/Conclusions/Improvements.

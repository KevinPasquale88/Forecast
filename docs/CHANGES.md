# Methodological corrections

Corrections made to the pipeline before the final runs (November 2026), with their measured effect where there is one. Each one fixes something the pipeline was already trying to do; none adds a feature. The full code history is in git.

## Evaluation protocol

1. **No oversampling before cross-validation.** SMOTENC balanced the whole training split before the 5-fold CV. On Diabetes130, 87% of the positives were synthetic, interpolated from neighbours in other folds, so the CV measured how recognisable synthetic records were. Recomputed from that run (sentence-biobert): CV AUC 0.765 overall, 0.558 on real records only, 0.794 for real negatives against synthetic positives; held-out AUC 0.552 (0.48–0.55 for every encoder). Now there is no oversampling and class imbalance is handled by the decision threshold; held-out AUC is 0.61–0.62.
2. **The held-out test split is used.** It was computed and discarded. Every encoder is now measured once on it (`holdout_evaluation.py`).
3. **Threshold never chosen on the labels it is evaluated on.** It was chosen on the validation fold itself. Now it is F1-optimal on out-of-fold scores of an inner 5-fold CV over the training data (`function.out_of_fold_threshold`).
4. **Standardized embeddings and per-encoder regularization.** Every encoder was probed with `LogisticRegression(C=1)` on raw vectors. Ollama returns unit-norm vectors, sentence-transformers vectors of norm 11–13, so the same L2 penalty was far stronger for the general-purpose encoders. Now: `StandardScaler` + logistic regression, with C chosen per encoder in {0.001, …, 100} by inner 5-fold CV (`function.fit_classifier`). On Heart Disease the general-purpose vs biomedical gap went from 3.8 to 1.2 AUC points, and significant cross-family DeLong comparisons from 12/12 to 5/12. On Diabetes130 the gap went from 8.6 to 0.3 points: under the old protocol e5-base and gte-base scored below 0.5 (`embedding_scale.csv`, produced by phase 8).
5. **Multiple-comparison correction.** Benjamini-Hochberg adjusted p-values are reported next to the raw ones for every pairwise test.
6. **Metrics for imbalanced data.** PR-AUC and Brier score in CV and on the test split; precision, recall and prevalence on the test split.

## Data and text representation

7. **No imputed values in the text.** Missing values were imputed (median, mode) and written in the sentence as if observed. Now every missing value is written as `not recorded`; imputation is used only on a copy of the training split for the UMAP projection and the correlation heatmap.
8. **Diabetes130 cleaning.** `"None"` in `max_glu_serum`/`A1Cresult` ("test not performed") was read as missing and is now a category; encounters ending in death or hospice are removed; only the first encounter per patient is kept, so no patient is in both training and test; `"Unknown/Invalid"` gender is missing.
9. **No truncation.** sentence-biobert's default limit of 100 tokens cut `slope`, `ca` and `thal` from sentences of 116–137 tokens. The limit is now 512 for every encoder.
10. **`thal` label.** It is the thallium stress test, not thalassemia.

## Reporting

11. **The report's discussion is computed from the run's data** instead of fixed text (which claimed a best model that was not the best on either dataset).

## Pipeline structure

12. **Supplementary analyses are a pipeline phase.** The tabular baselines, the per-centre analysis and the embedding-scale sensitivity analysis were separate scripts run by hand. They are now phase 8 of `main.py` (`supplementary_analysis.py`), write CSVs to `datas/<dataset>/results/` and appear in the report. Their Heart Disease results are identical to those of the former scripts; the scale analysis now also runs on Diabetes130. `LogisticRegressionCV` sets `l1_ratios=(0,)` and `use_legacy_attributes=False`, which silences the scikit-learn 1.8 FutureWarnings without changing any result.

## Deliberately unchanged

- Datasets, feature selection, target definitions and the 20,000-record Diabetes130 sample.
- Logistic regression as the only classifier on the embeddings (linear probe).
- Wilcoxon and paired t-tests on the 10,000 bootstrap resamples are kept and reported in the thesis; read them next to the mean differences and the confidence intervals, with DeLong as the reference test for ROC-AUC (see [STATISTICAL_TESTS.md](STATISTICAL_TESTS.md)).

## Verification

Runs on 14, 21 (Heart Disease) and 22 (Diabetes130) November 2026 give identical results, including after the final code cleanup.

```bash
source env/bin/activate
python -m pytest -q
python main.py --dataset heart_disease
python main.py --dataset diabetes130
```

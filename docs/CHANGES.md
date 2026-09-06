# Changes — pipeline correctness and quality fixes

This branch (`fix/pipeline-quality`) fixes methodological and code-quality issues found while
writing an exhaustive technical manual for this project. None of these are new features: each
addresses something the pipeline was already trying to do, but doing incorrectly, inconsistently,
or not at all. `master` is untouched — nothing here has been merged.

## 1. The held-out test set is now actually used

**Before:** `preprocessing.py` computed an 80/20 `train_test_split`, then only ever used the 80%
training partition. `X_test`/`y_test` were calculated and discarded; no phase of the pipeline
ever touched them again.

**After:** `preprocessing_data()` imputes the test split with statistics fitted on the training
split only (never on the test split itself — see fix 2), and persists it
(`preprocessing/X_test_raw.csv`, `preprocessing/y_test.npy`). `main.py` generates embeddings for
this split too (under a `_test` filename suffix, so it never overwrites the training embeddings
used for cross-validation), and a new module, `holdout_evaluation.py`, fits a fresh classifier
per model on the training pool and reports accuracy/macro-F1/AUC on the test split alone — data
none of training, threshold selection, or the existing cross-validation ever saw.
`generatereport.py` includes these results as a new report section when present.

## 2. Imputation no longer risks leaking test-set statistics into itself

**Before:** `impute_raw(X, num_cols, cat_cols)` computed `X[col].median()`/`.mode()` from
whatever frame it was given. It was only ever called on the training split, so this was not a
live bug — but a test-set imputation added under fix 1 using the same function would have
computed its fill values from the test split itself, leaking test-set statistics into the very
values used to describe it.

**After:** `fit_imputation_values(X, num_cols, cat_cols)` computes fill values from one frame;
`apply_imputation(X, fill_values)` applies already-computed values to any frame. `impute_raw()`
is kept as a fit-and-apply convenience wrapper around the two, for any caller that only has one
frame to impute.

## 3. Values imputed for majority-missing columns are no longer indistinguishable from real ones

**Before:** `ca`/`thal` (Heart Disease) are missing in over 90% of three of its four source
centres; `max_glu_serum`/`A1Cresult` (Diabetes130) are missing in 95%/83% of the raw file (see
the manual, capitoli 29.3/30.2, for how these numbers were obtained). Imputing them with the
median/mode and then writing that value into the generated text made an imputed value read
identically to an observed one — concretely, this meant a large share of "hardest to classify"
records were actually SMOTENC-synthesized records carrying the imputed default profile, not
clinically complex cases (manual, capitolo 46.2).

**After:** any column missing in more than `MISSING_INDICATOR_THRESHOLD` (30%) of the training
split gets an explicit `<col>_missing` indicator column, added before imputation and carried
through SMOTENC as a categorical feature (so a synthetic record's indicator is itself derived
from its real neighbours, not fabricated independently). `embedding.py`'s `record_to_text_*()`
functions check this indicator via a new `_masked()` helper and report "not recorded" for a
flagged value, exactly like a genuinely missing one, instead of presenting a fabricated number or
category as observed. This is dataset-agnostic — it is a missingness-rate threshold, not a
hardcoded list of column names — so it applies unchanged to both datasets.

## 4. The decision threshold is no longer chosen on the same labels a fold's metrics are reported on

**Before:** `classification.py` chose the F1-optimal threshold using `precision_recall_curve(y_val,
y_score)` — the validation fold's own labels — then measured accuracy/F1 on predictions made with
that same threshold on that same fold. The classifier itself never saw `y_val` during fitting,
but the threshold did, before being judged against it: a mild, threshold-only form of optimism.

**After:** each fold's training partition is itself split 80/20 into a fit set and a calibration
set (`train_test_split(..., stratify=...)`). The classifier is fit on the 80%; the threshold is
chosen (via the new shared `function.optimal_f1_threshold()`) on the 20% calibration slice;
predictions on the validation fold use that threshold. The classifier now trains on slightly less
data per fold in exchange for a threshold that owes nothing to the fold it is evaluated on. The
same pattern (fit / calibrate / evaluate on three disjoint slices) is used in
`holdout_evaluation.py`.

## 5. `function.py`'s `results` dict could silently drift from the configured model list

**Before:** `results` was hand-initialized with 4 of the 7 configured models. The other 3 were
added by plain dict assignment in `classification.py` (which works — Python dicts create missing
keys on assignment — but meant the initial dict no longer matched `models_all` even by
coincidence).

**After:** `results = {m["model_name"]: {...} for m in models_all}` — built from the same list
that defines which models exist, so the two structures cannot drift apart. A regression test
(`tests/test_function.py::test_results_dict_has_exactly_one_entry_per_configured_model`) checks
this holds.

## 6. `plot_family_comparison()` no longer silently drops an unrecognized model family

**Before:** `family_order` was a hardcoded list of the three families known at the time. A model
belonging to a fourth family would still get a colour from `get_model_palette()` (fallback grey)
in the per-model plots, but would be excluded entirely — with no warning — from the family
comparison plot's `hue_order`, and therefore from the plot.

**After:** `family_order` is built from `FAMILY_COLORS` (for the canonical ordering) plus any
family actually present in the data but not yet in `FAMILY_COLORS` (appended, with the same grey
fallback colour `get_model_palette()` already uses) — so a new family shows up in this plot too,
instead of disappearing from it.

## 7. No correction for multiple comparisons

**Before:** `statisticaltest.py` ran 21 pairwise comparisons per metric (`C(7,2)` model pairs) for
three metrics, with no adjustment — with enough simultaneous tests, some p-values fall under 0.05
by chance alone.

**After:** a Benjamini-Hochberg adjustment (`_benjamini_hochberg()`) adds `p_value_bh` and
`significant_bh` columns to `wilcoxon_comparison.csv`, `ttest_comparison.csv`, and
`delong_comparison.csv`, alongside — not replacing — the original `p_value`/`significant`
columns, so both readings remain available.

## 8. The generated report's narrative sections were fixed text, not computed from the run's data

**Before:** the "Discussion and Observations", "Conclusions", and "Potential Improvements"
sections of `generatereport.py` were fixed strings, identical for every run regardless of
dataset or result. One of them ("GTE-large tends to achieve higher ROC-AUC") was contradicted by
the numbers in both real reports already on `master` — GTE-large did not have the highest AUC in
either the Heart Disease or the Diabetes130 run.

**After:** `_build_discussion(summary)` and `_build_conclusions(summary, stat_results)` compute
their bullet points from the actual `summary` DataFrame (and, where available, the DeLong test
results) of the run being reported — the best model per metric, the tightest confidence interval,
the best-performing family on average, and how many of the pairwise comparisons are actually
significant. "Potential Improvements" is left as forward-looking suggestions (not a factual claim
about the data) but updated to remove items this branch already addresses.

## 9. Cleanup functions missed some of their own files

**Before:** `delete_files_preprocessing()` matched only files containing `"preprocessed"` — never
`X_train_raw.csv`, which no run has ever cleaned up. `delete_files_results()` did not match
`wilcoxon_comparison.csv`, `ttest_comparison.csv`, or `delong_comparison.csv`.

**After:** both pattern lists cover every file their own phase writes, including the new
`X_test_raw.csv`, `y_test.npy`, and `holdout_evaluation.csv`.

## 10. Miscellaneous

- `README.md`: the `ollama pull` command for `e5-base` referenced `yxchia/multilingual-e5-base`,
  a different model from the one `function.py` actually requests
  (`jeffh/intfloat-e5-base-v2:q8_0`) — following the README as written would fail with a
  "model not found" error at the embedding phase. Corrected to the model the code actually uses.
- `preprocessing.py`: the local variable `datasetChoosen` (camelCase) is now `dataset_chosen`,
  consistent with the snake_case used everywhere else in this file.
- Added `pytest` (plus its own dependencies, `pluggy` and `iniconfig`) to `requirements.txt`, and
  `pytest.ini` (`pythonpath = .`) so the test suite resolves this project's flat, package-less
  imports the same way `main.py` does, regardless of the directory `pytest` is invoked from.

## What this branch deliberately does not change

- The two clinical datasets, their feature selection, and the definition of both prediction
  targets are unchanged: those are the project's research design, not a defect.
- Diabetes130's 20,000-row stratified sample is unchanged (still a real, dataset-agnostic
  parameter, not something "fixed" here).
- No non-linear classifier was added; `LogisticRegression` remains the only classifier, per the
  linear-probing framing the manual (capitolo 32.3, 53.1) already documents for this project.
- The embeddings/results already committed on `master` for both datasets are untouched by this
  branch — this branch's own run of the pipeline (see the commit that follows this file)
  regenerates `datas/` locally on `fix/pipeline-quality` only.

## How to verify

```bash
source env/bin/activate
python -m pytest -v                      # 22 unit tests, no network/Ollama required
python main.py --dataset heart_disease   # full pipeline, real Ollama + Hugging Face calls
```

`datas/heart_disease/results/holdout_evaluation.csv` and the new "Held-Out Test Set Evaluation"
section of `datas/heart_disease/reports/report.md` are the concrete, new output of fix 1.

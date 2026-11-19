# inference.py — single-record inference, on `master`, outside the pipeline

`main.py` orchestrates eight phases that all train and validate on already-labeled data:
preprocessing, embedding, cross-validation, bootstrap evaluation, error analysis, statistical
tests, holdout evaluation, and reporting. None of them produce a prediction for a case the
pipeline has never seen. `inference.py` adds that third leg — record in, prediction out — as a
standalone module, deliberately **not** called from `main.py` or wired into any of its eight
phases: it is a separate, on-demand utility that consumes their output, not a ninth phase.

This capability already existed, in a different shape, on the unmerged `chatbot` branch
(`chatbot_core.py`, wired into Telegram and Streamlit conversation flows). `inference.py`
brings the same idea to `master`, without the conversation layer, and fixes two things the
chatbot's version left inconsistent (see "Differences from the chatbot's approach" below).

## Usage

```python
from inference import predict_record

result = predict_record(
    {
        "age": 63, "sex": 1, "cp": 1, "trestbps": 145, "chol": 233, "fbs": 1,
        "restecg": 0, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 3,
        "ca": 0, "thal": 6,
    },
    dataset="heart_disease",
)
# {'dataset': 'heart_disease', 'model': 'pubmedbert', 'text': '...',
#  'probability': 0.709, 'threshold': 0.388, 'prediction': 1, 'missing_fields': []}
```

```bash
python inference.py --dataset heart_disease --record-file patient.json
python inference.py --dataset diabetes130 --record '{"race": "Caucasian", ...}'
```

A record is a plain dict of raw feature values, using the same field names as
`function.columns` / `function.columns_diabetes130` (minus the target column). It requires a
completed run of that dataset (`python main.py --dataset ...`) to have produced
`datas/<dataset>/embeddings/`, `datas/<dataset>/preprocessing/X_train_raw.csv`, and
`datas/<dataset>/results/encoder_comparison_summary.csv` — inference fits on the same saved
embeddings the pipeline already produced, it does not regenerate them.

## Design choices, and why

**No model is ever saved to disk.** Nothing in this project does — `classification.py`,
`holdout_evaluation.py`, and `chatbot_core.py` all refit a fresh `LogisticRegression` from the
saved training embeddings on every use rather than `joblib`-dumping a fitted estimator.
`inference.py` follows the same convention instead of introducing model serialization as a new
concept; a fitted classifier is cached in memory per `(dataset, model)` for the life of the
process, so repeated calls in one session only pay the fit cost once. That cache is never
invalidated — if a dataset's embeddings are regenerated (`python main.py --dataset ...`) in the
same long-running process, call `predict_record()` again from a fresh process to pick it up.

**The decision threshold is chosen without touching the classifier's own fit**, with the same
protocol as `classification.py`/`holdout_evaluation.py`: the F1-optimal threshold is picked on
out-of-fold scores of a 5-fold CV over the whole training pool (`function.out_of_fold_threshold()`),
then the classifier is fit on the whole training pool, and only then is the new record scored.

**A field may be left unset only if it was missing in training too.** The pipeline never imputes:
a missing training value is written as `"not recorded"` in the text. Which fields were ever
missing is read directly from `X_train_raw.csv` (empty cells), not hardcoded. For those fields the
classifier has learned what `"not recorded"` means; for every other field that sentence never
occurred during training, so a prediction would have no empirical basis, and inference refuses it.
On the current data this allows `trestbps`, `chol`, `fbs`, `thalach`, `exang`, `oldpeak`, `slope`,
`ca`, `thal` for Heart Disease, and only `race`/`gender` for Diabetes130.

**The default model is chosen empirically, per dataset.** `predict_record()` defaults to the
model with the highest mean AUC in `encoder_comparison_summary.csv` — the same number the
manual's results chapters (44-45) call "best" for the same reason. Today that is `pubmedbert`
for `heart_disease` and `sentence-biobert` for `diabetes130`, both biomedical, Hugging
Face-backed models — meaning a default call needs a cached/downloadable Hugging Face model, not
a running Ollama server. Pass `model_name` explicitly to use any of the other configured
models, including the four Ollama-backed generalist ones.

## Differences from the chatbot's approach

Two things the manual's critical analysis of `chatbot_core.py` (capitolo 54) flags as real,
if minor, issues are handled differently here:

1. **Threshold/classifier alignment.** The chatbot's `_load_deployed_bundle()` fits a fresh
   classifier on 100% of the training embeddings, but reuses the decision threshold from
   `model_performance.csv` — the mean of the five per-fold thresholds computed during
   cross-validation by *different* classifiers. `inference.py` derives the threshold for the
   classifier it actually uses (out-of-fold scores on the same training pool).
2. **Missing values.** `inference.py` accepts "unknown" only for fields that were missing in some
   training records, so `"not recorded"` is always text the model was trained on. (The later
   `chatbot-forecast` repository accepts "Non lo so" for every question, including the 17 of 19
   Diabetes130 fields that are never missing in training.)

What it does **not** add: a conversational interface, input validation prompts for a
non-technical end user, or any clinical validation of the resulting predictions. It is a
utility for the research pipeline's own use (demonstrating the full train → validate → infer
cycle, e.g. for a thesis discussion), not a deployable clinical tool — the same caveats the
manual raises for the chatbot (capitolo 54.3) apply here too, and more so: this module has no
disclaimers of its own and assumes whoever calls it already knows what the output does and
does not mean.

## Tests

`tests/test_inference.py` covers the pure logic — reading the missing-eligible columns (empty cells,
with Diabetes130's `None` category not counted as missing) from a fake `X_train_raw.csv`, picking the best model from a fake summary CSV, model-name lookup, and
every branch of the required/optional field validation, including the NaN-vs-`None` edge case
(`record_to_text_*()` writes any NaN as `"not recorded"`, so checking `value is None` alone would let a NaN on a *required* field slip
past validation unflagged — `pd.isna()` is used throughout instead). It does not cover
`_embed_one()` or `_fit_classifier()`, which need a running Ollama server / cached Hugging Face
model or real saved embeddings respectively — the same boundary `tests/test_embedding.py`
already draws around `embedding.py`'s own network-facing functions.

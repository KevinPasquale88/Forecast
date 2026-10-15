"""Single-record inference: apply the pipeline to one new, unlabeled clinical record.

`main.py` covers training and validation (cross-validation, bootstrap, statistical tests,
holdout evaluation) but never the third leg of the training -> validation -> inference cycle:
producing a prediction for a case the pipeline has never seen, outside of an already-labeled
evaluation split. That capability exists only on the unmerged `chatbot` branch
(`chatbot_core.py`), wired into a Telegram/Streamlit conversation flow. This module brings the
same idea to `master` as a small, reusable function plus a CLI, without the conversation layer
and, by design, without being wired into main.py's own pipeline: the eight orchestrated phases
train and validate; this is a separate, on-demand utility that consumes their output. See
docs/INFERENCE.md for the full rationale, usage examples, and how this compares to the
chatbot's approach.

No model is ever persisted to disk anywhere in this project — classification.py,
holdout_evaluation.py, and chatbot_core.py all refit a fresh LogisticRegression from the saved
training embeddings on every use, rather than joblib-dumping a fitted estimator. This module
follows the same convention rather than introducing model serialization as a new concept; a
fitted classifier is cached in memory per (dataset, model) for the life of the process, so
repeated calls to predict_record() in one session only pay the fit cost once. That cache is
never invalidated: if `python main.py` regenerates a dataset's embeddings in the same
long-running process, call predict_record() in a fresh process to pick it up.

Threshold selection mirrors the fix already applied to classification.py and
holdout_evaluation.py (see docs/CHANGES.md and manual capitolo 23.2): the classifier is fit on
80% of the full training-pool embeddings, the decision threshold is chosen with
function.optimal_f1_threshold() on the other 20%, and only then is the new record scored — the
threshold never sees the same data used to fit the classifier, and (trivially, since there is
only one new record) never sees the record being predicted either.

A record is a dict of raw feature values, using the same field names as function.columns /
function.columns_diabetes130 (minus the target column). A field may be omitted (or set to None
/ NaN) only for the columns the run that produced this dataset's saved embeddings itself
flagged as missing too often to impute honestly — read directly from that run's
X_train_raw.csv header (the "<col>_missing" columns preprocessing.py adds, capitolo 21.2), not
hardcoded here, so this never drifts out of sync with whichever columns actually crossed
MISSING_INDICATOR_THRESHOLD in that specific run. For those columns,
record_to_text_*()'s existing "not recorded" handling (capitolo 21.2/22.1 of the manual) is
reused as-is. Every other field is required — this project never persists the training-time
imputation statistics (fit_imputation_values() computes them fresh, in memory, once per run)
that would let a missing value on any other field be filled in without fabricating data, so
inference refuses to guess instead of doing that silently.

Usage:
    from inference import predict_record
    result = predict_record({"age": 63, "sex": 1, "cp": 1, ...}, dataset="heart_disease")

    python inference.py --dataset heart_disease --record-file patient.json
    python inference.py --dataset diabetes130 --record '{"race": "Caucasian", ...}'
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from embedding import (
    generate_embeddings_batch, generate_embeddings_hf,
    record_to_text_diabetes130, record_to_text_heart_disease,
)
from function import (
    columns, columns_diabetes130, get_output_dirs, models_all, optimal_f1_threshold,
)

RECORD_TO_TEXT = {
    "heart_disease": record_to_text_heart_disease,
    "diabetes130": record_to_text_diabetes130,
}

TARGET_COLUMN = {"heart_disease": "num", "diabetes130": "readmitted"}

_REQUIRED_FIELDS = {
    "heart_disease": [c for c in columns if c != TARGET_COLUMN["heart_disease"]],
    "diabetes130": [c for c in columns_diabetes130 if c != TARGET_COLUMN["diabetes130"]],
}

_classifier_cache = {}
_missing_eligible_cache = {}


def _missing_eligible_columns(dataset, dirs):
    """Which columns got a "<col>_missing" indicator in the run that produced this dataset's
    saved training embeddings — read from X_train_raw.csv's own header (preprocessing.py,
    capitolo 21.2), not hardcoded, so this can never silently drift out of sync with a rerun
    that used a different MISSING_INDICATOR_THRESHOLD, sample, or dataset revision."""
    if dataset in _missing_eligible_cache:
        return _missing_eligible_cache[dataset]

    raw_path = os.path.join(dirs["preprocessing"], "X_train_raw.csv")
    if not os.path.exists(raw_path):
        raise FileNotFoundError(
            f"{raw_path} not found: run `python main.py --dataset {dataset}` first "
            "(inference reads which columns got a missing-value indicator from this file)."
        )
    header = pd.read_csv(raw_path, nrows=0).columns
    eligible = [c[: -len("_missing")] for c in header if c.endswith("_missing")]
    _missing_eligible_cache[dataset] = eligible
    return eligible


def _best_model_name(dataset, dirs):
    """The model with the highest mean AUC in this dataset's own bootstrap summary
    (encoder_comparison_summary.csv, evaluation.py) — the same number the manual's results
    chapters (44-45) call "best" for the same reason."""
    summary_path = os.path.join(dirs["results"], "encoder_comparison_summary.csv")
    if not os.path.exists(summary_path):
        raise FileNotFoundError(
            f"{summary_path} not found: run `python main.py --dataset {dataset}` first "
            "(inference needs a completed run to pick a default model and to fit on)."
        )
    summary = pd.read_csv(summary_path)
    return summary.loc[summary["auc_mean"].idxmax(), "model"]


def _model_config(model_name):
    for m in models_all:
        if m["model_name"] == model_name:
            return m
    raise ValueError(
        f"Unknown model_name '{model_name}'. Configured models: "
        f"{[m['model_name'] for m in models_all]}"
    )


def _prepare_row(record, dataset, dirs):
    """Build the pandas Series record_to_text_*() expects: the raw values the caller supplied,
    plus a "<col>_missing" flag for every column eligible for it (1 for a value the caller left
    unset or gave as None/NaN, 0 otherwise). Missingness is checked with pd.isna() rather than
    `is None`, so a caller passing float('nan') on a *required* field cannot silently slip past
    this check and reach record_to_text_*() as an unflagged NaN — its own "not recorded"
    fallback for a stray NaN (a safety net that should never fire once a value is imputed,
    capitolo 31.3) would otherwise mask exactly the fabrication this function exists to
    prevent."""
    eligible = _missing_eligible_columns(dataset, dirs)
    row = dict(record)
    missing_used = []
    for col in eligible:
        if pd.isna(row.get(col)):
            row[col] = np.nan
            row[f"{col}_missing"] = 1
            missing_used.append(col)
        else:
            row[f"{col}_missing"] = 0

    absent = [c for c in _REQUIRED_FIELDS[dataset] if c not in eligible and pd.isna(row.get(c))]
    if absent:
        raise ValueError(
            f"Missing required field(s) for dataset '{dataset}': {absent}. Only "
            f"{eligible} may be left unset (they become \"not recorded\", exactly how the "
            "trained model was taught to read a value that was never measured); every other "
            "field must be supplied, because this project does not persist the training-time "
            "imputation statistics that would let it be filled in without fabricating data."
        )
    return pd.Series(row), missing_used


def _fit_classifier(model, dataset, dirs):
    cache_key = (dataset, model["model_name"])
    if cache_key in _classifier_cache:
        return _classifier_cache[cache_key]

    X = np.load(os.path.join(dirs["embeddings"], model["filename"]), allow_pickle=True)
    y = np.load(os.path.join(dirs["embeddings"], model["filename_label"]), allow_pickle=True)
    X_fit, X_calib, y_fit, y_calib = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    classifier = LogisticRegression(max_iter=2000)
    classifier.fit(X_fit, y_fit)
    calib_score = classifier.predict_proba(X_calib)[:, 1]
    tau = optimal_f1_threshold(y_calib, calib_score)

    _classifier_cache[cache_key] = (classifier, tau)
    return classifier, tau


def _embed_one(text, model):
    if model["type"] == "ollama":
        return np.asarray(generate_embeddings_batch(model["name"], [text], batch_size=1)[0])
    if model["type"] == "huggingface":
        return np.asarray(generate_embeddings_hf([text], model["name"])[0])
    raise ValueError(f"Unknown model type '{model['type']}' for model '{model['model_name']}'")


def predict_record(record, dataset="heart_disease", model_name=None):
    """Predict the target for one new, unlabeled clinical record.

    record: dict of raw feature values (see function.columns / columns_diabetes130 for the
        exact field names). A column this dataset's saved run flagged as missing too often to
        impute honestly may be omitted or set to None/NaN; every other field is required (see
        module docstring for why).
    dataset: "heart_disease" (default) or "diabetes130".
    model_name: one of the 7 configured model_name values in function.models_all. Defaults to
        the model with the highest mean AUC for this dataset (encoder_comparison_summary.csv).

    Returns a dict: dataset, model, text (the generated sentence actually embedded),
    probability, threshold, prediction (0/1), missing_fields (the eligible columns actually
    left unset for this call).
    """
    dirs = get_output_dirs(dataset)  # raises ValueError for an unknown dataset
    if model_name is None:
        model_name = _best_model_name(dataset, dirs)
    model = _model_config(model_name)

    row, missing_used = _prepare_row(record, dataset, dirs)
    text = RECORD_TO_TEXT[dataset](row)
    embedding = _embed_one(text, model)

    classifier, tau = _fit_classifier(model, dataset, dirs)
    probability = float(classifier.predict_proba([embedding])[0, 1])
    prediction = int(probability >= tau)

    return {
        "dataset": dataset,
        "model": model_name,
        "text": text,
        "probability": probability,
        "threshold": tau,
        "prediction": prediction,
        "missing_fields": missing_used,
    }


def _cli():
    parser = argparse.ArgumentParser(
        description="Run inference on one new clinical record, using an already-completed "
                     "run of main.py for that dataset."
    )
    parser.add_argument(
        "--dataset", choices=["heart_disease", "diabetes130"], default="heart_disease",
        help="Clinical dataset whose trained embeddings to use (default: heart_disease)."
    )
    parser.add_argument(
        "--model", default=None,
        help="Embedding model to use (default: the model with the highest mean AUC for this "
             "dataset)."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--record-file", help="Path to a JSON file with the record fields.")
    group.add_argument("--record", help="Inline JSON string with the record fields.")
    args = parser.parse_args()

    if args.record_file:
        with open(args.record_file, encoding="utf-8") as f:
            record = json.load(f)
    else:
        record = json.loads(args.record)

    result = predict_record(record, dataset=args.dataset, model_name=args.model)

    print(f"Model used: {result['model']}")
    print(f"Generated text: {result['text']}")
    if result["missing_fields"]:
        print(f"Fields marked as not recorded: {result['missing_fields']}")
    print(f"Predicted probability: {result['probability']:.4f}")
    print(f"Decision threshold: {result['threshold']:.4f}")
    label = "positive" if result["prediction"] else "negative"
    print(f"Prediction: {label} ({result['prediction']})")


if __name__ == "__main__":
    _cli()

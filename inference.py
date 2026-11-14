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

No model is ever persisted to disk anywhere in this project — classification.py and
holdout_evaluation.py refit a fresh LogisticRegression from the saved training embeddings on
every use. This module follows the same convention; a fitted classifier is cached in memory per
(dataset, model) for the life of the process. That cache is never invalidated: if
`python main.py` regenerates a dataset's embeddings, call predict_record() from a fresh process.

The classifier and its threshold follow the same protocol as holdout_evaluation.py
(function.fit_classifier): standardized embeddings, C chosen by inner CV, threshold chosen on
out-of-fold scores of a 5-fold CV over the whole training pool, classifier fit on all of it.

A record is a dict of raw feature values, using the same field names as function.columns /
function.columns_diabetes130 (minus the target column). The pipeline never imputes: a missing
training value is written as "not recorded" in the text. A field may therefore be omitted (or
set to None / NaN) only if that same field was actually missing in at least one training record
of this dataset's saved run — read from X_train_raw.csv, not hardcoded. For any other field,
"not recorded" is a sentence the classifier has never seen during training, so its output would
have no empirical basis: those fields are required.

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

from embedding import (
    generate_embeddings_batch, generate_embeddings_hf,
    record_to_text_diabetes130, record_to_text_heart_disease,
)
from function import (
    columns, columns_diabetes130, fit_classifier, get_output_dirs, models_all,
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
    """Columns that are missing in at least one record of the training split this dataset's
    saved embeddings were generated from (X_train_raw.csv, written by preprocessing.py with
    missing values as empty cells). Only for these has the classifier seen "not recorded"."""
    if dataset in _missing_eligible_cache:
        return _missing_eligible_cache[dataset]

    raw_path = os.path.join(dirs["preprocessing"], "X_train_raw.csv")
    if not os.path.exists(raw_path):
        raise FileNotFoundError(
            f"{raw_path} not found: run `python main.py --dataset {dataset}` first "
            "(inference reads which fields were ever missing in training from this file)."
        )
    # keep_default_na=False + na_values=[""]: only an empty cell is missing. Diabetes130's
    # "None" ("test not performed") is a category, not a missing value.
    X_raw = pd.read_csv(raw_path, keep_default_na=False, na_values=[""])
    eligible = [c for c in X_raw.columns if X_raw[c].isna().any()]
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
    """Build the pandas Series record_to_text_*() expects from the caller's raw values. A value
    left unset (absent, None or NaN — checked with pd.isna(), so a float NaN cannot slip past) is
    accepted only for fields that were missing in training too, and becomes "not recorded"."""
    eligible = _missing_eligible_columns(dataset, dirs)
    row = {c: record.get(c, np.nan) for c in _REQUIRED_FIELDS[dataset]}
    unset = [c for c, v in row.items() if pd.isna(v)]
    for col in unset:
        row[col] = np.nan

    absent = [c for c in unset if c not in eligible]
    if absent:
        raise ValueError(
            f"Missing required field(s) for dataset '{dataset}': {absent}. Only {eligible} may "
            "be left unset: they were missing in some training records too, so the classifier "
            "has learned what \"not recorded\" means for them. For any other field it never saw "
            "that text, and a prediction would have no empirical basis."
        )
    missing_used = [c for c in unset if c in eligible]
    return pd.Series(row), missing_used


def _fit_classifier(model, dataset, dirs):
    cache_key = (dataset, model["model_name"])
    if cache_key in _classifier_cache:
        return _classifier_cache[cache_key]

    X = np.load(os.path.join(dirs["embeddings"], model["filename"]), allow_pickle=True)
    y = np.load(os.path.join(dirs["embeddings"], model["filename_label"]), allow_pickle=True)
    classifier, tau, _ = fit_classifier(X, y)

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
        exact field names). A field that was missing in some training record may be omitted or
        set to None/NaN; every other field is required (see module docstring for why).
    dataset: "heart_disease" (default) or "diabetes130".
    model_name: one of the 7 configured model_name values in function.models_all. Defaults to
        the model with the highest mean AUC for this dataset (encoder_comparison_summary.csv).

    Returns a dict: dataset, model, text (the generated sentence actually embedded),
    probability, threshold, prediction (0/1), missing_fields (the fields left unset for this
    call, written as "not recorded").
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

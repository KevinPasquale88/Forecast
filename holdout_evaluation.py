"""Evaluate each embedding model on a held-out test set that plays no part in training,
threshold selection, or the model-vs-model comparison of classification.py/statisticaltest.py.

The test split keeps the real class distribution (no oversampling anywhere in the pipeline).
For each model:

1. The regularization C is chosen by inner CV, the decision threshold on out-of-fold scores of a
   5-fold CV over the whole training pool, both with standardized embeddings
   (function.fit_classifier).
2. The classifier (StandardScaler + LogisticRegression) is fit on the whole training pool.
3. Accuracy, macro-F1, ROC-AUC, PR-AUC, precision, recall and Brier score are computed once, on
   the test-set embeddings alone.

Every number this module reports comes from data the fitting and thresholding steps never saw.
"""
import os

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, average_precision_score, brier_score_loss, f1_score, precision_score,
    recall_score, roc_auc_score,
)

from function import models_all, get_output_dirs, fit_classifier


def _test_filename(train_filename):
    stem, ext = os.path.splitext(train_filename)
    return f"{stem}_test{ext}"


def evaluate_holdout(dataset="heart_disease"):
    dirs = get_output_dirs(dataset)
    y_test_path = os.path.join(dirs["preprocessing"], "y_test.npy")
    if not os.path.exists(y_test_path):
        raise FileNotFoundError(
            f"{y_test_path} not found: run preprocessing_data(dataset='{dataset}') first "
            "(it persists the held-out test split), then generate its embeddings with "
            "embeddings(X_test, y_test, dataset=dataset, split='test') before calling this."
        )
    y_test = np.load(y_test_path)

    rows = []
    for model in models_all:
        name = model["model_name"]
        print(f"\n=== Holdout evaluation: {name} ===")

        X_train_full = np.load(os.path.join(dirs["embeddings"], model["filename"]), allow_pickle=True)
        y_train_full = np.load(os.path.join(dirs["embeddings"], model["filename_label"]), allow_pickle=True)
        test_emb_path = os.path.join(dirs["embeddings"], _test_filename(model["filename"]))
        if not os.path.exists(test_emb_path):
            raise FileNotFoundError(
                f"{test_emb_path} not found: generate test-split embeddings for '{name}' first "
                f"(embeddings(X_test, y_test, dataset='{dataset}', split='test'))."
            )
        X_test = np.load(test_emb_path, allow_pickle=True)

        classifier, tau, C = fit_classifier(X_train_full, y_train_full)

        y_score = classifier.predict_proba(X_test)[:, 1]
        y_pred = (y_score >= tau).astype(int)

        row = {
            "model": name,
            "n_test": len(y_test),
            "accuracy": accuracy_score(y_test, y_pred),
            "macro_f1": f1_score(y_test, y_pred, average="macro"),
            "auc": roc_auc_score(y_test, y_score),
            "pr_auc": average_precision_score(y_test, y_score),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred),
            "brier": brier_score_loss(y_test, y_score),
            "prevalence": float(np.mean(y_test)),
            "threshold": tau,
            "C": C,
        }
        rows.append(row)
        print(f"Accuracy: {row['accuracy']:.4f}  Macro-F1: {row['macro_f1']:.4f}  "
              f"AUC: {row['auc']:.4f}  PR-AUC: {row['pr_auc']:.4f}  (n={row['n_test']}, tau={tau:.4f})")

    df = pd.DataFrame(rows)
    out_path = os.path.join(dirs["results"], "holdout_evaluation.csv")
    df.to_csv(out_path, index=False)
    print(f"\n[OK] Saved held-out test set evaluation -> {out_path}")
    return df

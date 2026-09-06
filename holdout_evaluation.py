"""Evaluate each embedding model on a held-out test set that plays no part in training,
threshold selection, or the model-vs-model comparison of classification.py/statisticaltest.py.

This is the counterpart to the 5-fold cross-validation in classification.py: that loop estimates
generalization by rotating which slice of the (SMOTE-balanced) training pool is held back each
time, but the 20% split computed once in preprocessing.py was, before this module existed,
calculated and then never used for anything (see docs/CHANGES.md). Here, for each model:

1. A fresh LogisticRegression is fit on 80% of the full training-pool embeddings.
2. The decision threshold is chosen on the other 20% (a calibration slice, never the test set).
3. Accuracy, macro-F1 and AUC are computed once, on the test-set embeddings alone.

Every number this module reports comes from data the fitting and thresholding steps never saw.
"""
import os

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

from function import models_all, get_output_dirs, optimal_f1_threshold


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

        # Same calibration-split idea as classification.py: fit on 80%, choose tau on the other
        # 20%, so the threshold owes nothing to the test labels evaluated below.
        X_fit, X_calib, y_fit, y_calib = train_test_split(
            X_train_full, y_train_full, test_size=0.2, random_state=42, stratify=y_train_full
        )
        classifier = LogisticRegression(max_iter=2000)
        classifier.fit(X_fit, y_fit)

        calib_score = classifier.predict_proba(X_calib)[:, 1]
        tau = optimal_f1_threshold(y_calib, calib_score)

        y_score = classifier.predict_proba(X_test)[:, 1]
        y_pred = (y_score >= tau).astype(int)

        row = {
            "model": name,
            "n_test": len(y_test),
            "accuracy": accuracy_score(y_test, y_pred),
            "macro_f1": f1_score(y_test, y_pred, average="macro"),
            "auc": roc_auc_score(y_test, y_score),
            "threshold": tau,
        }
        rows.append(row)
        print(f"Accuracy: {row['accuracy']:.4f}  Macro-F1: {row['macro_f1']:.4f}  "
              f"AUC: {row['auc']:.4f}  (n={row['n_test']}, tau={tau:.4f})")

    df = pd.DataFrame(rows)
    out_path = os.path.join(dirs["results"], "holdout_evaluation.csv")
    df.to_csv(out_path, index=False)
    print(f"\n[OK] Saved held-out test set evaluation -> {out_path}")
    return df

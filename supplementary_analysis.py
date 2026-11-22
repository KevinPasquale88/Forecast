"""Supplementary analyses (phase 8 of main.py).

1. Tabular baselines: logistic regression and gradient boosting on the ORIGINAL columns, same
   80/20 split, same 5-fold CV and same out-of-fold F1 threshold protocol as the encoders.
   They tell whether converting records to text keeps, adds or loses information.
2. Heart Disease only (the only multi-centre dataset):
   - out-of-fold ROC-AUC of every encoder computed inside each source centre;
   - ROC-AUC of two non-clinical predictors: the centre's prevalence alone, and a model that only
     sees WHICH fields are missing. They measure how much of the signal is not clinical.
3. Embedding-scale sensitivity: out-of-fold ROC-AUC of every encoder under four probing
   protocols (raw vectors with C=1, standardized with C=1, unit-normalized with C=1, standardized
   with C chosen by inner CV), plus DeLong tests between encoders under the last one. Ollama
   returns unit-norm vectors and sentence-transformers vectors of norm 11-13, so without
   standardization one fixed C penalizes the two families very differently.

Outputs in datas/<dataset>/results/: tabular_baselines.csv, embedding_scale.csv,
embedding_scale_delong.csv and, for Heart Disease, centre_analysis.csv and non_clinical_signal.csv.
"""
import os
from itertools import combinations

import numpy as np
import pandas as pd
from MLstatkit import Delong_test
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer, OneHotEncoder, StandardScaler

from function import (
    cat_cols, cat_cols_diabetes130, columns, get_output_dirs, load_diabetes130,
    load_heart_disease, models_all, num_cols, num_cols_diabetes130, optimal_f1_threshold,
)
from statisticaltest import _benjamini_hochberg

HEART_CENTRE_FILES = {
    "Cleveland": "processed.cleveland.data",
    "Hungary": "processed.hungarian.data",
    "Switzerland": "processed.switzerland.data",
    "Long Beach VA": "processed.va.data",
}


def run_supplementary_analyses(dataset="heart_disease"):
    dirs = get_output_dirs(dataset)
    tabular_baselines(dataset, dirs)
    if dataset == "heart_disease":
        centre_analysis(dirs)
    embedding_scale(dirs)
    print("Supplementary analyses completed and saved.")


# ---------------------------------------------------------------- 1. tabular baselines
def _split(df, target):
    """Same split as preprocessing.preprocessing_data (stratified 80/20, seed 42)."""
    X = df.drop(target, axis=1)
    y = (df[target] > 0).astype(int)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    return (X_tr.reset_index(drop=True), X_te.reset_index(drop=True),
            y_tr.to_numpy(), y_te.to_numpy())


def _logreg(num, cat):
    num_pipe = make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler())
    cat_pipe = make_pipeline(
        SimpleImputer(strategy="constant", fill_value="missing"),
        OneHotEncoder(handle_unknown="ignore"),
    )
    pre = ColumnTransformer([("num", num_pipe, num), ("cat", cat_pipe, cat)])
    return lambda: make_pipeline(pre, LogisticRegression(max_iter=5000))


def _hgb(num, cat):
    def make():
        return HistGradientBoostingClassifier(
            categorical_features=[c in cat for c in num + cat], random_state=42
        )
    return make


def _as_category_codes(X, cat):
    X = X.copy()
    for c in cat:
        X[c] = X[c].astype("category").cat.codes.replace(-1, np.nan)
    return X


def _oof_threshold(make_model, X, y):
    inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = np.zeros(len(y))
    for tr, va in inner.split(X, y):
        m = make_model().fit(X.iloc[tr], y[tr])
        scores[va] = m.predict_proba(X.iloc[va])[:, 1]
    return optimal_f1_threshold(y, scores)


def _evaluate_tabular(make_model, X_train, y_train, X_test, y_test):
    kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    aucs, praucs = [], []
    for tr, va in kf.split(X_train, y_train):
        m = make_model().fit(X_train.iloc[tr], y_train[tr])
        s = m.predict_proba(X_train.iloc[va])[:, 1]
        aucs.append(roc_auc_score(y_train[va], s))
        praucs.append(average_precision_score(y_train[va], s))
    tau = _oof_threshold(make_model, X_train, y_train)
    m = make_model().fit(X_train, y_train)
    s = m.predict_proba(X_test)[:, 1]
    p = (s >= tau).astype(int)
    tp = int(((p == 1) & (y_test == 1)).sum())
    return {
        "cv_auc": float(np.mean(aucs)), "cv_auc_std": float(np.std(aucs)),
        "cv_pr_auc": float(np.mean(praucs)),
        "test_auc": float(roc_auc_score(y_test, s)),
        "test_pr_auc": float(average_precision_score(y_test, s)),
        "test_brier": float(brier_score_loss(y_test, s)),
        "test_precision": tp / max(int(p.sum()), 1),
        "test_recall": tp / max(int(y_test.sum()), 1),
        "threshold": float(tau),
    }


def tabular_baselines(dataset, dirs):
    if dataset == "diabetes130":
        df, target, num, cat = load_diabetes130(), "readmitted", num_cols_diabetes130, cat_cols_diabetes130
    else:
        df, target, num, cat = load_heart_disease(), "num", num_cols, cat_cols
    X_tr, X_te, y_tr, y_te = _split(df, target)

    # categorical columns as strings: a missing value becomes the category "nan" ("missing")
    def as_str(X):
        return X.assign(**{c: X[c].astype(str) for c in cat})

    rows = [
        {"model": "logistic_regression",
         **_evaluate_tabular(_logreg(num, cat), as_str(X_tr), y_tr, as_str(X_te), y_te)},
        {"model": "gradient_boosting",
         **_evaluate_tabular(_hgb(num, cat), _as_category_codes(X_tr[num + cat], cat), y_tr,
                             _as_category_codes(X_te[num + cat], cat), y_te)},
    ]
    df_out = pd.DataFrame(rows)
    df_out.to_csv(os.path.join(dirs["results"], "tabular_baselines.csv"), index=False)
    print("\n=== Tabular baselines ===")
    print(df_out[["model", "cv_auc", "test_auc"]].to_string(index=False))


# ---------------------------------------------------------------- 2. centres (Heart Disease)
def _heart_with_centre():
    centres = []
    for name, f in HEART_CENTRE_FILES.items():
        n = len(pd.read_csv(os.path.join("datasets/heart+disease", f), header=None))
        centres += [name] * n
    df = load_heart_disease()
    df["centre"] = centres
    return df


def centre_analysis(dirs):
    df = _heart_with_centre()
    X = df.drop("num", axis=1)
    y = (df["num"] > 0).astype(int)
    X_tr, _, y_tr, _ = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    X_tr = X_tr.reset_index(drop=True)
    saved = pd.read_csv(os.path.join(dirs["preprocessing"], "X_train_raw.csv"))
    if not np.allclose(saved["age"].to_numpy(), X_tr["age"].to_numpy()):
        raise RuntimeError("Training split not aligned with preprocessing/X_train_raw.csv")
    centre = X_tr["centre"].to_numpy()
    y_tr = y_tr.to_numpy()

    # out-of-fold AUC of every encoder inside each centre
    rows = []
    for c in HEART_CENTRE_FILES:
        mask = centre == c
        row = {"centre": c, "n_train": int(mask.sum()), "prevalence_train": float(y_tr[mask].mean())}
        for m in models_all:
            r = os.path.join(dirs["results"], m["model_name"])
            yt, ys, vi = np.load(r + "_y_true.npy"), np.load(r + "_y_score.npy"), np.load(r + "_val_idx.npy")
            sel = centre[vi] == c
            row[m["model_name"]] = float(roc_auc_score(yt[sel], ys[sel])) if len(set(yt[sel])) == 2 else np.nan
        rows.append(row)
    pd.DataFrame(rows).to_csv(os.path.join(dirs["results"], "centre_analysis.csv"), index=False)

    # non-clinical predictors, scored out-of-fold with the same 5 folds
    kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    centre_scores = np.zeros(len(y_tr))
    miss_scores = np.zeros(len(y_tr))
    miss = X_tr[[c for c in columns if c != "num"]].isna().astype(int)
    for tr, va in kf.split(X_tr, y_tr):
        prev = pd.Series(y_tr[tr]).groupby(centre[tr]).mean()
        centre_scores[va] = pd.Series(centre[va]).map(prev).to_numpy()
        lr = LogisticRegression(max_iter=2000).fit(miss.iloc[tr], y_tr[tr])
        miss_scores[va] = lr.predict_proba(miss.iloc[va])[:, 1]
    signal = pd.DataFrame([
        {"predictor": "centre_prevalence_only", "auc": float(roc_auc_score(y_tr, centre_scores))},
        {"predictor": "missingness_indicators_only", "auc": float(roc_auc_score(y_tr, miss_scores))},
    ])
    signal.to_csv(os.path.join(dirs["results"], "non_clinical_signal.csv"), index=False)
    print("\n=== Centre analysis (Heart Disease) ===")
    print(pd.DataFrame(rows)[["centre", "n_train", "prevalence_train"]].to_string(index=False))
    print(signal.to_string(index=False))


# ---------------------------------------------------------------- 3. embedding scale
SCALE_VARIANTS = {
    "raw_C1": lambda: LogisticRegression(max_iter=5000),
    "standardized_C1": lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000)),
    "unit_norm_C1": lambda: make_pipeline(Normalizer(), LogisticRegression(max_iter=5000)),
    "standardized_Ccv": lambda: make_pipeline(
        StandardScaler(),
        LogisticRegressionCV(
            Cs=np.logspace(-3, 2, 11), cv=5, scoring="roc_auc", max_iter=5000, n_jobs=-1,
            l1_ratios=(0,), use_legacy_attributes=False,
        ),
    ),
}


def _oof_scores(make, X, y):
    """Out-of-fold probabilities with the same 5 outer folds as classification.py."""
    kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    s = np.zeros(len(y))
    fitted = []
    for tr, va in kf.split(X, y):
        model = make().fit(X[tr], y[tr])
        s[va] = model.predict_proba(X[va])[:, 1]
        fitted.append(model)
    return s, fitted


def embedding_scale(dirs):
    rows, cv_scores = [], {}
    y = None
    for m in models_all:
        X = np.load(os.path.join(dirs["embeddings"], m["filename"]))
        y = np.load(os.path.join(dirs["embeddings"], m["filename_label"]))
        row = {"model": m["model_name"], "family": m["family"]}
        for name, make in SCALE_VARIANTS.items():
            s, fitted = _oof_scores(make, X, y)
            row[name] = float(roc_auc_score(y, s))
            if name == "standardized_Ccv":
                cv_scores[m["model_name"]] = s
                row["C_per_fold"] = " ".join(f"{model[-1].C_:g}" for model in fitted)
        rows.append(row)
        print(f"{m['model_name']}: " + ", ".join(f"{k}={row[k]:.3f}" for k in SCALE_VARIANTS))
    pd.DataFrame(rows).to_csv(os.path.join(dirs["results"], "embedding_scale.csv"), index=False)

    # DeLong between encoders under the fair protocol (standardized, C chosen by inner CV)
    delong = []
    for a, b in combinations(cv_scores, 2):
        z, p = Delong_test(y, cv_scores[a], cv_scores[b])[:2]
        auc_a, auc_b = roc_auc_score(y, cv_scores[a]), roc_auc_score(y, cv_scores[b])
        delong.append({"model_a": a, "model_b": b, "auc_a": float(auc_a), "auc_b": float(auc_b),
                       "delta_auc": float(auc_a - auc_b), "p_value": float(p)})
    df_delong = pd.DataFrame(delong)
    df_delong["p_value_bh"] = _benjamini_hochberg(df_delong["p_value"].values)
    df_delong["significant_bh"] = (df_delong["p_value_bh"] < 0.05).astype(int)
    df_delong.to_csv(os.path.join(dirs["results"], "embedding_scale_delong.csv"), index=False)

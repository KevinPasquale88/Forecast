"""Analisi aggiuntive per il manuale v2 (eseguire dalla radice del progetto):

    env/bin/python manuale_v2/analisi/analisi_aggiuntive.py

1. Baseline tabellari sugli stessi split della pipeline (80/20 stratificato, random_state=42),
   con lo stesso protocollo di soglia (out_of_fold_threshold) e la stessa CV a 5 fold:
   - regressione logistica su colonne numeriche imputate (mediana, fit solo sul training) +
     indicatori di mancanza + one-hot delle categoriche (mancante = categoria a sé);
   - HistGradientBoostingClassifier, che gestisce i NaN in modo nativo.
2. Heart Disease: centro di provenienza di ogni record, prevalenza per centro, ROC-AUC
   out-of-fold dei sette encoder per centro.
3. Heart Disease: ROC-AUC di un modello che vede solo QUALI campi mancano (indicatori 0/1),
   per misurare quanto la mancanza da sola predice la malattia.

Scrive manuale_v2/analisi/risultati_aggiuntivi.json, letto da genera_tabelle.py.
"""
import json
import os

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from function import (
    cat_cols, cat_cols_diabetes130, columns, load_diabetes130, load_heart_disease, models_all,
    num_cols, num_cols_diabetes130,
)

OUT = os.path.join("manuale_v2", "analisi", "risultati_aggiuntivi.json")


def _oof_threshold(make_model, X, y):
    from function import optimal_f1_threshold
    inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = np.zeros(len(y))
    for tr, va in inner.split(X, y):
        m = make_model().fit(X.iloc[tr], y[tr])
        scores[va] = m.predict_proba(X.iloc[va])[:, 1]
    return optimal_f1_threshold(y, scores)


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


def evaluate(make_model, X_train, y_train, X_test, y_test):
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
        "tau": float(tau),
    }


def split(df, target):
    X = df.drop(target, axis=1)
    y = (df[target] > 0).astype(int)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    return (X_tr.reset_index(drop=True), X_te.reset_index(drop=True),
            y_tr.to_numpy(), y_te.to_numpy())


def heart_with_centre():
    files = {
        "Cleveland": "processed.cleveland.data", "Ungheria": "processed.hungarian.data",
        "Svizzera": "processed.switzerland.data", "Long Beach VA": "processed.va.data",
    }
    centres = []
    for name, f in files.items():
        n = len(pd.read_csv(os.path.join("datasets/heart+disease", f), header=None))
        centres += [name] * n
    df = load_heart_disease()
    df["centro"] = centres
    return df


def main():
    res = {"baseline": {}, "heart_centri": {}, "heart_solo_mancanza": {}}

    # --- Baseline tabellari
    for name, df, target, num, cat in [
        ("heart_disease", load_heart_disease(), "num", num_cols, cat_cols),
        ("diabetes130", load_diabetes130(), "readmitted", num_cols_diabetes130, cat_cols_diabetes130),
    ]:
        X_tr, X_te, y_tr, y_te = split(df, target)
        as_str = lambda X: X.assign(**{c: X[c].astype(str) for c in cat})  # NaN -> "nan" = categoria "mancante"
        res["baseline"][name] = {
            "regressione_logistica": evaluate(_logreg(num, cat), as_str(X_tr), y_tr, as_str(X_te), y_te),
            "gradient_boosting": evaluate(
                _hgb(num, cat), _as_category_codes(X_tr[num + cat], cat), y_tr,
                _as_category_codes(X_te[num + cat], cat), y_te,
            ),
        }
        print(name, json.dumps(res["baseline"][name], indent=1))

    # --- Heart Disease: centro, prevalenza, AUC per centro
    df = heart_with_centre()
    X = df.drop("num", axis=1)
    y = (df["num"] > 0).astype(int)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    X_tr = X_tr.reset_index(drop=True)
    saved = pd.read_csv("datas/heart_disease/preprocessing/X_train_raw.csv")
    assert np.allclose(saved["age"].to_numpy(), X_tr["age"].to_numpy()), "split non allineato"
    centro = X_tr["centro"].to_numpy()
    y_tr = y_tr.to_numpy()
    rows = []
    for c in ["Cleveland", "Ungheria", "Svizzera", "Long Beach VA"]:
        mask = centro == c
        row = {"centro": c, "n_train": int(mask.sum()), "prevalenza_train": float(y_tr[mask].mean())}
        for m in models_all:
            r = f"datas/heart_disease/results/{m['model_name']}"
            yt, ys, vi = np.load(r + "_y_true.npy"), np.load(r + "_y_score.npy"), np.load(r + "_val_idx.npy")
            sel = centro[vi] == c
            row[m["model_name"]] = float(roc_auc_score(yt[sel], ys[sel])) if len(set(yt[sel])) == 2 else None
        rows.append(row)
    res["heart_centri"]["per_centro"] = rows

    # quanto pesa il centro da solo: AUC della sola prevalenza del centro (stimata nei fold)
    kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    centre_scores = np.zeros(len(y_tr))
    miss_scores = np.zeros(len(y_tr))
    miss = X_tr[[c for c in columns if c != "num"]].isna().astype(int)
    for tr, va in kf.split(X_tr, y_tr):
        prev = pd.Series(y_tr[tr]).groupby(centro[tr]).mean()
        centre_scores[va] = pd.Series(centro[va]).map(prev).to_numpy()
        lr = LogisticRegression(max_iter=2000).fit(miss.iloc[tr], y_tr[tr])
        miss_scores[va] = lr.predict_proba(miss.iloc[va])[:, 1]
    res["heart_centri"]["auc_solo_prevalenza_centro"] = float(roc_auc_score(y_tr, centre_scores))
    res["heart_solo_mancanza"]["auc_cv"] = float(roc_auc_score(y_tr, miss_scores))
    res["heart_solo_mancanza"]["campi"] = [c for c in miss.columns if miss[c].any()]
    print(json.dumps(res["heart_centri"], indent=1))
    print(json.dumps(res["heart_solo_mancanza"], indent=1))

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print("scritto", OUT)


if __name__ == "__main__":
    main()

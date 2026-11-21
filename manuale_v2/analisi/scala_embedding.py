"""Effetto della scala degli embedding sul confronto tra encoder (Heart Disease).
Stessa CV a 5 fold della pipeline; ROC-AUC out-of-fold con: (a) protocollo della pipeline
(LogisticRegression C=1 sui vettori grezzi), (b) StandardScaler + C=1, (c) vettori normalizzati
a norma 1 per tutti + C=1, (d) StandardScaler + C scelto per CV interna tra 1e-3 e 1e2.
Eseguire dalla radice:  env/bin/python manuale_v2/analisi/scala_embedding.py
"""
import json, os
import numpy as np
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer, StandardScaler
from function import models_all

def oof_auc(make, X, y):
    kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    s = np.zeros(len(y))
    for tr, va in kf.split(X, y):
        s[va] = make().fit(X[tr], y[tr]).predict_proba(X[va])[:, 1]
    return float(roc_auc_score(y, s))

variants = {
    "pipeline_C1": lambda: LogisticRegression(max_iter=5000),
    "standard_C1": lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000)),
    "norma1_C1": lambda: make_pipeline(Normalizer(), LogisticRegression(max_iter=5000)),
    "standard_Ccv": lambda: make_pipeline(StandardScaler(), LogisticRegressionCV(Cs=np.logspace(-3, 2, 11), cv=5, scoring="roc_auc", max_iter=5000)),
}
out = {}
for m in models_all:
    d = "datas/heart_disease/embeddings/"
    X, y = np.load(d + m["filename"]), np.load(d + m["filename_label"])
    out[m["model_name"]] = {k: oof_auc(f, X, y) for k, f in variants.items()}
    print(m["model_name"], {k: round(v, 3) for k, v in out[m["model_name"]].items()})
json.dump(out, open("manuale_v2/analisi/scala_embedding.json", "w"), indent=2)

# DeLong tra tutte le coppie con il protocollo equo (StandardScaler + C scelto per CV interna)
from itertools import combinations
from MLstatkit import Delong_test
from statisticaltest import _benjamini_hochberg
scores, chosen = {}, {}
for m in models_all:
    d = "datas/heart_disease/embeddings/"
    X, y = np.load(d + m["filename"]), np.load(d + m["filename_label"])
    kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    s = np.zeros(len(y)); cs = []
    for tr, va in kf.split(X, y):
        mdl = variants["standard_Ccv"]().fit(X[tr], y[tr])
        s[va] = mdl.predict_proba(X[va])[:, 1]; cs.append(float(mdl[-1].C_[0]))
    scores[m["model_name"]] = s; chosen[m["model_name"]] = cs
rows = []
for a, b in combinations(scores, 2):
    z, p = Delong_test(y, scores[a], scores[b])[:2]
    rows.append({"a": a, "b": b, "auc_a": roc_auc_score(y, scores[a]), "auc_b": roc_auc_score(y, scores[b]), "p": float(p)})
bh = _benjamini_hochberg([r["p"] for r in rows])
for r, q in zip(rows, bh):
    r["p_bh"] = float(q)
    print(f'{r["a"]:16s} {r["b"]:16s} {r["auc_a"]:.3f} {r["auc_b"]:.3f} p={r["p"]:.4f} p_bh={q:.4f}')
print("C scelti per fold:", chosen)
json.dump({"auc": out, "delong_equo": rows, "C_scelti": chosen}, open("manuale_v2/analisi/scala_embedding.json", "w"), indent=2)

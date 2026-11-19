import os
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, average_precision_score, brier_score_loss, f1_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from function import models_all, plot_metric_comparison, results, get_output_dirs, fit_classifier

def training_classifier(dataset="heart_disease"):
    dirs = get_output_dirs(dataset)
    for model in models_all:
        print(f"Evaluating model: {model['name']}")
        X = np.load(os.path.join(dirs["embeddings"], model['filename']), allow_pickle=True)
        y = np.load(os.path.join(dirs["embeddings"], model['filename_label']), allow_pickle=True)
        kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        tmp_results = []
        all_y_scores = []
        all_y_preds  = []
        all_y_true   = []
        all_val_idx  = []
        for train_idx, val_idx in kf.split(X, y):
            X_train_full, X_val = X[train_idx], X[val_idx]
            y_train_full, y_val = y[train_idx], y[val_idx]

            # Inside this fold's training partition only: C chosen by inner CV (embeddings are
            # standardized, see function.make_classifier), threshold chosen on out-of-fold scores
            # with that C, classifier fit on the whole partition. Class imbalance is handled by
            # the threshold: there is no oversampling (see preprocessing.py).
            logisticReg, tau, C = fit_classifier(X_train_full, y_train_full)
            # positive probabilities on the untouched validation fold
            y_score = logisticReg.predict_proba(X_val)[:, 1]
            # prediction with optimized threshold
            y_pred = (y_score >= tau).astype(int)
            # metrics
            acc = accuracy_score(y_val, y_pred)
            f1 = f1_score(y_val, y_pred, average='macro')
            auc = roc_auc_score(y_val, y_score)
            pr_auc = average_precision_score(y_val, y_score)
            brier = brier_score_loss(y_val, y_score)
            tmp_results.append((acc, f1, auc, tau, pr_auc, brier, C))
            all_y_true.append(y_val)
            all_y_scores.append(y_score)
            all_y_preds.append(y_pred)
            all_val_idx.append(val_idx)
        acc_mean = np.mean([r[0] for r in tmp_results])
        f1_mean  = np.mean([r[1] for r in tmp_results])
        auc_mean = np.mean([r[2] for r in tmp_results])
        tau_mean = np.mean([r[3] for r in tmp_results])
        pr_auc_mean = np.mean([r[4] for r in tmp_results])
        brier_mean = np.mean([r[5] for r in tmp_results])
        C_median = float(np.median([r[6] for r in tmp_results]))
        results[model['model_name']] = {
            "acc": acc_mean,
            "f1":  f1_mean,
            "auc": auc_mean,
            "tau": tau_mean,
            "pr_auc": pr_auc_mean,
            "brier": brier_mean,
            "C_median": C_median,
        }
        print(f"Accuracy (mean): {acc_mean:.4f}")
        print(f"Macro-F1 (mean): {f1_mean:.4f}")
        print(f"ROC-AUC (mean): {auc_mean:.4f}")
        print(f"PR-AUC (mean): {pr_auc_mean:.4f}  (prevalence {y.mean():.4f})")
        print(f"Brier (mean): {brier_mean:.4f}")
        print(f"C chosen per fold: {[r[6] for r in tmp_results]}")
        print(f"Mean optimized threshold τ: {tau_mean:.4f}")
        all_y_true  = np.concatenate(all_y_true)
        all_y_scores = np.concatenate(all_y_scores)
        all_y_preds = np.concatenate(all_y_preds)
        all_val_idx = np.concatenate(all_val_idx)
        np.save(os.path.join(dirs["results"], f"{model['model_name']}_y_true.npy"), all_y_true)
        np.save(os.path.join(dirs["results"], f"{model['model_name']}_y_score.npy"), all_y_scores)
        np.save(os.path.join(dirs["results"], f"{model['model_name']}_y_pred.npy"), all_y_preds)
        np.save(os.path.join(dirs["results"], f"{model['model_name']}_val_idx.npy"), all_val_idx)
        print(f"[OK] Saved y_true, y_score, y_pred, val_idx for model {model['model_name']}")
    df = pd.DataFrame(results).T   # transpose to have models as rows
    df.to_csv(os.path.join(dirs["results"], "model_performance.csv"))
    print("Saved to model_performance.csv")
    df_summary = pd.DataFrame({
        "model": list(results.keys()),
        "acc": [v["acc"] for v in results.values()],
        "f1": [v["f1"] for v in results.values()],
        "auc": [v["auc"] for v in results.values()],
        "tau": [v["tau"] for v in results.values()]
    })
    plot_metric_comparison(df_summary, results_dir=dirs["results"])
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_recall_curve, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from function import models_ollama, plot_metric_comparison, results

def training_classifier():
    for model in models_ollama:
        print(f"Evaluating model: {model['name']}")
        X = np.load(f"datas/embeddings/{model['filename']}",allow_pickle=True)
        y = np.load(f"datas/embeddings/{model['filename_label']}",allow_pickle=True)
        kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        logisticReg = LogisticRegression(max_iter=2000)
        tmp_results = []
        all_y_scores = []
        all_y_preds  = []
        all_y_true   = []
        for train_idx, val_idx in kf.split(X, y):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            # train
            logisticReg.fit(X_train, y_train)
            # positive probabilities
            y_score = logisticReg.predict_proba(X_val)[:, 1]
            # choose optimal threshold
            precision, recall, thresholds = precision_recall_curve(y_val, y_score)
            f1_scores = 2 * (precision * recall) / (precision + recall + 1e-6)
            best_idx = f1_scores.argmax()
            tau = thresholds[best_idx]
            # prediction with optimized threshold
            y_pred = (y_score >= tau).astype(int)
            # metrics
            acc = accuracy_score(y_val, y_pred)
            f1 = f1_score(y_val, y_pred, average='macro')
            auc = roc_auc_score(y_val, y_score)
            tmp_results.append((acc, f1, auc, tau))
            all_y_true.append(y_val)
            all_y_scores.append(y_score)
            all_y_preds.append(y_pred)
        acc_mean = np.mean([r[0] for r in tmp_results])
        f1_mean  = np.mean([r[1] for r in tmp_results])
        auc_mean = np.mean([r[2] for r in tmp_results])
        tau_mean = np.mean([r[3] for r in tmp_results])
        results[model['model_name']] = {
            "acc": acc_mean,
            "f1":  f1_mean,
            "auc": auc_mean,
            "tau": tau_mean
        }
        print(f"Accuracy (mean): {acc_mean:.4f}")
        print(f"Macro-F1 (mean): {f1_mean:.4f}")
        print(f"ROC-AUC (mean): {auc_mean:.4f}")
        print(f"Mean optimized threshold τ: {tau_mean:.4f}")
        all_y_true  = np.concatenate(all_y_true)
        all_y_scores = np.concatenate(all_y_scores)
        all_y_preds = np.concatenate(all_y_preds)
        np.save(f"datas/results/{model['model_name']}_y_true.npy", all_y_true)
        np.save(f"datas/results/{model['model_name']}_y_score.npy", all_y_scores)
        np.save(f"datas/results/{model['model_name']}_y_pred.npy", all_y_preds)
        print(f"[OK] Saved y_true, y_score, y_pred for model {model['model_name']}")
    df = pd.DataFrame(results).T   # transpose to have models as rows
    df.to_csv("datas/results/model_performance.csv")
    print("Saved to model_performance.csv")
    df_summary = pd.DataFrame({
        "model": list(results.keys()),
        "acc": [v["acc"] for v in results.values()],
        "f1": [v["f1"] for v in results.values()],
        "auc": [v["auc"] for v in results.values()],
        "tau": [v["tau"] for v in results.values()]
    })
    plot_metric_comparison(df_summary)
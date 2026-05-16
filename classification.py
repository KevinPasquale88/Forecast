import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_recall_curve, roc_auc_score
from sklearn.model_selection import StratifiedKFold
import seaborn as sns
import matplotlib.pyplot as plt
from function import models_ollama, results

def training_classifier():
    for model in models_ollama:
        print(f"Valutazione del modello: {model['name']}")
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
            # probabilità positive
            y_score = logisticReg.predict_proba(X_val)[:, 1]
            # scegli soglia ottimale
            precision, recall, thresholds = precision_recall_curve(y_val, y_score)
            f1_scores = 2 * (precision * recall) / (precision + recall + 1e-6)
            best_idx = f1_scores.argmax()
            tau = thresholds[best_idx]
            # predizione con soglia ottimizzata
            y_pred = (y_score >= tau).astype(int)
            # metriche
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
        print(f"Accuracy (media): {acc_mean:.4f}")
        print(f"Macro-F1 (media): {f1_mean:.4f}")
        print(f"ROC-AUC (media): {auc_mean:.4f}")
        print(f"Soglia τ ottimizzata media: {tau_mean:.4f}")
        all_y_true  = np.concatenate(all_y_true)
        all_y_scores = np.concatenate(all_y_scores)
        all_y_preds = np.concatenate(all_y_preds)
        np.save(f"datas/results/{model['model_name']}_y_true.npy", all_y_true)
        np.save(f"datas/results/{model['model_name']}_y_score.npy", all_y_scores)
        np.save(f"datas/results/{model['model_name']}_y_pred.npy", all_y_preds)
        print(f"[OK] Salvati y_true, y_score, y_pred per il modello {model['model_name']}")
    df = pd.DataFrame(results).T   # trasponi per avere modelli come righe
    df.to_csv("datas/results/model_performance.csv")
    print("Salvato in model_performance.csv")
    df_melt = df.reset_index().melt(id_vars="index", value_vars=["acc","f1","auc","tau"], var_name="variable", value_name="value")
    sns.boxplot(data=df_melt, x="variable", y="value", hue="index")
    plt.title("Confronto metriche tra encoder")
    plt.show()
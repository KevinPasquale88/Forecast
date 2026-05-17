import numpy as np
import pandas as pd
from function import models_ollama, plot_boxplots, plot_confusion, plot_roc
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

def evaluate_results():
    bootstrap_results = {}
    summary_rows = []
    for model in models_ollama:
        print(f"\n=== Analyzing: {model['model_name']} ===")
        # load data
        y_true = np.load(f"datas/results/{model['model_name']}_y_true.npy")
        y_score = np.load(f"datas/results/{model['model_name']}_y_score.npy")
        y_pred  = np.load(f"datas/results/{model['model_name']}_y_pred.npy")
        plot_roc(y_true, y_score, model["model_name"])
        plot_confusion(y_true, y_pred, model["model_name"])
        
        bootstrap_metrics_dict = bootstrap_metrics(y_true, y_score, y_pred)
        bootstrap_results[model["model_name"]] = bootstrap_metrics_dict
        print(f"Bootstrap Accuracy: {bootstrap_metrics_dict['acc'].mean():.4f}")
        print(f"Bootstrap F1-Score: {bootstrap_metrics_dict['f1'].mean():.4f}")
        print(f"Bootstrap AUC: {bootstrap_metrics_dict['auc'].mean():.4f}")
        acc_mean, acc_ci = ci(bootstrap_metrics_dict['acc'])
        f1_mean,  f1_ci  = ci(bootstrap_metrics_dict['f1'])
        auc_mean, auc_ci = ci(bootstrap_metrics_dict['auc'])
        summary_rows.append({
            "model": model["model_name"],
            "acc_mean": acc_mean,
            "acc_ci_low": acc_ci[0],
            "acc_ci_high": acc_ci[1],
            "f1_mean": f1_mean,
            "f1_ci_low": f1_ci[0],
            "f1_ci_high": f1_ci[1],
            "auc_mean": auc_mean,
            "auc_ci_low": auc_ci[0],
            "auc_ci_high": auc_ci[1]
        })
        print(f"Accuracy: {acc_mean:.4f}  CI: {acc_ci}")
        print(f"F1 Score: {f1_mean:.4f}  CI: {f1_ci}")
        print(f"AUC:      {auc_mean:.4f}  CI: {auc_ci}")
    plot_boxplots(bootstrap_results)
    # save final summary table
    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv("datas/results/encoder_comparison_summary.csv", index=False)
    print("\n=== ANALYSIS COMPLETED ===")
    print("Plots saved in /results/")
    print("Final table: encoder_comparison_summary.csv")


def bootstrap_metrics(y_true, y_score,y_pred, n_iter=10000, seed=42):
    rng = np.random.default_rng(seed)
    acc_list, f1_list, auc_list = [], [], []
    for _ in range(n_iter):
        idx = rng.integers(0, len(y_true), len(y_true))
        yt, yp, ys = y_true[idx], y_pred[idx], y_score[idx]
        acc_list.append(accuracy_score(yt, yp))
        f1_list.append(f1_score(yt, yp, average="macro"))
        auc_list.append(roc_auc_score(yt, ys))
    return {
        "acc": np.array(acc_list),
        "f1": np.array(f1_list),
        "auc": np.array(auc_list)
    }

def ci(a, alpha=0.95):
    low = np.percentile(a, (1-alpha)/2 * 100)
    high = np.percentile(a, (1+alpha)/2 * 100)
    mean = a.mean()
    return mean, (low, high)



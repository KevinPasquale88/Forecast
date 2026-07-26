import numpy as np
import pandas as pd
from function import models_all, num_cols, num_cols_diabetes130, plot_error_rates, plot_feature_deviation

def analyze_errors(dataset="heart_disease"):
    num_cols_used = num_cols_diabetes130 if dataset == "diabetes130" else num_cols
    X_raw = pd.read_csv("datas/preprocessing/X_train_raw.csv")
    n_records = len(X_raw)

    error_counts = np.zeros(n_records, dtype=int)
    eval_counts = np.zeros(n_records, dtype=int)

    error_rows = []
    correct_rows = []
    summary_rows = []

    for model in models_all:
        name = model["model_name"]
        y_true = np.load(f"datas/results/{name}_y_true.npy")
        y_pred = np.load(f"datas/results/{name}_y_pred.npy")
        y_score = np.load(f"datas/results/{name}_y_score.npy")
        val_idx = np.load(f"datas/results/{name}_val_idx.npy")

        fp_mask = (y_true == 0) & (y_pred == 1)
        fn_mask = (y_true == 1) & (y_pred == 0)
        error_mask = fp_mask | fn_mask

        records = X_raw.iloc[val_idx].reset_index(drop=True).copy()
        records["y_score"] = y_score

        records[fp_mask].to_csv(f"datas/results/{name}_false_positives.csv", index=False)
        records[fn_mask].to_csv(f"datas/results/{name}_false_negatives.csv", index=False)

        n_pos = int((y_true == 1).sum())
        n_neg = int((y_true == 0).sum())
        summary_rows.append({
            "model": name,
            "n_errors": int(error_mask.sum()),
            "n_fp": int(fp_mask.sum()),
            "n_fn": int(fn_mask.sum()),
            "fp_rate": fp_mask.sum() / n_neg if n_neg else 0.0,
            "fn_rate": fn_mask.sum() / n_pos if n_pos else 0.0,
        })

        eval_counts[val_idx] += 1
        error_counts[val_idx] += error_mask.astype(int)

        error_rows.append(X_raw.iloc[val_idx[error_mask]][num_cols_used])
        correct_rows.append(X_raw.iloc[val_idx[~error_mask]][num_cols_used])

    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv("datas/results/error_summary.csv", index=False)
    plot_error_rates(df_summary)

    # Hardest cases: records misclassified most often across models
    hardest_idx = np.argsort(-error_counts)[:20]
    hardest_idx = hardest_idx[error_counts[hardest_idx] > 0]
    df_hardest = X_raw.iloc[hardest_idx].copy()
    df_hardest["n_models_wrong"] = error_counts[hardest_idx]
    df_hardest["n_models_evaluated"] = eval_counts[hardest_idx]
    df_hardest.to_csv("datas/results/hardest_cases.csv", index=False)

    # Feature deviation: standardized mean difference between pooled misclassified cases
    # and pooled correctly classified cases, across all models
    df_error = pd.concat(error_rows, ignore_index=True)
    df_correct = pd.concat(correct_rows, ignore_index=True)
    deviation_rows = []
    for feature in num_cols_used:
        pooled_std = pd.concat([df_error[feature], df_correct[feature]]).std()
        deviation = (df_error[feature].mean() - df_correct[feature].mean()) / pooled_std if pooled_std else 0.0
        deviation_rows.append({"feature": feature, "deviation": deviation})
    df_deviation = pd.DataFrame(deviation_rows)
    df_deviation.to_csv("datas/results/feature_deviation.csv", index=False)
    plot_feature_deviation(df_deviation)

    print("\n=== ERROR ANALYSIS COMPLETED ===")
    print(df_summary.to_string(index=False))
    print(f"Hardest cases saved: datas/results/hardest_cases.csv ({len(df_hardest)} records)")
    print("Feature deviation saved: datas/results/feature_deviation.csv")

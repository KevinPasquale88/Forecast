
"""Pairwise statistical comparison of the seven encoders (phase 6 of main.py).

- Wilcoxon signed-rank and paired t-test on the 10,000 paired bootstrap values of accuracy,
  macro-F1 and ROC-AUC saved by evaluation.py (same resampled patients for every model, seed 42).
- DeLong test on the out-of-fold ROC-AUC of each pair (same patients, same labels).
- Benjamini-Hochberg adjusted p-values, computed over all the rows of each output file (63 for
  Wilcoxon and t-test: 21 pairs x 3 metrics; 21 for DeLong), reported alongside the raw ones.
"""
import os
from MLstatkit import Delong_test
import numpy as np
import pandas as pd
from scipy.stats import ttest_rel
from scipy.stats import wilcoxon
from function import get_output_dirs, models_all


def _benjamini_hochberg(p_values):
    """Benjamini-Hochberg adjusted p-values (controls the false discovery rate), same order as
    the input. With 21 pairwise comparisons per metric (C(7,2) for 7 models), some raw p-values
    fall below 0.05 by chance alone; the adjusted values say which comparisons remain
    significant once that is accounted for."""
    p = np.asarray(p_values, dtype=float)
    n = len(p)
    if n == 0:
        return p
    order = np.argsort(p)
    ranked = p[order]
    adjusted = ranked * n / np.arange(1, n + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]  # enforce monotonicity by rank
    adjusted = np.clip(adjusted, 0, 1)
    result = np.empty(n)
    result[order] = adjusted
    return result


def _add_bh_columns(df):
    if len(df) == 0:
        return df
    df["p_value_bh"] = np.round(_benjamini_hochberg(df["p_value"].values), 4)
    df["significant_bh"] = (df["p_value_bh"] < 0.05).astype(int).astype(str)
    return df

def test_statistical_tests(dataset="heart_disease"):
    dirs = get_output_dirs(dataset)
    metrics = ["acc", "f1", "auc"]
    wilcoxon_results = []
    ttest_results = []

    models = [m["model_name"] for m in models_all]

    for metric in metrics:
        # the 10,000 bootstrap values of this metric for each model
        boot_scores = {}
        for model_name in models:
            boot_scores[model_name] = np.load(
                os.path.join(dirs["results"], f"{model_name}_boot_{metric}.npy")
            )

        # Compare each pair of models
        for i in range(len(models)):
            for j in range(i + 1, len(models)):
                a = models[i]
                b = models[j]
                scores_a = boot_scores[a]
                scores_b = boot_scores[b]

                # Wilcoxon
                stat_w, p_w = wilcoxon(scores_a, scores_b)
                wilcoxon_results.append({
                    "metric":      metric,
                    "model_a":     a,
                    "model_b":     b,
                    "mean_a":      scores_a.mean().round(4),
                    "mean_b":      scores_b.mean().round(4),
                    "statistic":   round(stat_w, 4),
                    "p_value":     round(p_w, 4),
                    "significant": "1" if p_w < 0.05 else "0"
                })

                # Paired t-test
                stat_t, p_t = ttest_rel(scores_a, scores_b)
                ttest_results.append({
                    "metric":      metric,
                    "model_a":     a,
                    "model_b":     b,
                    "mean_a":      scores_a.mean().round(4),
                    "mean_b":      scores_b.mean().round(4),
                    "statistic":   round(stat_t, 4),
                    "p_value":     round(p_t, 4),
                    "significant": "1" if p_t < 0.05 else "0"
                })

    # p_value_bh / significant_bh: Benjamini-Hochberg correction across all pairwise comparisons
    # of this test type, in addition to the raw p_value / significant columns
    _add_bh_columns(pd.DataFrame(wilcoxon_results)).to_csv(
        os.path.join(dirs["results"], "wilcoxon_comparison.csv"), index=False
    )
    _add_bh_columns(pd.DataFrame(ttest_results)).to_csv(
        os.path.join(dirs["results"], "ttest_comparison.csv"), index=False
    )
    test_delong(dirs)
    print("Statistical tests completed and saved.")

def test_delong(dirs):
    """DeLong test on every pair of models, from the out-of-fold predictions of classification.py."""
    delong_results = []
    models = [m["model_name"] for m in models_all]

    # out-of-fold labels and scores of every model
    scores = {}
    for model_name in models:
        scores[model_name] = {
            "y_true":  np.load(os.path.join(dirs["results"], f"{model_name}_y_true.npy")),
            "y_score": np.load(os.path.join(dirs["results"], f"{model_name}_y_score.npy"))
        }
        
    for i in range(len(models)):
        for j in range(i + 1, len(models)):
            a = models[i]
            b = models[j]

            y_true_a = scores[a]["y_true"]
            y_true_b = scores[b]["y_true"]

            if not np.array_equal(y_true_a, y_true_b):
                print(f"[WARNING] different y_true for {a} vs {b}: skipped")
                continue

            z, p, auc_a, auc_b = Delong_test(
                y_true_a,
                scores[a]["y_score"],
                scores[b]["y_score"],
                return_ci=False,
                return_auc=True,
                verbose=0,
            )

            delong_results.append({
                "model_a":     a,
                "model_b":     b,
                "auc_a":       round(float(auc_a), 4),
                "auc_b":       round(float(auc_b), 4),
                "delta_auc":   round(float(auc_a - auc_b), 4),
                "z_statistic": round(float(z), 4),
                "p_value":     round(float(p), 4),
                "significant": "1" if p < 0.05 else "0"
            })

            print(
                f"{a} vs {b}: "
                f"AUC={auc_a:.4f} vs {auc_b:.4f}, "
                f"z={z:.3f}, p={p:.4f} "
                f"{'significant' if p < 0.05 else 'not significant'}"
            )

    df_delong = _add_bh_columns(pd.DataFrame(delong_results))
    df_delong.to_csv(os.path.join(dirs["results"], "delong_comparison.csv"), index=False)
    print("\nDeLong test completed -> delong_comparison.csv")
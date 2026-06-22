
import numpy as np
import pandas as pd
from scipy.stats import ttest_rel
from scipy.stats import wilcoxon
from function import models_all

def test_statistical_tests():
    metrics = ["acc", "f1", "auc"]
    wilcoxon_results = []
    ttest_results = []

    models = [m["model_name"] for m in models_all]

    for metric in metrics:
        # Load  10.000 bootstrap scores for each model
        boot_scores = {}
        for model_name in models:
            boot_scores[model_name] = np.load(
                f"datas/results/{model_name}_boot_{metric}.npy"
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

    # Salva CSV
    pd.DataFrame(wilcoxon_results).to_csv(
        "datas/results/wilcoxon_comparison.csv", index=False
    )
    pd.DataFrame(ttest_results).to_csv(
        "datas/results/ttest_comparison.csv", index=False
    )
    print("End statistical tests completed and saved.")
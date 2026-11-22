# Uncertainty estimation and statistical tests

This document describes how the pipeline estimates uncertainty and compares the seven encoders, and how to read the outputs. Code: [evaluation.py](../evaluation.py) (bootstrap) and [statisticaltest.py](../statisticaltest.py) (tests).

## What is compared

For each encoder, classification.py produces one **out-of-fold** prediction per training record (736 for Heart Disease, 16,000 for Diabetes130): the probability and the thresholded class from a classifier that never saw that record. All the analyses below use these predictions. The held-out test split is evaluated separately (holdout_evaluation.py) and is not used by the tests.

## Bootstrap confidence intervals

- 10,000 resamples with replacement of the out-of-fold predictions; on each resample, accuracy, macro-F1 and ROC-AUC are recomputed.
- 95% percentile interval: 2.5th and 97.5th percentiles of the 10,000 values (`*_ci_low`, `*_ci_high` in `encoder_comparison_summary.csv`).
- **Paired**: the same generator and seed (42) are used for every encoder, so resample *k* contains the same patients for all of them. Differences between encoders can therefore be compared resample by resample.
- **What it captures**: variability due to which patients are observed. It does not capture variability due to training (a classifier fit on other data would give different scores), so the intervals are somewhat narrower than the total uncertainty. Repeated cross-validation with different seeds would add that component.

The 10,000 values per encoder and metric are saved as `{model}_boot_{acc,f1,auc}.npy`.

## Pairwise tests

All 21 pairs of the 7 encoders are compared.

### Wilcoxon signed-rank test (on bootstrap values)

- Data: the 10,000 paired differences between two encoders' bootstrap values of a metric (accuracy, macro-F1, ROC-AUC).
- Non-parametric: ranks of the absolute differences, sums of positive and negative ranks.
- H₀: the differences are symmetric around zero.

### Paired t-test (on bootstrap values)

- Same paired differences; t = mean difference / (standard deviation / √n), with n = 10,000.
- H₀: mean difference zero. With n this large the mean is approximately normal by the central limit theorem.

### DeLong test (on out-of-fold predictions)

- Compares the ROC-AUC of two encoders evaluated on the same patients and labels, estimating the covariance between the two AUCs from their structural components (DeLong, DeLong & Clarke-Pearson, 1988). Implemented with `MLstatkit.Delong_test`.
- H₀: the two AUCs are equal.
- This is the standard test for comparing AUCs in clinical research, and it does not depend on an arbitrarily chosen number of resamples.

### Multiple comparisons

With 21 pairs per metric, some raw p-values fall below 0.05 by chance. Every output file therefore also has Benjamini-Hochberg adjusted p-values (`p_value_bh`) and significance flags (`significant_bh`), which control the false discovery rate. The correction is computed over all the rows of each file: 63 for Wilcoxon and t-test (21 pairs × 3 metrics), 21 for DeLong. Raw `p_value` and `significant` are kept.

## Output files (`datas/<dataset>/results/`)

| File | Columns |
|---|---|
| `wilcoxon_comparison.csv` | `metric`, `model_a`, `model_b`, `mean_a`, `mean_b`, `statistic`, `p_value`, `significant`, `p_value_bh`, `significant_bh` |
| `ttest_comparison.csv` | same as above |
| `delong_comparison.csv` | `model_a`, `model_b`, `auc_a`, `auc_b`, `delta_auc`, `z_statistic`, `p_value`, `significant`, `p_value_bh`, `significant_bh` |

The sign of `z_statistic` follows MLstatkit's convention and is opposite to `delta_auc`; use `delta_auc` (= `auc_a` − `auc_b`) for the direction of the difference.

## How to read the results

1. **Start from the size of the difference** and the confidence intervals. A difference of 0.001 AUC is not relevant in practice, whatever its p-value.
2. **Use DeLong as the reference test for ROC-AUC.**
3. **Read Wilcoxon and t-test as a stability check.** With 10,000 paired resamples their power is extremely high: even differences of a few thousandths are significant. They answer "does the difference have the same sign in almost all resamples?", not "is the difference large or relevant?". Always report their p-values next to the mean difference. This is expected behaviour, not a defect.
4. **Use the BH-adjusted columns** to decide significance.

Example from the November 2026 runs:

- Heart Disease: 9 of 21 DeLong comparisons significant after BH; 62 of 63 Wilcoxon (and t-test) comparisons significant, including differences as small as 0.0008.
- Diabetes130: 0 of 21 DeLong comparisons significant (largest AUC difference 0.009, smallest adjusted p 0.52); 63 of 63 Wilcoxon and t-test comparisons significant. The encoders are equivalent on this task: the two results are consistent once read as above.

## Statistical vs clinical significance

A statistically significant difference is unlikely to be due to chance; it is not necessarily large enough to matter for clinical decisions. Report effect sizes (differences in AUC, accuracy, sensitivity) with their intervals, and discuss relevance separately from significance.

## Possible extensions

- Repeated cross-validation with different seeds, with the corrected resampled t-test of Nadeau & Bengio (2003) or the 5×2 cv test of Dietterich (1998), to include training variability.
- Bias-corrected and accelerated (BCa) bootstrap intervals.

## References

- DeLong, E. R., DeLong, D. M., & Clarke-Pearson, D. L. (1988). Comparing the areas under two or more correlated receiver operating characteristic curves: a nonparametric approach. Biometrics, 44(3), 837–845.
- Efron, B., & Tibshirani, R. J. (1993). An Introduction to the Bootstrap. Chapman & Hall.
- Wilcoxon, F. (1945). Individual comparisons by ranking methods. Biometrics Bulletin, 1(6), 80–83.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate. Journal of the Royal Statistical Society, Series B, 57(1), 289–300.
- Nadeau, C., & Bengio, Y. (2003). Inference for the generalization error. Machine Learning, 52, 239–281.
- Dietterich, T. G. (1998). Approximate statistical tests for comparing supervised classification learning algorithms. Neural Computation, 10(7), 1895–1923.

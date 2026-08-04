# Statistical Testing

## Overview
Statistical significance testing is performed to rigorously compare classification performance across different embedding models. This phase validates whether observed performance differences are statistically significant or due to chance variation.

## Methodology
- **Main file**: [statisticaltest.py](../statisticaltest.py)
- **Bootstrap framework**: Builds upon bootstrap metrics generated during classification phase
- **Test sample size**: 10,000 bootstrap resamples per model and metric
- **Comparison scope**: All pairwise model comparisons

## Metrics Tested
The following performance metrics are compared across all model pairs:
1. **Accuracy (acc)**: Overall classification correctness
2. **F1-Score (f1)**: Harmonic mean of precision and recall (macro-averaged)
3. **ROC-AUC (auc)**: Area under the receiver operating characteristic curve

## Statistical Tests Implemented

### 1. Wilcoxon Signed-Rank Test
**Purpose**: Non-parametric test for paired samples; does not assume normality.

**When used**:
- Comparing two related samples (bootstrap scores from same cross-validation folds)
- Robust to outliers and non-normal distributions
- More appropriate for clinical/medical data which often deviates from normality

**Hypotheses**:
- H₀: No difference in distribution between model A and model B
- H₁: Significant difference between distributions

**Output**: Test statistic (W), p-value, significance flag (1 if p < 0.05, else 0)

### 2. Paired t-test (Dependent Samples t-test)
**Purpose**: Parametric test for comparing means of two related samples.

**When used**:
- As a complementary parametric approach
- Assumes approximately normal distribution
- More powerful than Wilcoxon if normality assumption holds

**Hypotheses**:
- H₀: μ_A = μ_B (means are equal)
- H₁: μ_A ≠ μ_B (means differ significantly)

**Output**: Test statistic (t), p-value, significance flag (1 if p < 0.05, else 0)

### 3. DeLong Test
**Purpose**: Compares ROC-AUC between two correlated models evaluated on the same labels.

**When used**:
- Directly testing whether the AUC difference between two embedding models is statistically significant
- Implemented via `MLstatkit.Delong_test`

**Output**: z-statistic, p-value, AUC for each model, and the AUC delta

## Results Interpretation
Results are saved in three CSV files:
- `datas/results/wilcoxon_comparison.csv` — Wilcoxon signed-rank test results
- `datas/results/ttest_comparison.csv` — Paired t-test results
- `datas/results/delong_comparison.csv` — DeLong AUC comparison results

**Key columns** (Wilcoxon/t-test):
- `metric`: Performance metric being compared (acc, f1, auc)
- `model_a`, `model_b`: Models in comparison
- `mean_a`, `mean_b`: Mean bootstrap scores for each model
- `statistic`: Test statistic value
- `p_value`: Statistical significance (p-value)
- `significant`: Binary flag for α = 0.05 significance level

**Interpretation guidelines**:
- **p_value < 0.05**: Statistically significant difference (reject H₀)
- **p_value ≥ 0.05**: No statistically significant difference (fail to reject H₀)
- **significant = 1**: Difference is significant at 95% confidence level
- **significant = 0**: Difference is not statistically significant

## Clinical vs. Statistical Significance
**Important distinction**:
- **Statistical significance** (p < 0.05): Difference is unlikely due to random chance
- **Clinical significance**: Difference is practically meaningful for clinical decision-making
  - Example: A 0.5% difference in accuracy may be statistically significant but not clinically relevant
  - Example: A 5% difference in sensitivity may be both statistically and clinically significant (especially for FN implications)

## Test Robustness
**Why Wilcoxon, paired t-test, and DeLong together**:
- Provides cross-validation of results through complementary statistical approaches
- Wilcoxon is more robust if normality assumption is violated
- Paired t-test has higher power if normality assumption holds
- DeLong is AUC-specific and accounts for the correlation between models evaluated on the same labels
- Consistency between tests strengthens confidence in results

**Bootstrap validation**:
- 10,000 resamples provides stable estimates of metric distributions
- StratifiedKFold ensures representative sampling
- Reduces false discovery rate from repeated comparisons

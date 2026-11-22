import pandas as pd
import os
import datetime

from function import get_output_dirs, MODEL_FAMILY

# ============================================================
#  LOAD SUMMARY DATA (CSV with mean metrics and confidence intervals)
# ============================================================

def load_summary(summary_path):
    if not os.path.exists(summary_path):
        raise FileNotFoundError(f"File not found: {summary_path}")
    return pd.read_csv(summary_path)


def load_statistical_results(wilcoxon_path, ttest_path, delong_path):
    results = {}
    if os.path.exists(wilcoxon_path):
        results["wilcoxon"] = pd.read_csv(wilcoxon_path)
    else:
        results["wilcoxon"] = None

    if os.path.exists(ttest_path):
        results["ttest"] = pd.read_csv(ttest_path)
    else:
        results["ttest"] = None

    if os.path.exists(delong_path):
        results["delong"] = pd.read_csv(delong_path)
    else:
        results["delong"] = None

    return results


# ============================================================
#  BUILD MARKDOWN CONTENT
# ============================================================

def generate_markdown(summary, dirs):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    md = []

    md.append(f"# 📊 Encoder Evaluation Report\n")
    md.append(f"**Generated:** {now}\n")
    md.append("---\n")

    md.append("## 🎯 Objective\n")
    md.append("Compare seven locally run text encoders (four general-purpose, three biomedical) as "
              "representations for clinical classification: each record is converted into a sentence, "
              "embedded, and classified by the same linear probe (standardized embeddings + L2 "
              "logistic regression), with 5-fold cross-validation, bootstrap confidence intervals, "
              "pairwise statistical tests and a held-out test split.\n")

    md.append("## 📘 Evaluated Models\n")
    for model in summary["model"]:
        md.append(f"- **{model}**")

    md.append("\n---\n")

    # ============================
    # METRICS WITH CI
    # ============================

    md.append("## 📈 Metric results with confidence intervals (Bootstrap 10,000)\n")

    md.append(summary.to_markdown(index=False))
    md.append("\n\n---\n")

    # ============================
    # CHARTS INCLUDED IN REPORT
    # ============================

    md.append("## 📉 ROC Curve Comparison\n")
    roc_path = os.path.join(dirs["graphics"], "ROC_comparison.png")
    real_roc_path = "../graphics/ROC_comparison.png"
    if os.path.exists(roc_path):
        md.append(f"![ROC Comparison]({real_roc_path})\n")

    md.append("\n---\n")

    md.append("## 🧩 Confusion Matrix\n")
    for model in summary["model"]:
        cm_path = os.path.join(dirs["graphics"], f"CM_{model}.png")
        real_cm_path = f"../graphics/CM_{model}.png"
        if os.path.exists(cm_path):
            md.append(f"### {model}\n")
            md.append(f"![CM {model}]({real_cm_path})\n")

    md.append("\n---\n")

    boxplot_path = os.path.join(dirs["results"], "BOXPLOT_metrics.png")
    real_boxplot_path = "../results/BOXPLOT_metrics.png"
    if os.path.exists(boxplot_path):
        md.append("## 📦 Bootstrapped Metric Boxplot\n")
        md.append(f"![Boxplot]({real_boxplot_path})\n")

    md.append("\n---\n")

    meanci_path = os.path.join(dirs["results"], "MeanCI_metrics.png")
    real_meanci_path = "../results/MeanCI_metrics.png"
    if os.path.exists(meanci_path):
        md.append("## 📐 Mean ± Confidence Interval\n")
        md.append("Mean metric per model with 95% bootstrap confidence interval (thin whisker) and ±1 standard deviation (thick whisker).\n")
        md.append(f"![Mean and Confidence Interval]({real_meanci_path})\n")

    md.append("\n---\n")

    family_path = os.path.join(dirs["results"], "FamilyComparison_metrics.png")
    real_family_path = "../results/FamilyComparison_metrics.png"
    if os.path.exists(family_path):
        md.append("## 🧬 Model Family Comparison\n")
        md.append("Bootstrap metric distributions pooled by model family: general-purpose vs. biomedical vs. biomedical sentence-transformers.\n")
        md.append(f"![Model Family Comparison]({real_family_path})\n")

    md.append("\n---\n")

    # ============================
    # ERROR ANALYSIS
    # ============================

    error_summary_path = os.path.join(dirs["results"], "error_summary.csv")
    if os.path.exists(error_summary_path):
        md.append("## 🩺 Error Analysis\n")
        md.append("Misclassified cases (false positives / false negatives) are traced back to the original clinical record for every model, using the fold validation indices saved during training.\n")

        df_error_summary = pd.read_csv(error_summary_path)
        md.append("### Error rates per model\n")
        md.append(df_error_summary.to_markdown(index=False))
        md.append("\n\n")

        error_rates_path = os.path.join(dirs["results"], "ErrorAnalysis_rates.png")
        real_error_rates_path = "../results/ErrorAnalysis_rates.png"
        if os.path.exists(error_rates_path):
            md.append(f"![Error Rates]({real_error_rates_path})\n")

        feature_dev_path = os.path.join(dirs["results"], "ErrorAnalysis_feature_deviation.png")
        real_feature_dev_path = "../results/ErrorAnalysis_feature_deviation.png"
        if os.path.exists(feature_dev_path):
            md.append("### Clinical feature deviation: misclassified vs. correctly classified\n")
            md.append("Standardized mean difference per clinical feature, pooled across all models (positive = higher in misclassified cases).\n")
            md.append(f"![Feature Deviation]({real_feature_dev_path})\n")

        hardest_cases_path = os.path.join(dirs["results"], "hardest_cases.csv")
        if os.path.exists(hardest_cases_path):
            df_hardest = pd.read_csv(hardest_cases_path)
            md.append("### Hardest cases (most frequently misclassified across models)\n")
            md.append(df_hardest.head(10).to_markdown(index=False))
            md.append("\n\n")

        md.append("---\n")

    # ============================
    # STATISTICAL TESTS
    # ============================

    stat_results = load_statistical_results(
        wilcoxon_path=os.path.join(dirs["results"], "wilcoxon_comparison.csv"),
        ttest_path=os.path.join(dirs["results"], "ttest_comparison.csv"),
        delong_path=os.path.join(dirs["results"], "delong_comparison.csv"),
    )
    if stat_results["wilcoxon"] is not None or stat_results["ttest"] is not None or stat_results["delong"] is not None:
        md.append("## 🧪 Statistical Tests\n")
        md.append("This section reports pairwise comparisons between model bootstrap metrics using Wilcoxon signed-rank tests, paired t-tests, and DeLong AUC comparisons.\n")

        if stat_results["wilcoxon"] is not None:
            md.append("### Wilcoxon Signed-Rank Test\n")
            md.append("The Wilcoxon test compares paired bootstrap distributions for each model pair.\n")
            md.append(stat_results["wilcoxon"].to_markdown(index=False))
            md.append("\n\n")

        if stat_results["ttest"] is not None:
            md.append("### Paired t-test\n")
            md.append("The paired t-test compares paired bootstrap means for each model pair.\n")
            md.append(stat_results["ttest"].to_markdown(index=False))
            md.append("\n\n")

        if stat_results["delong"] is not None:
            md.append("### DeLong AUC Comparison\n")
            md.append("The DeLong test compares AUC performance between model pairs on the same test labels.\n")
            md.append(stat_results["delong"].to_markdown(index=False))
            md.append("\n\n")

        md.append("---\n")
    else:
        md.append("## 🧪 Statistical Tests\n")
        md.append(f"No statistical test results were found. Ensure `{dirs['results']}/wilcoxon_comparison.csv`, `{dirs['results']}/ttest_comparison.csv`, and `{dirs['results']}/delong_comparison.csv` are generated before running report generation.\n")
        md.append("---\n")

    # ============================
    # HOLDOUT TEST SET EVALUATION
    # ============================

    holdout_path = os.path.join(dirs["results"], "holdout_evaluation.csv")
    if os.path.exists(holdout_path):
        md.append("## 🧾 Held-Out Test Set Evaluation\n")
        md.append(
            "Metrics on the 20% test split created in `preprocessing.py` and never used for "
            "training, threshold calibration, or the model comparisons above — the counterpart "
            "to the 5-fold cross-validation results, on data none of those steps ever saw.\n"
        )
        md.append(pd.read_csv(holdout_path).to_markdown(index=False))
        md.append("\n\n---\n")

    # ============================
    # SUPPLEMENTARY ANALYSES
    # ============================

    md.append(_build_supplementary(dirs))

    # ============================
    # DISCUSSION (computed from `summary`, not fixed text)
    # ============================

    md.append("## 🔍 Discussion and Observations\n")
    md.append(_build_discussion(summary))

    md.append("\n---\n")

    # ============================
    # CONCLUSIONS (computed from `summary` and `stat_results`, not fixed text)
    # ============================

    md.append("## 🏁 Conclusions\n")
    md.append(_build_conclusions(summary, stat_results))

    md.append("\n---\n")

    # ============================
    # IMPROVEMENTS
    # ============================

    md.append("## 🚀 Potential Improvements\n")
    md.append("""
- Use the task prefixes recommended by the E5 model cards (`query: `, or the instruction format
  of multilingual-e5-large-instruct) and measure their effect.
- Write the Diabetes130 admission/discharge codes as their text labels (IDS_mapping.csv).
- Leave-one-centre-out validation on Heart Disease.
- Report calibration curves, not only discrimination metrics and the Brier score.
- Repeated cross-validation with different seeds, to include training variability in the
  confidence intervals.
- A non-linear classifier on the embeddings as an additional comparison point.
""")

    return "\n".join(md)


def _build_supplementary(dirs):
    """Tables written by supplementary_analysis.py, if present."""
    md = []
    res = dirs["results"]
    sections = [
        ("tabular_baselines.csv", "## 📋 Tabular Baselines",
         "Logistic regression and gradient boosting on the original columns, same split, same "
         "5-fold CV and same threshold protocol as the encoders: the reference for judging the "
         "text representation."),
        ("centre_analysis.csv", "## 🏥 ROC-AUC Inside Each Centre",
         "Out-of-fold ROC-AUC of every encoder computed within each source centre, where the centre "
         "itself cannot help."),
        ("non_clinical_signal.csv", "## 🧭 Non-Clinical Signal",
         "Out-of-fold ROC-AUC obtained from the centre's prevalence alone and from the pattern of "
         "missing fields alone."),
        ("embedding_scale.csv", "## ⚖️ Embedding-Scale Sensitivity",
         "Out-of-fold ROC-AUC under four probing protocols: raw vectors with C=1, standardized with "
         "C=1, unit-normalized with C=1, standardized with C chosen by inner CV."),
        ("embedding_scale_delong.csv", "### DeLong under the standardized, CV-tuned protocol", None),
    ]
    for fname, title, text in sections:
        path = os.path.join(res, fname)
        if not os.path.exists(path):
            continue
        md.append(f"{title}\n")
        if text:
            md.append(text + "\n")
        md.append(pd.read_csv(path).to_markdown(index=False))
        md.append("\n\n")
    if md:
        md.append("---\n")
    return "\n".join(md)


def _build_discussion(summary):
    """Observations computed from the `summary` DataFrame of this run."""
    best_acc = summary.loc[summary["acc_mean"].idxmax()]
    best_f1 = summary.loc[summary["f1_mean"].idxmax()]
    best_auc = summary.loc[summary["auc_mean"].idxmax()]
    ci_width = summary["auc_ci_high"] - summary["auc_ci_low"]
    tightest = summary.loc[ci_width.idxmin()]

    lines = [
        f"- **{best_acc['model']}** has the highest mean accuracy in this run ({best_acc['acc_mean']:.4f}).",
        f"- **{best_f1['model']}** has the highest mean macro-F1 ({best_f1['f1_mean']:.4f}).",
        f"- **{best_auc['model']}** has the highest mean ROC-AUC ({best_auc['auc_mean']:.4f}), "
        f"95% bootstrap CI [{best_auc['auc_ci_low']:.4f}, {best_auc['auc_ci_high']:.4f}].",
        f"- **{tightest['model']}** has the narrowest AUC confidence interval "
        f"({ci_width.loc[tightest.name]:.4f} wide) — the most stable AUC estimate across the "
        "bootstrap resamples, independent of whether its mean AUC is also the highest.",
    ]
    family_auc = summary.assign(family=summary["model"].map(MODEL_FAMILY)).groupby("family")["auc_mean"].mean()
    if len(family_auc) > 1:
        best_family = family_auc.idxmax()
        lines.append(
            f"- Averaged by family, **{best_family}** has the highest mean AUC "
            f"({family_auc[best_family]:.4f}) among the families present in this run. This is "
            "a descriptive average, not a statistical test: see the DeLong comparison above "
            "for which specific pairwise differences are actually significant."
        )
    return "\n".join(lines)


def _build_conclusions(summary, stat_results):
    """Conclusions computed from `summary` and, where available, from the statistical tests."""
    lines = [
        "- Validation folds and the test split keep the real class distribution (no oversampling), "
        "so accuracy must be read against the majority-class rate, not 50%. ROC-AUC is the "
        "threshold-free reference: 0.5 means no ranking ability; PR-AUC should be compared with "
        "the prevalence reported in the held-out table.",
        "- Bootstrap resampling (10,000 iterations) gives every metric a reported confidence "
        "interval: treat a numerically higher mean as a meaningful difference only where the "
        "corresponding pairwise test below also reports significance, not from the ranking alone.",
    ]
    delong = stat_results.get("delong")
    if delong is not None and len(delong):
        sig = delong["significant"].astype(str).isin(["1", "1.0"])
        lines.append(
            f"- Of the {len(delong)} pairwise AUC comparisons (DeLong test), {int(sig.sum())} "
            f"are statistically significant at alpha=0.05 — see `delong_comparison.csv` for "
            "which specific pairs, rather than assuming every numeric difference is real."
        )
    return "\n".join(lines)


# ============================================================
#  MAIN
# ============================================================

def generate_report(dataset="heart_disease"):
    dirs = get_output_dirs(dataset)

    print("[INFO] Loading metric summary...")
    summary = load_summary(os.path.join(dirs["results"], "encoder_comparison_summary.csv"))

    print("[INFO] Generating markdown report...")
    md_content = generate_markdown(summary, dirs)

    md_path = os.path.join(dirs["reports"], "report.md")

    with open(md_path, "w") as f:
        f.write(md_content)

    print(f"[OK] Markdown report created: {md_path}")
    print("\n=== REPORT GENERATED SUCCESSFULLY ===")

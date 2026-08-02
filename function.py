import os
import numpy as np
import pandas as pd
from umap import UMAP
from sklearn.metrics import confusion_matrix, roc_curve, roc_auc_score
from sklearn.model_selection import train_test_split
import seaborn as sns
import matplotlib.pyplot as plt

columns = [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
        "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"
    ]
num_cols = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'ca']
cat_cols = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']

# Diabetes 130-US Hospitals dataset (UCI). The raw file has ~50 columns; most are
# near-constant drug-dosage flags (e.g. examide, citoglipton) or high-missingness
# identifiers (weight, payer_code, patient_nbr) that add no signal, so only a
# clinically meaningful subset is kept here.
columns_diabetes130 = [
    "race", "gender", "age", "admission_type_id", "discharge_disposition_id",
    "admission_source_id", "time_in_hospital", "num_lab_procedures", "num_procedures",
    "num_medications", "number_outpatient", "number_emergency", "number_inpatient",
    "number_diagnoses", "max_glu_serum", "A1Cresult", "insulin", "change",
    "diabetesMed", "readmitted"
]
num_cols_diabetes130 = [
    "time_in_hospital", "num_lab_procedures", "num_procedures", "num_medications",
    "number_outpatient", "number_emergency", "number_inpatient", "number_diagnoses"
]
cat_cols_diabetes130 = [
    "race", "gender", "age", "admission_type_id", "discharge_disposition_id",
    "admission_source_id", "max_glu_serum", "A1Cresult", "insulin", "change", "diabetesMed"
]


models_ollama = [
    {"type": "ollama", "model_name":"e5-base","name": "jeffh/intfloat-e5-base-v2:q8_0", "filename": "e5_base_embeddings.npy", "filename_label": "e5_base_embeddings_labels.npy", "family": "general-purpose"},
    {"type": "ollama", "model_name":"gte-base","name": "twwch/m3e-base", "filename": "gte_base_embeddings.npy", "filename_label": "gte_base_embeddings_labels.npy", "family": "general-purpose"},
    {"type": "ollama", "model_name":"gte-large","name": "zyw0605688/gte-large-zh", "filename": "gte_large_embeddings.npy", "filename_label": "gte_large_embeddings_labels.npy", "family": "general-purpose"},
    {"type": "ollama", "model_name":"e5-large","name": "jeffh/intfloat-multilingual-e5-large-instruct:q8_0", "filename": "e5_large_embeddings.npy", "filename_label": "e5_large_embeddings_labels.npy", "family": "general-purpose"}
]

models_medical = [
    {"type": "huggingface", "model_name": "bioclinicalbert", "name": "emilyalsentzer/Bio_ClinicalBERT", "filename": "bioclinicalbert_embeddings.npy", "filename_label": "bioclinicalbert_embeddings_labels.npy", "family": "biomedical"},
    {"type": "huggingface", "model_name": "pubmedbert", "name": "NeuML/pubmedbert-base-embeddings", "filename": "pubmedbert_embeddings.npy", "filename_label": "pubmedbert_embeddings_labels.npy", "family": "biomedical"},
    {"type": "huggingface", "model_name": "sentence-biobert", "name": "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb", "filename": "sentence_biobert_embeddings.npy", "filename_label": "sentence_biobert_embeddings_labels.npy", "family": "biomedical-st"},
]

models_all = models_ollama + models_medical

# Model family lookup: general-purpose vs biomedical vs biomedical sentence-transformers
MODEL_FAMILY = {m["model_name"]: m["family"] for m in models_all}

# Colorblind-safe, family-based palette (base hue per family; individual models get shades of it)
FAMILY_COLORS = {
    "general-purpose": "#2a78d6",
    "biomedical": "#1baf7a",
    "biomedical-st": "#eda100",
}

# Standard figure sizes so every plot shares the same footprint
FIGSIZE_STD = (7, 5)
FIGSIZE_WIDE = (9, 5.5)

results = {
    "e5-base":    {"acc": [], "f1": [], "auc": [], "tau": []},
    "e5-large":   {"acc": [], "f1": [], "auc": [], "tau": []},
    "gte-large":  {"acc": [], "f1": [], "auc": [], "tau": []},
    "gte-base":  {"acc": [], "f1": [], "auc": [], "tau": []}
}

datasets = ["heart_disease", "diabetes130"]

# Per-dataset output tree: each dataset gets its own preprocessing/embeddings/results/
# graphics/reports folders under datas/<dataset>/, so switching --dataset never deletes
# or overwrites the previous run of a different dataset.
def get_output_dirs(dataset):
    if dataset not in datasets:
        raise ValueError(f"Invalid dataset '{dataset}'. Valid options are: {datasets}")

    base = os.path.join("datas", dataset)
    dirs = {
        "preprocessing": os.path.join(base, "preprocessing"),
        "embeddings": os.path.join(base, "embeddings"),
        "results": os.path.join(base, "results"),
        "graphics": os.path.join(base, "graphics"),
        "reports": os.path.join(base, "reports"),
    }
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)
    return dirs

#load data from files and concatenate into one dataframe
def load_heart_disease():
    files = [
        "datasets/heart+disease/processed.cleveland.data",
        "datasets/heart+disease/processed.hungarian.data",
        "datasets/heart+disease/processed.switzerland.data",
        "datasets/heart+disease/processed.va.data"
    ]
    dfs = [pd.read_csv(f, header=None, na_values="?") for f in files]
    df = pd.concat(dfs, ignore_index=True)
    df.columns = columns

    # In some source files (notably Switzerland and Hungary) missing cholesterol/resting
    # blood pressure readings are encoded as 0 rather than "?". 0 mg/dl or 0 mm Hg is not a
    # physiologically valid value for either, so treat it as missing like the rest of the pipeline.
    df["chol"] = df["chol"].replace(0, np.nan)
    df["trestbps"] = df["trestbps"].replace(0, np.nan)

    return df

#load and sample the Diabetes 130-US Hospitals dataset from a local CSV
def load_diabetes130(sample_size=20000, random_state=42):
    df = pd.read_csv(
        "datasets/diabetes+130-us+hospitals+for+years+1999-2008/diabetic_data.csv", na_values="?"
    )
    df = df[columns_diabetes130].copy()

    # Binarize to the standard early-readmission benchmark task for this dataset:
    # 1 = readmitted within 30 days, 0 = readmitted later or not at all.
    df["readmitted"] = (df["readmitted"] == "<30").astype(int)

    if sample_size is not None and sample_size < len(df):
        df, _ = train_test_split(
            df, train_size=sample_size, stratify=df["readmitted"], random_state=random_state
        )
        df = df.reset_index(drop=True)

    return df

def _configure_plot_style():
    sns.set_style("white")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.labelsize": 10.5,
        "legend.fontsize": 9,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.grid": True,
        "grid.alpha": 0.25,
        "axes.edgecolor": "#4d4d4d",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })

_configure_plot_style()


def save_figure(fig, path_no_ext):
    fig.savefig(f"{path_no_ext}.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(f"{path_no_ext}.pdf", bbox_inches="tight", facecolor="white")


def get_model_palette(model_names):
    family_members = {}
    for name in model_names:
        family = MODEL_FAMILY.get(name, "general-purpose")
        family_members.setdefault(family, []).append(name)

    palette = {}
    for family, members in family_members.items():
        base_color = FAMILY_COLORS.get(family, "#888888")
        shades = sns.light_palette(base_color, n_colors=len(members) + 1)[1:]
        for name, shade in zip(members, shades):
            palette[name] = shade
    return palette


#delete files functions - each takes the dataset-specific folder to clean, so a rerun of
#one dataset never touches another dataset's saved run
def delete_files_embeddings(folder):
    pattern = "embeddings"
    for file_name in os.listdir(folder):
        full_path = os.path.join(folder, file_name)
        if os.path.isfile(full_path) and pattern in file_name:
            os.remove(full_path)
            print(f"Successfully deleted file: {file_name}")

def delete_files_preprocessing(folder):
    pattern = "preprocessed"
    for file_name in os.listdir(folder):
        full_path = os.path.join(folder, file_name)
        if os.path.isfile(full_path) and pattern in file_name:
            os.remove(full_path)
            print(f"Successfully deleted file: {file_name}")

def delete_files_results(folder):
    pattern_list = ["model_performance","_y_true", "_y_score", "_y_pred", "_val_idx", "BOXPLOT_metrics", "metric_comparison","encoder_comparison_summary", "MeanCI_metrics", "FamilyComparison_metrics", "error_summary", "hardest_cases", "false_positives", "false_negatives", "feature_deviation", "ErrorAnalysis"]
    for file_name in os.listdir(folder):
        full_path = os.path.join(folder, file_name)
        if os.path.isfile(full_path) and any(s in file_name for s in pattern_list):
            os.remove(full_path)
            print(f"Successfully deleted file: {file_name}")

def delete_files_graphics(folder):
    pattern_list = ["ROC", "CM", "bootstrap_metrics", "UMAP", "metric_comparison", "heatmap"]
    for file_name in os.listdir(folder):
        full_path = os.path.join(folder, file_name)
        if os.path.isfile(full_path) and any(s in file_name for s in pattern_list):
            os.remove(full_path)
            print(f"Successfully deleted file: {file_name}")


# print all datas in one markdown report
def plot_data_heatmap(X, num_cols=None, graphics_dir="datas/graphics"):
    if num_cols is None:
        num_cols = ["age", "trestbps", "chol", "thalach", "oldpeak", "ca"]
    fig, ax = plt.subplots(figsize=FIGSIZE_STD)
    sns.heatmap(X[num_cols].corr(), annot=True, cmap="coolwarm", center=0, ax=ax,
                cbar_kws={"shrink": 0.75}, linewidths=0.4, linecolor="white")
    ax.set_title("Correlation among numerical variables")
    save_figure(fig, os.path.join(graphics_dir, "heatmap_correlation"))
    plt.close(fig)

def plot_umap(X, y, title, graphics_dir="datas/graphics"):
    reducer = UMAP(n_components=2, random_state=42)
    X_umap = reducer.fit_transform(X)
    fig, ax = plt.subplots(figsize=FIGSIZE_STD)
    sns.scatterplot(x=X_umap[:, 0], y=X_umap[:, 1], hue=y, palette="coolwarm", s=40,
                     ax=ax, edgecolor="white", linewidth=0.3)
    ax.set_title(f"UMAP - {title}")
    ax.set_xlabel("UMAP1")
    ax.set_ylabel("UMAP2")
    ax.legend(title="Target", frameon=False, loc="best")
    save_figure(fig, os.path.join(graphics_dir, f"UMAP_{title}"))
    plt.close(fig)

def plot_boxplots(results_dict, results_dir="datas/results"):
    rows = []
    for model_name, metrics in results_dict.items():
        for v in metrics["acc"]:
            rows.append([model_name, "Accuracy", v])
        for v in metrics["f1"]:
            rows.append([model_name, "F1", v])
        for v in metrics["auc"]:
            rows.append([model_name, "AUC", v])
    df = pd.DataFrame(rows, columns=["Model", "Metric", "Value"])
    model_order = sorted(results_dict.keys(), key=lambda m: (MODEL_FAMILY.get(m, ""), m))
    palette = get_model_palette(model_order)

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    sns.boxplot(data=df, x="Metric", y="Value", hue="Model", hue_order=model_order,
                palette=palette, ax=ax, linewidth=0.8, fliersize=1.5)
    ax.set_title("Bootstrap (10k) Metric Distribution per Model")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False, borderaxespad=0)
    save_figure(fig, os.path.join(results_dir, "BOXPLOT_metrics"))
    plt.close(fig)

def plot_roc_comparison(roc_data, filename="ROC_comparison", graphics_dir="datas/graphics"):
    model_order = [name for name, _, _ in roc_data]
    palette = get_model_palette(model_order)

    fig, ax = plt.subplots(figsize=FIGSIZE_STD)

    for name, y_true, y_score in roc_data:
        fpr, tpr, _ = roc_curve(y_true, y_score)
        auc = roc_auc_score(y_true, y_score)
        ax.plot(fpr, tpr, color=palette[name], linewidth=2.2, label=f"{name} (AUC = {auc:.3f})")

    ax.plot([0, 1], [0, 1], linestyle="--", color="#a0a0a0", linewidth=1.2, label="Chance")
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.02])
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve Comparison - All Models")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8, frameon=False, labelspacing=0.4)

    save_figure(fig, os.path.join(graphics_dir, filename))
    plt.close(fig)

def plot_confusion(y_true, y_pred, name, graphics_dir="datas/graphics"):
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                cbar_kws={"shrink": 0.75}, linewidths=0.4, linecolor="white")
    ax.set_title(f"Confusion Matrix - {name}")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    save_figure(fig, os.path.join(graphics_dir, f"CM_{name}"))
    plt.close(fig)

def plot_metric_comparison(df_summary, results_dir="datas/results"):
    df_melted = df_summary.melt(id_vars="model", value_vars=["acc", "f1", "auc", "tau"], var_name="metric", value_name="value")
    model_order = sorted(df_summary["model"], key=lambda m: (MODEL_FAMILY.get(m, ""), m))
    palette = get_model_palette(model_order)

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    sns.barplot(data=df_melted, x="metric", y="value", hue="model", hue_order=model_order, palette=palette, ax=ax)
    ax.set_title("Metric Comparison (Mean) per Model")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False, borderaxespad=0)
    save_figure(fig, os.path.join(results_dir, "metric_comparison"))
    plt.close(fig)

def plot_mean_ci(df_summary, results_dir="datas/results"):
    metrics = [("acc", "Accuracy"), ("f1", "F1"), ("auc", "AUC")]
    df_sorted = df_summary.copy()
    df_sorted["family"] = df_sorted["model"].map(MODEL_FAMILY)
    df_sorted = df_sorted.sort_values(["family", "model"]).reset_index(drop=True)
    y_pos = np.arange(len(df_sorted))
    colors = [FAMILY_COLORS.get(f, "#888888") for f in df_sorted["family"]]

    fig, axes = plt.subplots(1, len(metrics), figsize=(13, 5), sharey=True)
    for ax, (key, label) in zip(axes, metrics):
        mean = df_sorted[f"{key}_mean"]
        ci_low = mean - df_sorted[f"{key}_ci_low"]
        ci_high = df_sorted[f"{key}_ci_high"] - mean
        std = df_sorted[f"{key}_std"]

        ax.errorbar(mean, y_pos, xerr=[ci_low, ci_high], fmt="none",
                     ecolor="#999999", elinewidth=1.2, capsize=3, zorder=1)
        ax.errorbar(mean, y_pos, xerr=std, fmt="none",
                     ecolor="#333333", elinewidth=2.8, capsize=0, zorder=2)
        ax.scatter(mean, y_pos, c=colors, s=55, zorder=3, edgecolor="white", linewidth=0.6)

        ax.set_title(label)
        ax.set_xlabel("Score")

    axes[0].set_yticks(y_pos)
    axes[0].set_yticklabels(df_sorted["model"])
    axes[0].invert_yaxis()

    handles = [plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=8, label=family)
               for family, c in FAMILY_COLORS.items()]
    fig.legend(handles=handles, loc="upper center", ncol=len(FAMILY_COLORS), frameon=False, bbox_to_anchor=(0.5, 1.08))
    fig.suptitle("Mean ± Bootstrap 95% CI (thin) and ± 1 SD (thick)", y=1.16, fontsize=11)
    fig.tight_layout()
    save_figure(fig, os.path.join(results_dir, "MeanCI_metrics"))
    plt.close(fig)

def plot_family_comparison(bootstrap_results, results_dir="datas/results"):
    rows = []
    for model_name, metrics in bootstrap_results.items():
        family = MODEL_FAMILY.get(model_name, "general-purpose")
        for v in metrics["acc"]:
            rows.append([family, "Accuracy", v])
        for v in metrics["f1"]:
            rows.append([family, "F1", v])
        for v in metrics["auc"]:
            rows.append([family, "AUC", v])
    df = pd.DataFrame(rows, columns=["Family", "Metric", "Value"])
    family_order = [f for f in ["general-purpose", "biomedical", "biomedical-st"] if f in df["Family"].unique()]

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    sns.boxplot(data=df, x="Metric", y="Value", hue="Family", hue_order=family_order,
                palette=FAMILY_COLORS, ax=ax, linewidth=0.9, fliersize=1.5)
    ax.set_title("Model Family Comparison - Bootstrap Metric Distributions")
    ax.legend(title="Model family", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False, borderaxespad=0)
    save_figure(fig, os.path.join(results_dir, "FamilyComparison_metrics"))
    plt.close(fig)

def plot_error_rates(df_error_summary, results_dir="datas/results"):
    df_melted = df_error_summary.melt(id_vars="model", value_vars=["fp_rate", "fn_rate"],
                                       var_name="error_type", value_name="rate")
    df_melted["error_type"] = df_melted["error_type"].map({"fp_rate": "False Positive Rate", "fn_rate": "False Negative Rate"})
    model_order = sorted(df_error_summary["model"], key=lambda m: (MODEL_FAMILY.get(m, ""), m))

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    sns.barplot(data=df_melted, x="model", y="rate", hue="error_type", order=model_order,
                palette=["#e34948", "#4a3aa7"], ax=ax)
    ax.set_title("False Positive / False Negative Rate per Model")
    ax.set_xlabel("Model")
    ax.set_ylabel("Rate")
    ax.tick_params(axis="x", rotation=30)
    ax.legend(title=None, bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False, borderaxespad=0)
    save_figure(fig, os.path.join(results_dir, "ErrorAnalysis_rates"))
    plt.close(fig)

def plot_feature_deviation(df_deviation, results_dir="datas/results"):
    df_sorted = df_deviation.reindex(df_deviation["deviation"].abs().sort_values().index)
    colors = ["#e34948" if v > 0 else "#2a78d6" for v in df_sorted["deviation"]]

    fig, ax = plt.subplots(figsize=FIGSIZE_STD)
    ax.barh(df_sorted["feature"], df_sorted["deviation"], color=colors)
    ax.axvline(0, color="#4d4d4d", linewidth=0.8)
    ax.set_title("Feature Deviation: Misclassified vs. Correctly Classified")
    ax.set_xlabel("Standardized mean difference (error - correct)")
    save_figure(fig, os.path.join(results_dir, "ErrorAnalysis_feature_deviation"))
    plt.close(fig)

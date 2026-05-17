import os
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics import RocCurveDisplay, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

columns = [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
        "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"
    ]
num_cols = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'ca']
cat_cols = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']


models_ollama = [
    {"model_name":"e5-base","name": "yxchia/multilingual-e5-base", "filename": "e5_base_embeddings.npy", "filename_label": "e5_base_embeddings_labels.npy"},
    {"model_name":"gte-base","name": "granite3-dense", "filename": "gte_base_embeddings.npy", "filename_label": "gte_base_embeddings_labels.npy"},
    {"model_name":"gte-large","name": "zyw0605688/gte-large-zh", "filename": "gte_large_embeddings.npy", "filename_label": "gte_large_embeddings_labels.npy"},
    {"model_name":"e5-large","name": "jeffh/intfloat-multilingual-e5-large-instruct:q8_0", "filename": "e5_large_embeddings.npy", "filename_label": "e5_large_embeddings_labels.npy" }
]


results = {
    "e5-base":    {"acc": [], "f1": [], "auc": [], "tau": []},
    "e5-large":   {"acc": [], "f1": [], "auc": [], "tau": []},
    "gte-large":  {"acc": [], "f1": [], "auc": [], "tau": []},
    "gte-base":  {"acc": [], "f1": [], "auc": [], "tau": []}
}

def delete_files_embeddings():
    folder = "datas/embeddings"
    pattern = "embeddings"
    for file_name in os.listdir(folder):
        full_path = os.path.join(folder, file_name)
        if os.path.isfile(full_path) and pattern in file_name:
            os.remove(full_path)
            print(f"Successfully deleted file: {file_name}")
            
def delete_files_preprocessing():
    folder = "datas/preprocessing"
    pattern = "preprocessed"
    for file_name in os.listdir(folder):
        full_path = os.path.join(folder, file_name)
        if os.path.isfile(full_path) and pattern in file_name:
            os.remove(full_path)
            print(f"Successfully deleted file: {file_name}")
            
def delete_files_results():
    folder = "datas/results"
    pattern_list = ["model_performance","_y_true", "_y_score", "_y_pred", "BOXPLOT_metrics", "metric_comparison","encoder_comparison_summary"]
    for file_name in os.listdir(folder):
        full_path = os.path.join(folder, file_name)
        if os.path.isfile(full_path) and any(s in file_name for s in pattern_list):
            os.remove(full_path)
            print(f"Successfully deleted file: {file_name}")
            
def delete_files_graphics():
    folder = "datas/graphics"
    pattern_list = ["ROC", "CM", "bootstrap_metrics", "PCA", "metric_comparison", "heatmap"]
    for file_name in os.listdir(folder):
        full_path = os.path.join(folder, file_name)
        if os.path.isfile(full_path) and any(s in file_name for s in pattern_list):
            os.remove(full_path)
            print(f"Successfully deleted file: {file_name}")

def plot_data_heatmap(X):
    num_cols = ["age", "trestbps", "chol", "thalach", "oldpeak", "ca"]
    fig, ax = plt.subplots(figsize=(8,6))
    sns.heatmap(X[num_cols].corr(), annot=True, cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation among numerical variables")
    fig.savefig("datas/graphics/heatmap_correlation.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

def plot_pca(X, y, title):
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    plt.figure(figsize=(7,5))
    sns.scatterplot(x=X_pca[:,0], y=X_pca[:,1], hue=y, palette="coolwarm", s=40)
    plt.title(f"PCA - {title}")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.savefig(f"datas/graphics/PCA_{title}.png", dpi=300, bbox_inches="tight")
    plt.close()

def plot_boxplots(results_dict):
    rows = []
    for model_name, metrics in results_dict.items():
        for v in metrics["acc"]:
            rows.append([model_name, "Accuracy", v])
        for v in metrics["f1"]:
            rows.append([model_name, "F1", v])
        for v in metrics["auc"]:
            rows.append([model_name, "AUC", v])
    df = pd.DataFrame(rows, columns=["Model", "Metric", "Value"])
    plt.figure(figsize=(10,6))
    sns.boxplot(data=df, x="Metric", y="Value", hue="Model")
    plt.title("Bootstrap (10k) Metric Distribution per Model")
    plt.savefig("datas/results/BOXPLOT_metrics.png", dpi=300, bbox_inches="tight")
    plt.close()
    
def plot_roc(y_true, y_score, title):
    roc_display = RocCurveDisplay.from_predictions(y_true, y_score)
    fig = roc_display.figure_
    fig.set_size_inches(6,6)
    fig.savefig(f"datas/graphics/ROC_{title}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

def plot_confusion(y_true, y_pred, name):
    cm = confusion_matrix(y_true, y_pred) 
    plt.figure(figsize=(5,4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title(f"Confusion Matrix - {name}")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.savefig(f"datas/graphics/CM_{name}.png", dpi=300, bbox_inches="tight")
    plt.close()
    
def plot_metric_comparison(df_summary):
    df_melted = df_summary.melt(id_vars="model", value_vars=["acc", "f1", "auc","tau"], var_name="metric", value_name="value")
    plt.figure(figsize=(10,6))
    sns.barplot(data=df_melted, x="metric", y="value", hue="model")
    plt.title("Metric Comparison (Mean) per Model")
    plt.savefig("datas/results/metric_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()
    
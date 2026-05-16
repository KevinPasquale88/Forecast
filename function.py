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
    cartella = "datas/embeddings"
    stringa_da_cercare = "embeddings"
    for nome_file in os.listdir(cartella):
        percorso_completo = os.path.join(cartella, nome_file)
        if os.path.isfile(percorso_completo) and stringa_da_cercare in nome_file:
            os.remove(percorso_completo)
            print(f"File eliminato con successo: {nome_file}")
            
def delete_files_preprocessing():
    cartella = "datas/preprocessing"
    stringa_da_cercare = "preprocessed"
    for nome_file in os.listdir(cartella):
        percorso_completo = os.path.join(cartella, nome_file)
        if os.path.isfile(percorso_completo) and stringa_da_cercare in nome_file:
            os.remove(percorso_completo)
            print(f"File eliminato con successo: {nome_file}")
            
def delete_files_results():
    cartella = "datas/results"
    stringa_da_cercare = ["model_performance","_y_true", "_y_score", "_y_pred"]
    for nome_file in os.listdir(cartella):
        percorso_completo = os.path.join(cartella, nome_file)
        if os.path.isfile(percorso_completo) and any(s in nome_file for s in stringa_da_cercare):
            os.remove(percorso_completo)
            print(f"File eliminato con successo: {nome_file}")
            
def delete_files_graphics():
    cartella = "datas/graphics"
    stringa_da_cercare = ["ROC", "CM", "bootstrap_metrics", "PCA", "metric_comparison"]
    for nome_file in os.listdir(cartella):
        percorso_completo = os.path.join(cartella, nome_file)
        if os.path.isfile(percorso_completo) and any(s in nome_file for s in stringa_da_cercare):
            os.remove(percorso_completo)
            print(f"File eliminato con successo: {nome_file}")

def plot_data_heatmap(X):
    num_cols = ["age", "trestbps", "chol", "thalach", "oldpeak", "ca"]
    plt.figure(figsize=(8,6))
    sns.heatmap(X[num_cols].corr(), annot=True, cmap="coolwarm", center=0)
    plt.title("Correlazione tra variabili numeriche")
    plt.show()
    plt.savefig("datas/graphics/heatmap_correlation.png", dpi=300)
    plt.close()

def plot_pca(X, y, title):
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    plt.figure(figsize=(7,5))
    sns.scatterplot(x=X_pca[:,0], y=X_pca[:,1], hue=y, palette="coolwarm", s=40)
    plt.title(f"PCA - {title}")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.show()
    plt.savefig(f"datas/graphics/PCA_{title}.png", dpi=300)
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
    plt.show()
    plt.savefig("datas/results/BOXPLOT_metrics.png", dpi=300)
    plt.close()
    
def plot_roc(y_true, y_score, title):
    roc_display = RocCurveDisplay.from_predictions(y_true, y_score)
    plt.figure(figsize=(6,6))
    plt.plot(roc_display.fpr, roc_display.tpr, label=f"ROC curve (AUC = {roc_display.roc_auc:.4f})", color="blue")
    plt.plot([0, 1], [0, 1], label="Random Classifier", color="red")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(title)
    plt.legend()
    plt.show()
    plt.savefig(f"datas/graphics/ROC_{title}.png", dpi=300)
    plt.close()

def plot_confusion(y_true, y_pred, name):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(5,4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title(f"Confusion Matrix - {name}")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.savefig(f"datas/graphics/CM_{name}.png", dpi=300)
    plt.close()
import os

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import RocCurveDisplay, accuracy_score, confusion_matrix, f1_score, precision_recall_curve, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import seaborn as sns
import matplotlib.pyplot as plt

columns = [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
        "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"
    ]
num_cols = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'ca']
cat_cols = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']


models_ollama = [{"name": "yxchia/multilingual-e5-base", "filename": "e5_base_embeddings.npy", "filename_label": "e5_base_embeddings_labels.npy"},
                 {"name": "granite-embedding", "filename": "granite_embedding_embeddings.npy", "filename_label": "granite_embedding_embeddings_labels.npy"},
                 {"name": "jeffh/intfloat-multilingual-e5-large-instruct:q8_0", "filename": "e5_largeembeddings.npy", "filename_label": "e5_largeembeddings_labels.npy" }]

#loading dataset from csv files
def load_heart_disease():
    files = [
        "heart+disease/processed.cleveland.data",
        "heart+disease/processed.hungarian.data",
        "heart+disease/processed.switzerland.data",
        "heart+disease/processed.va.data"
    ]
    dfs = [pd.read_csv(f, header=None, na_values="?") for f in files]
    df = pd.concat(dfs, ignore_index=True)
    df.columns = columns
    return df

def clean_data(X, y):
    # handle missing values, encode categoricals and scale numericals in one pipeline
    numeric_transformer = ImbPipeline(steps=[('imputer', SimpleImputer(strategy='median')),('scaler', StandardScaler())])

    categorical_transformer = ImbPipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')), 
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    # combine transformations
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, num_cols),
            ('cat', categorical_transformer, cat_cols)
        ]
    )

    full_pipeline = ImbPipeline(steps=[
        ('preprocessor', preprocessor),   
        ('smote', SMOTE(random_state=42))
    ])

    full_pipeline = full_pipeline.fit(X, y)
    return full_pipeline

def data_processed(X_train, y_train, pipeline):
    # estrai il preprocessor già addestrato
    preprocessor = pipeline.named_steps['preprocessor']

    # ottieni le feature trasformate (embedding)
    X_train_emb = preprocessor.transform(X_train)

    # nomi colonne numeriche (rimaste uguali)
    num_features = num_cols

    # nomi delle colonne categoriche encodate
    cat_features = list(
        preprocessor.named_transformers_['cat']
        .named_steps['onehot']
        .get_feature_names_out(cat_cols)
    )

    feature_names = num_features + cat_features
    X_train_emb_df = pd.DataFrame(X_train_emb, columns=feature_names)
    X_train_emb_df['target'] = y_train.values
    return X_train_emb_df

def record_to_text(row):
    desc = f"{'Male' if row['sex'] == 1 else 'Female'}, Years old: {row['age']}, Cholesterol: {row['chol']} mg/dl, Blood Pressure: {row['trestbps']}, Chest Pain: {row['cp']}"
    return desc


def save_embeddings_to_npy(embeddings, filename):
    np.save(filename, embeddings)
    
def save_embeddindgs_label_to_npy(labels, filename):
    np.save(filename, labels)

def delete_files_embeddings():
    cartella = "."
    stringa_da_cercare = "embeddings"
    for nome_file in os.listdir(cartella):
        percorso_completo = os.path.join(cartella, nome_file) 
        if os.path.isfile(percorso_completo) and stringa_da_cercare in nome_file:
            os.remove(percorso_completo)  # Cancella il file
            print(f"File eliminato con successo: {nome_file}")

def evaluate_embeddings(X, y):
    clf = LogisticRegression(max_iter=2000)
    clf.fit(X, y)
    preds = clf.predict(X)
    return accuracy_score(y, preds), f1_score(y, preds, average="macro")

def plot_data(X,y):
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    plt.figure(figsize=(8,6))
    sns.scatterplot(x=X_pca[:, 0],y=X_pca[:, 1],hue=y,palette="Set1")
    plt.title("PCA dopo preprocessing + encoding + scaling")
    plt.show(block=False)
    
def training_classifier():
    for model in models_ollama:
        print(f"Valutazione del modello: {model['name']}")
        X = np.load(model["filename"],allow_pickle=True)
        y = np.load(model["filename_label"],allow_pickle=True)
        kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        logisticReg = LogisticRegression(max_iter=2000)
        results = []
        for train_idx, val_idx in kf.split(X, y):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            # train
            logisticReg.fit(X_train, y_train)
            # probabilità positive
            y_score = logisticReg.predict_proba(X_val)[:, 1]
            # scegli soglia ottimale
            precision, recall, thresholds = precision_recall_curve(y_val, y_score)
            f1_scores = 2 * (precision * recall) / (precision + recall + 1e-6)
            best_idx = f1_scores.argmax()
            tau = thresholds[best_idx]
            # predizione con soglia ottimizzata
            y_pred = (y_score >= tau).astype(int)
            # metriche
            acc = accuracy_score(y_val, y_pred)
            f1 = f1_score(y_val, y_pred, average='macro')
            auc = roc_auc_score(y_val, y_score)
            results.append((acc, f1, auc, tau))
        acc_mean = np.mean([r[0] for r in results])
        f1_mean  = np.mean([r[1] for r in results])
        auc_mean = np.mean([r[2] for r in results])
        tau_mean = np.mean([r[3] for r in results])
        print(f"Accuracy (media): {acc_mean:.4f}")
        print(f"Macro-F1 (media): {f1_mean:.4f}")
        print(f"ROC-AUC (media): {auc_mean:.4f}")
        print(f"Soglia τ ottimizzata media: {tau_mean:.4f}")
        logisticReg.fit(X, y)
        y_score = logisticReg.predict_proba(X)[:, 1]
        plot_roc(y, y_score, title=f"ROC Curve - {model['name']}")
        y_pred = (y_score >= tau_mean).astype(int)
        plot_conf(y, y_pred, title=f"Confusion Matrix - {model['name']}")
        # bootstrap per stima incertezza
        boot_results = bootstrap_metrics(y, y_score)
        ci_acc = ci(boot_results['acc'])
        ci_f1 = ci(boot_results['f1'])
        ci_auc = ci(boot_results['auc'])
        print(f"Bootstrap Accuracy: {ci_acc[0]:.4f} (CI: {ci_acc[1][0]:.4f} - {ci_acc[1][1]:.4f})")
        print(f"Bootstrap Macro-F1: {ci_f1[0]:.4f} (CI: {ci_f1[1][0]:.4f} - {ci_f1[1][1]:.4f})")
        print(f"Bootstrap ROC-AUC: {ci_auc[0]:.4f} (CI: {ci_auc[1][0]:.4f} - {ci_auc[1][1]:.4f})")
        plot_boxplots(boot_results)
        
def bootstrap_metrics(y_true, y_score, n_iter=10000, seed=42):
    rng = np.random.default_rng(seed)
    acc_list, f1_list, auc_list = [], [], []
    y_pred = (y_score >= 0.5).astype(int)
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

def plot_roc(y_true, y_score, title):
    RocCurveDisplay.from_predictions(y_true, y_score)
    plt.title(title)
    plt.show()

def plot_conf(y_true, y_pred, title):
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title(title)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.show()

def plot_boxplots(results_dict):
    plt.figure(figsize=(10,5))
    sns.boxplot(data=results_dict)
    plt.title("Distribuzione Bootstrap delle metriche")
    plt.show()
from concurrent.futures import ThreadPoolExecutor
import os

from dotenv import load_dotenv
from huggingface_hub import login
import numpy as np
import pandas as pd
from ollama import Client
from sentence_transformers import SentenceTransformer
from function import models_all

def embeddings(X,y):
    texts = [record_to_text(r) for _, r in X.iterrows()]
    #embedding generation
    generate_all_embeddings(texts, np.asarray(y))


# Standard UCI Heart Disease attribute encodings
CP_LABELS = {1: "typical angina", 2: "atypical angina", 3: "non-anginal pain", 4: "asymptomatic"}
RESTECG_LABELS = {0: "normal", 1: "ST-T wave abnormality", 2: "left ventricular hypertrophy"}
SLOPE_LABELS = {1: "upsloping", 2: "flat", 3: "downsloping"}
THAL_LABELS = {3: "normal", 6: "fixed defect", 7: "reversable defect"}

def _fmt_num(value, unit="", ndigits=1):
    if pd.isna(value):
        return "not recorded"
    return f"{round(float(value), ndigits):g}{unit}"

def _fmt_cat(value, labels):
    if pd.isna(value):
        return "not recorded"
    return labels.get(int(round(float(value))), "unknown")

def _fmt_bool(value, true_label, false_label):
    if pd.isna(value):
        return "not recorded"
    return true_label if int(round(float(value))) == 1 else false_label

def record_to_text(row):
    sex = _fmt_bool(row["sex"], "Male", "Female")
    parts = [
        f"{sex} patient, {_fmt_num(row['age'], ndigits=0)} years old",
        f"chest pain type: {_fmt_cat(row['cp'], CP_LABELS)}",
        f"resting blood pressure: {_fmt_num(row['trestbps'], ' mm Hg', ndigits=0)}",
        f"serum cholesterol: {_fmt_num(row['chol'], ' mg/dl', ndigits=0)}",
        f"fasting blood sugar > 120 mg/dl: {_fmt_bool(row['fbs'], 'yes', 'no')}",
        f"resting electrocardiographic results: {_fmt_cat(row['restecg'], RESTECG_LABELS)}",
        f"maximum heart rate achieved: {_fmt_num(row['thalach'], ndigits=0)}",
        f"exercise-induced angina: {_fmt_bool(row['exang'], 'yes', 'no')}",
        f"ST depression induced by exercise: {_fmt_num(row['oldpeak'])}",
        f"slope of the peak exercise ST segment: {_fmt_cat(row['slope'], SLOPE_LABELS)}",
        f"number of major vessels colored by fluoroscopy: {_fmt_num(row['ca'], ndigits=0)}",
        f"thalassemia: {_fmt_cat(row['thal'], THAL_LABELS)}",
    ]
    return ", ".join(parts)

def save_embeddings_to_npy(embeddings, filename):
    embeddings = np.array(embeddings, dtype=np.float32)
    np.save(filename, embeddings)
    
def save_labels_to_npy(labels, filename):
    labels = np.array(labels, dtype=np.int32)
    np.save(filename, labels)

def generate_embeddings_batch(model_name, texts):
    client = Client()
    print(f"[Batch] Generating embeddings for model: {model_name}")
    result = client.embed(model=model_name, input=texts)
    return result.embeddings

def generate_embeddings_hf(texts, model_name):
    print(f"[HF] Inizializzazione modello: {model_name}")
    
    # Carica le variabili d'ambiente dal file .env
    load_dotenv()

    # 1. Autenticazione sicura con Hugging Face
    hf_token = os.getenv("HF_READ_TOKEN")
    if hf_token:
        print("[HF] Token rilevato. Autenticazione in corso...")
        login(token=hf_token)
    else:
        print("[HF] Nessun token rilevato. Procedo senza autenticazione.")

    # 2. Gestione della modalità Offline
    # Leggiamo dal .env se vogliamo forzare l'offline (es. OFFLINE_MODE=1)
    is_offline = os.getenv("OFFLINE_MODE", "0") == "1"
    
    if is_offline:
        print("[HF] Modalità offline attivata. Verrà usata solo la cache locale.")
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["HF_DATASETS_OFFLINE"] = "1"
        os.environ["HF_HUB_OFFLINE"] = "1"
    else:
        # Assicuriamoci che l'offline sia disabilitato per permettere il download
        os.environ["TRANSFORMERS_OFFLINE"] = "0"
        os.environ["HF_DATASETS_OFFLINE"] = "0"
        os.environ["HF_HUB_OFFLINE"] = "0"

    # 3. Caricamento del modello
    try:
        # SentenceTransformer applicherà automaticamente il "mean pooling" ai token di Bio_ClinicalBERT
        model = SentenceTransformer(model_name, local_files_only=is_offline)
    except Exception as e:
        print(f"[HF] Errore critico durante il caricamento del modello. model_name: {model_name}, dettagli: {e}")
        raise e

    # 4. Generazione degli embeddings
    print(f"[HF] Generazione embeddings in corso...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    
    return embeddings

def process_model(model, texts, labels):
    name = model["name"]
    file_emb = f"datas/embeddings/{model['filename']}"
    file_lab = f"datas/embeddings/{model['filename_label']}"
    try:
        print(f"\n=== Processing {name} ===")
        
        if model["type"] == "ollama":
            embeddings = generate_embeddings_batch(name, texts)
        elif model["type"] == "huggingface":
            embeddings = generate_embeddings_hf(texts, name)
        
        save_embeddings_to_npy(embeddings, file_emb)
        save_labels_to_npy(labels, file_lab)
        print(f"[OK] Saved embeddings → {file_emb}")
        print(f"[OK] Saved labels → {file_lab}")
    except Exception as e:
        print(f"[ERROR] Model {name}: {e}")

def generate_all_embeddings(texts, labels, max_workers=3):
    print(f"\nRunning embedding generation for {len(models_all)} models...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for m in models_all:
            futures.append(executor.submit(process_model, m, texts, labels))
        for f in futures:
            f.result()
    print("\nAll embeddings generated successfully!")

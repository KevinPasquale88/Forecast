from concurrent.futures import ThreadPoolExecutor
import os
import threading
import time

from dotenv import load_dotenv
from huggingface_hub import login
import numpy as np
import pandas as pd
from ollama import Client
from sentence_transformers import SentenceTransformer
from function import get_output_dirs, models_all

def embeddings(X, y, dataset="heart_disease"):
    dirs = get_output_dirs(dataset)
    record_to_text = record_to_text_diabetes130 if dataset == "diabetes130" else record_to_text_heart_disease
    texts = [record_to_text(r) for _, r in X.iterrows()]
    #embedding generation
    generate_all_embeddings(texts, np.asarray(y), dirs["embeddings"])


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

def record_to_text_heart_disease(row):
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

def _fmt_raw(value):
    return "not recorded" if pd.isna(value) else str(value)

def record_to_text_diabetes130(row):
    parts = [
        f"{_fmt_raw(row['gender'])} patient, age range {_fmt_raw(row['age'])}",
        f"race: {_fmt_raw(row['race'])}",
        f"admission type id: {_fmt_raw(row['admission_type_id'])}",
        f"discharge disposition id: {_fmt_raw(row['discharge_disposition_id'])}",
        f"admission source id: {_fmt_raw(row['admission_source_id'])}",
        f"time in hospital: {_fmt_raw(row['time_in_hospital'])} days",
        f"number of lab procedures: {_fmt_raw(row['num_lab_procedures'])}",
        f"number of procedures: {_fmt_raw(row['num_procedures'])}",
        f"number of medications: {_fmt_raw(row['num_medications'])}",
        f"outpatient visits in prior year: {_fmt_raw(row['number_outpatient'])}",
        f"emergency visits in prior year: {_fmt_raw(row['number_emergency'])}",
        f"inpatient visits in prior year: {_fmt_raw(row['number_inpatient'])}",
        f"number of diagnoses: {_fmt_raw(row['number_diagnoses'])}",
        f"max glucose serum test result: {_fmt_raw(row['max_glu_serum'])}",
        f"A1C test result: {_fmt_raw(row['A1Cresult'])}",
        f"insulin therapy: {_fmt_raw(row['insulin'])}",
        f"medication changed during encounter: {_fmt_raw(row['change'])}",
        f"prescribed diabetes medication: {_fmt_raw(row['diabetesMed'])}",
    ]
    return ", ".join(parts)

def save_embeddings_to_npy(embeddings, filename):
    embeddings = np.array(embeddings, dtype=np.float32)
    np.save(filename, embeddings)
    
def save_labels_to_npy(labels, filename):
    labels = np.array(labels, dtype=np.int32)
    np.save(filename, labels)

# Ollama's local server spawns a tokenizer subprocess reachable over a local HTTP
# port; sending very large batches (and running several models concurrently) can
# exhaust local ephemeral ports and/or overload it, causing connection errors like
# "dial tcp 127.0.0.1:xxxxx: connect: can't assign requested address". Serializing
# calls and chunking into small batches keeps a single, short-lived request in
# flight at a time so the local server never gets overwhelmed.
_ollama_semaphore = threading.Semaphore(1)

def generate_embeddings_batch(model_name, texts, batch_size=16, max_retries=5,
                               retry_delay=2.0, inter_batch_delay=0.3):
    client = Client()
    num_batches = (len(texts) + batch_size - 1) // batch_size
    print(f"[Batch] Generating embeddings for model: {model_name} "
          f"({len(texts)} texts in {num_batches} batches of {batch_size})")

    all_embeddings = []
    for batch_idx in range(num_batches):
        start = batch_idx * batch_size
        batch = texts[start:start + batch_size]

        for attempt in range(1, max_retries + 1):
            try:
                with _ollama_semaphore:
                    result = client.embed(model=model_name, input=batch)
                all_embeddings.extend(result.embeddings)
                break
            except Exception as e:
                if attempt == max_retries:
                    raise RuntimeError(
                        f"[Batch] {model_name}: batch {batch_idx + 1}/{num_batches} "
                        f"failed after {max_retries} attempts: {e}"
                    ) from e
                wait = retry_delay * attempt
                print(f"[Batch] {model_name}: batch {batch_idx + 1}/{num_batches} "
                      f"failed (attempt {attempt}/{max_retries}): {e}. "
                      f"Retrying in {wait:.1f}s...")
                time.sleep(wait)

        if (batch_idx + 1) % 10 == 0 or (batch_idx + 1) == num_batches:
            print(f"[Batch] {model_name}: {batch_idx + 1}/{num_batches} batches done")
        time.sleep(inter_batch_delay)

    return all_embeddings

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

def process_model(model, texts, labels, embeddings_dir):
    name = model["name"]
    file_emb = os.path.join(embeddings_dir, model['filename'])
    file_lab = os.path.join(embeddings_dir, model['filename_label'])
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
        raise RuntimeError(f"Embedding generation failed for model '{name}': {e}") from e

def generate_all_embeddings(texts, labels, embeddings_dir, max_workers=3):
    print(f"\nRunning embedding generation for {len(models_all)} models...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for m in models_all:
            futures.append(executor.submit(process_model, m, texts, labels, embeddings_dir))
        for f in futures:
            f.result()
    print("\nAll embeddings generated successfully!")

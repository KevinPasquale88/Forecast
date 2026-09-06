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

def embeddings(X, y, dataset="heart_disease", split="train"):
    dirs = get_output_dirs(dataset)
    record_to_text = record_to_text_diabetes130 if dataset == "diabetes130" else record_to_text_heart_disease
    texts = [record_to_text(r) for _, r in X.iterrows()]
    #embedding generation
    generate_all_embeddings(texts, np.asarray(y), dirs["embeddings"], split=split)


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

def _masked(row, col, formatter):
    """Apply `formatter` to row[col], unless a "<col>_missing" indicator column (added by
    preprocessing.py for columns missing too often to impute honestly, see
    MISSING_INDICATOR_THRESHOLD there) marks this value as imputed — or, for a synthetic
    SMOTENC record, interpolated mostly from imputed neighbours. In that case report it as "not
    recorded", exactly like a genuinely missing value, instead of writing a fabricated number or
    category into the record as if it had been observed. A row with no such indicator column
    (because that field was never missing often enough to need one) falls through to `formatter`
    unchanged, so this is safe to apply to every field uniformly."""
    flag_col = f"{col}_missing"
    if flag_col in row.index and pd.notna(row[flag_col]) and int(round(float(row[flag_col]))) == 1:
        return "not recorded"
    return formatter(row[col])


def record_to_text_heart_disease(row):
    sex = _masked(row, "sex", lambda v: _fmt_bool(v, "Male", "Female"))
    parts = [
        f"{sex} patient, {_masked(row, 'age', lambda v: _fmt_num(v, ndigits=0))} years old",
        f"chest pain type: {_masked(row, 'cp', lambda v: _fmt_cat(v, CP_LABELS))}",
        f"resting blood pressure: {_masked(row, 'trestbps', lambda v: _fmt_num(v, ' mm Hg', ndigits=0))}",
        f"serum cholesterol: {_masked(row, 'chol', lambda v: _fmt_num(v, ' mg/dl', ndigits=0))}",
        f"fasting blood sugar > 120 mg/dl: {_masked(row, 'fbs', lambda v: _fmt_bool(v, 'yes', 'no'))}",
        f"resting electrocardiographic results: {_masked(row, 'restecg', lambda v: _fmt_cat(v, RESTECG_LABELS))}",
        f"maximum heart rate achieved: {_masked(row, 'thalach', lambda v: _fmt_num(v, ndigits=0))}",
        f"exercise-induced angina: {_masked(row, 'exang', lambda v: _fmt_bool(v, 'yes', 'no'))}",
        f"ST depression induced by exercise: {_masked(row, 'oldpeak', _fmt_num)}",
        f"slope of the peak exercise ST segment: {_masked(row, 'slope', lambda v: _fmt_cat(v, SLOPE_LABELS))}",
        f"number of major vessels colored by fluoroscopy: {_masked(row, 'ca', lambda v: _fmt_num(v, ndigits=0))}",
        f"thalassemia: {_masked(row, 'thal', lambda v: _fmt_cat(v, THAL_LABELS))}",
    ]
    return ", ".join(parts)

def _fmt_raw(value):
    return "not recorded" if pd.isna(value) else str(value)

def record_to_text_diabetes130(row):
    parts = [
        f"{_masked(row, 'gender', _fmt_raw)} patient, age range {_masked(row, 'age', _fmt_raw)}",
        f"race: {_masked(row, 'race', _fmt_raw)}",
        f"admission type id: {_masked(row, 'admission_type_id', _fmt_raw)}",
        f"discharge disposition id: {_masked(row, 'discharge_disposition_id', _fmt_raw)}",
        f"admission source id: {_masked(row, 'admission_source_id', _fmt_raw)}",
        f"time in hospital: {_masked(row, 'time_in_hospital', _fmt_raw)} days",
        f"number of lab procedures: {_masked(row, 'num_lab_procedures', _fmt_raw)}",
        f"number of procedures: {_masked(row, 'num_procedures', _fmt_raw)}",
        f"number of medications: {_masked(row, 'num_medications', _fmt_raw)}",
        f"outpatient visits in prior year: {_masked(row, 'number_outpatient', _fmt_raw)}",
        f"emergency visits in prior year: {_masked(row, 'number_emergency', _fmt_raw)}",
        f"inpatient visits in prior year: {_masked(row, 'number_inpatient', _fmt_raw)}",
        f"number of diagnoses: {_masked(row, 'number_diagnoses', _fmt_raw)}",
        f"max glucose serum test result: {_masked(row, 'max_glu_serum', _fmt_raw)}",
        f"A1C test result: {_masked(row, 'A1Cresult', _fmt_raw)}",
        f"insulin therapy: {_masked(row, 'insulin', _fmt_raw)}",
        f"medication changed during encounter: {_masked(row, 'change', _fmt_raw)}",
        f"prescribed diabetes medication: {_masked(row, 'diabetesMed', _fmt_raw)}",
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

def _split_filename(filename, split):
    """Insert a "_<split>" suffix before the extension, unless split is "train" (kept as the
    original, unsuffixed name so existing training-embedding filenames — and anything that
    already depends on them — are unaffected)."""
    if split == "train":
        return filename
    stem, ext = os.path.splitext(filename)
    return f"{stem}_{split}{ext}"


def process_model(model, texts, labels, embeddings_dir, split="train"):
    name = model["name"]
    file_emb = os.path.join(embeddings_dir, _split_filename(model['filename'], split))
    file_lab = os.path.join(embeddings_dir, _split_filename(model['filename_label'], split))
    try:
        print(f"\n=== Processing {name} ({split}) ===")

        if model["type"] == "ollama":
            embeddings = generate_embeddings_batch(name, texts)
        elif model["type"] == "huggingface":
            embeddings = generate_embeddings_hf(texts, name)

        save_embeddings_to_npy(embeddings, file_emb)
        save_labels_to_npy(labels, file_lab)
        print(f"[OK] Saved embeddings → {file_emb}")
        print(f"[OK] Saved labels → {file_lab}")
    except Exception as e:
        raise RuntimeError(f"Embedding generation failed for model '{name}' ({split}): {e}") from e

def generate_all_embeddings(texts, labels, embeddings_dir, max_workers=3, split="train"):
    print(f"\nRunning embedding generation for {len(models_all)} models ({split} split)...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for m in models_all:
            futures.append(executor.submit(process_model, m, texts, labels, embeddings_dir, split))
        for f in futures:
            f.result()
    print(f"\nAll embeddings generated successfully for the {split} split!")

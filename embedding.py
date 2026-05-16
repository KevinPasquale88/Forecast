from concurrent.futures import ThreadPoolExecutor

import numpy as np
from ollama import Client
from function import models_ollama

def embeddings(X,y):
    texts = [record_to_text(r) for _, r in X.iterrows()]
    #embedding generation
    generate_all_embeddings(texts, y.values)


def record_to_text(row):
    desc = f"{'Male' if row['sex'] == 1 else 'Female'}, Years old: {row['age']}, Cholesterol: {row['chol']} mg/dl, Blood Pressure: {row['trestbps']}, Chest Pain: {row['cp']}"
    return desc

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

def process_model(model, texts, labels):
    name = model["name"]
    file_emb = f"datas/embeddings/{model['filename']}"
    file_lab = f"datas/embeddings/{model['filename_label']}"
    try:
        print(f"\n=== Processing {name} ===")
        embeddings = generate_embeddings_batch(name, texts)
        save_embeddings_to_npy(embeddings, file_emb)
        save_labels_to_npy(labels, file_lab)
        print(f"[OK] Saved embeddings → {file_emb}")
        print(f"[OK] Saved labels → {file_lab}")
    except Exception as e:
        print(f"[ERROR] Model {name}: {e}")

def generate_all_embeddings(texts, labels, max_workers=3):
    print(f"\nRunning embedding generation for {len(models_ollama)} models...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for m in models_ollama:
            futures.append(executor.submit(process_model, m, texts, labels))
        for f in futures:
            f.result()
    print("\nAll embeddings generated successfully!")

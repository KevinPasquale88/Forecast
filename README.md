# Forecast — Documentazione del progetto

Questo repository è organizzato in quattro fasi principali: dataset, preprocessing, embedding, addestramento (classificazione) e valutazione. Di seguito trovi una descrizione concisa di ciascuna fase e istruzioni rapide per eseguire il progetto.

## Dataset
- I dati originali si trovano nella cartella `heart+disease/` e sono i file:
  - `processed.cleveland.data`, `processed.hungarian.data`, `processed.switzerland.data`, `processed.va.data`
- Il caricamento e l'unione dei file è gestito da `preprocessing.py::load_heart_disease()`.

## Preprocessing
- File principale: [preprocessing.py](preprocessing.py)
- Passaggi eseguiti:
  - gestione dei valori mancanti (imputazione: mediana per numeriche, moda per categoriche)
  - scaling delle feature numeriche (`StandardScaler`)
  - one-hot encoding per le feature categoriche
  - bilanciamento della classe target tramite `SMOTE`
- Funzioni utili:
  - `clean_data(X, y)` — costruisce e adatta la pipeline di preprocessing
  - `data_processed(...)` — genera il DataFrame trasformato pronto per ulteriori analisi
  - `record_to_text(row)` — converte una riga in una stringa testuale (usata per generare embeddings)

## Embedding
- File principale: [embedding.py](embedding.py)
- Descrizione:
  - Le rappresentazioni vettoriali vengono generate (nel flusso originale) usando il client `ollama` in `main.py`.
  - La lista dei modelli provvisti è definita in `embedding.py` (variabili `models_ollama`).
  - Gli embeddings e le etichette vengono salvati in file `.npy` tramite `save_embeddings_to_npy()` e `save_embeddindgs_label_to_npy()`.

## Addestramento / Classificazione
- File principale: [classification.py](classification.py)
- Approccio:
  - Classificatore base: `LogisticRegression` (max_iter=2000)
  - Validazione: `StratifiedKFold` con 5 fold
  - Per ogni fold si calcola la soglia ottimale massimizzando l'F1 dalla curva precision-recall
  - Metriche riportate: Accuracy, Macro-F1, ROC-AUC e soglia media ottimizzata
  - Stima dell'incertezza tramite bootstrap sulle metriche (vedi `bootstrap_metrics`)

## Valutazione e Visualizzazione
- File principale: [evaluation.py](evaluation.py)
- Grafici prodotti:
  - PCA 2D dei vettori pre-elaborati
  - ROC curve per modello
  - Confusion matrix
  - Boxplot delle metriche bootstrap

## Esecuzione
1. Attiva l'ambiente virtuale:
```bash
source env/bin/activate
```
2. Esegui lo script principale:
```bash
python main.py
```

Nota: la generazione di embeddings usa `ollama.Client` in `main.py` — assicurati che il servizio/endpoint richiesto sia disponibile e configurato (se necessario).

## Requisiti
- Controlla [requirements.txt](requirements.txt) per le dipendenze richieste.

## Struttura dei file
- `main.py` — orchestratore che esegue tutte le fasi
- `preprocessing.py` — caricamento e pipeline di preprocessing
- `embedding.py` — configurazione modelli e salvataggio embeddings
- `classification.py` — training e validazione del classificatore
- `evaluation.py` — funzioni di plotting e bootstrap

Se vuoi, posso aggiungere una sezione con esempi di output o includere i comandi per rigenerare solo gli embeddings senza rieseguire l'intera pipeline.

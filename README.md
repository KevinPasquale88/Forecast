# Forecast — Project Documentation

## Thesis Title
Automatic disease prediction from clinical datasets using a local pipeline based on modern encoders and Ollama.

## Project Description
This thesis aims to build a fully local classification pipeline using the same technology as the advisor's work: a Python + Ollama environment that runs language or embedding models without relying on external APIs. The goal is to predict the presence or absence of a pathology from structured clinical data while ensuring privacy and full reproducibility.

This repository is organized into four main phases: dataset, preprocessing, embedding, training (classification), and evaluation. Below is a concise description of each phase and quick instructions to run the project.

## Dataset
- The original data is stored in the `heart+disease/` folder and includes:
  - `processed.cleveland.data`, `processed.hungarian.data`, `processed.switzerland.data`, `processed.va.data`
- Loading and concatenating these files is handled by `preprocessing.py::load_heart_disease()`.

## Preprocessing
- Main file: [preprocessing.py](preprocessing.py)
- Steps performed:
  - handle missing values (median imputation for numeric features, most frequent imputation for categorical features)
  - scale numeric features (`StandardScaler`)
  - one-hot encode categorical features
  - balance the target class using `SMOTE`
- Useful functions:
  - `clean_data(X, y)` — builds and fits the preprocessing pipeline
  - `data_processed(...)` — generates the transformed DataFrame ready for analysis
  - `record_to_text(row)` — converts a row into a text description (used for embedding generation)

## Embedding
- Main file: [embedding.py](embedding.py)
- Description:
  - Vector representations are generated using the `ollama` client in `main.py`.
  - The available model list is defined in `embedding.py` via `models_ollama`.
  - Embeddings and labels are saved to `.npy` files using `save_embeddings_to_npy()` and `save_labels_to_npy()`.

## Training / Classification
- Main file: [classification.py](classification.py)
- Approach:
  - Base classifier: `LogisticRegression` (`max_iter=2000`)
  - Validation: `StratifiedKFold` with 5 folds
  - Each fold selects an optimal threshold by maximizing F1 from the precision-recall curve
  - Reported metrics: Accuracy, Macro-F1, ROC-AUC, and mean optimized threshold
  - Uncertainty estimation via bootstrap on metrics (see `bootstrap_metrics`)

## Evaluation and Visualization
- Main file: [evaluation.py](evaluation.py)
- Generated plots:
  - 2D PCA of preprocessed vectors
  - ROC curves for each model
  - Confusion matrices
  - Bootstrap metric boxplots

## Execution
1. Activate the virtual environment:
```bash
source env/bin/activate
```
2. Run the main script:
```bash
python main.py
```

Note: embedding generation uses `ollama.Client` in `main.py` — ensure the required service/endpoint is available and configured.

## Requirements
- Check [requirements.txt](requirements.txt) for required dependencies.

## File Structure
- `main.py` — orchestrates all phases
- `preprocessing.py` — data loading and preprocessing pipeline
- `embedding.py` — model configuration and embedding saving
- `classification.py` — classifier training and validation
- `evaluation.py` — plotting and bootstrap utilities

If you want, I can also add an example outputs section or commands to regenerate only embeddings without rerunning the full pipeline.

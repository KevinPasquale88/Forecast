# Forecast — Project Documentation

## Thesis Title
Automatic disease prediction from clinical datasets using a local pipeline based on modern encoders and Ollama.

## Project Description
This thesis aims to build a fully local classification pipeline using the same technology as the advisor's work: a Python + Ollama environment that runs language or embedding models without relying on external APIs. The goal is to predict the presence or absence of a pathology from structured clinical data while ensuring privacy and full reproducibility.

The pipeline runs in six phases: preprocessing, embedding generation, classification, evaluation, error analysis, and statistical testing, followed by an automated markdown report. Below is a concise description of each phase, the research questions the pipeline is designed to answer, and quick instructions to run the project.

## Research Questions

**Primary research question:**
> L'utilizzo di embedding semantici generati localmente tramite modelli linguistici consente di supportare efficacemente task di classificazione clinica a partire da dati strutturati convertiti in linguaggio naturale?

**Secondary research question:**
> Gli embedding model specializzati per il dominio biomedicale producono rappresentazioni semantiche più efficaci rispetto ai modelli general-purpose nel task di classificazione clinica basato su dati tabellari trasformati in testo?

The secondary question is answered directly by the pipeline's model configuration in [function.py](function.py), which tags every encoder with a `family`:
- **general-purpose**: `e5-base`, `e5-large`, `gte-base`, `gte-large` (`models_ollama`)
- **biomedical**: `bioclinicalbert`, `pubmedbert` (`models_medical`)
- **biomedical sentence-transformers**: `sentence-biobert` (`models_medical`)

This grouping drives the Model Family Comparison plot (see [Evaluation and Visualization](#evaluation-and-visualization)) and the color palette used across every figure.

## Dataset

### Origine e Descrizione
The dataset used in this project is the **UCI Heart Disease dataset** from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/45/heart+disease). 

**Dataset Characteristics:**
- **Multicentre composition**: Data collected from four different international medical centers:
  - Cleveland Clinic Foundation (USA)
  - Hungarian Institute of Cardiology, Budapest
  - University Hospital, Zurich, Switzerland
  - V.A. Medical Center, Long Beach VA (USA)
  
- **Clinical context**: Structured clinical and diagnostic data from cardiac patients undergoing clinical evaluation for heart disease presence/absence.

- **Total records**: 297 instances from combined centers
- **Original attributes**: 76 features in the full dataset
- **Features commonly used**: 14 clinical attributes (as per literature standard)
- **Target**: Binary classification (0 = no disease, 1 = disease present)

### Dataset Composition and Features
The preprocessed version used in this project (`processed.cleveland.data`, `processed.hungarian.data`, `processed.switzerland.data`, `processed.va.data`) includes 14 clinical features:
1. Age
2. Sex
3. Chest pain type
4. Resting blood pressure
5. Serum cholesterol
6. Fasting blood sugar
7. Resting electrocardiographic results
8. Maximum heart rate achieved
9. Exercise-induced angina
10. ST depression induced by exercise
11. Slope of the ST segment
12. Number of major vessels
13. Thalassemia
14. Diagnosis (target variable)

Loading and concatenating these files is handled by `preprocessing.py::load_heart_disease()`.

### Data Characteristics
- **Data type**: Structured/tabular clinical records (NOT raw clinical notes)
- **Original dataset attributes**: 76 features available in the full UCI repository
- **Processing versions**: This project uses official preprocessed versions that have undergone initial cleaning and standardization
- **Data accessibility**: Data represents historical clinical records with appropriate de-identification

### Ethical and Privacy Considerations
- The dataset is de-identified and publicly available
- Data has been previously anonymized and follows standard ethical guidelines for medical research datasets
- The dataset should be cited appropriately when used in publications (see References)

### Limitations
- **Temporal**: Historical data from the 1980s-1990s; may not reflect current diagnostic standards
- **Representation**: Imbalanced class distribution in the original data (addressed via SMOTE in preprocessing)
- **Geographic bias**: Data predominantly from Western medical centers
- **Missing values**: Some records contain missing attributes handled through imputation

### Methodological Context
**Important clarification**: This project's contribution is NOT a direct classification task on tabular data. Rather, it implements a **tabular-to-text transformation pipeline** where:
1. Structured clinical records are converted into natural language descriptions
2. Semantic embeddings from modern biomedical encoders capture domain knowledge
3. Classification leverages the transformed representation space

This approach bridges structured clinical data and semantic embeddings, enabling investigation of how modern language models capture clinical domain knowledge.

### References
- **Dataset source**: Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1988). Heart Disease. UCI Machine Learning Repository. https://doi.org/10.24432/C52P4W
- **Original publications**: Detrano, R., Janosi, A., Steinbrunn, W., Pfisterer, M., Schmid, K., Sandhu, S., ... & Froelicher, V. (1989). "International application of a new probability algorithm for the diagnosis of coronary artery disease." American Journal of Cardiology, 64(5), 304-310.

## Prerequisites
- **Python**: 3.14 (the committed virtual environment in `env/` is built against this version; earlier 3.x versions are untested).
- **Platform**: developed and verified on Apple Silicon (arm64/macOS). No ARM-specific issues have been encountered with the current dependency set (PyTorch, sentence-transformers, umap-learn all ship arm64 wheels); on Intel/Linux the same steps should apply, but this hasn't been verified.
- **Ollama**: required and must be installed and running locally — the general-purpose embedding models (E5, GTE) are served through it. Install from [ollama.com](https://ollama.com).
- **Hugging Face access**: the biomedical models (`bioclinicalbert`, `pubmedbert`, `sentence-biobert`) are downloaded via `sentence-transformers`/`huggingface_hub`, which requires a `.env` file in the project root with `HF_READ_TOKEN` and `OFFLINE_MODE` (see [Installation](#installation), step 5).
- **Hardware**: no GPU required. The slow steps are local embedding generation (Ollama inference + downloading/running the biomedical transformer models on CPU) and the 10,000-iteration bootstrap in the evaluation phase — expect the full pipeline to take from several minutes to tens of minutes depending on machine specs. At least ~8 GB of free RAM is recommended for the HuggingFace models.

## Installation
1. Clone the repository and move into it.
2. Create and activate the virtual environment:
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install and start Ollama, then pull the general-purpose models used by the pipeline (`models_ollama` in `function.py`):
   ```bash
   ollama serve &
   ollama pull yxchia/multilingual-e5-base
   ollama pull twwch/m3e-base
   ollama pull zyw0605688/gte-large-zh
   ollama pull jeffh/intfloat-multilingual-e5-large-instruct:q8_0
   ```
5. Create a `.env` file in the project root with the Hugging Face token and offline-mode flag used for the biomedical model calls in `embedding.py`:
   ```
   HF_READ_TOKEN=your_token_here
   OFFLINE_MODE=0
   ```
   `HF_READ_TOKEN` authenticates with Hugging Face (needed the first time each biomedical model is downloaded, or if a model is gated); `OFFLINE_MODE=1` forces `sentence-transformers` to use only the local cache (set it to `1` after the models have already been downloaded once, to skip the network check).
6. Run the pipeline:
   ```bash
   python main.py
   ```

Alternatively, `./run_all.sh` automates steps 2–6 end-to-end (creates/activates `env`, installs dependencies, starts Ollama, pulls the required models, and runs `main.py`).

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
- Also persists `datas/preprocessing/X_train_raw.csv`: the raw (pre-encoding) clinical features in the exact row order used for embedding generation, later used by the error analysis phase to trace predictions back to real patient records.

## Embedding
- Main file: [embedding.py](embedding.py)
- Description:
  - Vector representations are generated using the `ollama` client for general-purpose models, and `sentence-transformers` for biomedical models.
  - The available model list is defined in `function.py` via `models_ollama` (general-purpose) and `models_medical` (biomedical), combined into `models_all`.
  - Embeddings and labels are saved to `.npy` files using `save_embeddings_to_npy()` and `save_labels_to_npy()`.

## Training / Classification
- Main file: [classification.py](classification.py)
- Approach:
  - Base classifier: `LogisticRegression` (`max_iter=2000`)
  - Validation: `StratifiedKFold` with 5 folds
  - Each fold selects an optimal threshold by maximizing F1 from the precision-recall curve
  - Reported metrics: Accuracy, Macro-F1, ROC-AUC, and mean optimized threshold
  - Uncertainty estimation via bootstrap on metrics (see `bootstrap_metrics` in `evaluation.py`)
  - Per-fold validation indices are also saved (`{model}_val_idx.npy`), so every prediction can be traced back to its original clinical record for error analysis

## Evaluation and Visualization
- Main file: [evaluation.py](evaluation.py)
- Generated plots (all saved as 300 DPI PNG, white background, colorblind-safe family-consistent palette):
  - UMAP 2D projection of preprocessed vectors (`datas/graphics/UMAP_*`)
  - Unified ROC curve comparison across all models, including biomedical ones (`datas/graphics/ROC_comparison`)
  - Confusion matrices per model (`datas/graphics/CM_*`)
  - Bootstrap metric boxplots per model (`datas/results/BOXPLOT_metrics`)
  - Mean ± bootstrap 95% confidence interval (and ± 1 SD) per model, per metric (`datas/results/MeanCI_metrics`)
  - Model family comparison: pooled bootstrap distributions for general-purpose vs. biomedical vs. biomedical sentence-transformer encoders (`datas/results/FamilyComparison_metrics`)

## Error Analysis
- Main file: [error_analysis.py](error_analysis.py)
- Beyond aggregate metrics, this phase traces every misclassification back to the real clinical record using the `val_idx` saved during training, and computes:
  - **Per-model error rates**: false positive rate and false negative rate for every model (`datas/results/error_summary.csv`, plotted in `ErrorAnalysis_rates`)
  - **Misclassified records**: the actual false positive / false negative clinical records per model (`datas/results/{model}_false_positives.csv`, `{model}_false_negatives.csv`)
  - **Hardest cases**: the patient records misclassified most often across models — candidates for intrinsically ambiguous or atypical presentations (`datas/results/hardest_cases.csv`)
  - **Feature deviation**: the standardized mean difference of each numeric clinical feature (age, blood pressure, cholesterol, max heart rate, ST depression, number of major vessels) between misclassified and correctly classified cases, pooled across all models — highlighting which features are associated with classification ambiguity (`datas/results/feature_deviation.csv`, plotted in `ErrorAnalysis_feature_deviation`)
- All of the above are included in the generated report (see `generatereport.py`), so the discussion of failure modes is grounded in the actual run's data rather than a fixed narrative.

## Test Statistici

### Overview
Statistical significance testing is performed to rigorously compare classification performance across different embedding models. This phase validates whether observed performance differences are statistically significant or due to chance variation.

### Methodologia
- **Main file**: [statisticaltest.py](statisticaltest.py)
- **Bootstrap framework**: Builds upon bootstrap metrics generated during classification phase
- **Test sample size**: 10,000 bootstrap resamples per model and metric
- **Comparison scope**: All pairwise model comparisons

### Metriche Testate
The following performance metrics are compared across all model pairs:
1. **Accuracy (acc)**: Overall classification correctness
2. **F1-Score (f1)**: Harmonic mean of precision and recall (macro-averaged)
3. **ROC-AUC (auc)**: Area under the receiver operating characteristic curve

### Test Statistici Implementati

#### 1. Wilcoxon Signed-Rank Test
**Purpose**: Non-parametric test for paired samples; does not assume normality.

**When used**: 
- Comparing two related samples (bootstrap scores from same cross-validation folds)
- Robust to outliers and non-normal distributions
- More appropriate for clinical/medical data which often deviates from normality

**Hypotheses**:
- H₀: No difference in distribution between model A and model B
- H₁: Significant difference between distributions

**Output**:
- Test statistic (W)
- P-value
- Significance flag (1 if p < 0.05, else 0)

#### 2. Paired t-test (Dependent Samples t-test)
**Purpose**: Parametric test for comparing means of two related samples.

**When used**:
- As a complementary parametric approach
- Assumes approximately normal distribution
- More powerful than Wilcoxon if normality assumption holds

**Hypotheses**:
- H₀: μ_A = μ_B (means are equal)
- H₁: μ_A ≠ μ_B (means differ significantly)

**Output**:
- Test statistic (t)
- P-value
- Significance flag (1 if p < 0.05, else 0)

#### 3. DeLong Test
**Purpose**: Compares ROC-AUC between two correlated models evaluated on the same labels.

**When used**:
- Directly testing whether the AUC difference between two embedding models is statistically significant
- Implemented via `MLstatkit.Delong_test`

**Output**:
- z-statistic, p-value, AUC for each model, and the AUC delta

### Interpretazione dei Risultati
Results are saved in three CSV files:
- `datas/results/wilcoxon_comparison.csv` — Wilcoxon signed-rank test results
- `datas/results/ttest_comparison.csv` — Paired t-test results
- `datas/results/delong_comparison.csv` — DeLong AUC comparison results

**Key columns** (Wilcoxon/t-test):
- `metric`: Performance metric being compared (acc, f1, auc)
- `model_a`, `model_b`: Models in comparison
- `mean_a`, `mean_b`: Mean bootstrap scores for each model
- `statistic`: Test statistic value
- `p_value`: Statistical significance (p-value)
- `significant`: Binary flag for α = 0.05 significance level

**Interpretation guidelines**:
- **p_value < 0.05**: Statistically significant difference (reject H₀)
- **p_value ≥ 0.05**: No statistically significant difference (fail to reject H₀)
- **significant = 1**: Difference is significant at 95% confidence level
- **significant = 0**: Difference is not statistically significant

### Significato Clinico vs. Statistico
**Important distinction**:
- **Statistical significance** (p < 0.05): Difference is unlikely due to random chance
- **Clinical significance**: Difference is practically meaningful for clinical decision-making
  - Example: A 0.5% difference in accuracy may be statistically significant but not clinically relevant
  - Example: A 5% difference in sensitivity may be both statistically and clinically significant (especially for FN implications)

### Robustezza del Test
**Why Wilcoxon, paired t-test, and DeLong together**:
- Provides cross-validation of results through complementary statistical approaches
- Wilcoxon is more robust if normality assumption is violated
- Paired t-test has higher power if normality assumption holds
- DeLong is AUC-specific and accounts for the correlation between models evaluated on the same labels
- Consistency between tests strengthens confidence in results

**Bootstrap validation**:
- 10,000 resamples provides stable estimates of metric distributions
- StratifiedKFold ensures representative sampling
- Reduces false discovery rate from repeated comparisons

## `datas/` Folder Structure
| Folder | Contents |
|---|---|
| `datas/heart+disease/` | Raw UCI source files (`processed.cleveland.data`, etc.) |
| `datas/preprocessing/` | `preprocessed_data.npy` / `preprocessed_labels.npy` (encoded features) and `X_train_raw.csv` (raw clinical features, row-aligned with embeddings) |
| `datas/embeddings/` | Per-model embedding vectors (`*_embeddings.npy`) and labels (`*_embeddings_labels.npy`) |
| `datas/results/` | Per-model predictions (`*_y_true/_y_score/_y_pred/_val_idx.npy`), bootstrap arrays (`*_boot_*.npy`), comparison tables (`encoder_comparison_summary.csv`, `wilcoxon/ttest/delong_comparison.csv`), error-analysis outputs (`error_summary.csv`, `hardest_cases.csv`, `*_false_positives/negatives.csv`, `feature_deviation.csv`), and the plots saved directly into this folder (boxplot, mean±CI, family comparison, error analysis) |
| `datas/graphics/` | UMAP, ROC comparison, confusion matrix, and heatmap plots (PNG) |
| `datas/reports/` | The generated `report.md` |

## Execution
The full pipeline (preprocessing → embedding → classification → evaluation → error analysis → statistical tests → report) is orchestrated by `main.py`:
```bash
source env/bin/activate
python main.py
```
or, to also automate environment setup and Ollama model downloads:
```bash
./run_all.sh
```
Note: embedding generation for the general-purpose models uses `ollama.Client` in `embedding.py` — ensure the Ollama service is running and the required models have been pulled (see [Installation](#installation)).

## Troubleshooting
- **ARM/x86 mismatch (Apple Silicon)**: make sure `python3` and the virtual environment are built natively for `arm64` (run `python3 -c "import platform; print(platform.machine())"` — it should print `arm64`, not `x86_64`, on Apple Silicon). A Rosetta-translated Python install can cause slow or failing installs of `torch`/`numba`.
- **`ollama pull` / model not found errors**: the general-purpose models must be pulled before running the pipeline (see [Installation](#installation), step 4). Verify with `ollama list`.
- **Hugging Face authentication / gated model errors**: set `HF_READ_TOKEN` in `.env` (see [Installation](#installation), step 5); for fully offline runs after the first download, set `OFFLINE_MODE=1`.
- **`FileNotFoundError` on `.npy` files in `datas/embeddings` or `datas/results`**: an earlier phase hasn't completed successfully yet — rerun `python main.py` from the beginning, or check the console output of the specific phase (embedding generation and classification are the most failure-prone due to external model dependencies).
- **Virtual environment issues**: if `source env/bin/activate` fails, delete the `env/` folder and recreate it (`python3 -m venv env`), then reinstall with `pip install -r requirements.txt`.

## Requirements
- Check [requirements.txt](requirements.txt) for required dependencies.

## File Structure
- `main.py` — orchestrates all phases
- `preprocessing.py` — data loading and preprocessing pipeline
- `embedding.py` — model configuration and embedding saving
- `classification.py` — classifier training and validation
- `evaluation.py` — evaluation, bootstrap, and plotting orchestration
- `error_analysis.py` — traces misclassifications back to clinical records and computes error patterns
- `statisticaltest.py` — Wilcoxon, paired t-test, and DeLong significance tests
- `function.py` — shared configuration (model list/families), plotting style, and plot functions
- `generatereport.py` — assembles the final markdown report
- `run_all.sh` — one-command setup + pipeline execution

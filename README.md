# Forecast — Project Documentation

## Thesis Title
Automatic disease prediction from clinical datasets using a local pipeline based on modern encoders and Ollama.

## Project Description
This thesis aims to build a fully local classification pipeline using the same technology as the advisor's work: a Python + Ollama environment that runs language or embedding models without relying on external APIs. The goal is to predict the presence or absence of a pathology from structured clinical data while ensuring privacy and full reproducibility.

This repository is organized into four main phases: dataset, preprocessing, embedding, training (classification), and evaluation. Below is a concise description of each phase and quick instructions to run the project.

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

## Analisi dell'Errore

### Obiettivi dell'Analisi
Beyond reporting aggregate metrics (accuracy, F1, AUC), this project includes a qualitative analysis of misclassifications to understand:
- **Failure modes**: In which clinical scenarios does the model struggle?
- **Semantic representation limits**: What are the limitations of the embedding space for clinical discrimination?
- **Intrinsic difficulty**: Which cases are inherently harder to classify?
- **Error patterns**: Are there recurring characteristics in misclassified patients?

### Falsi Positivi (False Positives)
**Definition**: Patients predicted as having heart disease but who are actually healthy.

**Clinical implications**:
- Unnecessary interventions and patient anxiety
- Resource allocation inefficiency
- Potential for iatrogenic harm from unnecessary treatments

**Analysis**:
- Identifying feature combinations that trigger false alarms
- Examining whether certain feature patterns (e.g., borderline chest pain + mild hypertension) consistently cause over-prediction
- Comparing semantic representations of FP cases vs. true negative controls

### Falsi Negativi (False Negatives)
**Definition**: Patients predicted as healthy but who actually have heart disease.

**Clinical implications**:
- Delayed diagnosis and potentially severe health consequences
- Most critical from a clinical safety perspective
- May indicate cases where semantic embeddings fail to capture subtle disease indicators

**Analysis**:
- Identifying clinical patterns consistently missed by the model
- Examining feature ranges and feature interactions unique to FN cases
- Assessing whether "atypical presentations" are underrepresented in the embedding space
- Evaluating whether certain patient subgroups (e.g., by age, risk factors) have higher FN rates

### Pattern Ricorrenti nei Pazienti Classificati Male
**Systematic error patterns to investigate**:

1. **By clinical feature**:
   - Which features most frequently contribute to errors?
   - Are errors concentrated in patients with specific feature combinations?
   - Do preprocessing/imputation strategies affect error distribution?

2. **By data centre origin**:
   - Do certain hospital centers have systematically higher error rates?
   - Could this indicate dataset-specific characteristics or diagnostic practice variations?

3. **By patient demographics**:
   - Age-stratified error analysis
   - Sex-based differences in classification performance
   - Risk factor combinations

4. **By embedding model**:
   - Which encoder models produce larger error sets?
   - Are FP and FN distributions consistent across different embedding models?
   - How does semantic representation quality correlate with error rates?

### Feature Cliniche e Ambiguità
**Feature-level analysis**:
- **Boundary cases**: Patients with features near decision thresholds
- **Feature ambiguity**: Clinical features inherently difficult to distinguish between disease/no-disease
  - E.g., chest pain type (overlapping symptom presentations across disease states)
  - ST depression (present in both pathological and benign contexts)
  - Heart rate response to exercise (variable across healthy individuals)

- **Semantic representation gaps**: Some feature combinations might lack discriminative representation in the embedding space
  - Missing nuanced clinical relationships
  - Limited generalization to rare feature combinations
  - Insufficient representation of complex interactions between features

### Limitazioni Metodologiche Identificate
Through error analysis, the following limitations emerge:

1. **Data limitations**:
   - Historical dataset (1980s-1990s) may not reflect modern diagnostic standards
   - Imbalanced class distribution (partially addressed via SMOTE)
   - Missing feature interactions potentially important for diagnosis

2. **Semantic representation limits**:
   - Biomedical encoders trained on natural language may not optimally encode tabular clinical data
   - Text descriptions of structured data might lose important relational information
   - Embedding space dimensionality and learned representations may not capture all clinical nuances

3. **Model limitations**:
   - LogisticRegression assumes linear separability in embedding space
   - Single threshold optimization per fold may not generalize across diverse patient populations
   - Bootstrap uncertainty estimates assume data homogeneity

### Raccomandazioni per Miglioramenti Futuri
- Implement instance-level error explanations (e.g., SHAP, LIME)
- Conduct stratified analysis by risk factors and demographics
- Investigate decision boundary visualization in embedding space
- Explore non-linear classifiers on embedding representations
- Perform ablation studies on feature engineering choices
- Compare error patterns across different embedding models systematically

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

### Interpretazione dei Risultati
Results are saved in two CSV files:
- `datas/results/wilcoxon_comparison.csv` — Wilcoxon signed-rank test results
- `datas/results/ttest_comparison.csv` — Paired t-test results

**Key columns**:
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
**Why both Wilcoxon and paired t-test**:
- Provides cross-validation of results through complementary statistical approaches
- Wilcoxon is more robust if normality assumption is violated
- Paired t-test has higher power if normality assumption holds
- Consistency between tests strengthens confidence in results

**Bootstrap validation**:
- 10,000 resamples provides stable estimates of metric distributions
- StratifiedKFold ensures representative sampling
- Reduces false discovery rate from repeated comparisons

### Execution in Pipeline
Statistical testing is **Phase 5** of the main pipeline (after evaluation, before report generation):
```
Phase 1: Preprocessing → Phase 2: Embedding → Phase 3: Classification
    → Phase 4: Evaluation → Phase 5: Statistical Tests → Phase 6: Report Generation
```

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

# Datasets

The pipeline supports two clinical datasets, selected via `--dataset {heart_disease,diabetes130}` (default `heart_disease`). Each dataset gets its own output tree under `datas/<dataset>/` (see [main README](../README.md#datas-folder-structure)), so runs never overwrite each other.

## Dataset 1 — UCI Heart Disease

## Origin and Description
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

## Dataset Composition and Features
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

## Data Characteristics
- **Data type**: Structured/tabular clinical records (NOT raw clinical notes)
- **Original dataset attributes**: 76 features available in the full UCI repository
- **Processing versions**: This project uses official preprocessed versions that have undergone initial cleaning and standardization
- **Data accessibility**: Data represents historical clinical records with appropriate de-identification

## Ethical and Privacy Considerations
- The dataset is de-identified and publicly available
- Data has been previously anonymized and follows standard ethical guidelines for medical research datasets
- The dataset should be cited appropriately when used in publications (see References)

## Limitations
- **Temporal**: Historical data from the 1980s-1990s; may not reflect current diagnostic standards
- **Representation**: Imbalanced class distribution in the original data (addressed via SMOTENC in preprocessing)
- **Geographic bias**: Data predominantly from Western medical centers
- **Missing values**: Some records contain missing attributes handled through imputation. Beyond the `?` placeholder, some source files (Switzerland, Hungary) encode missing cholesterol/resting blood pressure as `0`, which is not a physiologically valid value for either — `load_heart_disease()` in [preprocessing.py](../preprocessing.py) converts these to `NaN` before imputation

## Methodological Context
**Important clarification**: This project's contribution is NOT a direct classification task on tabular data. Rather, it implements a **tabular-to-text transformation pipeline** where:
1. Structured clinical records are converted into natural language descriptions
2. Semantic embeddings from modern biomedical encoders capture domain knowledge
3. Classification leverages the transformed representation space

This approach bridges structured clinical data and semantic embeddings, enabling investigation of how modern language models capture clinical domain knowledge.

## References
- **Dataset source**: Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1988). Heart Disease. UCI Machine Learning Repository. https://doi.org/10.24432/C52P4W
- **Original publications**: Detrano, R., Janosi, A., Steinbrunn, W., Pfisterer, M., Schmid, K., Sandhu, S., ... & Froelicher, V. (1989). "International application of a new probability algorithm for the diagnosis of coronary artery disease." American Journal of Cardiology, 64(5), 304-310.

---

## Dataset 2 — Diabetes 130-US Hospitals

### Origin and Description
The **Diabetes 130-US Hospitals dataset (1999–2008)** from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008) contains records of hospital encounters for patients with diabetes, collected across 130 US hospitals and integrated delivery networks over 10 years.

**Dataset Characteristics:**
- **Scale**: ~100,000 hospital encounters in the original file; the pipeline stratified-samples **20,000 encounters** by default (`sample_size` in `load_diabetes130()`, [function.py](../function.py)) to keep runtime tractable
- **Clinical context**: Inpatient encounters for diabetic patients, including admission/discharge circumstances, lab results, medications, and prior utilization of care
- **Target**: Binarized to the standard early-readmission benchmark task — **1 = readmitted within 30 days, 0 = readmitted later or not at all** (`readmitted` column, binarized in `load_diabetes130()`)

### Dataset Composition and Features
The raw file has ~50 columns; most are near-constant drug-dosage flags (e.g. `examide`, `citoglipton`) or high-missingness identifiers (`weight`, `payer_code`, `patient_nbr`) that add no signal, so only a clinically meaningful subset of **19 features** is kept (`columns_diabetes130` in [function.py](../function.py)):

| Category | Features |
|---|---|
| Demographics | `race`, `gender`, `age` |
| Admission context | `admission_type_id`, `discharge_disposition_id`, `admission_source_id` |
| Encounter utilization (numeric) | `time_in_hospital`, `num_lab_procedures`, `num_procedures`, `num_medications`, `number_outpatient`, `number_emergency`, `number_inpatient`, `number_diagnoses` |
| Lab / medication (categorical) | `max_glu_serum`, `A1Cresult`, `insulin`, `change`, `diabetesMed` |
| Target | `readmitted` |

Loading, column filtering, target binarization, and stratified sampling are handled by `load_diabetes130()` in [function.py](../function.py). The text conversion for embedding is handled by `record_to_text_diabetes130()` in [embedding.py](../embedding.py).

### Data Characteristics
- **Data type**: Structured/tabular hospital encounter records (NOT raw clinical notes)
- **Missing values**: Encoded as `?` in the source CSV and loaded as `NaN` (`na_values="?"`), then handled through the same imputation pipeline as the heart disease dataset

### Ethical and Privacy Considerations
- The dataset is de-identified and publicly available
- Data represents historical (1999–2008) hospital encounters and follows standard ethical guidelines for medical research datasets

### Limitations
- **Temporal**: Data from 1999–2008; may not reflect current admission/discharge practices or diagnostic coding
- **Sampling**: The pipeline uses a stratified 20,000-record sample rather than the full ~100,000 encounters, for runtime reasons — results should be interpreted with this in mind
- **Feature reduction**: Only 19 of the ~50 original columns are retained; some potentially informative but sparse or high-cardinality fields (e.g. `diag_1`/`diag_2`/`diag_3` ICD codes, `medical_specialty`) are excluded
- **Task framing**: The readmission target is binarized to the "within 30 days" benchmark definition, which is the standard framing in the literature but discards information about later readmissions

### Methodological Context
As with the heart disease dataset, this project's contribution is a **tabular-to-text transformation pipeline**: structured hospital encounter records are converted into natural language descriptions, embedded with modern encoders, and classified — enabling the same general-purpose vs. biomedical model comparison on a second, larger and differently-structured clinical task (readmission risk rather than diagnosis).

### References
- **Dataset source**: Strack, B., DeShazo, J.P., Gennings, C., Olmo, J.L., Ventura, S., Cios, K.J., & Clore, J. (2014). Diabetes 130-US Hospitals for Years 1999-2008. UCI Machine Learning Repository. https://doi.org/10.24432/C5230J
- **Original publication**: Strack, B., et al. (2014). "Impact of HbA1c Measurement on Hospital Readmission Rates: Analysis of 70,000 Clinical Database Patient Records." BioMed Research International, 2014.

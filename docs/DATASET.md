# Dataset — UCI Heart Disease

## Origine e Descrizione
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

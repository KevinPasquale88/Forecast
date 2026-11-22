# Datasets

The pipeline supports two public clinical datasets, selected with `--dataset {heart_disease,diabetes130}` (default `heart_disease`). Each gets its own output tree under `datas/<dataset>/`, so runs never overwrite each other. Both are loaded in [function.py](../function.py) (`load_heart_disease()`, `load_diabetes130()`) and converted into sentences in [embedding.py](../embedding.py) (`record_to_text_heart_disease()`, `record_to_text_diabetes130()`).

The two datasets were chosen for opposite characteristics: a diagnostic task with direct measurements of the disease, strong signal and balanced classes (Heart Disease), and a prognostic task with administrative variables, weak signal and 9% positives (Diabetes130).

---

## Dataset 1 — UCI Heart Disease

### Origin

The dataset comes from the study by Detrano et al. (1989), which developed a probability algorithm for the diagnosis of coronary artery disease at the Cleveland Clinic and tested it on three external centres. The UCI repository version has 76 attributes; almost all the literature, and this project, uses the 14 of the "processed" files. Many works use Cleveland only (303 records, 297 without missing `ca`/`thal`); this project pools the four centres.

| Centre | File | Records | Disease prevalence |
|---|---|---|---|
| Cleveland Clinic Foundation (USA) | `processed.cleveland.data` | 303 | 45.9% |
| Hungarian Institute of Cardiology, Budapest | `processed.hungarian.data` | 294 | 36.1% |
| University Hospitals Zurich and Basel (Switzerland) | `processed.switzerland.data` | 123 | 93.5% |
| V.A. Medical Center, Long Beach (USA) | `processed.va.data` | 200 | 74.5% |
| **Total** | | **920** | **55.3%** |

After the stratified 80/20 split: 736 training and 184 test records.

### Target

`num` is the angiography result: 0 if no major vessel has more than 50% diameter narrowing, 1–4 otherwise. The pipeline binarizes it: `num > 0` → disease present (1).

### Features

| Feature | Test or source | Values | Text written by the pipeline |
|---|---|---|---|
| `age` | History | years | `63 years old` |
| `sex` | History | 1 male, 0 female | `Male patient` / `Female patient` |
| `cp` | Chest pain history | 1 typical angina, 2 atypical angina, 3 non-anginal pain, 4 asymptomatic | `chest pain type: asymptomatic` |
| `trestbps` | Resting blood pressure | mm Hg | `resting blood pressure: 145 mm Hg` |
| `chol` | Blood test | serum cholesterol, mg/dl | `serum cholesterol: 233 mg/dl` |
| `fbs` | Blood test | fasting blood sugar > 120 mg/dl | `fasting blood sugar > 120 mg/dl: yes` |
| `restecg` | Resting ECG | 0 normal, 1 ST-T wave abnormality, 2 left ventricular hypertrophy | `resting electrocardiographic results: normal` |
| `thalach` | Exercise test | maximum heart rate | `maximum heart rate achieved: 150` |
| `exang` | Exercise test | exercise-induced angina | `exercise-induced angina: no` |
| `oldpeak` | Exercise test | ST depression, mm | `ST depression induced by exercise: 2.3` |
| `slope` | Exercise test | 1 upsloping, 2 flat, 3 downsloping | `slope of the peak exercise ST segment: flat` |
| `ca` | Fluoroscopy | major vessels coloured (0–3) | `number of major vessels colored by fluoroscopy: 0` |
| `thal` | Thallium stress scintigraphy | 3 normal, 6 fixed defect, 7 reversible defect | `thallium stress test: reversible defect` |

`thal` is the result of the thallium stress test, not thalassemia, despite how it is described in many secondary sources.

### Missing values

`?` in the source files is read as missing. In some files missing cholesterol and resting blood pressure are encoded as `0`, which is not physiologically possible: `load_heart_disease()` converts them to missing. Missing values are **not imputed**: they are written as `not recorded` in the sentence.

Missingness depends strongly on the centre:

| Centre | `ca` | `thal` | `slope` | `chol` |
|---|---|---|---|---|
| Cleveland | 1% | 1% | 0% | 0% |
| Hungary | 99% | 90% | 65% | 8% |
| Switzerland | 96% | 42% | 14% | 100% |
| Long Beach VA | 99% | 83% | 51% | 28% |

In the training split: `ca` 65.9%, `thal` 51.8%, `slope` 32.7%, `chol` 21.6%, `fbs` 9.2%, `oldpeak` 7.1%, `trestbps` 6.8%, `thalach` and `exang` 6.4%.

Because both missingness and prevalence depend on the centre, `not recorded` can indirectly reveal the centre and therefore part of the outcome. The supplementary-analysis phase of the pipeline (phase 8, `centre_analysis.csv` and `non_clinical_signal.csv`) measures this: the centre prevalence alone gives ROC-AUC 0.70, missingness indicators alone 0.74, while the encoders reach 0.86–0.89 inside Cleveland, where almost nothing is missing.

### Limitations

- Late-1980s data; diagnostic criteria and populations have changed.
- Very different prevalence across centres (Switzerland has 7 healthy patients in the training split).
- `ca` and `thal`, among the strongest predictors, are missing for about two thirds of the records.
- Small sample: the 184-record test split gives AUC estimates with roughly ±0.04 uncertainty.

### References

- Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1988). Heart Disease. UCI Machine Learning Repository. https://doi.org/10.24432/C52P4W
- Detrano, R., et al. (1989). International application of a new probability algorithm for the diagnosis of coronary artery disease. American Journal of Cardiology, 64(5), 304–310.

---

## Dataset 2 — Diabetes 130-US Hospitals (1999–2008)

### Origin

Hospital encounters of diabetic patients from 130 US hospitals and integrated delivery networks, extracted from the Health Facts database (Strack et al., 2014): 101,766 encounters, about 50 columns. The original study analyses the association between HbA1c measurement during the stay and readmission.

### Cleaning (`load_diabetes130()`)

| Step | Reason | Encounters left |
|---|---|---|
| Original file | — | 101,766 |
| Drop discharges to hospice or death (`discharge_disposition_id` 11, 13, 14, 19, 20, 21) | Readmission is not defined for them | 99,343 |
| Keep the first encounter per patient (`patient_nbr`) | Independent observations; no patient in both training and test | 69,990 |
| Stratified sample (`sample_size=20000`, seed 42) | Embedding time for seven encoders | 20,000 |

`"Unknown/Invalid"` gender becomes missing. The CSV is read with `keep_default_na=False`: only `?` is missing, while `"None"` in `max_glu_serum` and `A1Cresult` means "test not performed" and is kept as a category (95.2% and 81.6% of encounters). After the stratified 80/20 split: 16,000 training and 4,000 test encounters.

### Target

`readmitted` has three values: `<30`, `>30`, `NO`. The pipeline uses the standard early-readmission task: `<30` → 1, everything else → 0. Prevalence drops from 11.2% in the raw file to 9.0% after cleaning, because patients with many encounters now count once.

### Features (19, `columns_diabetes130` in `function.py`)

| Group | Features | Notes |
|---|---|---|
| Demographics | `race`, `gender`, `age` | age in ten-year bands, e.g. `[60-70)` |
| Admission | `admission_type_id`, `discharge_disposition_id`, `admission_source_id` | numeric codes (meaning in `IDS_mapping.csv`), written as numbers in the text |
| Utilization | `time_in_hospital`, `num_lab_procedures`, `num_procedures`, `num_medications`, `number_outpatient`, `number_emergency`, `number_inpatient`, `number_diagnoses` | counts |
| Lab tests | `max_glu_serum`, `A1Cresult` | `None` = not performed |
| Therapy | `insulin`, `change`, `diabetesMed` | insulin No/Up/Down/Steady; medication change; any diabetes medication |

Excluded: diagnosis codes (`diag_1/2/3`), medical specialty, weight (97% missing), payer code, the individual drug columns, identifiers. The only real missing values are `race` (about 3%) and a few `gender` values.

### Univariate signal

In the 20,000-encounter sample the strongest single predictor is the number of inpatient stays in the previous year: 8.1% readmitted with none, 13.6% with one, 19.4% with two, 24.2% with three or more. Other variables shift the rate by one or two points, which is why no model exceeds a ROC-AUC of about 0.65.

### Limitations

- 1999–2008 data; admission and coding practices have changed.
- Stratified sample of 20,000 of the 69,990 eligible encounters.
- Administrative variables only; readmission depends on factors that are not in the data (adherence, social support, access to care).
- Admission and discharge codes are written as numbers in the text: meaningless for a language encoder. Translating them with `IDS_mapping.csv` is a planned improvement.

### References

- Strack, B., et al. (2014). Diabetes 130-US Hospitals for Years 1999-2008. UCI Machine Learning Repository. https://doi.org/10.24432/C5230J
- Strack, B., et al. (2014). Impact of HbA1c measurement on hospital readmission rates: analysis of 70,000 clinical database patient records. BioMed Research International, 2014, 781670.

---

## Ethics and privacy

Both datasets are public and de-identified. The pipeline runs entirely locally: no record or sentence is sent to an external service. Health data are a special category under the GDPR (Regulation (EU) 2016/679, art. 9); using real patient data would require a legal basis and safeguards that are outside the scope of this research prototype, which is not intended for clinical use.

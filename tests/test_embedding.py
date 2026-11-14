"""Tests for the pure tabular-to-text conversion functions in embedding.py.

Pure functions — no disk, no network, no Ollama/Hugging Face — are the cheapest, highest-value
place to start testing this project (see the manual, capitolo 48.2). Missing values are never
imputed (see preprocessing.py), so every missing field must read as "not recorded".
"""
import pandas as pd
import pytest

from embedding import (
    record_to_text_heart_disease,
    record_to_text_diabetes130,
    _fmt_num,
    _fmt_cat,
    _fmt_bool,
)


def test_record_to_text_heart_disease_translates_codes():
    row = pd.Series({
        "sex": 1, "age": 63, "cp": 1, "trestbps": 145, "chol": 233,
        "fbs": 1, "restecg": 0, "thalach": 150, "exang": 0,
        "oldpeak": 2.3, "slope": 3, "ca": 0, "thal": 6,
    })
    text = record_to_text_heart_disease(row)
    assert "Male patient, 63 years old" in text
    assert "chest pain type: typical angina" in text
    assert "thallium stress test: fixed defect" in text
    assert "serum cholesterol: 233 mg/dl" in text


def test_record_to_text_heart_disease_handles_missing_value():
    row = pd.Series({
        "sex": 0, "age": 55, "cp": 4, "trestbps": float("nan"), "chol": 200,
        "fbs": 0, "restecg": 0, "thalach": 140, "exang": 1,
        "oldpeak": 1.0, "slope": 2, "ca": 1, "thal": 3,
    })
    text = record_to_text_heart_disease(row)
    assert "resting blood pressure: not recorded" in text


def test_record_to_text_heart_disease_reports_every_missing_field_as_not_recorded():
    row = pd.Series({
        "sex": 1, "age": 60, "cp": 4, "trestbps": 130, "chol": float("nan"),
        "fbs": float("nan"), "restecg": 0, "thalach": 120, "exang": 0,
        "oldpeak": 0.5, "slope": float("nan"), "ca": float("nan"), "thal": 3,
    })
    text = record_to_text_heart_disease(row)
    assert "serum cholesterol: not recorded" in text
    assert "fasting blood sugar > 120 mg/dl: not recorded" in text
    assert "slope of the peak exercise ST segment: not recorded" in text
    assert "number of major vessels colored by fluoroscopy: not recorded" in text
    assert "thallium stress test: normal" in text


def test_record_to_text_diabetes130_basic_fields():
    row = pd.Series({
        "gender": "Female", "age": "[60-70)", "race": "Caucasian",
        "admission_type_id": 1, "discharge_disposition_id": 1, "admission_source_id": 7,
        "time_in_hospital": 4, "num_lab_procedures": 41, "num_procedures": 0,
        "num_medications": 13, "number_outpatient": 0, "number_emergency": 0,
        "number_inpatient": 0, "number_diagnoses": 9, "max_glu_serum": "None",
        "A1Cresult": "None", "insulin": "No", "change": "No", "diabetesMed": "Yes",
    })
    text = record_to_text_diabetes130(row)
    assert "Female patient, age range [60-70)" in text
    assert "race: Caucasian" in text


def test_record_to_text_diabetes130_keeps_none_as_a_category():
    """"None" in max_glu_serum/A1Cresult means "test not performed": it is a category of its own
    and must reach the text as such, not as a missing value."""
    row = pd.Series({
        "gender": "Male", "age": "[50-60)", "race": float("nan"),
        "admission_type_id": 1, "discharge_disposition_id": 1, "admission_source_id": 7,
        "time_in_hospital": 3, "num_lab_procedures": 20, "num_procedures": 1,
        "num_medications": 10, "number_outpatient": 0, "number_emergency": 0,
        "number_inpatient": 0, "number_diagnoses": 7, "max_glu_serum": "None",
        "A1Cresult": ">7", "insulin": "No", "change": "No", "diabetesMed": "Yes",
    })
    text = record_to_text_diabetes130(row)
    assert "max glucose serum test result: None" in text
    assert "A1C test result: >7" in text
    assert "race: not recorded" in text

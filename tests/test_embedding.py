"""Tests for the pure tabular-to-text conversion functions in embedding.py.

Pure functions — no disk, no network, no Ollama/Hugging Face — are the cheapest, highest-value
place to start testing this project (see the manual, capitolo 48.2). These also cover the
missing-value-indicator behaviour introduced alongside preprocessing.py's changes: a value
flagged as imputed must never be presented in the generated text as if it had been observed.
"""
import pandas as pd
import pytest

from embedding import (
    record_to_text_heart_disease,
    record_to_text_diabetes130,
    _masked,
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
    assert "thalassemia: fixed defect" in text
    assert "serum cholesterol: 233 mg/dl" in text


def test_record_to_text_heart_disease_handles_missing_value():
    row = pd.Series({
        "sex": 0, "age": 55, "cp": 4, "trestbps": float("nan"), "chol": 200,
        "fbs": 0, "restecg": 0, "thalach": 140, "exang": 1,
        "oldpeak": 1.0, "slope": 2, "ca": 1, "thal": 3,
    })
    text = record_to_text_heart_disease(row)
    assert "resting blood pressure: not recorded" in text


def test_record_to_text_heart_disease_masks_imputed_value():
    """A value that was imputed (indicator column == 1) must read as "not recorded", exactly
    like a genuinely missing one — even though the imputed number itself (0) looks like a
    perfectly ordinary observation and would otherwise pass through unflagged."""
    row = pd.Series({
        "sex": 1, "age": 60, "cp": 4, "trestbps": 130, "chol": 240,
        "fbs": 0, "restecg": 0, "thalach": 120, "exang": 0,
        "oldpeak": 0.5, "slope": 2, "ca": 0, "thal": 3,
        "ca_missing": 1, "thal_missing": 0,
    })
    text = record_to_text_heart_disease(row)
    assert "number of major vessels colored by fluoroscopy: not recorded" in text
    assert "thalassemia: normal" in text  # thal_missing == 0: the real value is still reported


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


def test_record_to_text_diabetes130_masks_imputed_lab_result():
    row = pd.Series({
        "gender": "Male", "age": "[50-60)", "race": "AfricanAmerican",
        "admission_type_id": 1, "discharge_disposition_id": 1, "admission_source_id": 7,
        "time_in_hospital": 3, "num_lab_procedures": 20, "num_procedures": 1,
        "num_medications": 10, "number_outpatient": 0, "number_emergency": 0,
        "number_inpatient": 0, "number_diagnoses": 7, "max_glu_serum": "Norm",
        "A1Cresult": "Norm", "insulin": "No", "change": "No", "diabetesMed": "Yes",
        "max_glu_serum_missing": 1, "A1Cresult_missing": 1,
    })
    text = record_to_text_diabetes130(row)
    assert "max glucose serum test result: not recorded" in text
    assert "A1C test result: not recorded" in text


@pytest.mark.parametrize("flag_value", [1, 1.0, "1"])
def test_masked_recognizes_true_flag_regardless_of_dtype(flag_value):
    row = pd.Series({"chol": 200, "chol_missing": flag_value})
    assert _masked(row, "chol", lambda v: _fmt_num(v, ndigits=0)) == "not recorded"


def test_masked_falls_through_when_no_indicator_column_present():
    """A field that was never flagged as majority-missing (no "<col>_missing" column at all)
    must behave exactly as before this change: _masked is applied uniformly to every field in
    record_to_text_*(), so this is what keeps it a safe, backward-compatible no-op for them."""
    row = pd.Series({"chol": 200})
    assert _masked(row, "chol", lambda v: _fmt_num(v, ndigits=0)) == "200"

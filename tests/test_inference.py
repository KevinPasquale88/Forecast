"""Tests for the pure/testable logic in inference.py. Functions that call Ollama/Hugging Face
(_embed_one) or fit a classifier on real embeddings (_fit_classifier) are not covered here, for
the same reason embedding.py's network-facing functions aren't: they need a running service or
a real training run, not a unit test (capitolo 48.2 of the manual)."""
import numpy as np
import pandas as pd
import pytest

import inference


@pytest.fixture(autouse=True)
def _clear_inference_caches():
    """Every testable function here takes `dirs` explicitly rather than resolving it itself, so
    tests never touch real project data — but inference.py's module-level caches are keyed only
    by dataset name, not by `dirs`, so two tests using the same dataset name with different
    tmp_path fixtures would otherwise see each other's cached results."""
    inference._missing_eligible_cache.clear()
    inference._classifier_cache.clear()
    yield
    inference._missing_eligible_cache.clear()
    inference._classifier_cache.clear()


def _make_dirs(tmp_path):
    dirs = {
        "preprocessing": str(tmp_path / "preprocessing"),
        "results": str(tmp_path / "results"),
    }
    for d in dirs.values():
        __import__("os").makedirs(d, exist_ok=True)
    return dirs


def test_missing_eligible_columns_are_the_columns_with_empty_cells_in_x_train_raw(tmp_path):
    dirs = _make_dirs(tmp_path)
    pd.DataFrame({
        "age": [63, 50], "sex": [1, 0], "ca": [0, np.nan], "thal": [np.nan, 7],
    }).to_csv(f"{dirs['preprocessing']}/X_train_raw.csv", index=False)
    assert set(inference._missing_eligible_columns("heart_disease", dirs)) == {"ca", "thal"}


def test_missing_eligible_columns_does_not_treat_diabetes_none_category_as_missing(tmp_path):
    dirs = _make_dirs(tmp_path)
    pd.DataFrame({
        "race": ["Caucasian", np.nan], "max_glu_serum": ["None", "Norm"],
    }).to_csv(f"{dirs['preprocessing']}/X_train_raw.csv", index=False)
    assert inference._missing_eligible_columns("diabetes130", dirs) == ["race"]


def test_missing_eligible_columns_raises_when_run_never_happened(tmp_path):
    dirs = _make_dirs(tmp_path)
    with pytest.raises(FileNotFoundError):
        inference._missing_eligible_columns("heart_disease", dirs)


def test_model_config_looks_up_a_configured_model():
    model = inference._model_config("pubmedbert")
    assert model["type"] == "huggingface"


def test_model_config_rejects_an_unknown_model_name():
    with pytest.raises(ValueError):
        inference._model_config("not-a-real-model")


def test_best_model_name_picks_the_highest_mean_auc(tmp_path):
    dirs = _make_dirs(tmp_path)
    pd.DataFrame({
        "model": ["e5-base", "pubmedbert", "gte-large"],
        "auc_mean": [0.84, 0.89, 0.85],
    }).to_csv(f"{dirs['results']}/encoder_comparison_summary.csv", index=False)
    assert inference._best_model_name("heart_disease", dirs) == "pubmedbert"


def test_best_model_name_raises_when_run_never_happened(tmp_path):
    dirs = _make_dirs(tmp_path)
    with pytest.raises(FileNotFoundError):
        inference._best_model_name("heart_disease", dirs)


def _heart_disease_dirs_with_ca_thal_missing_in_training(tmp_path):
    dirs = _make_dirs(tmp_path)
    record = _full_heart_disease_record()
    rows = [record, {**record, "ca": np.nan, "thal": np.nan}]
    pd.DataFrame(rows).to_csv(f"{dirs['preprocessing']}/X_train_raw.csv", index=False)
    return dirs


def _full_heart_disease_record():
    return {
        "age": 63, "sex": 1, "cp": 1, "trestbps": 145, "chol": 233, "fbs": 1,
        "restecg": 0, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 3,
        "ca": 0, "thal": 6,
    }


def test_prepare_row_accepts_a_fully_specified_record(tmp_path):
    dirs = _heart_disease_dirs_with_ca_thal_missing_in_training(tmp_path)
    row, missing = inference._prepare_row(_full_heart_disease_record(), "heart_disease", dirs)
    assert missing == []
    assert row["ca"] == 0
    assert not any(c.endswith("_missing") for c in row.index)


def test_prepare_row_accepts_a_field_missing_in_training_left_as_none(tmp_path):
    dirs = _heart_disease_dirs_with_ca_thal_missing_in_training(tmp_path)
    record = _full_heart_disease_record()
    record["ca"] = None
    row, missing = inference._prepare_row(record, "heart_disease", dirs)
    assert missing == ["ca"]
    assert pd.isna(row["ca"])
    assert row["thal"] == 6


def test_prepare_row_accepts_a_field_missing_in_training_omitted_entirely(tmp_path):
    dirs = _heart_disease_dirs_with_ca_thal_missing_in_training(tmp_path)
    record = _full_heart_disease_record()
    del record["thal"]
    row, missing = inference._prepare_row(record, "heart_disease", dirs)
    assert missing == ["thal"]
    assert pd.isna(row["thal"])


def test_prepare_row_rejects_a_required_field_left_as_none(tmp_path):
    dirs = _heart_disease_dirs_with_ca_thal_missing_in_training(tmp_path)
    record = _full_heart_disease_record()
    record["age"] = None
    with pytest.raises(ValueError, match="age"):
        inference._prepare_row(record, "heart_disease", dirs)


def test_prepare_row_rejects_a_required_field_left_as_nan(tmp_path):
    """Regression test: checking `value is None` alone would let a float NaN on a required field
    slip past validation and reach record_to_text_*() as "not recorded". pd.isna() catches it."""
    dirs = _heart_disease_dirs_with_ca_thal_missing_in_training(tmp_path)
    record = _full_heart_disease_record()
    record["trestbps"] = float("nan")
    with pytest.raises(ValueError, match="trestbps"):
        inference._prepare_row(record, "heart_disease", dirs)


def test_prepare_row_rejects_multiple_missing_required_fields_at_once(tmp_path):
    dirs = _heart_disease_dirs_with_ca_thal_missing_in_training(tmp_path)
    record = _full_heart_disease_record()
    del record["age"]
    del record["sex"]
    with pytest.raises(ValueError, match="age.*sex|sex.*age"):
        inference._prepare_row(record, "heart_disease", dirs)

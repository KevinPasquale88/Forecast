"""Tests for the imputation and missing-value-indicator logic in preprocessing.py.

These specifically guard against the leakage this code used to have: fitting an imputation
statistic (median/mode) on the test split instead of reusing the value already fitted on
training. See docs/CHANGES.md.
"""
import numpy as np
import pandas as pd

from preprocessing import (
    fit_imputation_values,
    apply_imputation,
    impute_raw,
    columns_needing_missing_indicator,
    add_missing_indicators,
)


def test_fit_imputation_values_uses_only_the_given_frame():
    X_train = pd.DataFrame({"age": [50.0, 60.0, np.nan, 70.0]})
    fill_values = fit_imputation_values(X_train, num_cols=["age"], cat_cols=[])
    assert fill_values["age"] == 60.0  # median of [50, 60, 70]


def test_apply_imputation_does_not_recompute_statistics_from_test_split():
    """The core guarantee: the test split's own values must never influence the fill value
    applied to it. Here the test split's median, if it were (wrongly) fit on itself, would be
    very different from the training median — apply_imputation must use the training one."""
    X_train = pd.DataFrame({"age": [50.0, 52.0, 54.0, 56.0]})  # median 53.0
    X_test = pd.DataFrame({"age": [np.nan, 900.0, 900.0, 900.0]})  # median of non-missing: 900.0

    fill_values = fit_imputation_values(X_train, num_cols=["age"], cat_cols=[])
    X_test_imputed = apply_imputation(X_test, fill_values)

    assert X_test_imputed["age"].iloc[0] == 53.0  # the training median, not 900.0
    assert not X_test_imputed["age"].isna().any()


def test_apply_imputation_does_not_mutate_its_input():
    X = pd.DataFrame({"age": [50.0, np.nan]})
    fill_values = {"age": 50.0}
    apply_imputation(X, fill_values)
    assert X["age"].isna().sum() == 1  # the original frame is untouched


def test_impute_raw_matches_fit_then_apply_on_a_single_frame():
    X = pd.DataFrame({
        "age": [50.0, 60.0, np.nan],
        "sex": ["M", "M", np.nan],
    })
    combined = impute_raw(X, num_cols=["age"], cat_cols=["sex"])
    separate = apply_imputation(X, fit_imputation_values(X, num_cols=["age"], cat_cols=["sex"]))
    pd.testing.assert_frame_equal(combined, separate)


def test_columns_needing_missing_indicator_respects_threshold():
    X = pd.DataFrame({
        "mostly_missing": [np.nan, np.nan, np.nan, 1.0],   # 75% missing
        "rarely_missing": [1.0, 2.0, 3.0, np.nan],          # 25% missing
    })
    flagged = columns_needing_missing_indicator(X, ["mostly_missing", "rarely_missing"], threshold=0.30)
    assert flagged == ["mostly_missing"]


def test_add_missing_indicators_reflects_original_missingness_not_the_imputed_value():
    X = pd.DataFrame({"ca": [0.0, np.nan, 2.0]})
    X_flagged = add_missing_indicators(X, ["ca"])
    assert list(X_flagged["ca_missing"]) == [0, 1, 0]
    # the original column is untouched by add_missing_indicators: imputation is a later, separate step
    assert X_flagged["ca"].isna().sum() == 1


def test_add_missing_indicators_does_not_mutate_its_input():
    X = pd.DataFrame({"ca": [0.0, np.nan]})
    add_missing_indicators(X, ["ca"])
    assert "ca_missing" not in X.columns

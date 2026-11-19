"""Tests for the imputation helpers in preprocessing.py.

Imputation is now used only for the UMAP/heatmap visualization copy of the training split (the
records that get embedded keep their missing values). These tests still guard against fitting an
imputation statistic on a frame other than the one it is meant to come from. See docs/CHANGES.md.
"""
import numpy as np
import pandas as pd

from preprocessing import (
    fit_imputation_values,
    apply_imputation,
    impute_raw,
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

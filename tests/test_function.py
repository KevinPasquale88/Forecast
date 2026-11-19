"""Tests for the shared utilities in function.py, and for the multiple-comparison correction in
statisticaltest.py."""
import numpy as np
import pytest

from function import get_output_dirs, optimal_f1_threshold, out_of_fold_threshold, results, models_all
from statisticaltest import _benjamini_hochberg


def test_get_output_dirs_rejects_unknown_dataset():
    with pytest.raises(ValueError):
        get_output_dirs("not_a_real_dataset")


def test_results_dict_has_exactly_one_entry_per_configured_model():
    """Regression test for the bug this replaced: `results` used to be hand-initialized with
    only 4 of the (currently) 7 configured models, so it could silently drift out of sync with
    models_all. It must always match exactly, in both directions."""
    expected = {m["model_name"] for m in models_all}
    assert set(results.keys()) == expected


def test_optimal_f1_threshold_on_perfectly_separated_scores():
    y_true = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    y_score = np.array([0.1, 0.2, 0.15, 0.05, 0.9, 0.8, 0.95, 0.85])
    tau = optimal_f1_threshold(y_true, y_score)
    # any threshold in this range perfectly separates the two classes
    assert 0.2 < tau <= 0.8


def test_optimal_f1_threshold_returns_a_valid_probability():
    rng = np.random.default_rng(42)
    y_true = rng.integers(0, 2, 50)
    y_score = rng.random(50)
    tau = optimal_f1_threshold(y_true, y_score)
    assert 0.0 <= tau <= 1.0


def test_benjamini_hochberg_never_increases_the_smallest_p_value_rank_order():
    """BH-adjusted p-values must preserve the original rank order and never be smaller than the
    raw p-value they came from (the correction only ever makes things harder to call significant,
    never easier)."""
    raw = np.array([0.001, 0.20, 0.03, 0.049, 0.5])
    adjusted = _benjamini_hochberg(raw)
    assert len(adjusted) == len(raw)
    assert np.all(adjusted >= raw - 1e-12)
    # the smallest raw p-value must still be among the smallest adjusted ones
    assert np.argmin(raw) == np.argmin(adjusted)


def test_benjamini_hochberg_handles_empty_input():
    assert len(_benjamini_hochberg(np.array([]))) == 0


def test_out_of_fold_threshold_returns_a_valid_probability_on_imbalanced_data():
    rng = np.random.default_rng(0)
    y = np.r_[np.zeros(180, dtype=int), np.ones(20, dtype=int)]
    X = rng.normal(size=(200, 5)) + y[:, None] * 1.5
    tau = out_of_fold_threshold(X, y)
    assert 0.0 < tau < 1.0
    # with ~10% prevalence the F1-optimal threshold must sit well below 0.5
    assert tau < 0.5


def test_load_diabetes130_keeps_none_category_one_encounter_per_patient_and_no_hospice():
    import pandas as pd
    from function import load_diabetes130, hospice_or_death_discharge_ids

    df = load_diabetes130(sample_size=None)
    assert not df["discharge_disposition_id"].isin(hospice_or_death_discharge_ids).any()
    assert (df["max_glu_serum"] == "None").any()
    assert df["max_glu_serum"].isna().sum() == 0
    raw = pd.read_csv(
        "datasets/diabetes+130-us+hospitals+for+years+1999-2008/diabetic_data.csv",
        usecols=["patient_nbr", "discharge_disposition_id"],
    )
    kept = raw[~raw["discharge_disposition_id"].isin(hospice_or_death_discharge_ids)]
    assert len(df) == kept["patient_nbr"].nunique()


def test_fit_classifier_picks_C_from_grid_and_is_scale_invariant():
    """The probe standardizes its inputs, so multiplying every embedding by a constant (unit-norm
    Ollama vectors vs norm ~12 Hugging Face vectors) must not change C, threshold or scores."""
    from function import C_GRID, fit_classifier
    rng = np.random.default_rng(1)
    y = np.r_[np.zeros(120, dtype=int), np.ones(80, dtype=int)]
    X = rng.normal(size=(200, 10)) + y[:, None] * 0.8
    clf_a, tau_a, C_a = fit_classifier(X, y)
    clf_b, tau_b, C_b = fit_classifier(X * 12.0, y)
    assert C_a in C_GRID and C_a == C_b
    assert abs(tau_a - tau_b) < 1e-6
    assert np.allclose(clf_a.predict_proba(X)[:, 1], clf_b.predict_proba(X * 12.0)[:, 1], atol=1e-6)

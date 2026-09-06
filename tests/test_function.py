"""Tests for the shared utilities in function.py, and for the multiple-comparison correction in
statisticaltest.py."""
import numpy as np
import pytest

from function import get_output_dirs, optimal_f1_threshold, results, models_all
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

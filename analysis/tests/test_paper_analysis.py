from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from paper_analysis import (  # noqa: E402
    as_bool,
    bootstrap_ci,
    holm_adjust,
    paired_bootstrap_difference,
    same_size_random_box,
    wilcoxon_with_effect,
)


def test_as_bool_does_not_treat_false_string_as_true():
    assert as_bool("False") is False
    assert as_bool("True") is True


def test_bootstrap_ci_is_reproducible_and_centered_on_mean():
    first = bootstrap_ci([0, 1, 1, 0], n_boot=1000, seed=7)
    second = bootstrap_ci([0, 1, 1, 0], n_boot=1000, seed=7)
    assert first == second
    assert first["point"] == 0.5


def test_paired_bootstrap_uses_pairwise_difference():
    result = paired_bootstrap_difference([2, 3, 4], [1, 1, 1], n_boot=1000, seed=4)
    assert result["point"] == 2.0
    assert result["n"] == 3


def test_wilcoxon_effect_direction_is_positive_when_a_is_larger():
    result = wilcoxon_with_effect([2, 3, 4, 5], [1, 1, 1, 1])
    assert result["effect_size"] > 0
    assert result["n"] == 4


def test_holm_adjust_is_monotone_and_restores_input_order():
    adjusted = holm_adjust([0.04, 0.001, 0.03])
    assert adjusted == [0.06, 0.003, 0.06]


def test_matched_random_box_preserves_target_dimensions():
    target = (10.2, 20.1, 40.4, 60.3)
    random_box, overlap = same_size_random_box((200, 100), target, seed=42, image_id="0000007")
    assert random_box[2] - random_box[0] == 30
    assert random_box[3] - random_box[1] == 40
    assert overlap <= 0.05


def test_matched_random_box_handles_full_frame_target():
    random_box, overlap = same_size_random_box((20, 10), (0, 0, 20, 10), seed=1, image_id="1")
    assert random_box == (0, 0, 20, 10)
    assert math.isclose(overlap, 1.0)

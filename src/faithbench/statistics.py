"""Statistical utilities for benchmark reporting."""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable

import numpy as np


def bootstrap_ci(
    values: Iterable[float],
    statistic: Callable[[np.ndarray], float] = np.mean,
    *,
    n_boot: int = 10_000,
    ci: float = 0.95,
    seed: int = 20_260_716,
) -> dict[str, float | int]:
    """Return a reproducible percentile-bootstrap interval after dropping NaNs."""
    arr = np.asarray(list(values), dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return {"point": math.nan, "lo": math.nan, "hi": math.nan, "n": 0, "ci": ci}
    point = float(statistic(arr))
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, arr.size, size=(n_boot, arr.size))
    estimates = np.apply_along_axis(statistic, 1, arr[indices])
    alpha = (1.0 - ci) / 2.0
    lo, hi = np.quantile(estimates, [alpha, 1.0 - alpha])
    return {"point": point, "lo": float(lo), "hi": float(hi), "n": int(arr.size), "ci": ci}


def paired_bootstrap_difference(
    a: Iterable[float],
    b: Iterable[float],
    *,
    n_boot: int = 10_000,
    ci: float = 0.95,
    seed: int = 20_260_716,
) -> dict[str, float | int]:
    """Bootstrap the paired mean difference a - b."""
    aa = np.asarray(list(a), dtype=float)
    bb = np.asarray(list(b), dtype=float)
    keep = np.isfinite(aa) & np.isfinite(bb)
    diff = aa[keep] - bb[keep]
    return bootstrap_ci(diff, n_boot=n_boot, ci=ci, seed=seed)


def holm_adjust(p_values: Iterable[float]) -> list[float]:
    """Return Holm step-down adjusted p-values in the input order."""
    values = np.asarray(list(p_values), dtype=float)
    if values.size == 0:
        return []
    order = np.argsort(values)
    adjusted_sorted = np.empty(values.size, dtype=float)
    running_max = 0.0
    for rank, index in enumerate(order):
        running_max = max(running_max, (values.size - rank) * values[index])
        adjusted_sorted[rank] = min(1.0, running_max)
    adjusted = np.empty(values.size, dtype=float)
    adjusted[order] = adjusted_sorted
    return adjusted.tolist()


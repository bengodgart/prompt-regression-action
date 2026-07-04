"""Paired-difference statistics with a 95% confidence interval. Stdlib only.

We treat each example as a paired observation: the old prompt's score and the
new prompt's score on the same input. The quantity of interest is the mean
difference (new - old). If we can be 95% confident that difference is below
zero, the new prompt is a significant regression.

No scipy: we use a small t-critical table (two-sided, alpha 0.05) and fall back
to the normal approximation (1.96) for large samples.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# two-sided 95% t critical values by degrees of freedom
_T_TABLE = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
    8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145,
    15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
    21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056,
    27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042,
}


def _t_critical(df: int) -> float:
    if df <= 0:
        return float("inf")
    if df in _T_TABLE:
        return _T_TABLE[df]
    if df < 40:
        return 2.021
    if df < 60:
        return 2.000
    return 1.96


@dataclass
class PairedResult:
    n: int
    mean_diff: float          # mean of (new - old)
    ci_low: float
    ci_high: float
    old_mean: float
    new_mean: float
    test: str = "paired difference, 95% t confidence interval"

    @property
    def significant_regression(self) -> bool:
        # 95% confident the new prompt is worse
        return self.ci_high < 0.0


def paired_ci(old_scores: list[float], new_scores: list[float]) -> PairedResult:
    if len(old_scores) != len(new_scores):
        raise ValueError("old and new score lists must be the same length")
    n = len(old_scores)
    if n == 0:
        raise ValueError("no scored examples")

    diffs = [new - old for old, new in zip(old_scores, new_scores)]
    mean_diff = sum(diffs) / n
    old_mean = sum(old_scores) / n
    new_mean = sum(new_scores) / n

    if n == 1:
        return PairedResult(n, mean_diff, mean_diff, mean_diff, old_mean, new_mean)

    variance = sum((d - mean_diff) ** 2 for d in diffs) / (n - 1)
    sd = math.sqrt(variance)
    se = sd / math.sqrt(n)
    tcrit = _t_critical(n - 1)
    margin = tcrit * se
    return PairedResult(
        n=n,
        mean_diff=round(mean_diff, 4),
        ci_low=round(mean_diff - margin, 4),
        ci_high=round(mean_diff + margin, 4),
        old_mean=round(old_mean, 4),
        new_mean=round(new_mean, 4),
    )

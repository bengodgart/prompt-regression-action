"""promptreg: gate prompt changes in CI on a statistically significant regression.

Scores an old prompt against a new one over the same examples, computes the
paired score difference with a 95% confidence interval, and fails the build when
the new prompt is significantly worse. Deterministic core, stdlib-only; the
public demo runs offline with precomputed outputs. See README.md.
"""

__version__ = "0.1.0"

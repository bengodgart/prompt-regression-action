"""Smoke + unit tests for promptreg. Stdlib unittest, no deps.

Run: python -m unittest discover -s tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from promptreg.scorers import exact, contains, regex, get_scorer
from promptreg.stats import paired_ci
from promptreg.harness import run

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN = os.path.join(ROOT, "examples", "examples.jsonl")
REGRESS = os.path.join(ROOT, "examples", "examples-regression.jsonl")


class TestScorers(unittest.TestCase):
    def test_exact(self):
        self.assertEqual(exact("Positive", "positive"), 1.0)
        self.assertEqual(exact("negative", "positive"), 0.0)

    def test_contains(self):
        self.assertEqual(contains("the answer is positive", "positive"), 1.0)
        self.assertEqual(contains("nope", "positive"), 0.0)

    def test_regex(self):
        self.assertEqual(regex("score: 42", r"\d+"), 1.0)
        self.assertEqual(regex("no digits", r"\d+"), 0.0)
        self.assertEqual(regex("x", "("), 0.0)  # invalid regex -> 0, not a crash

    def test_unknown_scorer_raises(self):
        with self.assertRaises(ValueError):
            get_scorer("nope")


class TestStats(unittest.TestCase):
    def test_no_change_is_not_significant(self):
        r = paired_ci([1, 1, 1, 0, 0], [1, 1, 1, 0, 0])
        self.assertEqual(r.mean_diff, 0.0)
        self.assertFalse(r.significant_regression)

    def test_clear_regression_is_significant(self):
        old = [1.0] * 12
        new = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]  # 6 dropped
        r = paired_ci(old, new)
        self.assertLess(r.mean_diff, 0)
        self.assertLess(r.ci_high, 0)
        self.assertTrue(r.significant_regression)

    def test_mismatched_lengths_raise(self):
        with self.assertRaises(ValueError):
            paired_ci([1, 0], [1])


class TestHarness(unittest.TestCase):
    def test_clean_set_passes(self):
        report = run(CLEAN, scorer_name="exact", runner="precomputed")
        self.assertTrue(report.passed, msg=f"unexpected: {report.reasons}")
        self.assertEqual(report.stats.old_mean, 1.0)
        self.assertEqual(report.stats.new_mean, 1.0)

    def test_regression_set_fails(self):
        report = run(REGRESS, scorer_name="exact", runner="precomputed")
        self.assertFalse(report.passed)
        self.assertTrue(report.reasons)
        self.assertEqual(report.stats.old_mean, 1.0)
        self.assertEqual(report.stats.new_mean, 0.5)     # 6 of 12 dropped
        self.assertLess(report.stats.ci_high, 0)

    def test_allow_drop_tolerates_small_regression(self):
        # allowing a big drop makes even the regression set pass
        report = run(REGRESS, scorer_name="exact", runner="precomputed", allow_drop=0.9)
        self.assertTrue(report.passed, msg=f"unexpected: {report.reasons}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

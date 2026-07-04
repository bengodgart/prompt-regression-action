"""Run the regression comparison and decide pass/fail.

For each example: get the old-prompt output and the new-prompt output, score
each against the example's `expected`, then compute the paired confidence
interval on (new - old). The build fails when the new prompt is a significant
regression beyond an allowed drop.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .scorers import get_scorer
from .stats import paired_ci, PairedResult
from . import runner as runner_mod


@dataclass
class ExampleResult:
    index: int
    input: str
    expected: str
    old_output: str
    new_output: str
    old_score: float
    new_score: float


@dataclass
class RegressionReport:
    scorer: str
    runner: str
    allow_drop: float
    results: list[ExampleResult] = field(default_factory=list)
    stats: PairedResult | None = None
    reasons: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.reasons) == 0


def load_examples(path: str) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            examples.append(json.loads(line))
    if not examples:
        raise ValueError(f"no examples found in {path}")
    return examples


def _read(path: str | None) -> str:
    if not path:
        return ""
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def run(
    examples_path: str,
    old_prompt_path: str | None = None,
    new_prompt_path: str | None = None,
    scorer_name: str = "exact",
    runner: str = "precomputed",
    allow_drop: float = 0.0,
    model: str = "claude-sonnet-5",
) -> RegressionReport:
    examples = load_examples(examples_path)
    scorer = get_scorer(scorer_name)
    old_prompt = _read(old_prompt_path)
    new_prompt = _read(new_prompt_path)

    report = RegressionReport(scorer=scorer_name, runner=runner, allow_drop=allow_drop)

    for i, ex in enumerate(examples):
        ex_input = str(ex.get("input", ""))
        expected = str(ex.get("expected", ""))

        if runner == "precomputed":
            old_out, new_out = runner_mod.precomputed_outputs(ex)
        elif runner == "anthropic":  # pragma: no cover - optional network path
            old_out = runner_mod.anthropic_output(old_prompt, ex_input, model)
            new_out = runner_mod.anthropic_output(new_prompt, ex_input, model)
        else:
            raise ValueError(f"unknown runner '{runner}' (choices: precomputed, anthropic)")

        report.results.append(
            ExampleResult(
                index=i,
                input=ex_input,
                expected=expected,
                old_output=old_out,
                new_output=new_out,
                old_score=scorer(old_out, expected),
                new_score=scorer(new_out, expected),
            )
        )

    stats = paired_ci(
        [r.old_score for r in report.results],
        [r.new_score for r in report.results],
    )
    report.stats = stats

    # Fail rule: new is worse than old by more than the allowed drop, AND the
    # 95% CI is entirely below the allowed-drop line (statistically significant).
    threshold = -abs(allow_drop)
    if stats.mean_diff < threshold and stats.ci_high < threshold:
        report.reasons.append(
            f"significant regression: mean score change {stats.mean_diff:+.3f} "
            f"(95% CI [{stats.ci_low:+.3f}, {stats.ci_high:+.3f}]), "
            f"old {stats.old_mean:.3f} -> new {stats.new_mean:.3f}"
        )
    return report

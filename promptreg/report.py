"""Render a RegressionReport to text and to a GitHub-flavored Markdown summary."""

from __future__ import annotations

from .harness import RegressionReport


def render_text(report: RegressionReport) -> str:
    s = report.stats
    lines: list[str] = []
    lines.append("Prompt regression check")
    lines.append(f"scorer: {report.scorer}   runner: {report.runner}   allowed drop: {report.allow_drop}")
    lines.append("")
    lines.append(f"VERDICT: {'PASS' if report.passed else 'FAIL'}")
    for r in report.reasons:
        lines.append(f"  - {r}")
    lines.append("")
    if s:
        lines.append(f"examples (n)      {s.n}")
        lines.append(f"old mean score    {s.old_mean:.3f}")
        lines.append(f"new mean score    {s.new_mean:.3f}")
        lines.append(f"mean change       {s.mean_diff:+.3f}")
        lines.append(f"95% CI            [{s.ci_low:+.3f}, {s.ci_high:+.3f}]")
        lines.append(f"test              {s.test}")
    lines.append("")
    lines.append("Per-example (old -> new)")
    for r in report.results:
        flag = "  " if r.new_score >= r.old_score else "! "
        lines.append(f"  {flag}#{r.index} exp={r.expected!r}  old={r.old_score:.0f} new={r.new_score:.0f}")
    return "\n".join(lines)


def render_markdown(report: RegressionReport) -> str:
    s = report.stats
    md: list[str] = []
    verdict = "PASS ✅" if report.passed else "FAIL ❌"
    md.append(f"## Prompt regression check: {verdict}")
    md.append("")
    if report.reasons:
        for r in report.reasons:
            md.append(f"> {r}")
        md.append("")
    if s:
        md.append("| Metric | Value |")
        md.append("|---|---|")
        md.append(f"| Examples (n) | {s.n} |")
        md.append(f"| Old mean score | {s.old_mean:.3f} |")
        md.append(f"| New mean score | {s.new_mean:.3f} |")
        md.append(f"| Mean change (new - old) | {s.mean_diff:+.3f} |")
        md.append(f"| 95% confidence interval | [{s.ci_low:+.3f}, {s.ci_high:+.3f}] |")
        md.append(f"| Allowed drop | {report.allow_drop} |")
        md.append("")
    regressed = [r for r in report.results if r.new_score < r.old_score]
    if regressed:
        md.append(f"**{len(regressed)} example(s) got worse:**")
        md.append("")
        for r in regressed[:20]:
            md.append(f"- `#{r.index}` expected `{r.expected}` - new output: `{r.new_output[:60]}`")
    return "\n".join(md)

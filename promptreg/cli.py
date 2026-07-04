"""Command-line interface for promptreg.

Usage:
    python -m promptreg run --examples examples.jsonl [options]

Options:
    --examples PATH     JSONL, one example per line: {input, expected, output_old, output_new}
                        (output_old/new required for the default precomputed runner)
    --old PATH          old prompt template file (used by the anthropic runner)
    --new PATH          new prompt template file (used by the anthropic runner)
    --scorer NAME       exact | contains | regex   (default exact)
    --runner NAME       precomputed | anthropic     (default precomputed)
    --allow-drop F      tolerated mean score drop before failing, 0..1 (default 0.0)
    --model NAME        model for the anthropic runner (default claude-sonnet-5)
    --md PATH           write a Markdown summary (e.g. $GITHUB_STEP_SUMMARY)
    --quiet             suppress the text report on stdout

Exit code 0 on PASS, 1 on a significant regression (FAIL), 2 on a usage/IO error.
So it gates a pull request in CI.
"""

from __future__ import annotations

import argparse
import os
import sys

from .harness import run as run_harness
from . import report as report_mod


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="promptreg",
        description="Gate prompt changes on a statistically significant regression.",
    )
    sub = parser.add_subparsers(dest="command")
    r = sub.add_parser("run", help="run the regression comparison")
    r.add_argument("--examples", required=True)
    r.add_argument("--old", default=None)
    r.add_argument("--new", default=None)
    r.add_argument("--scorer", default="exact")
    r.add_argument("--runner", default="precomputed")
    r.add_argument("--allow-drop", type=float, default=0.0, dest="allow_drop")
    r.add_argument("--model", default="claude-sonnet-5")
    r.add_argument("--md", default=None)
    r.add_argument("--quiet", action="store_true")
    return parser


def run_cmd(args) -> int:
    try:
        report = run_harness(
            examples_path=args.examples,
            old_prompt_path=args.old,
            new_prompt_path=args.new,
            scorer_name=args.scorer,
            runner=args.runner,
            allow_drop=args.allow_drop,
            model=args.model,
        )
    except FileNotFoundError as exc:
        print(f"error: file not found: {exc.filename}", file=sys.stderr)
        return 2
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not args.quiet:
        print(report_mod.render_text(report))
    if args.md:
        parent = os.path.dirname(args.md)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(args.md, "a", encoding="utf-8") as handle:
            handle.write(report_mod.render_markdown(report) + "\n")
    return 0 if report.passed else 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        return run_cmd(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())

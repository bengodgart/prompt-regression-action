# PRD — prompt-regression-action (promptreg)

**One-liner (from brief 03):** A free, copy-paste GitHub Action plus a tiny harness that scores an old prompt against a new one on the same examples and fails the build when the change causes a significant regression, for any team that ships prompt edits by eyeballing a few completions and hoping.

**Usefulness (from brief 03):** Prompt changes ship with no evaluation gate; a cited one-line edit raised refusal rate 14 points. The drop-in CI template is described across sources but not offered as a free, installable artifact. A team adds one workflow file and gets a merge gate on prompt quality on day one, no platform signup.

## v1 scope (capped)

1. A workflow YAML a user drops into `.github/workflows/` (delivered as a composite Action + example workflow).
2. A harness that scores `prompt_old` vs `prompt_new` over a JSONL examples file with a pluggable scorer (exact / contains / regex; optional off-by-default LLM path).
3. A significance check: report n, the test used, the confidence interval, pass/fail against a threshold. Fail the build on a significant regression.
4. A demo showing the check red on a bad prompt edit and green after, with the CI wired in the repo's own workflows.

## Non-goals (NOT v1 - expansion paths, parked)

- Hosted eval platform, dashboard service, accounts, storing prompts/data.
- Multi-metric orchestration.
- LLM-judge scorer as a default (documented v2; v1 core is deterministic and offline).
- Online/production trace scoring (v2).

## Demo path (stranger sees value in under 2 minutes)

Clone -> `python -m promptreg run --examples examples/examples-regression.jsonl` -> FAIL, exit 1, with the CI and the six regressed examples shown. Run it on `examples/examples.jsonl` -> PASS, exit 0. In CI, the action posts a Markdown summary and fails the PR.

## Done when

- A stranger runs both example sets and sees FAIL/exit 1 then PASS/exit 0 in under 2 minutes.
- The significance math matches a hand-checked example (paste n, the test, the interval).
- README opens with the real failing output; no em-dashes in user-facing copy.
- Public repo + composite action.yml + example workflow; smoke tests pass; runs at $0 offline.

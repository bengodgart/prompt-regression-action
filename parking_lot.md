# Parking lot — prompt-regression-action

Ideas that surfaced during the v1 build. NOT in v1 scope.

- **LLM-judge scorer** - a rubric-based judge for open-ended outputs (uses the user's key, off by default). v2. The deterministic scorers + optional anthropic runner cover v1.
- **Online / production trace scoring** - score live traces on a schedule to catch drift, pairing offline gates with online monitoring (the pattern postings ask for).
- **Standalone CLI packaging on PyPI** - `pip install promptreg` beyond the repo; cross-links to portfolio brief 01's CI expansion.
- **More significance tests** - McNemar for paired binary outcomes, bootstrap CIs for skewed score distributions.
- **Cost line** - report token/dollar cost of a run when the anthropic runner is used (cross-links to portfolio brief 06).

Product-creep tripwire (doctrine T11): a hosted dashboard, accounts, or a "team plan" means it has become an app. Stop and park.

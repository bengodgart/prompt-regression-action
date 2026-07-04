# prompt-regression-action

**Regression tests for your prompts, as a GitHub check.** Add one workflow file and a pull request that makes your prompt worse fails the build, the same way a broken unit test does.

Most teams ship prompt changes by editing in a playground, eyeballing a few outputs, and merging. There is no gate. A one-line edit can quietly move your quality several points and you find out from users. This scores the old prompt against the new one on the same examples, computes the change with a 95% confidence interval, and fails the build only when the new prompt is a *statistically significant* regression.

The core is deterministic and dependency-free, so the demo and CI run offline at $0. You bring a model only when you want it to generate fresh outputs.

## What a failing check looks like

```
VERDICT: FAIL
  - significant regression: mean score change -0.500 (95% CI [-0.832, -0.168]), old 1.000 -> new 0.500

examples (n)      12
old mean score    1.000
new mean score    0.500
mean change       -0.500
95% CI            [-0.832, -0.168]
test              paired difference, 95% t confidence interval
```

That new prompt told the model to "always look for the bright side," and it started calling negative reviews positive. Six of twelve examples regressed. The build stops.

Point it at a clean example set and it passes with exit code 0. That is the whole gate: exit 1 on a significant regression, exit 0 otherwise.

## Use it in CI (the point)

```yaml
# .github/workflows/prompt-regression.yml
name: Prompt regression
on:
  pull_request:
    paths: ["prompts/**", "examples/**"]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - uses: bengodgart/prompt-regression-action@v1
        with:
          examples: examples/examples.jsonl
          scorer: exact
          allow-drop: "0.0"
```

The check posts a Markdown summary to the PR and fails it on a significant regression.

## The examples file

One JSON object per line. For the default offline runner, each row carries the outputs the two prompts produced:

```json
{"input": "This is terrible", "expected": "negative", "output_old": "negative", "output_new": "positive"}
```

Fields: `input`, `expected`, and (for the `precomputed` runner) `output_old` / `output_new`. Scorers: `exact`, `contains`, `regex`.

## Generating outputs with a model (optional)

If you would rather have the harness run the prompts itself, use the `anthropic` runner with prompt template files (`{input}` is the placeholder) and an `ANTHROPIC_API_KEY`. This is the only path that touches the network, and it is off by default:

```bash
python -m promptreg run --examples examples.jsonl \
  --runner anthropic --old prompts/old.txt --new prompts/new.txt --model claude-sonnet-5
```

## Run it locally

```bash
git clone https://github.com/bengodgart/prompt-regression-action
cd prompt-regression-action
python -m promptreg run --examples examples/examples-regression.jsonl   # FAILs, exit 1
python -m promptreg run --examples examples/examples.jsonl              # PASSes, exit 0
```

Python 3.9+, standard library only.

## How "significant" is decided

Each example is a paired observation: the old prompt's score and the new prompt's score on the same input. The harness computes the mean difference (new minus old) and a 95% confidence interval using a paired t interval. If the whole interval sits below the allowed drop, the regression is significant and the build fails. A bare "the number went down" is not enough; the drop has to be beyond chance. Raise `allow-drop` to tolerate small movements.

## Tests

```bash
python -m unittest discover -s tests -v   # 10 tests, no dependencies
```

## Why I built it

I spent years writing regression tests as a QA engineer, then watched the AI world ship prompts with no tests at all. The advice to gate prompt changes in CI was everywhere as a blog post and nowhere as a thing you could install. So I built the installable version, with an honest significance test instead of a vibe.

## License

MIT. See [LICENSE](LICENSE).

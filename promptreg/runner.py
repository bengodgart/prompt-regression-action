"""Runners produce an output for a (prompt, example) pair.

Two modes:
- precomputed: the examples file already carries `output_old` and `output_new`
  (each produced by running the respective prompt). This is the default: it lets
  the demo and CI run fully offline at $0, and it lets anyone who already has
  outputs use the harness without wiring a model.
- anthropic: call the Claude API, templating the prompt with the example input.
  Lazy-imported and never touched in tests/CI. Requires ANTHROPIC_API_KEY.

The prompt template uses `{input}` as the placeholder for the example input.
"""

from __future__ import annotations

from typing import Any


def render(template: str, example_input: str) -> str:
    return template.replace("{input}", example_input)


def precomputed_outputs(example: dict[str, Any]) -> tuple[str, str]:
    """Return (old_output, new_output) from a precomputed example row."""
    if "output_old" not in example or "output_new" not in example:
        raise ValueError(
            "precomputed runner needs 'output_old' and 'output_new' in each example"
        )
    return str(example["output_old"]), str(example["output_new"])


def anthropic_output(prompt_template: str, example_input: str, model: str) -> str:
    """Call the Claude API for one output. Lazy import; not used in CI/tests."""
    import os

    try:
        import anthropic  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional path
        raise RuntimeError(
            "anthropic runner needs the 'anthropic' package: pip install anthropic"
        ) from exc

    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:  # pragma: no cover - optional path
        raise RuntimeError("anthropic runner needs ANTHROPIC_API_KEY in the environment")

    client = anthropic.Anthropic(api_key=key)
    message = client.messages.create(
        model=model,
        max_tokens=256,
        messages=[{"role": "user", "content": render(prompt_template, example_input)}],
    )
    return "".join(block.text for block in message.content if getattr(block, "type", "") == "text")

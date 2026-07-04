"""Scorers: turn (output, expected) into a 0..1 score.

Deterministic scorers only in v1, so the whole thing runs offline with no API.
An LLM-judge scorer is a documented v2 expansion (see parking_lot.md), kept out
of v1 so nothing here needs a key or the network.
"""

from __future__ import annotations

import re
from typing import Callable

Scorer = Callable[[str, str], float]


def _norm(text: str) -> str:
    return (text or "").strip().lower()


def exact(output: str, expected: str) -> float:
    return 1.0 if _norm(output) == _norm(expected) else 0.0


def contains(output: str, expected: str) -> float:
    return 1.0 if _norm(expected) in _norm(output) else 0.0


def regex(output: str, expected: str) -> float:
    try:
        return 1.0 if re.search(expected, output or "") else 0.0
    except re.error:
        return 0.0


SCORERS: dict[str, Scorer] = {
    "exact": exact,
    "contains": contains,
    "regex": regex,
}


def get_scorer(name: str) -> Scorer:
    if name not in SCORERS:
        raise ValueError(f"unknown scorer '{name}'. choices: {', '.join(SCORERS)}")
    return SCORERS[name]

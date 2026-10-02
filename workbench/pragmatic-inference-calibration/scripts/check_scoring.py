#!/usr/bin/env python3
"""Adversarial checks: ambiguity, explanation lists, and full-data oracle scoring."""
import json
import sys
from scoring import parse_choice, summarize

choices = list("ABCDE")
for c in choices:
    for fmt in ["{}", "({}) Explanation", "Answer: {}", "The correct answer is: ({})"]:
        assert parse_choice(fmt.format(c), choices) == c, fmt.format(c)
for text in ["No clear response", "Could be (A), could be (B).", "(A) or (B)"]:
    assert parse_choice(text, choices) is None, text
assert parse_choice("(A) first\n(B) second\nThus, the most appropriate meaning is:\n(A) first", choices) == "A"
assert parse_choice("Let's analyze:\n(A) first\n(B) second\nTherefore, the correct answer is (B).", choices) == "B"
assert parse_choice(r"(A) text (B) text. Therefore: \boxed{B}", choices) == "B"
assert parse_choice(r"Therefore: \boxed{\text{E}}", choices) == "E"
assert parse_choice("따라서 가장 적절한 의미는 (A)입니다.", choices) == "A"
assert parse_choice("Somit wähle ich Option (B).", choices) == "B"
rows = [json.loads(s) for s in open(sys.argv[1])]
for r in rows:
    r["prediction"] = parse_choice(f"({r['gold']})", r["choices"])
assert summarize(rows)["all"]["accuracy"] == 1
for r in rows:
    wrong = next(c for c in r["choices"] if c != r["gold"])
    r["prediction"] = parse_choice(f"({wrong})", r["choices"])
assert summarize(rows)["all"]["accuracy"] == 0
print(f"parser adversarial fixtures and {len(rows)} oracle/wrong-label round trips passed")

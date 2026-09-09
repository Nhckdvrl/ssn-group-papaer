#!/usr/bin/env python3
"""Frozen positive and refusal controls for the CPC18 terminal parser."""

from cpc18_common import parse_terminal_choice


POSITIVE = {
    "A": [
        "A",
        "I'll choose... A.",
        "I'm going with A.",
        "I will choose: A",
        "The final answer is option A.",
        "analysis</think>\n\\boxed{A}",
    ],
    "B": [
        "B.",
        "I'll select B.",
        "Going with B",
        "Final choice: B",
        "analysis</think>\nThe answer is B.",
    ],
}

NEGATIVE = [
    "I cannot choose between A or B.",
    "Please provide probabilities for Option A and Option B.",
    "A and B have the same observed average, so either is possible.",
    "analysis without a closed reasoning delimiter",
]


def main():
    for expected, cases in POSITIVE.items():
        for text in cases:
            require_closed = "</think>" in text
            observed, _ = parse_terminal_choice(text, require_closed)
            assert observed == expected, (text, expected, observed)
    for text in NEGATIVE:
        observed, _ = parse_terminal_choice(text)
        assert observed is None, (text, observed)
    print(f"parser controls passed: {sum(map(len, POSITIVE.values()))} positive, {len(NEGATIVE)} negative")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Frozen positive and refusal controls for the CPC18 terminal parser."""

from cpc18_common import (
    is_decision_segment,
    parse_terminal_choice,
    strip_terminal_conclusion,
)


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
    assert not is_decision_segment("I have to choose between A and B.")
    assert not is_decision_segment("We need to select between option A and option B.")
    assert not is_decision_segment("Alright, so I have to choose between A and B.")
    assert is_decision_segment("After comparing them, I choose option A.")
    assert is_decision_segment("Therefore, B is best.")
    stripped, removed = strip_terminal_conclusion(
        "I have to choose between A and B. The expected values differ. I choose A."
    )
    assert stripped == "I have to choose between A and B. The expected values differ."
    assert removed == ["I choose A."]
    print(
        f"parser controls passed: {sum(map(len, POSITIVE.values()))} positive, "
        f"{len(NEGATIVE)} negative; stripping controls passed: 6"
    )


if __name__ == "__main__":
    main()
